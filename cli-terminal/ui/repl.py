"""
Interactive Tactical REPL & Command Shell for Buddy Agent
Provides Claude Code-style interactive shell with Prompt-Toolkit autocomplete,
Project I.G.I. tactical prompts, hotkey shortcuts, tool catalog integration,
and end-of-conversation session ID preservation banner.
"""

import os
import sys
import time
from typing import Optional

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from .config import (
    COLOR_PEACH, COLOR_MINT, COLOR_BLUE, COLOR_PURPLE, COLOR_ROSE, COLOR_MUTED, COLOR_AMBER
)
from .state import SessionState
from .banner import render_banner
from .dialogs import (
    show_help_table, show_models_dialog, show_session_dialog, show_tool_list_table
)
from .executor import execute_agent_task

# Prompt Toolkit integration
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style as PTKStyle
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


def run_interactive_shell(session: SessionState, console: Optional[Console] = None) -> None:
    """Main interactive REPL loop matching Claude Code & Project I.G.I. style."""
    if console is None:
        console = Console()

    console.clear()
    console.print(render_banner(session))
    console.print()

    commands_list = [
        "/help",
        "/tools",
        "/top",
        "/menu",
        "/model",
        "/session",
        "/demo",
        "/clear",
        "/exit",
    ]
    
    if HAS_PROMPT_TOOLKIT:
        completer = WordCompleter(commands_list, ignore_case=True, match_middle=False)

        ptk_history = InMemoryHistory()
        ptk_session = PromptSession(history=ptk_history)
        
        ptk_style = PTKStyle.from_dict({
            "prompt": "#00ff55 bold",
            "arrow": "#00ff55 bold",
            "bottom-toolbar": "#f0fdf4",
            "bottom-toolbar.key": "#00ff55 bold",
            "bottom-toolbar.value": "#38bdf8",
        })
    else:
        ptk_session = None

    def get_bottom_toolbar():
        return HTML(
            f' ⚡ <b>Buddy Agent</b> | Model: <b>{session.model_key}</b> | Session: <b>{session.session_id[:13]}...</b> | Type <b>/tools</b> for MCP tools or <b>/help</b> '
        )

    while True:
        try:
            # Tactical single prompt header
            cwd_name = os.path.basename(os.getcwd()) or "workspace"
            console.print(
                f"[dim]╭─[/dim] 🎯 [bold {COLOR_PEACH}]PROJECT BUDDY // TACTICAL HUD[/bold {COLOR_PEACH}] "
                f"[dim]in[/dim] [bold {COLOR_BLUE}]~/{cwd_name}[/bold {COLOR_BLUE}] "
                f"[dim]on[/dim] [bold {COLOR_PURPLE}]satellite:{session.model_key}[/bold {COLOR_PURPLE}] "
                f"[dim]•[/dim] [bold #38bdf8]{session.session_id}[/bold #38bdf8]"
            )

            if HAS_PROMPT_TOOLKIT and ptk_session is not None:
                user_input = ptk_session.prompt(
                    HTML("<style color='#00ff55'><b>╰─❯ </b></style>"),
                    # pyrefly: ignore [unbound-name]
                    completer=completer,
                    bottom_toolbar=get_bottom_toolbar,
                    # pyrefly: ignore [unbound-name]
                    style=ptk_style,
                ).strip()
            else:
                user_input = Prompt.ask(f"[dim]╰─[/dim][bold {COLOR_PEACH}]❯[/bold {COLOR_PEACH}] ").strip()

            if not user_input:
                continue

            # Command routing
            cmd = user_input.lower()
            if cmd in ("exit", "quit", "q", ":q", "/exit", "/quit"):
                break
            elif cmd in ("/help", "help", "?"):
                show_help_table(console)
                continue
            elif cmd in ("/tools", "tools", "/tool_list", "tool_list", "tools_list", "/tools_list"):
                show_tool_list_table(console)
                continue
            elif cmd in ("/menu", "menu", "m"):
                from .menu import run_btop_game_interface
                run_btop_game_interface(session, console)
                console.clear()
                console.print(render_banner(session))
                continue
            elif cmd in ("/monitor", "/top", "/btop", "monitor", "top", "btop"):
                console.print(f"[{COLOR_MINT}]🚀 Launching Btop Live System Resource & AI Telemetry Monitor... Press 'q' to return.[/{COLOR_MINT}]")
                time.sleep(0.4)
                from .monitor import run_btop_monitor
                run_btop_monitor(
                    console,
                    theme_name=getattr(session, "theme", "igi"),
                    initial_refresh_rate=getattr(session, "radar_interval", 1.0),
                    session_obj=session
                )
                console.clear()
                console.print(render_banner(session))
                continue
            elif cmd in ("/model", "model", "/models"):
                show_models_dialog(session, console)
                continue
            elif cmd in ("/session", "session", "/sessions"):
                show_session_dialog(session, console)
                continue
            elif cmd in ("/clear", "clear", "cls"):
                console.clear()
                console.print(render_banner(session))
                console.print()
                continue
            elif cmd in ("/demo", "demo"):
                execute_agent_task(
                    "Create a POST health check endpoint using FastAPI and python framework and store it as app.py",
                    session,
                    console
                )
                continue

            # Regular prompt execution
            execute_agent_task(user_input, session, console)

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[dim]Interrupted. Type /exit to quit.[/dim]\n")
            break
        except Exception as ex:
            console.print(f"\n[{COLOR_ROSE}]❌ An error occurred: {ex}[/{COLOR_ROSE}]\n")

    # Graceful exit with prominent copyable Session ID box
    exit_text = Text()
    exit_text.append("💾 SESSION SAVED & PRESERVED!\n", style="bold #facc15")
    exit_text.append(f"🔑 Session ID: {session.session_id}\n\n", style="bold #00ff55")
    exit_text.append("📋 Copy and paste this ID in the Session Menu or run /session to resume your conversation.\n", style="dim #94a3b8")
    exit_text.append("⚡ Tactical HUD Shutdown. Have a productive day, Champ! 🐾", style="bold #38bdf8")

    console.print()
    console.print(Panel(exit_text, border_style="bold #00ff55", padding=(1, 2)))
    console.print()
