"""Hooks package for Buddy Agent."""

from agent.hooks.hitl_hook import (
    DEFAULT_AUTO_APPROVED_TOOLS,
    HumanInTheLoopHook,
)

__all__ = [
    "HumanInTheLoopHook",
    "DEFAULT_AUTO_APPROVED_TOOLS",
]

