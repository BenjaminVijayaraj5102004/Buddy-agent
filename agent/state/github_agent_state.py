"""Structured state and output models for GitHub Operations Agent."""

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class GitHubAgentOutput(BaseModel):
    """Structured output produced by GitHub Agent."""

    operation: str = Field(
        description="Type of GitHub operation performed (e.g. issue_write, search_code, create_pull_request).",
    )
    repository: Optional[str] = Field(
        default=None,
        description="Target GitHub repository (owner/repo).",
    )
    resource_id: Optional[str] = Field(
        default=None,
        description="Identifier or URL of the created/queried resource (e.g. issue number #12, PR URL).",
    )
    summary: str = Field(
        description="Precise summary of the GitHub action taken.",
    )
    status: Literal["success", "failed"] = Field(
        default="success",
        description="Outcome of the GitHub operation.",
    )
