"""Structured state and output models for REST API Worker Agent."""

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class RouteInfo(BaseModel):
    """Details of a generated route handler."""

    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(
        description="HTTP method verb.",
    )
    path: str = Field(
        description="Route path.",
    )
    status_code: int = Field(
        default=200,
        description="HTTP response status code.",
    )
    handler_name: str = Field(
        description="Name of the Python route function.",
    )


class RESTAgentOutput(BaseModel):
    """Structured output produced by REST API Agent."""

    framework: str = Field(
        default="FastAPI",
        description="Framework used for routes and models.",
    )
    created_endpoints: List[RouteInfo] = Field(
        default_factory=list,
        description="List of route endpoints implemented.",
    )
    schemas_defined: List[str] = Field(
        default_factory=list,
        description="Names of Pydantic v2 schemas defined (e.g. UserCreate, UserResponse).",
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Path of the file created or modified via Text Editor MCP.",
    )
    summary: str = Field(
        description="Precise summary of code generated and actions taken.",
    )
    status: Literal["success", "failed"] = Field(
        default="success",
        description="Outcome of the REST generation task.",
    )
