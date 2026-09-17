from typing import Any
from strands.models.ollama import OllamaModel
from agent.config import settings


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


# Default Ollama model instance for agents
default_model = get_ollama_model()
model = default_model