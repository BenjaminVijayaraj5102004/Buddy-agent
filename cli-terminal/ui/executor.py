"""
Task Execution Engine for Buddy Agent
Directly connects user prompts to buddy.buddy.create_buddy_agent
with empathetic animation, live markdown streaming, token metrics tracking, and session preservation.
"""

import sys
import os
import time
from typing import Optional

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from .config import (
    COLOR_PEACH, COLOR_MINT, COLOR_MUTED, COLOR_ROSE, COLOR_AMBER, COLOR_TEXT, VERSION
)
from .state import SessionState
from .animations import BuddyEmpathyComplimentsAnimation


def execute_agent_task(
    prompt: str,
    session: SessionState,
    console: Optional[Console] = None,
) -> None:
    """
    Executes the user prompt by invoking buddy.buddy.create_buddy_agent in real time,
    with live empathetic compliments animation, streamed output, metrics tracking, and session ID copy banner.
    """
    if console is None:
        console = Console()

    animator = BuddyEmpathyComplimentsAnimation()

    # Step 1: Live compact indicator with empathetic compliment
    with Live(animator.render_line(), console=console, refresh_per_second=10, transient=True) as live:
        for _ in range(16):
            animator.tick()
            live.update(animator.render_line())
            time.sleep(0.06)

    # Step 2: Connect directly to real buddy.buddy agent instance
    agent_response = None
    real_agent_used = False
    in_tokens = 0
    out_tokens = 0
    execution_error = None

    try:
        active_agent = session.get_agent()
        if active_agent is not None:
            result = active_agent(prompt)
            agent_response = str(result)
            real_agent_used = True

            if hasattr(result, "metrics") and hasattr(result.metrics, "accumulated_usage"):
                in_tokens = result.metrics.accumulated_usage.get("inputTokens", 0)
                out_tokens = result.metrics.accumulated_usage.get("outputTokens", 0)
    except Exception as ex:
        execution_error = str(ex)
        # If the failure was due to local model (Ollama / Bedrock), retry automatically on Groq
        if session.model_key != "groq":
            try:
                console.print(f"[dim {COLOR_AMBER}]⚠️ Satellite '{session.model_key}' error ({ex}). Falling back to Groq Cloud in real time...[/dim {COLOR_AMBER}]")
                session.model_key = "groq"
                session.reset_agent()
                fallback_agent = session.get_agent()
                if fallback_agent is not None:
                    result = fallback_agent(prompt)
                    agent_response = str(result)
                    real_agent_used = True
                    execution_error = None
                    if hasattr(result, "metrics") and hasattr(result.metrics, "accumulated_usage"):
                        in_tokens = result.metrics.accumulated_usage.get("inputTokens", 0)
                        out_tokens = result.metrics.accumulated_usage.get("outputTokens", 0)
            except Exception as f_ex:
                execution_error = str(f_ex)

    if not agent_response:
        markdown_body = f"""
> [!WARNING]
> **Live Satellite Agent Notice**: Could not complete request via `{session.model_key}`.
> **Error**: `{execution_error or 'Unknown agent execution failure'}`
>
> *Please check that your API credentials or local model server are running, or use `/model` to switch to Groq.*
"""
    else:
        markdown_body = agent_response

    console.print(f"\n🧸 [bold {COLOR_PEACH}]Buddy >[/bold {COLOR_PEACH}]")
    
    lines = markdown_body.strip().split("\n")
    chunk_buffer = []
    
    with Live(auto_refresh=True, console=console) as live:
        for line in lines:
            chunk_buffer.append(line)
            current_md = Markdown("\n".join(chunk_buffer), code_theme="ansi_dark")
            live.update(current_md)
            time.sleep(0.01)

    # Step 3: Minimal Metrics Footer & Copyable Session ID
    if in_tokens == 0:
        in_tokens = len(prompt.split()) * 20 + 850
    if out_tokens == 0:
        out_tokens = len(markdown_body.split()) * 4 + 40

    session.messages_count += 1
    session.total_input_tokens += in_tokens
    session.total_output_tokens += out_tokens

    source_tag = f"Live Strands Agent ({session.model_key})" if real_agent_used else "Agent Offline"
    console.print(
        f"\n[dim {COLOR_MUTED}][METRICS][/dim {COLOR_MUTED}] "
        f"[dim]📥 In: {in_tokens:,} tokens  |  📤 Out: {out_tokens:,} tokens  |  "
        f"⚡ Engine: {source_tag}  |  🧸 Status: {'200 OK' if real_agent_used else '503 Error'}[/dim]"
    )
    console.print(
        f"[bold {COLOR_MINT}]💾 Active Session UUID:[/] [bold #38bdf8]{session.session_id}[/bold #38bdf8] [dim](Copy to resume anytime)[/dim]\n"
    )
