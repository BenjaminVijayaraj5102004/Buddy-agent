"""
Robust Conversation Manager Wrappers for Buddy Agent
Gracefully handles cross-session and cross-manager restoration without raising
`ValueError: Invalid conversation manager state.`
"""
from typing import Any
from strands.agent.conversation_manager import (
    SlidingWindowConversationManager,
    SummarizingConversationManager,
)
from strands.types.content import Message


class SafeSlidingWindowConversationManager(SlidingWindowConversationManager):
    """Sliding window conversation manager with safe cross-session restoration."""

    def get_state(self) -> dict[str, Any]:
        return {
            "__name__": "SlidingWindowConversationManager",
            "removed_message_count": self.removed_message_count,
        }

    def restore_from_session(self, state: dict[str, Any]) -> list[Message] | None:
        if isinstance(state, dict):
            self.removed_message_count = state.get("removed_message_count", 0)
        return None


class SafeSummarizingConversationManager(SummarizingConversationManager):
    """Summarizing conversation manager with safe cross-session restoration."""

    def get_state(self) -> dict[str, Any]:
        return {
            "__name__": "SummarizingConversationManager",
            "summary_message": self._summary_message,
            "removed_message_count": self.removed_message_count,
        }

    def restore_from_session(self, state: dict[str, Any]) -> list[Message] | None:
        if not isinstance(state, dict):
            return None
        self.removed_message_count = state.get("removed_message_count", 0)
        self._summary_message = state.get("summary_message")
        return [self._summary_message] if self._summary_message else None
