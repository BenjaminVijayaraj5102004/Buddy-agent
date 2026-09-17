"""Human-In-The-Loop (HITL) Hook for tool execution governance and corrective feedback."""

import json
from typing import Any, Callable, Optional, Set
from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

# Safe tools permitted to run without human intervention
DEFAULT_AUTO_APPROVED_TOOLS: Set[str] = {
    # Core agent & delegation tools (both tool names and callable names)
    "api_manager",
    "call_api_manager",
    "sam_cli_agent",
    "call_sam_cli_agent",
    "REST_Agent",
    "call_rest_agent",
    "github_agent",
    "call_github_agent",
    # Codebase inspection & memory tools
    "search_code",
    "search_repositories",
    "get_file_contents",
    "search_memory",
    "add_memory",
    # SAM CLI operations
    "sam init",
    "sam build",
    "sam local invoke",
    "sam_deploy",
}





class HumanInTheLoopHook(HookProvider):
    """Intercepts tool executions and prompts human operator for approval, usage guidance, or rejection."""

    def __init__(
        self,
        auto_approved_tools: Optional[Set[str]] = None,
        feedback_handler: Optional[
            Callable[[str, str, dict[str, Any]], tuple[bool, Optional[str]]]
        ] = None,
    ) -> None:
        """Initialize HITL Hook.

        Args:
            auto_approved_tools: Safe tools allowed to execute directly without human intervention.
            feedback_handler: Optional custom handler returning (is_approved, optional_guidance_or_feedback).
        """
        self.auto_approved_tools = (
            set(auto_approved_tools) if auto_approved_tools is not None else DEFAULT_AUTO_APPROVED_TOOLS
        )
        self.feedback_handler = feedback_handler or self._cli_feedback_handler

    def _cli_feedback_handler(
        self, tool_name: str, tool_description: str, tool_args: dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Interactive terminal prompt to review tool purpose, approve with guidance, or reject with feedback."""
        print("\n" + "=" * 64)
        print("[HITL INTERVENTION] Tool Execution Review & Approval")
        print(f"Tool Name        : {tool_name}")
        print(f"Tool Description : {tool_description or 'No description available'}")
        print("Parameters       :")
        try:
            print(json.dumps(tool_args, indent=2, default=str))
        except Exception:
            print(str(tool_args))
        print("=" * 64)
        print("Actions:")
        print("  [y] Approve execution (with optional guidance on how to use it)")
        print("  [n] Reject execution and provide corrective instructions to AI")
        print("-" * 64)

        while True:
            try:
                choice = input("Select action (y/n) [default: n]: ").strip().lower()
                if choice in ("y", "yes"):
                    guidance = input(
                        "Optional guidance/instructions for AI on using this tool (press Enter to skip): "
                    ).strip()
                    if guidance:
                        print(f"[HITL] Tool '{tool_name}' approved with operator guidance.")
                        return True, guidance
                    print(f"[HITL] Tool '{tool_name}' approved.")
                    return True, None
                elif choice in ("n", "no", ""):
                    print("\n[HITL] Execution rejected.")
                    feedback = input(
                        "Provide corrective feedback to AI (e.g., why this tool is wrong and what to do): "
                    ).strip()
                    if not feedback:
                        feedback = "Tool execution rejected by human operator. Please re-evaluate your approach."
                    print("[HITL] Corrective feedback recorded and returned to agent.")
                    return False, feedback
                else:
                    print("Invalid input. Please enter 'y' to approve or 'n' to reject.")
            except (KeyboardInterrupt, EOFError):
                print("\n[HITL] Interrupted by operator. Rejecting execution.")
                return False, "Tool execution aborted by human operator."

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """Callback triggered before any tool is executed."""
        tool_name = ""
        tool_description = ""
        tool_input: dict[str, Any] = {}

        if isinstance(event.tool_use, dict):
            tool_name = str(event.tool_use.get("name", ""))
            input_val = event.tool_use.get("input", {})
            tool_input = input_val if isinstance(input_val, dict) else {"raw_input": input_val}
        elif event.selected_tool is not None:
            tool_name = getattr(event.selected_tool, "name", str(event.selected_tool))
            tool_input = event.invocation_state if isinstance(event.invocation_state, dict) else {}

        if event.selected_tool is not None:
            tool_description = getattr(
                event.selected_tool,
                "description",
                getattr(event.selected_tool, "__doc__", "") or "",
            )
            if not tool_description and hasattr(event.selected_tool, "mcp_tool"):
                tool_description = getattr(event.selected_tool.mcp_tool, "description", "")

        # Safe tools in auto_approved_tools execute directly without HITL
        if tool_name in self.auto_approved_tools:
            return

        # Intercept tool for human review and guidance
        is_approved, message = self.feedback_handler(tool_name, tool_description, tool_input)

        if is_approved:
            # If the user provided guidance during approval, inject it into the task context
            if message and isinstance(tool_input, dict):
                if "task_description" in tool_input and isinstance(tool_input["task_description"], str):
                    tool_input["task_description"] += f"\n[Human Operator Guidance]: {message}"
                else:
                    tool_input["human_operator_guidance"] = message
                if isinstance(event.tool_use, dict):
                    event.tool_use["input"] = tool_input
        else:
            guidance_message = message or "Tool execution rejected by human operator."
            event.cancel_tool = (
                f"Action Rejected. Corrective guidance for AI: {guidance_message}"
            )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """Register the BeforeToolCallEvent callback with HookRegistry."""
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)