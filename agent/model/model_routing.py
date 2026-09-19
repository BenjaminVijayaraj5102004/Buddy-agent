"""Model routing module for dynamic LLM provider and model selection."""

from typing import Any
from strands.models.model import Model
from agent.config import settings
from agent.model.models import (
    get_bedrock_model,
    get_groq_model,
    get_ollama_model,
)

GROQ_DEFAULT_MODEL = "qwen/qwen3.8-27b"
OLLAMA_DEFAULT_MODEL = "llama3.1:8b"
BEDROCK_DEFAULT_MODEL = settings.BEDROCK_MODEL_ID or "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# Predefined Models Catalog
GROQ_MODELS = [
    {
        "id": "1",
        "key": "groq",
        "model_id": "qwen/qwen3.8-27b",
        "name": "Groq Cloud - Qwen 3.8 27B (Default)",
        "provider": "groq",
        "default": True,
        "description": "Ultra-fast Qwen 3.8 27B model on Groq Cloud LPUs",
    },
    {
        "id": "2",
        "key": "groq:openai/gpt-oss-120b",
        "model_id": "openai/gpt-oss-120b",
        "name": "Groq Cloud - GPT-OSS 120B",
        "provider": "groq",
        "default": False,
        "description": "Massive 120B open weights model on Groq Cloud",
    },
    {
        "id": "3",
        "key": "groq:meta-llama/llama-prompt-guard-2-22m",
        "model_id": "meta-llama/llama-prompt-guard-2-22m",
        "name": "Groq Cloud - Llama Prompt Guard 2 22M",
        "provider": "groq",
        "default": False,
        "description": "Lightweight safety & prompt guard model on Groq",
    },
]

OLLAMA_MODELS = [
    {
        "id": "4",
        "key": "ollama",
        "model_id": "llama3.1:8b",
        "name": "Ollama Local - Llama 3.1 8B (Default)",
        "provider": "ollama",
        "default": True,
        "description": "Local Llama 3.1 8B model running on Ollama",
    },
    {
        "id": "5",
        "key": "ollama:qwen:7b",
        "model_id": "qwen:7b",
        "name": "Ollama Local - Qwen 7B",
        "provider": "ollama",
        "default": False,
        "description": "Local Qwen 7B general-purpose model on Ollama",
    },
    {
        "id": "6",
        "key": "ollama:qwen2.5-coder:32b",
        "model_id": "qwen2.5-coder:32b",
        "name": "Ollama Local - Qwen 2.5 Coder 32B",
        "provider": "ollama",
        "default": False,
        "description": "High performance local coding model on Ollama",
    },
]

BEDROCK_MODELS = [
    {
        "id": "7",
        "key": "bedrock",
        "model_id": BEDROCK_DEFAULT_MODEL,
        "name": "AWS Bedrock - Claude 3.7 Sonnet",
        "provider": "bedrock",
        "default": True,
        "description": "Anthropic Claude 3.7 Sonnet hosted on AWS Bedrock",
    },
]

BYOM_PLACEHOLDER = {
    "id": "8",
    "key": "byom",
    "model_id": "custom",
    "name": "Bring Your Own Model (BYOM)",
    "provider": "custom",
    "default": False,
    "description": "Enter any custom model ID for Groq, Ollama, or Bedrock",
}

AVAILABLE_MODELS = GROQ_MODELS + OLLAMA_MODELS + BEDROCK_MODELS + [BYOM_PLACEHOLDER]

_active_model_key: str = "groq" if settings.GROQ_API_KEY else "ollama"


def get_active_model_key() -> str:
    """Return currently active model key."""
    global _active_model_key
    return _active_model_key


def set_active_model_key(key: str | None) -> str:
    """Set and normalize the active model key."""
    global _active_model_key
    if not key:
        return _active_model_key
    _active_model_key = key.strip()
    return _active_model_key


def list_available_models() -> list[dict[str, Any]]:
    """Return all available model configuration options."""
    return AVAILABLE_MODELS


def get_model_info(choice: str | None = None) -> dict[str, Any]:
    """Get metadata dictionary for the chosen model."""
    raw = (choice or _active_model_key or "").strip().lower()

    # Exact ID / Key matching
    for m in AVAILABLE_MODELS:
        if raw == m["id"].lower() or raw == m["key"].lower() or raw == m["model_id"].lower():
            return m

    # Partial name or keyword matching
    if raw in ("1", "groq", "groq-default", "qwen3.8", "qwen3.8-27b", "qwen/qwen3.8-27b"):
        return GROQ_MODELS[0]
    elif raw in ("2", "gpt-oss", "gpt-oss-120b", "openai/gpt-oss-120b"):
        return GROQ_MODELS[1]
    elif raw in ("3", "prompt-guard", "llama-prompt-guard", "meta-llama/llama-prompt-guard-2-22m"):
        return GROQ_MODELS[2]
    elif raw in ("4", "ollama", "ollama-default", "llama3.1", "llama3.1:8b", "local"):
        return OLLAMA_MODELS[0]
    elif raw in ("5", "qwen:7b", "qwen7b", "qwen-7b"):
        return OLLAMA_MODELS[1]
    elif raw in ("6", "qwen2.5-coder", "qwen2.5-coder:32b", "coder:32b", "coder32b"):
        return OLLAMA_MODELS[2]
    elif raw in ("7", "bedrock", "claude", "claude-3-7", "aws"):
        return BEDROCK_MODELS[0]
    elif raw.startswith("groq:"):
        custom_id = raw.split(":", 1)[1]
        return {
            "id": "custom",
            "key": raw,
            "model_id": custom_id,
            "name": f"Groq Cloud - {custom_id} (Custom)",
            "provider": "groq",
            "default": False,
            "description": f"Custom Groq model '{custom_id}'",
        }
    elif raw.startswith("ollama:"):
        custom_id = raw.split(":", 1)[1]
        return {
            "id": "custom",
            "key": raw,
            "model_id": custom_id,
            "name": f"Ollama Local - {custom_id} (Custom)",
            "provider": "ollama",
            "default": False,
            "description": f"Custom Ollama model '{custom_id}'",
        }
    elif raw.startswith("bedrock:"):
        custom_id = raw.split(":", 1)[1]
        return {
            "id": "custom",
            "key": raw,
            "model_id": custom_id,
            "name": f"AWS Bedrock - {custom_id} (Custom)",
            "provider": "bedrock",
            "default": False,
            "description": f"Custom Bedrock model '{custom_id}'",
        }

    # Fallback to default
    return GROQ_MODELS[0] if settings.GROQ_API_KEY else OLLAMA_MODELS[0]


