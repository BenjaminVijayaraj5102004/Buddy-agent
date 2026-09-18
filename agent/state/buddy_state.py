"""Structured state and output models for Buddy Master Agent."""

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class BuddyAgentOutput(BaseModel):
    """Structured output representation for Buddy Agent orchestration."""

    task_type: Literal[
        "api_endpoint",
        "github_operation",
        "sam_deployment",
        "general_query",
    ] = Field(
        description="The classified domain intent of the user prompt.",
    )
    target_agent: Optional[
        Literal["api_manager", "sam_cli_agent", "github_agent", "none"]
    ] = Field(
        default="none",
        description="The delegated sub-agent responsible for the task.",
    )
    summary: str = Field(
        description="A concise summary of what was accomplished or answered, optimized for minimal token size.",
    )
    framework: Optional[str] = Field(
        default=None,
        description="The technology or framework used (e.g. FastAPI, AWS SAM, GitHub REST).",
    )
    files_affected: List[str] = Field(
        default_factory=list,
        description="List of file paths created, modified, or inspected.",
    )
    status: Literal["success", "completed", "failed", "pending"] = Field(
        default="completed",
        description="Final execution status of the request.",
    )
    next_steps: Optional[List[str]] = Field(
        default=None,
        description="Optional recommendations or follow-up actions for the user.",
    )
