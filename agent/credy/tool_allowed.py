"""Allowed tools registry, categorization, and per-agent whitelist definitions.

Modularizes safe auto-approved tools, categorized tool registries, and per-agent
whitelists previously embedded in execution hooks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

logger = logging.getLogger("buddy.credy.tool_allowed")

# ============================================================================
# CATEGORIZED TOOL REGISTRIES
# ============================================================================

# Core Agent & Delegation tools
DELEGATION_TOOLS: Set[str] = {
    "api_manager",
    "call_api_manager",
    "sam_cli_agent",
    "call_sam_cli_agent",
    "REST_Agent",
    "call_rest_agent",
    "github_agent",
    "call_github_agent",
}

# Strands Skills Plugin tools
SKILL_TOOLS: Set[str] = {
    "skills",
    "load_skill",
    "agent_skills",
}

# Codebase inspection & GitHub MCP tools
GITHUB_TOOLS: Set[str] = {
    "search_code",
    "search_repositories",
    "get_file_contents",
}

# Session & conversation memory tools
MEMORY_TOOLS: Set[str] = {
    "search_memory",
    "add_memory",
}

# AWS SAM CLI operations
SAM_CLI_TOOLS: Set[str] = {
    "sam init",
    "sam build",
    "sam local invoke",
}

# Text Editor safe operations (creation, reading, incremental editing)
TEXT_EDITOR_SAFE_TOOLS: Set[str] = {
    "create_text_file",
    "get_text_file_contents",
    "insert_text_file_contents",
    "append_text_file_contents",
    "patch_text_file_contents",
}

# Dangerous / Destructive tools requiring strict HITL intervention or prohibition
DANGEROUS_TOOLS: Set[str] = {
    "delete_text_file_contents",
    "execute_command",
    "sam deploy",
    "sam deploy --guided",
}

# Master list of all auto-approved safe tools (bypasses HITL prompt)
DEFAULT_AUTO_APPROVED_TOOLS: Set[str] = (
    DELEGATION_TOOLS
    | SKILL_TOOLS
    | GITHUB_TOOLS
    | MEMORY_TOOLS
    | SAM_CLI_TOOLS
    | TEXT_EDITOR_SAFE_TOOLS
)

# ============================================================================
# PER-AGENT ALLOWED TOOL WHITELISTS
# ============================================================================

BUDDY_ALLOWED_TOOLS: Set[str] = (
    {
        "api_manager",
        "call_api_manager",
        "sam_cli_agent",
        "call_sam_cli_agent",
        "github_agent",
        "call_github_agent",
    }
    | SKILL_TOOLS
    | MEMORY_TOOLS
)

API_MANAGER_ALLOWED_TOOLS: Set[str] = (
    {
        "REST_Agent",
        "call_rest_agent",
    }
    | SKILL_TOOLS
)

SAM_CLI_ALLOWED_TOOLS: Set[str] = (
    SAM_CLI_TOOLS
    | TEXT_EDITOR_SAFE_TOOLS
    | SKILL_TOOLS
)

GITHUB_ALLOWED_TOOLS: Set[str] = (
    GITHUB_TOOLS
    | SKILL_TOOLS
)

REST_AGENT_ALLOWED_TOOLS: Set[str] = (
    TEXT_EDITOR_SAFE_TOOLS
    | GITHUB_TOOLS
    | SKILL_TOOLS
)

# Master agent-to-allowed-tools mapping
AGENT_ALLOWED_TOOLS_MAP: Dict[str, Set[str]] = {
    "Buddy": BUDDY_ALLOWED_TOOLS,
    "buddy_agent": BUDDY_ALLOWED_TOOLS,
    "API_MANAGER": API_MANAGER_ALLOWED_TOOLS,
    "api_manager": API_MANAGER_ALLOWED_TOOLS,
    "sam-cli-agent": SAM_CLI_ALLOWED_TOOLS,
    "sam_cli_agent": SAM_CLI_ALLOWED_TOOLS,
    "github-agent": GITHUB_ALLOWED_TOOLS,
    "github_agent": GITHUB_ALLOWED_TOOLS,
    "REST_API": REST_AGENT_ALLOWED_TOOLS,
    "rest_agent": REST_AGENT_ALLOWED_TOOLS,
}


# ============================================================================
# UTILITIES & QUERY HELPERS
# ============================================================================

def get_allowed_tools_for_agent(agent_name: str) -> Set[str]:
    """Returns the set of allowed tool names for the given agent."""
    if agent_name in AGENT_ALLOWED_TOOLS_MAP:
        return set(AGENT_ALLOWED_TOOLS_MAP[agent_name])
    for name, tools in AGENT_ALLOWED_TOOLS_MAP.items():
        if name.lower() == agent_name.lower():
            return set(tools)
    return set(DEFAULT_AUTO_APPROVED_TOOLS)


def is_tool_allowed(agent_name: str, tool_name: str) -> bool:
    """Checks whether an agent is permitted to invoke the specified tool."""
    allowed = get_allowed_tools_for_agent(agent_name)
    if tool_name in allowed:
        return True
    for item in allowed:
        if item.lower() == tool_name.lower():
            return True
    return False


def is_auto_approved(tool_name: str) -> bool:
    """Checks whether a tool is in the safe auto-approved whitelist."""
    return tool_name in DEFAULT_AUTO_APPROVED_TOOLS


def filter_agent_tools(agent_name: str, tools: List[Any]) -> List[Any]:
    """Filters a list of tools or MCP clients to only include those allowed for the agent."""
    allowed = get_allowed_tools_for_agent(agent_name)
    filtered = []
    for t in tools:
        t_name = getattr(t, "name", str(t))
        if t_name in allowed:
            filtered.append(t)
    return filtered


# ============================================================================
# STRANDS TOOL ALLOWED HOOK
# ============================================================================

class ToolAllowedHook(HookProvider):
    """Strands hook to ensure an agent only invokes tools within its authorized whitelist."""

    def __init__(
        self,
        agent_name: str = "Buddy",
        allowed_tools: Optional[Set[str]] = None,
    ) -> None:
        """Initialize ToolAllowedHook.

        Args:
            agent_name: Name of the agent using this hook.
            allowed_tools: Optional explicit set of allowed tools (defaults to agent whitelist).
        """
        self.agent_name = agent_name
        self.allowed_tools = (
            set(allowed_tools)
            if allowed_tools is not None
            else get_allowed_tools_for_agent(agent_name)
        )

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """Validates tool against the agent's whitelist before execution."""
        tool_name = ""
        if isinstance(event.tool_use, dict):
            tool_name = event.tool_use.get("name", "")
        elif event.selected_tool is not None:
            tool_name = getattr(event.selected_tool, "name", str(event.selected_tool))

        if not tool_name:
            return

        if not is_tool_allowed(self.agent_name, tool_name):
            logger.warning(
                "Unauthorized tool execution blocked: Agent '%s' attempted to use '%s'",
                self.agent_name,
                tool_name,
            )
            event.cancel_tool = (
                f"Unauthorized Tool: Tool '{tool_name}' is not in the allowed toolset "
                f"for agent '{self.agent_name}'. Execution blocked."
            )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """Register the BeforeToolCallEvent callback with HookRegistry."""
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)


__all__ = [
    "DELEGATION_TOOLS",
    "SKILL_TOOLS",
    "GITHUB_TOOLS",
    "MEMORY_TOOLS",
    "SAM_CLI_TOOLS",
    "TEXT_EDITOR_SAFE_TOOLS",
    "DANGEROUS_TOOLS",
    "DEFAULT_AUTO_APPROVED_TOOLS",
    "BUDDY_ALLOWED_TOOLS",
    "API_MANAGER_ALLOWED_TOOLS",
    "SAM_CLI_ALLOWED_TOOLS",
    "GITHUB_ALLOWED_TOOLS",
    "REST_AGENT_ALLOWED_TOOLS",
    "AGENT_ALLOWED_TOOLS_MAP",
    "get_allowed_tools_for_agent",
    "is_tool_allowed",
    "is_auto_approved",
    "filter_agent_tools",
    "ToolAllowedHook",
]