def route_model(
    choice: str | None = None,
    model_id: str | None = None,
    **kwargs: Any,
) -> Model:
    """Route and instantiate the selected LLM based on user input.

    Supports numeric choices ("1"-"7"), provider prefixes ("groq:model", "ollama:model"),
    direct model names ("qwen:7b", "openai/gpt-oss-120b", "llama3.1:8b"), and custom BYOM models.

    Args:
        choice: Selection string (e.g., "1", "qwen:7b", "groq", "ollama:mistral:7b", "bedrock")
        model_id: Optional model ID override.
        **kwargs: Extra parameters passed to the model constructor.

    Returns:
        Configured Model instance.
    """
    raw_choice = (choice or _active_model_key or "").strip()
    raw_lower = raw_choice.lower()

    # Route 1: Groq Models
    if raw_lower in ("1", "groq", "groq-default", "qwen3.8", "qwen3.8-27b", "qwen/qwen3.8-27b"):
        set_active_model_key("groq")
        target_model = model_id or GROQ_DEFAULT_MODEL
        return get_groq_model(model_id=target_model, **kwargs)

    elif raw_lower in ("2", "gpt-oss", "gpt-oss-120b", "openai/gpt-oss-120b", "groq:openai/gpt-oss-120b"):
        set_active_model_key("groq:openai/gpt-oss-120b")
        target_model = model_id or "openai/gpt-oss-120b"
        return get_groq_model(model_id=target_model, **kwargs)

    elif raw_lower in (
        "3",
        "prompt-guard",
        "llama-prompt-guard",
        "meta-llama/llama-prompt-guard-2-22m",
        "groq:meta-llama/llama-prompt-guard-2-22m",
    ):
        set_active_model_key("groq:meta-llama/llama-prompt-guard-2-22m")
        target_model = model_id or "meta-llama/llama-prompt-guard-2-22m"
        return get_groq_model(model_id=target_model, **kwargs)

    elif raw_lower.startswith("groq:"):
        custom_model = raw_choice.split(":", 1)[1].strip()
        set_active_model_key(raw_choice)
        return get_groq_model(model_id=model_id or custom_model, **kwargs)

    # Route 2: Ollama Models
    elif raw_lower in ("4", "ollama", "ollama-default", "llama3.1", "llama3.1:8b", "local"):
        set_active_model_key("ollama")
        target_model = model_id or OLLAMA_DEFAULT_MODEL
        return get_ollama_model(model_id=target_model, **kwargs)

    elif raw_lower in ("5", "qwen:7b", "qwen7b", "qwen-7b", "ollama:qwen:7b"):
        set_active_model_key("ollama:qwen:7b")
        target_model = model_id or "qwen:7b"
        return get_ollama_model(model_id=target_model, **kwargs)

    elif raw_lower in ("6", "qwen2.5-coder", "qwen2.5-coder:32b", "coder:32b", "coder32b", "ollama:qwen2.5-coder:32b"):
        set_active_model_key("ollama:qwen2.5-coder:32b")
        target_model = model_id or "qwen2.5-coder:32b"
        return get_ollama_model(model_id=target_model, **kwargs)

    elif raw_lower.startswith("ollama:"):
        custom_model = raw_choice.split(":", 1)[1].strip()
        set_active_model_key(raw_choice)
        return get_ollama_model(model_id=model_id or custom_model, **kwargs)

    # Route 3: AWS Bedrock (Claude 3.7 Sonnet)
    elif raw_lower in ("7", "bedrock", "claude", "claude-3-7", "aws"):
        set_active_model_key("bedrock")
        target_model = model_id or BEDROCK_DEFAULT_MODEL
        return get_bedrock_model(model_id=target_model, **kwargs)

    elif raw_lower.startswith("bedrock:"):
        custom_model = raw_choice.split(":", 1)[1].strip()
        set_active_model_key(raw_choice)
        return get_bedrock_model(model_id=model_id or custom_model, **kwargs)

    # Heuristic detection for direct custom model input:
    elif "/" in raw_choice:  # E.g. "meta-llama/Llama-3-8b-chat-hf" -> Groq
        set_active_model_key(f"groq:{raw_choice}")
        return get_groq_model(model_id=raw_choice, **kwargs)

    elif ":" in raw_choice:  # E.g. "mistral:7b" -> Ollama
        set_active_model_key(f"ollama:{raw_choice}")
        return get_ollama_model(model_id=raw_choice, **kwargs)

    # Default fallback
    else:
        if settings.GROQ_API_KEY:
            set_active_model_key("groq")
            return get_groq_model(model_id=model_id or GROQ_DEFAULT_MODEL, **kwargs)
        else:
            set_active_model_key("ollama")
            return get_ollama_model(model_id=model_id or OLLAMA_DEFAULT_MODEL, **kwargs)

