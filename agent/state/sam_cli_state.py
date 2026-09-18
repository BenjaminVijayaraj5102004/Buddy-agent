"""Structured state and output models for SAM CLI Infrastructure Agent."""

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class SAMCLIAgentOutput(BaseModel):
    """Structured output produced by SAM CLI Agent."""

    framework: str = Field(
        default="AWS SAM",
        description="Infrastructure framework used.",
    )
    template_path: Optional[str] = Field(
        default=None,
        description="Path to the generated template.yaml or samconfig.toml file.",
    )
    resources_configured: List[str] = Field(
        default_factory=list,
        description="List of AWS CloudFormation / SAM resources declared.",
    )
    cli_command: Optional[str] = Field(
        default=None,
        description="Suggested or executed SAM CLI command (e.g. sam build, sam deploy).",
    )
    summary: str = Field(
        description="Precise summary of SAM infrastructure and deployment steps.",
    )
    status: Literal["success", "failed"] = Field(
        default="success",
        description="Outcome of SAM CLI operation.",
    )
