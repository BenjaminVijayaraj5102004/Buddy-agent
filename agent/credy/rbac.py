"""Role-Based Access Control (RBAC) governance for Buddy Agent system.

Configured Rules:
- User (e.g. Benjamin / Admin): Superuser with unrestricted access to ALL agents and tools.
- Buddy Agent: Orchestrator role permitted to access and delegate to all sub-agents
  (API Manager, SAM CLI Agent, GitHub Agent) as well as memory and skill tools.
- API Manager: Specialized agent permitted to delegate to REST Agent and manage API design.
- SAM CLI Agent: Permitted to access AWS SAM CLI MCP tools and text editor tools.
- GitHub Agent: Permitted to access GitHub MCP tools and repository inspection tools.
- REST Agent: Permitted to access GitHub REST MCP tools and text editor tools.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Set

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

logger = logging.getLogger("buddy.credy.rbac")


class Role(str, Enum):
    """System and agent roles for RBAC authorization."""

    # Superuser / Administrator roles
    ADMIN = "admin"
    BENJAMIN = "benjamin"
    SUPERUSER = "superuser"

    # Operator / Developer roles
    DEVELOPER = "developer"
    OPERATOR = "operator"

    # Agent roles
    AGENT_ORCHESTRATOR = "agent_orchestrator"  # Buddy Agent
    AGENT_API_MANAGER = "agent_api_manager"    # API Manager
    AGENT_SAM_CLI = "agent_sam_cli"            # SAM CLI Agent
    AGENT_GITHUB = "agent_github"              # GitHub Agent
    AGENT_REST = "agent_rest"                  # REST API Agent

    # Restricted roles
    GUEST = "guest"
    READ_ONLY = "read_only"


@dataclass(frozen=True)
class User:
    """Represents a human user or operator principal."""

    user_id: str
    username: str
    roles: Set[Role] = field(default_factory=set)

    @property
    def is_admin(self) -> bool:
        """Returns True if the user has superuser / admin privileges."""
        return any(
            role in (Role.ADMIN, Role.BENJAMIN, Role.SUPERUSER) for role in self.roles
        )


# Default built-in user identities
BENJAMIN_USER = User(
    user_id="benjamin",
    username="Benjamin V",
    roles={Role.ADMIN, Role.BENJAMIN, Role.SUPERUSER, Role.DEVELOPER},
)

GUEST_USER = User(
    user_id="guest",
    username="Guest User",
    roles={Role.GUEST, Role.READ_ONLY},
)


# Master mapping of agent names to their assigned Agent Role
AGENT_ROLE_MAPPING: Dict[str, Role] = {
    "Buddy": Role.AGENT_ORCHESTRATOR,
    "buddy_agent": Role.AGENT_ORCHESTRATOR,
    "API_MANAGER": Role.AGENT_API_MANAGER,
    "api_manager": Role.AGENT_API_MANAGER,
    "sam-cli-agent": Role.AGENT_SAM_CLI,
    "sam_cli_agent": Role.AGENT_SAM_CLI,
    "github-agent": Role.AGENT_GITHUB,
    "github_agent": Role.AGENT_GITHUB,
    "REST_API": Role.AGENT_REST,
    "rest_agent": Role.AGENT_REST,
}

# Role permissions: resources / agents / tools allowed per role
ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
    # Benjamin / Admin has wildcard access to all agents and all tools
    Role.ADMIN: {"*"},
    Role.BENJAMIN: {"*"},
    Role.SUPERUSER: {"*"},

    # Developer has access to all agents and development tools
    Role.DEVELOPER: {
        "Buddy",
        "API_MANAGER",
        "sam-cli-agent",
        "github-agent",
        "REST_API",
        "api_manager",
        "sam_cli_agent",
        "github_agent",
        "REST_Agent",
        "skills",
        "agent_skills",
        "load_skill",
        "search_memory",
        "add_memory",
        "search_code",
        "search_repositories",
        "get_file_contents",
        "create_text_file",
        "get_text_file_contents",
        "insert_text_file_contents",
        "append_text_file_contents",
        "patch_text_file_contents",
        "sam init",
        "sam build",
        "sam local invoke",
    },

    # Orchestrator (Buddy Agent) can delegate to all specialized agents and memory/skills
    Role.AGENT_ORCHESTRATOR: {
        "api_manager",
        "call_api_manager",
        "sam_cli_agent",
        "call_sam_cli_agent",
        "github_agent",
        "call_github_agent",
        "skills",
        "load_skill",
        "agent_skills",
        "search_memory",
        "add_memory",
    },

    # API Manager can delegate to REST Agent and manage API design
    Role.AGENT_API_MANAGER: {
        "REST_Agent",
        "call_rest_agent",
        "skills",
        "load_skill",
        "agent_skills",
    },

    # SAM CLI Agent can execute SAM operations and edit configuration files
    Role.AGENT_SAM_CLI: {
        "sam init",
        "sam build",
        "sam local invoke",
        "create_text_file",
        "get_text_file_contents",
        "insert_text_file_contents",
        "append_text_file_contents",
        "patch_text_file_contents",
        "skills",
        "load_skill",
        "agent_skills",
    },

    # GitHub Agent can query repository data and pull requests
    Role.AGENT_GITHUB: {
        "search_code",
        "search_repositories",
        "get_file_contents",
        "skills",
        "load_skill",
        "agent_skills",
    },

    # REST Agent can inspect code and generate schemas/routes in text files
    Role.AGENT_REST: {
        "create_text_file",
        "get_text_file_contents",
        "insert_text_file_contents",
        "append_text_file_contents",
        "patch_text_file_contents",
        "search_code",
        "get_file_contents",
        "skills",
        "load_skill",
        "agent_skills",
    },

    # Guest user can only read files and search memory
    Role.GUEST: {
        "get_file_contents",
        "get_text_file_contents",
        "search_memory",
    },
    Role.READ_ONLY: {
        "get_file_contents",
        "get_text_file_contents",
        "search_memory",
    },
}


class RBACAccessDeniedError(Exception):
    """Raised when an actor lacks sufficient RBAC privileges to access an agent or tool."""

    def __init__(self, subject: str, resource: str, role: Optional[str] = None) -> None:
        self.subject = subject
        self.resource = resource
        self.role = role
        super().__init__(
            f"RBAC Access Denied: Subject '{subject}' (Role: '{role or 'Unspecified'}') "
            f"is not authorized to access resource '{resource}'."
        )


class RBACManager:
    """Manages role assignments, permission evaluation, and authorization policies."""

    def __init__(
        self,
        role_permissions: Optional[Dict[Role, Set[str]]] = None,
        agent_role_mapping: Optional[Dict[str, Role]] = None,
    ) -> None:
        self.role_permissions = (
            dict(role_permissions) if role_permissions is not None else dict(ROLE_PERMISSIONS)
        )
        self.agent_role_mapping = (
            dict(agent_role_mapping)
            if agent_role_mapping is not None
            else dict(AGENT_ROLE_MAPPING)
        )

    def get_role_for_agent(self, agent_name: str) -> Optional[Role]:
        """Resolves the Role assigned to a specific agent name."""
        if agent_name in self.agent_role_mapping:
            return self.agent_role_mapping[agent_name]
        for name, role in self.agent_role_mapping.items():
            if name.lower() == agent_name.lower():
                return role
        return None

    def has_permission(self, subject: User | Role | str, resource: str) -> bool:
        """Checks if a User, Role, or Agent has permission to access a tool or sub-agent."""
        # 1. Subject is a User object
        if isinstance(subject, User):
            if subject.is_admin:
                return True
            for role in subject.roles:
                if self._role_has_permission(role, resource):
                    return True
            return False

        # 2. Subject is a Role enum
        if isinstance(subject, Role):
            return self._role_has_permission(subject, resource)

        # 3. Subject is an agent name string or username string
        if isinstance(subject, str):
            # Check if subject is 'benjamin' or 'admin'
            if subject.lower() in ("benjamin", "admin", "superuser", "owner"):
                return True

            role = self.get_role_for_agent(subject)
            if role is not None:
                return self._role_has_permission(role, resource)

        return False

    def _role_has_permission(self, role: Role, resource: str) -> bool:
        """Internal helper to check if a specific role grants access to a resource."""
        perms = self.role_permissions.get(role, set())
        if "*" in perms:
            return True
        if resource in perms:
            return True
        for perm in perms:
            if perm.lower() == resource.lower():
                return True
        return False

    def can_access_agent(self, subject: User | Role | str, target_agent: str) -> bool:
        """Verifies if subject is allowed to invoke or delegate to target_agent."""
        return self.has_permission(subject, target_agent)

    def can_access_tool(self, subject: User | Role | str, tool_name: str) -> bool:
        """Verifies if subject is allowed to invoke a specific tool."""
        return self.has_permission(subject, tool_name)


# Global default RBAC manager instance
rbac_manager = RBACManager()


class RBACHook(HookProvider):
    """Strands hook to enforce role-based access control policies before tool execution."""

    def __init__(
        self,
        agent_name: str = "Buddy",
        user: Optional[User] = None,
        manager: Optional[RBACManager] = None,
    ) -> None:
        """Initialize RBACHook.

        Args:
            agent_name: Name of the agent using this hook.
            user: Optional current active User (defaults to BENJAMIN_USER).
            manager: Optional RBACManager instance.
        """
        self.agent_name = agent_name
        self.user = user or BENJAMIN_USER
        self.manager = manager or rbac_manager

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """Enforces RBAC authorization before a tool is invoked."""
        tool_name = ""
        if isinstance(event.tool_use, dict):
            tool_name = event.tool_use.get("name", "")
        elif event.selected_tool is not None:
            tool_name = getattr(event.selected_tool, "name", str(event.selected_tool))

        if not tool_name:
            return

        # 1. Check user permission (Superuser/Benjamin has full access)
        if self.user and self.user.is_admin:
            return

        # 2. Check agent authorization
        if not self.manager.can_access_tool(self.agent_name, tool_name):
            role = self.manager.get_role_for_agent(self.agent_name)
            logger.warning(
                "RBAC Denied: Agent '%s' (Role: %s) unauthorized for tool '%s'",
                self.agent_name,
                role,
                tool_name,
            )
            event.cancel_tool = (
                f"RBAC Access Denied: Agent '{self.agent_name}' (Role: {role.value if role else 'None'}) "
                f"is not permitted to execute tool '{tool_name}'."
            )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """Register the BeforeToolCallEvent callback with HookRegistry."""
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)


__all__ = [
    "Role",
    "User",
    "BENJAMIN_USER",
    "GUEST_USER",
    "AGENT_ROLE_MAPPING",
    "ROLE_PERMISSIONS",
    "RBACAccessDeniedError",
    "RBACManager",
    "rbac_manager",
    "RBACHook",
]
