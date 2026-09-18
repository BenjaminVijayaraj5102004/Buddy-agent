import logging
import os
from typing import Optional

from strands.telemetry import StrandsTelemetry, get_tracer
from agent.config import settings

logger = logging.getLogger(__name__)


def setup_langsmith_tracing(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    project_name: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Optional[StrandsTelemetry]:
    """Configure OpenTelemetry tracing in Strands to export spans directly to LangSmith.

    Args:
        api_key: LangSmith API key (falls back to settings.LANGSMITH_API_KEY or LANGCHAIN_API_KEY).
        endpoint: OTLP endpoint (defaults to settings.LANGSMITH_ENDPOINT or https://api.smith.langchain.com/otel/v1/traces).
        project_name: LangSmith project name (defaults to settings.LANGSMITH_PROJECT or LANGCHAIN_PROJECT).
        enabled: Whether tracing is enabled (defaults to settings.LANGSMITH_TRACING).

    Returns:
        Configured StrandsTelemetry instance if successful, None otherwise.
    """
    is_enabled = settings.LANGSMITH_TRACING if enabled is None else enabled
    if not is_enabled:
        logger.info("LangSmith tracing is disabled via configuration.")
        return None

    key = (
        api_key
        or settings.LANGSMITH_API_KEY
        or os.getenv("LANGSMITH_API_KEY", "")
        or os.getenv("LANGCHAIN_API_KEY", "")
    )
    target_endpoint = (
        endpoint
        or settings.LANGSMITH_ENDPOINT
        or os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com/otel/v1/traces")
    )
    project = (
        project_name
        or settings.LANGSMITH_PROJECT
        or os.getenv("LANGSMITH_PROJECT", "")
        or os.getenv("LANGCHAIN_PROJECT", "sdk")
    )

    if not key:
        logger.warning(
            "LangSmith API Key is not set. Add LANGSMITH_API_KEY to your .env file to enable tracing."
        )
        return None

    # Set up OTLP HTTP headers required by LangSmith
    headers = {
        "x-api-key": key,
        "x-project-name": project,
    }

    try:
        telemetry = StrandsTelemetry()
        telemetry.setup_otlp_exporter(
            endpoint=target_endpoint,
            headers=headers,
        )
        logger.info(
            "LangSmith OpenTelemetry tracing successfully configured for project '%s' -> %s",
            project,
            target_endpoint,
        )
        return telemetry
    except Exception as exc:
        logger.error("Failed to initialize LangSmith tracing: %s", exc)
        return None


# Global telemetry instance
telemetry: Optional[StrandsTelemetry] = setup_langsmith_tracing()

__all__ = ["setup_langsmith_tracing", "telemetry", "get_tracer"]
