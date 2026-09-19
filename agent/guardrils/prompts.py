"""Backwards-compatibility re-exporter for agent system prompts."""

from agent.guardrils.buddy_prompt import BUDDY_AGENT_BASE_PROMPT, BUDDY_AGENT_PROMPT
from agent.guardrils.api_manager_prompt import API_MANAGER_BASE_PROMPT, API_MANAGER_PROMPT
from agent.guardrils.rest_prompt import REST_AGENT_BASE_PROMPT, REST_AGENT_PROMPT
from agent.guardrils.sam_cli_prompt import SAM_CLI_AGENT_BASE_PROMPT, SAM_CLI_AGENT_PROMPT
from agent.guardrils.github_prompt import GITHUB_AGENT_BASE_PROMPT, GITHUB_AGENT_PROMPT

__all__ = [
    "BUDDY_AGENT_BASE_PROMPT",
    "BUDDY_AGENT_PROMPT",
    "API_MANAGER_BASE_PROMPT",
    "API_MANAGER_PROMPT",
    "REST_AGENT_BASE_PROMPT",
    "REST_AGENT_PROMPT",
    "SAM_CLI_AGENT_BASE_PROMPT",
    "SAM_CLI_AGENT_PROMPT",
    "GITHUB_AGENT_BASE_PROMPT",
    "GITHUB_AGENT_PROMPT",
]
