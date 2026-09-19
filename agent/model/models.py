"""Model factory and provider exports for Strands agents."""

from typing import Any
from strands.models.model import Model
from strands.models.ollama import OllamaModel
from strands.models.bedrock import BedrockModel
from agent.model.groq_model import (
    GroqModel,
    acall_groq_model,
    call_groq_model,
)
from agent.config import settings


def get_groq_model(
    model_id: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
    **kwargs: Any,
) -> GroqModel:
    """Create and return a custom GroqModel instance configured for Strands Agent with max_retries=3."""
    return GroqModel(
        model_id=model_id or settings.GROQ_MODEL_ID,
        api_key=api_key or settings.GROQ_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=max_retries,
        **kwargs,
    )


def get_ollama_model(
    model_id: str = settings.OLLAMA_MODEL_ID,
    host: str = settings.OLLAMA_BASE_URL,
    **kwargs: Any,
) -> OllamaModel:
    """Create and return an OllamaModel instance configured for Strands Agent."""
    return OllamaModel(
        host=host,
        model_id=model_id,
        **kwargs,
    )


def get_bedrock_model(
    model_id: str = settings.BEDROCK_MODEL_ID,
    region_name: str = settings.AWS_REGION,
    **kwargs: Any,
) -> BedrockModel:
    """Create and return an Amazon Bedrock model instance configured for Strands Agent."""
    return BedrockModel(
        model_id=model_id,
        region_name=region_name,
        **kwargs,
    )


def get_model(
    provider: str | None = None,
    model_id: str | None = None,
    **kwargs: Any,
) -> Model:
    """Create and return a configured Model instance for Strands agents.

    Args:
        provider: "groq", "ollama", or "bedrock".
                  If None, auto-selects from active model key or default configured provider.
        model_id: Optional model identifier override.
        **kwargs: Extra parameters passed to the model constructor.

    Returns:
        A Model subclass instance (GroqModel, OllamaModel, or BedrockModel).
    """
    if provider is None:
        try:
            from agent.model.model_routing import get_active_model_key
            active_key = get_active_model_key()
        except ImportError:
            active_key = None
        target_provider = (active_key or ("groq" if settings.GROQ_API_KEY else "ollama")).lower()
    else:
        target_provider = provider.lower()

    if target_provider == "groq":
        return get_groq_model(model_id=model_id, **kwargs)
    elif target_provider == "ollama":
        return get_ollama_model(model_id=model_id or settings.OLLAMA_MODEL_ID, **kwargs)
    elif target_provider == "bedrock":
        return get_bedrock_model(model_id=model_id or settings.BEDROCK_MODEL_ID, **kwargs)
    else:
        raise ValueError(f"Unsupported model provider: {provider}. Use 'groq', 'ollama', or 'bedrock'.")


# Pre-instantiated instances
ollama_model = get_ollama_model()
groq_model = get_groq_model()
bedrock_model = get_bedrock_model()

# Default model used across all agents
default_model = groq_model if settings.GROQ_API_KEY else ollama_model
model = default_model