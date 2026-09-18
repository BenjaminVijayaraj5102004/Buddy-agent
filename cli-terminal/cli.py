"""
Buddy Agent - Tactical UI/UX CLI Entrypoint
Clean modular CLI powered by Typer, Rich, Prompt-Toolkit, and the ui package.
Directly connects to buddy.buddy.create_buddy_agent.
"""

import sys
import os
from typing import Optional

# Ensure UTF-8 output encoding for terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure buddy-agent and cli-terminal are in sys.path
CLI_DIR = os.path.dirname(os.path.abspath(__file__))
BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(CLI_DIR, ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)
if CLI_DIR not in sys.path:
    sys.path.insert(0, CLI_DIR)

import typer
from rich.console import Console

from ui import (
    SessionState,
    MODELS_CATALOG,
    show_tool_list_table,
    show_models_dialog,
    show_help_table,
    show_session_dialog,
    execute_agent_task,
    run_interactive_shell,
    run_btop_monitor,
    run_btop_game_interface,
    render_banner,
)

console = Console(highlight=True)

app = typer.Typer(
    name="buddy",
    help="⚡ BUDDY AGENT - Tactical AI Companion & Btop Telemetry Monitor",
    add_completion=False,
    no_args_is_help=False,
)


@app.command("tools")
def tools_command():
    """List all active MCP tools across GitHub, SAM CLI, and Text Editor (excluding hardcoded safe tools)."""
    show_tool_list_table(console)


@app.command("tool_list")
def tool_list_command():
    """List all active MCP tools across GitHub, SAM CLI, and Text Editor (excluding hardcoded safe tools)."""
    show_tool_list_table(console)


@app.command("top")
def top_command(
    theme: Optional[str] = typer.Option("igi", "--theme", "-t", help="Theme: igi, matrix, tokyo_night, catppuccin, dracula"),
    rate: Optional[float] = typer.Option(1.0, "--rate", "-r", help="Refresh rate in seconds"),
):
    """Launch interactive btop++ live system resource & AI sonar radar monitor."""
    run_btop_monitor(console=console, theme_name=theme or "igi", initial_refresh_rate=rate or 1.0)


@app.command("monitor")
def monitor_command(
    theme: Optional[str] = typer.Option("igi", "--theme", "-t", help="Theme: igi, matrix, tokyo_night, catppuccin, dracula"),
    rate: Optional[float] = typer.Option(1.0, "--rate", "-r", help="Refresh rate in seconds"),
):
    """Launch interactive btop++ live system resource & AI sonar radar monitor."""
    run_btop_monitor(console=console, theme_name=theme or "igi", initial_refresh_rate=rate or 1.0)


@app.command("session")
def session_command(
    session_id: Optional[str] = typer.Option(None, "--id", "-i", help="Session UUID to activate"),
):
    """View stored sessions archive, paste UUID, or switch active session context."""
    session = SessionState(session_id=session_id)
    if session_id:
        try:
            from agent.memory import set_current_session_id
            set_current_session_id(session_id)
        except Exception:
            pass
        console.print(f"[bold #00ff55]🔄 Activated Session UUID:[/] [bold #38bdf8]{session.session_id}[/]\n")
    else:
        show_session_dialog(session, console)


@app.command("chat")
def chat_command(
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Resume an existing session UUID"),
    model: Optional[str] = typer.Option("groq", "--model", "-m", help="AI Model: groq, ollama, or bedrock"),
):
    """Launch interactive tactical chat shell with live telemetry and auto-completion."""
    session = SessionState(session_id=session_id, model_key=model or "groq")
    run_interactive_shell(session, console)


@app.command("ask")
def ask_command(
    prompt: str = typer.Argument(..., help="Prompt or task instructions to execute"),
    model: Optional[str] = typer.Option("groq", "--model", "-m", help="Model to use: groq, ollama, bedrock"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID for conversation context"),
):
    """Execute a one-shot query with live compliments animation and markdown response."""
    session = SessionState(session_id=session_id, model_key=model or "groq")
    console.print(render_banner(session))
    console.print(f"[bold #00ff55]You >[/bold #00ff55] {prompt}\n")
    execute_agent_task(prompt, session, console)


@app.command("demo")
def demo_command():
    """Run an automated tactical mission showcasing FastAPI & SAM scaffolding."""
    session = SessionState()
    console.print(render_banner(session))
    prompt = "Create a POST health check endpoint using FastAPI and python framework and store it as app.py"
    console.print(f"[bold #00ff55]You >[/bold #00ff55] {prompt}\n")
    execute_agent_task(prompt, session, console)


@app.command("models")
def models_command():
    """List all supported AI models and latency specifications."""
    session = SessionState()
    show_models_dialog(session, console)


@app.command("help_manual")
def help_manual_command():
    """Display the tactical HUD manual and keyboard shortcuts."""
    show_help_table(console)


@app.command("menu")
def menu_command():
    """Launch interactive Project I.G.I. tactical HUD menu and dashboard."""
    session = SessionState()
    run_btop_game_interface(session, console)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Default entrypoint: launch authentic Project I.G.I. tactical HUD menu and dashboard."""
    if ctx.invoked_subcommand is None:
        session = SessionState()
        run_btop_game_interface(session, console)


if __name__ == "__main__":
    app()
