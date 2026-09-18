"""State and structured output models for all Buddy agents."""

from agent.state.buddy_state import BuddyAgentOutput
from agent.state.api_manager_state import APIManagerOutput, APIEndpointSpec
from agent.state.rest_agent_state import RESTAgentOutput, RouteInfo
from agent.state.sam_cli_state import SAMCLIAgentOutput
from agent.state.github_agent_state import GitHubAgentOutput

__all__ = [
    "BuddyAgentOutput",
    "APIManagerOutput",
    "APIEndpointSpec",
    "RESTAgentOutput",
    "RouteInfo",
    "SAMCLIAgentOutput",
    "GitHubAgentOutput",
]
