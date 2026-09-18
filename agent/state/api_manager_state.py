"""Structured state and output models for API Manager Agent."""

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class APIEndpointSpec(BaseModel):
    """Specification of an API endpoint to be created or managed."""

    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(
        description="HTTP method verb.",
    )
    path: str = Field(
        description="Endpoint URL path (e.g. /api/v1/users/register).",
    )
    summary: str = Field(
        description="Brief purpose of the endpoint.",
    )
    request_schema: Optional[str] = Field(
        default=None,
        description="Name of the Pydantic request model.",
    )
    response_schema: Optional[str] = Field(
        default=None,
        description="Name of the Pydantic response model.",
    )
    status_code: int = Field(
        default=200,
        description="Default HTTP response status code (e.g. 200, 201, 204).",
    )


class APIManagerOutput(BaseModel):
    """Structured output from API Manager passed down to REST Agent or returned to orchestrator."""

    domain: str = Field(
        default="REST API",
        description="Domain category.",
    )
    framework: str = Field(
        default="FastAPI",
        description="Web API framework (e.g. FastAPI, Flask).",
    )
    target_file_path: Optional[str] = Field(
        default=None,
        description="File path where API routes and schemas are written.",
    )
    endpoints: List[APIEndpointSpec] = Field(
        default_factory=list,
        description="List of endpoints specified or delegated.",
    )
    schemas_required: List[str] = Field(
        default_factory=list,
        description="List of required Pydantic v2 data models.",
    )
    task_summary: str = Field(
        description="Concise summary of requirements and delegation instructions.",
    )
    status: Literal["delegated", "completed", "failed"] = Field(
        default="completed",
        description="Management status of the API task.",
    )
