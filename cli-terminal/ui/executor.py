"""
Task Execution Engine for Buddy Agent
Directly connects user prompts to buddy.buddy.create_buddy_agent
with empathetic animation, live markdown streaming, token metrics tracking, and session preservation.
"""

import sys
import os
import io
import time
from contextlib import redirect_stdout
from typing import Optional

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from .config import (
    COLOR_PEACH, COLOR_MINT, COLOR_MUTED, COLOR_ROSE, COLOR_AMBER, COLOR_TEXT, VERSION
)
from .state import SessionState
from .animations import BuddyEmpathyComplimentsAnimation


def clean_agent_output(text: str) -> str:
    """Cleans and formats agent responses to ensure natural, clean markdown output without raw JSON dumps or thinking scratchpads."""
    import re
    import json

    if not text:
        return ""

    # Remove reasoning/thinking tags
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

    # If the response is a JSON string or contains a JSON code block
    trimmed = cleaned.strip()
    if (trimmed.startswith("{") and trimmed.endswith("}")) or (
        trimmed.startswith("```json") and trimmed.endswith("```")
    ) or (
        trimmed.startswith("```") and trimmed.endswith("```")
    ):
        try:
            json_str = trimmed
            if json_str.startswith("```json"):
                json_str = json_str[7:-3].strip()
            elif json_str.startswith("```"):
                json_str = json_str[3:-3].strip()

            data = json.loads(json_str)
            if isinstance(data, dict):
                lines = []
                if "summary" in data:
                    lines.append(f"{data['summary']}\n")
                if "status" in data:
                    lines.append(f"**Status**: `{data['status']}`")
                if "file_path" in data:
                    lines.append(f"**File**: `{data['file_path']}`")
                if "created_endpoints" in data and isinstance(data["created_endpoints"], list):
                    lines.append("\n**Created Endpoints**:")
                    for ep in data["created_endpoints"]:
                        lines.append(f"- `{ep}`")
                if "schemas_defined" in data and isinstance(data["schemas_defined"], list):
                    lines.append("\n**Schemas Defined**:")
                    for sc in data["schemas_defined"]:
                        lines.append(f"- `{sc}`")
                if "tool" in data:
                    args = data.get("arguments", {})
                    task_desc = args.get("task_description", "")
                    if task_desc:
                        lines.append(f"**Delegated Task**: `{data.get('tool')}`\n\n{task_desc}")

                if lines:
                    return "\n".join(lines).strip()
        except Exception:
            pass

    return cleaned


def execute_agent_task(
    prompt: str,
    session: SessionState,
    console: Optional[Console] = None,
) -> None:
    """
    Executes the user prompt by invoking buddy.buddy.create_buddy_agent in real time,
    with streamed output, metrics tracking, and session ID copy banner.
    """
    if console is None:
        console = Console()

    # Step 1: Connect directly to real buddy.buddy agent instance
    agent_response = None
    real_agent_used = False
    in_tokens = 0
    out_tokens = 0
    execution_error = None

    try:
        active_agent = session.get_agent()
        if active_agent is not None:
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                result = active_agent(prompt)
            raw_str = str(result) if result is not None else ""
            agent_response = raw_str or stdout_capture.getvalue().strip()
            real_agent_used = True

            if hasattr(result, "metrics") and hasattr(result.metrics, "accumulated_usage"):
                in_tokens = result.metrics.accumulated_usage.get("inputTokens", 0)
                out_tokens = result.metrics.accumulated_usage.get("outputTokens", 0)
    except Exception as ex:
        execution_error = str(ex)

    cleaned_response = clean_agent_output(agent_response or "")

    if not cleaned_response:
        markdown_body = f"""
> [!WARNING]
> **Live Satellite Agent Notice**: Could not complete request via `{session.model_key}`.
> **Error**: `{execution_error or 'Unknown agent execution failure'}`
>
> *Please check that your API credentials or local model server are running, or use `/model` to switch to Groq.*
"""
    else:
        markdown_body = cleaned_response

    console.print(f"\n🧸 [bold {COLOR_PEACH}]Buddy >[/bold {COLOR_PEACH}]")
    console.print(Markdown(markdown_body.strip(), code_theme="ansi_dark"))
    console.print()


    # Step 3: Minimal Metrics Footer & Copyable Session ID (Preserved for future demo presentation)
    # if in_tokens == 0:
    #     in_tokens = len(prompt.split()) * 20 + 850
    # if out_tokens == 0:
    #     out_tokens = len(markdown_body.split()) * 4 + 40
    #
    # session.messages_count += 1
    # session.total_input_tokens += in_tokens
    # session.total_output_tokens += out_tokens
    #
    # source_tag = f"Live Strands Agent ({session.model_key})" if real_agent_used else "Agent Offline"
    # console.print(
    #     f"\n[dim {COLOR_MUTED}][METRICS][/dim {COLOR_MUTED}] "
    #     f"[dim]📥 In: {in_tokens:,} tokens  |  📤 Out: {out_tokens:,} tokens  |  "
    #     f"⚡ Engine: {source_tag}  |  🧸 Status: {'200 OK' if real_agent_used else '503 Error'}[/dim]"
    # )
    # console.print(
    #     f"[bold {COLOR_MINT}]💾 Active Session UUID:[/] [bold #38bdf8]{session.session_id}[/bold #38bdf8] [dim](Copy to resume anytime)[/dim]\n"
    # )
