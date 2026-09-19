"""Custom Groq Model provider and calling functions for Strands Agents SDK."""

import json
import logging
import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypeVar
from groq import AsyncGroq, Groq
from pydantic import BaseModel
from strands.models.model import BaseModelConfig, Model
from strands.types.content import Messages, SystemContentBlock
from strands.types.exceptions import ContextWindowOverflowException, ModelThrottledException
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolChoice, ToolSpec
from agent.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class GroqConfig(BaseModelConfig, total=False):
    """Configuration options for Groq models."""

    model_id: str
    api_key: str | None
    params: dict[str, Any] | None
    temperature: float | None
    max_tokens: int | None
    stream: bool


class GroqModel(Model):
    """Custom Groq model provider implementing the Strands Model interface with retry resilience."""

    def __init__(
        self,
        model_id: str | None = None,
        api_key: str | None = None,
        client: AsyncGroq | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_retries: int = 3,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self.model_id = model_id or getattr(settings, "GROQ_MODEL_ID", "qwen/qwen3.8-27b")
        self.api_key = api_key or getattr(settings, "GROQ_API_KEY", "")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.params = params or {}
        self.client_kwargs = kwargs
        self._custom_client = client
        self.config = {
            "model_id": self.model_id,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_retries": self.max_retries,
            "params": self.params,
        }

    def update_config(self, **model_config: Any) -> None:
        if "model_id" in model_config:
            self.model_id = model_config["model_id"]
        if "api_key" in model_config:
            self.api_key = model_config["api_key"]
        if "max_retries" in model_config:
            self.max_retries = model_config["max_retries"]
        self.config.update(model_config)

    def get_config(self) -> dict[str, Any]:
        return dict(self.config)

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[AsyncGroq, None]:
        if self._custom_client is not None:
            yield self._custom_client
        else:
            client_args: dict[str, Any] = {
                "max_retries": self.max_retries,
            }
            if self.api_key:
                client_args["api_key"] = self.api_key
            async with AsyncGroq(**client_args, **self.client_kwargs) as client:
                yield client

    def format_request_messages(
        self,
        messages: Messages,
        system_prompt: str | None = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
    ) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []

        # 1. System Prompt
        sys_text = ""
        if system_prompt:
            sys_text = system_prompt
        elif system_prompt_content:
            sys_text = "\n".join(b["text"] for b in system_prompt_content if "text" in b)
        if sys_text:
            formatted.append({"role": "system", "content": sys_text})

        # 2. Conversation Messages
        for msg in messages:
            role = msg["role"]
            contents = msg["content"]

            text_parts: list[str] = []
            tool_calls: list[dict[str, Any]] = []
            tool_results: list[dict[str, Any]] = []

            for block in contents:
                if "text" in block:
                    text_parts.append(block["text"])
                elif "toolUse" in block:
                    tu = block["toolUse"]
                    tool_calls.append({
                        "id": tu["toolUseId"],
                        "type": "function",
                        "function": {
                            "name": tu["name"],
                            "arguments": json.dumps(tu.get("input", {}), ensure_ascii=False) if isinstance(tu.get("input"), dict) else str(tu.get("input", "{}")),
                        },
                    })
                elif "toolResult" in block:
                    tr = block["toolResult"]
                    res_content = ""
                    for c in tr.get("content", []):
                        if "text" in c:
                            res_content += c["text"]
                        elif "json" in c:
                            res_content += json.dumps(c["json"], ensure_ascii=False)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tr["toolUseId"],
                        "content": res_content or "Success",
                    })

            msg_dict: dict[str, Any] = {"role": role}
            content_str = "\n".join(text_parts) if text_parts else None

            if role == "assistant":
                if content_str is not None:
                    msg_dict["content"] = content_str
                elif not tool_calls:
                    msg_dict["content"] = ""
                if tool_calls:
                    msg_dict["tool_calls"] = tool_calls
                formatted.append(msg_dict)
            else:
                if content_str is not None:
                    msg_dict["content"] = content_str
                    formatted.append(msg_dict)

            # Tool responses appended after message
            for tr_dict in tool_results:
                formatted.append(tr_dict)

        # Filter messages that have content or tool_calls or role tool
        return [m for m in formatted if "content" in m or "tool_calls" in m or m.get("role") == "tool"]

    def format_tools(self, tool_specs: list[ToolSpec] | None) -> list[dict[str, Any]]:
        if not tool_specs:
            return []
        tools: list[dict[str, Any]] = []
        for ts in tool_specs:
            tools.append({
                "type": "function",
                "function": {
                    "name": ts["name"],
                    "description": ts.get("description", ""),
                    "parameters": ts.get("inputSchema", {}).get("json", {"type": "object", "properties": {}}),
                },
            })
        return tools

    def format_chunk(self, event: dict[str, Any]) -> StreamEvent:
        match event["chunk_type"]:
            case "message_start":
                return {"messageStart": {"role": "assistant"}}
            case "content_start":
                if event.get("data_type") == "tool":
                    return {
                        "contentBlockStart": {
                            "start": {
                                "toolUse": {
                                    "name": event["data"]["name"],
                                    "toolUseId": event["data"]["id"],
                                }
                            }
                        }
                    }
                return {"contentBlockStart": {"start": {}}}
            case "content_delta":
                if event.get("data_type") == "tool":
                    return {
                        "contentBlockDelta": {
                            "delta": {
                                "toolUse": {
                                    "input": event["data"]["arguments"]
                                }
                            }
                        }
                    }
                if event.get("data_type") == "reasoning_content":
                    return {"contentBlockDelta": {"delta": {"reasoningContent": {"text": event["data"]}}}}
                return {"contentBlockDelta": {"delta": {"text": event["data"]}}}
            case "content_stop":
                return {"contentBlockStop": {}}
            case "message_stop":
                match event["data"]:
                    case "tool_calls":
                        return {"messageStop": {"stopReason": "tool_use"}}
                    case "length":
                        return {"messageStop": {"stopReason": "max_tokens"}}
                    case _:
                        return {"messageStop": {"stopReason": "end_turn"}}
            case "metadata":
                return {
                    "metadata": {
                        "usage": {
                            "inputTokens": getattr(event["data"], "prompt_tokens", 0),
                            "outputTokens": getattr(event["data"], "completion_tokens", 0),
                            "totalTokens": getattr(event["data"], "total_tokens", 0),
                        }
                    }
                }
            case _:
                return {}

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: ToolChoice | None = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamEvent, None]:
        formatted_messages = self.format_request_messages(
            messages, system_prompt=system_prompt, system_prompt_content=system_prompt_content
        )
        tools = self.format_tools(tool_specs)

        req_kwargs: dict[str, Any] = {
            "model": self.model_id,
            "messages": formatted_messages,
            "stream": True,
            **self.params,
        }
        if tools:
            req_kwargs["tools"] = tools
        if self.temperature is not None:
            req_kwargs["temperature"] = self.temperature
        if self.max_tokens is not None:
            req_kwargs["max_tokens"] = self.max_tokens

        for attempt in range(self.max_retries + 1):
            try:
                async with self._get_client() as client:
                    response = await client.chat.completions.create(**req_kwargs)

                    yield self.format_chunk({"chunk_type": "message_start"})

                    accumulated_tools: dict[int, dict[str, Any]] = {}
                    in_text_block = False
                    finish_reason = None
                    usage_info = None

                    async for chunk in response:
                        if hasattr(chunk, "usage") and chunk.usage:
                            usage_info = chunk.usage

                        if not getattr(chunk, "choices", None):
                            continue

                        choice = chunk.choices[0]
                        delta = getattr(choice, "delta", None)

                        if choice.finish_reason:
                            finish_reason = choice.finish_reason

                        if delta:
                            # Regular text (clean output without reasoning scratchpads)
                            if delta.content:
                                if not in_text_block:
                                    yield self.format_chunk({"chunk_type": "content_start", "data_type": "text"})
                                    in_text_block = True
                                yield self.format_chunk({"chunk_type": "content_delta", "data_type": "text", "data": delta.content})

                            # Tool calls
                            if delta.tool_calls:
                                for tc in delta.tool_calls:
                                    idx = tc.index
                                    if idx not in accumulated_tools:
                                        accumulated_tools[idx] = {
                                            "id": tc.id or "",
                                            "name": (tc.function.name if tc.function else "") or "",
                                            "arguments": (tc.function.arguments if tc.function else "") or "",
                                        }
                                    else:
                                        if tc.id:
                                            accumulated_tools[idx]["id"] += tc.id
                                        if tc.function and tc.function.name:
                                            accumulated_tools[idx]["name"] += tc.function.name
                                        if tc.function and tc.function.arguments:
                                            accumulated_tools[idx]["arguments"] += tc.function.arguments

                    # Close open text content block if any
                    if in_text_block:
                        yield self.format_chunk({"chunk_type": "content_stop", "data_type": "text"})


                    # Emit tool calls
                    if accumulated_tools:
                        for idx, tc_data in accumulated_tools.items():
                            yield self.format_chunk({
                                "chunk_type": "content_start",
                                "data_type": "tool",
                                "data": {
                                    "name": tc_data["name"],
                                    "id": tc_data["id"] or f"call_{idx}",
                                },
                            })
                            yield self.format_chunk({
                                "chunk_type": "content_delta",
                                "data_type": "tool",
                                "data": {
                                    "arguments": tc_data["arguments"],
                                },
                            })
                            yield self.format_chunk({"chunk_type": "content_stop", "data_type": "tool"})

                    stop_reason = "tool_calls" if accumulated_tools else (finish_reason or "end_turn")
                    yield self.format_chunk({"chunk_type": "message_stop", "data": stop_reason})

                    if usage_info:
                        yield self.format_chunk({"chunk_type": "metadata", "data": usage_info})

                    break  # Success

            except Exception as e:
                error_str = str(e).lower()
                is_retryable = (
                    "rate_limit" in error_str
                    or "429" in error_str
                    or "modelthrottled" in error_str
                    or "connection error" in error_str
                    or "connecterror" in error_str
                    or "timeout" in error_str
                    or "timed out" in error_str
                    or "service unavailable" in error_str
                    or "503" in error_str
                    or "502" in error_str
                    or "500" in error_str
                )
                if is_retryable and attempt < self.max_retries:
                    delay = (2 ** attempt) * 3.0
                    logger.warning(f"Groq stream error encountered ({e}) (attempt {attempt+1}/{self.max_retries}). Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                if "rate_limit" in error_str or "429" in error_str:
                    raise ModelThrottledException(str(e)) from e
                if "context_length" in error_str or "maximum context length" in error_str:
                    raise ContextWindowOverflowException(str(e)) from e
                raise

    async def structured_output(
        self, output_model: type[T], prompt: Messages, system_prompt: str | None = None, **kwargs: Any
    ) -> AsyncGenerator[dict[str, T | Any], None]:
        formatted_messages = self.format_request_messages(prompt, system_prompt=system_prompt)
        schema = output_model.model_json_schema()
        instruction = f"\n\nYou must respond strictly with a valid JSON object conforming to this schema:\n{json.dumps(schema)}"

        if formatted_messages and formatted_messages[0]["role"] == "system":
            formatted_messages[0]["content"] += instruction
        else:
            formatted_messages.insert(0, {"role": "system", "content": instruction})

        req_kwargs: dict[str, Any] = {
            "model": self.model_id,
            "messages": formatted_messages,
            "stream": False,
            "response_format": {"type": "json_object"},
            **self.params,
        }
        if self.temperature is not None:
            req_kwargs["temperature"] = self.temperature

        for attempt in range(self.max_retries + 1):
            try:
                async with self._get_client() as client:
                    response = await client.chat.completions.create(**req_kwargs)
                    content = response.choices[0].message.content or "{}"
                    parsed = output_model.model_validate_json(content)
                    yield {"output": parsed}
                    break
            except Exception as e:
                error_str = str(e).lower()
                is_retryable = (
                    "rate_limit" in error_str
                    or "429" in error_str
                    or "modelthrottled" in error_str
                    or "connection error" in error_str
                    or "connecterror" in error_str
                    or "timeout" in error_str
                    or "timed out" in error_str
                    or "service unavailable" in error_str
                    or "503" in error_str
                    or "502" in error_str
                    or "500" in error_str
                )
                if is_retryable and attempt < self.max_retries:
                    delay = (2 ** attempt) * 3.0
                    logger.warning(f"Groq structured_output error ({e}) (attempt {attempt+1}/{self.max_retries}). Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                if "rate_limit" in error_str or "429" in error_str:
                    raise ModelThrottledException(str(e)) from e
                if "context_length" in error_str or "maximum context length" in error_str:
                    raise ContextWindowOverflowException(str(e)) from e
                raise


def call_groq_model(
    prompt: str,
    system_prompt: str | None = None,
    model_id: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
    **kwargs: Any,
) -> str:
    """Synchronous function to invoke Groq model directly and return response text with retries."""
    key = api_key or getattr(settings, "GROQ_API_KEY", "")
    mid = model_id or getattr(settings, "GROQ_MODEL_ID", "qwen/qwen3.8-27b")
    client = Groq(api_key=key, max_retries=max_retries) if key else Groq(max_retries=max_retries)

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    req_args: dict[str, Any] = {
        "model": mid,
        "messages": messages,
        **kwargs,
    }
    if temperature is not None:
        req_args["temperature"] = temperature
    if max_tokens is not None:
        req_args["max_tokens"] = max_tokens

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(**req_args)
            return response.choices[0].message.content or ""
        except Exception as e:
            error_str = str(e).lower()
            is_retryable = (
                "rate_limit" in error_str
                or "429" in error_str
                or "connection error" in error_str
                or "connecterror" in error_str
                or "timeout" in error_str
                or "timed out" in error_str
                or "service unavailable" in error_str
                or "503" in error_str
                or "502" in error_str
                or "500" in error_str
            )
            if is_retryable and attempt < max_retries:
                delay = (2 ** attempt) * 3.0
                logger.warning(f"Groq sync error encountered ({e}) (attempt {attempt+1}/{max_retries}). Retrying in {delay:.1f}s...")
                time.sleep(delay)
                continue
            raise


async def acall_groq_model(
    prompt: str,
    system_prompt: str | None = None,
    model_id: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
    **kwargs: Any,
) -> str:
    """Asynchronous function to invoke Groq model directly and return response text with retries."""
    key = api_key or getattr(settings, "GROQ_API_KEY", "")
    mid = model_id or getattr(settings, "GROQ_MODEL_ID", "qwen/qwen3.8-27b")
    client = AsyncGroq(api_key=key, max_retries=max_retries) if key else AsyncGroq(max_retries=max_retries)

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    req_args: dict[str, Any] = {
        "model": mid,
        "messages": messages,
        **kwargs,
    }
    if temperature is not None:
        req_args["temperature"] = temperature
    if max_tokens is not None:
        req_args["max_tokens"] = max_tokens

    for attempt in range(max_retries + 1):
        try:
            response = await client.chat.completions.create(**req_args)
            return response.choices[0].message.content or ""
        except Exception as e:
            error_str = str(e).lower()
            is_retryable = (
                "rate_limit" in error_str
                or "429" in error_str
                or "connection error" in error_str
                or "connecterror" in error_str
                or "timeout" in error_str
                or "timed out" in error_str
                or "service unavailable" in error_str
                or "503" in error_str
                or "502" in error_str
                or "500" in error_str
            )
            if is_retryable and attempt < max_retries:
                delay = (2 ** attempt) * 3.0
                logger.warning(f"Groq async error encountered ({e}) (attempt {attempt+1}/{max_retries}). Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
                continue
            raise
