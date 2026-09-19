"""Rate limiting governance and invocation quota enforcement for Buddy Agent.

Configured Rules:
- Buddy Agent -> API Manager: Max 5 invocations
- Buddy Agent -> SAM CLI Agent: Max 5 invocations
- Buddy Agent -> GitHub Agent: Max 5 invocations
- API Manager -> REST API Agent: Max 5 invocations
- Default quota: 5 invocations per tool/agent
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, Optional, Tuple

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

logger = logging.getLogger("buddy.credy.ratelimiting")

# Default rate limits per (caller_agent, tool_or_target_agent)
DEFAULT_AGENT_RATE_LIMITS: Dict[Tuple[str, str], int] = {
    # Buddy Agent delegations (max 5 calls each)
    ("Buddy", "api_manager"): 5,
    ("Buddy", "call_api_manager"): 5,
    ("Buddy", "sam_cli_agent"): 5,
    ("Buddy", "call_sam_cli_agent"): 5,
    ("Buddy", "github_agent"): 5,
    ("Buddy", "call_github_agent"): 5,
    ("buddy_agent", "api_manager"): 5,
    ("buddy_agent", "call_api_manager"): 5,
    ("buddy_agent", "sam_cli_agent"): 5,
    ("buddy_agent", "call_sam_cli_agent"): 5,
    ("buddy_agent", "github_agent"): 5,
    ("buddy_agent", "call_github_agent"): 5,
    # API Manager delegations (max 5 calls to REST Agent)
    ("API_MANAGER", "REST_Agent"): 5,
    ("API_MANAGER", "call_rest_agent"): 5,
    ("api_manager", "REST_Agent"): 5,
    ("api_manager", "call_rest_agent"): 5,
}

DEFAULT_FALLBACK_LIMIT: int = 5


class RateLimitExceededError(Exception):
    """Raised when an agent or tool execution exceeds its allowed rate limit quota."""

    def __init__(self, caller: str, target: str, limit: int, current: int) -> None:
        self.caller = caller
        self.target = target
        self.limit = limit
        self.current = current
        super().__init__(
            f"Rate limit exceeded: '{caller}' has invoked '{target}' {current} times "
            f"(maximum allowed: {limit})."
        )


@dataclass
class RateLimitTracker:
    """Thread-safe rate limit quota tracker."""

    limits: Dict[Tuple[str, str], int] = field(
        default_factory=lambda: dict(DEFAULT_AGENT_RATE_LIMITS)
    )
    default_limit: int = DEFAULT_FALLBACK_LIMIT
    _counts: Dict[str, Dict[Tuple[str, str], int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )
    _lock: Lock = field(default_factory=Lock)

    def _normalize_key(self, caller: str, target: str) -> Tuple[str, str]:
        """Normalizes caller and target names for lookup."""
        return (caller.strip(), target.strip())

    def get_limit(self, caller: str, target: str) -> int:
        """Retrieves the rate limit for a specific caller and target pair."""
        key = self._normalize_key(caller, target)
        if key in self.limits:
            return self.limits[key]
        # Check case-insensitive / normalized fallbacks
        for (c, t), limit in self.limits.items():
            if c.lower() == caller.lower() and t.lower() == target.lower():
                return limit
        return self.default_limit

    def set_limit(self, caller: str, target: str, limit: int) -> None:
        """Dynamically set or override rate limit for a specific caller and target."""
        with self._lock:
            key = self._normalize_key(caller, target)
            self.limits[key] = limit

    def get_count(
        self, caller: str, target: str, session_id: Optional[str] = None
    ) -> int:
        """Gets current invocation count for the specified session or global context."""
        sid = session_id or "global"
        key = self._normalize_key(caller, target)
        with self._lock:
            return self._counts[sid][key]

    def get_remaining(
        self, caller: str, target: str, session_id: Optional[str] = None
    ) -> int:
        """Returns the number of remaining allowed calls."""
        limit = self.get_limit(caller, target)
        count = self.get_count(caller, target, session_id)
        return max(0, limit - count)

    def can_execute(
        self, caller: str, target: str, session_id: Optional[str] = None
    ) -> bool:
        """Checks whether the caller is within the rate limit quota."""
        limit = self.get_limit(caller, target)
        count = self.get_count(caller, target, session_id)
        return count < limit

    def record_call(
        self, caller: str, target: str, session_id: Optional[str] = None
    ) -> int:
        """Increments and returns the new call count.

        Raises:
            RateLimitExceededError: If the call exceeds the configured limit.
        """
        sid = session_id or "global"
        key = self._normalize_key(caller, target)
        limit = self.get_limit(caller, target)

        with self._lock:
            current = self._counts[sid][key]
            if current >= limit:
                logger.warning(
                    "Rate limit exceeded: %s -> %s (limit: %d, current: %d)",
                    caller,
                    target,
                    limit,
                    current,
                )
                raise RateLimitExceededError(caller, target, limit, current + 1)
            self._counts[sid][key] = current + 1
            new_count = self._counts[sid][key]
            logger.info(
                "Rate limit count updated: %s -> %s [%d/%d]",
                caller,
                target,
                new_count,
                limit,
            )
            return new_count

    def reset(
        self,
        session_id: Optional[str] = None,
        caller: Optional[str] = None,
        target: Optional[str] = None,
    ) -> None:
        """Resets rate limit counters."""
        with self._lock:
            if session_id and caller and target:
                key = self._normalize_key(caller, target)
                self._counts[session_id].pop(key, None)
            elif session_id:
                self._counts.pop(session_id, None)
            elif caller and target:
                key = self._normalize_key(caller, target)
                for sid in self._counts:
                    self._counts[sid].pop(key, None)
            else:
                self._counts.clear()


# Global default rate limiter tracker
rate_limiter = RateLimitTracker()


class RateLimiterHook(HookProvider):
    """Strands agent hook to intercept tool executions and enforce rate limits."""

    def __init__(
        self,
        agent_name: str = "Buddy",
        tracker: Optional[RateLimitTracker] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Initialize RateLimiterHook.

        Args:
            agent_name: Name of the agent using this hook (e.g. 'Buddy', 'API_MANAGER').
            tracker: Optional shared RateLimitTracker instance.
            session_id: Optional session identifier for per-session limits.
        """
        self.agent_name = agent_name
        self.tracker = tracker or rate_limiter
        self.session_id = session_id

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """Validates tool execution against configured rate limits before invocation."""
        tool_name = ""
        if isinstance(event.tool_use, dict):
            tool_name = event.tool_use.get("name", " ")
        elif event.selected_tool is not None:
            tool_name = getattr(event.selected_tool, "name", str(event.selected_tool))

        if not tool_name:
            return

        try:
            self.tracker.record_call(
                caller=self.agent_name,
                target=tool_name,
                session_id=self.session_id,
            )
        except RateLimitExceededError as err:
            limit = self.tracker.get_limit(self.agent_name, tool_name)
            event.cancel_tool = (
                f"Rate Limit Exceeded: Agent '{self.agent_name}' has reached the maximum allowed "
                f"quota of {limit} calls for tool/agent '{tool_name}'. Action aborted."
            )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """Register the BeforeToolCallEvent callback with HookRegistry."""
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)


__all__ = [
    "DEFAULT_AGENT_RATE_LIMITS",
    "DEFAULT_FALLBACK_LIMIT",
    "RateLimitExceededError",
    "RateLimitTracker",
    "rate_limiter",
    "RateLimiterHook",
]
