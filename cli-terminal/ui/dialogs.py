"""
Interactive Dialogs & Tables for Buddy Agent UI
Provides Help, Models, Sessions Archive & Switcher, and MCP Tools Catalog modals and tables.
"""

import sys
import os
import uuid
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from .config import (
    COLOR_PEACH, COLOR_AMBER, COLOR_MINT, COLOR_BLUE,
    COLOR_PURPLE, COLOR_ROSE, COLOR_TEXT, COLOR_MUTED,
    IGI_GREEN_BRIGHT, MODELS_CATALOG
)
from .state import SessionState
from .tools_catalog import get_non_hardcoded_mcp_tools


def show_help_table(console: Optional[Console] = None) -> None:
    """Renders the comprehensive help & keybindings cheat-sheet table."""
    if console is None:
        console = Console()

    table = Table(
        title="💡 [bold #00ff55]BUDDY AGENT // TACTICAL COMMAND MANUAL[/bold #00ff55]",
        border_style=f"dim {COLOR_MUTED}",
        header_style=f"bold {COLOR_PEACH}",
        expand=True,
        padding=(0, 1),
    )

    table.add_column("Command / Hotkey", style=f"bold {COLOR_BLUE}", ratio=3)
    table.add_column("Category", style=f"bold {COLOR_AMBER}", ratio=2)
    table.add_column("Description", style=f"dim {COLOR_TEXT}", ratio=5)

    commands = [
        ("/tools", "Governance", "List active MCP tools (GitHub, SAM CLI, Text Editor)"),
        ("/top", "Telemetry", "Launch interactive btop++ live system & AI radar"),
        ("/menu", "Interface", "Open Project I.G.I. 3D tactical HUD configuration menu"),
        ("/model", "AI Satellite", "Switch LLM satellite (Groq Llama-3.3, Bedrock Claude, Ollama)"),
        ("/session", "Memory", "View, paste, or switch session UUID and context"),
        ("/clear", "Display", "Clear screen and redraw tactical HUD banner"),
        ("/help", "Manual", "Display this tactical command reference"),
        ("/exit", "System", "Save session and exit tactical shell cleanly"),
    ]

    for cmd, cat, desc in commands:
        table.add_row(cmd, cat, desc)

    console.print()
    console.print(table)
    console.print()


def show_models_dialog(session: SessionState, console: Optional[Console] = None) -> None:
    """Displays multi-agent satellite topology, model matrix, and prompts user to assign models per agent."""
    if console is None:
        console = Console()

    # 1. Multi-Agent Topology Table
    topo_table = Table(
        title="🛰️  [bold #00ff55]ACTIVE MULTI-AGENT SATELLITE TOPOLOGY[/bold #00ff55]",
        border_style=f"dim {COLOR_MUTED}",
        header_style=f"bold {COLOR_PEACH}",
        expand=True,
    )
    topo_table.add_column("Agent / Role", style=f"bold {COLOR_BLUE}", width=24)
    topo_table.add_column("Assigned Satellite Model", style=f"bold {COLOR_TEXT}", ratio=4)
    topo_table.add_column("Provider", style=f"dim {COLOR_MINT}", width=16)

    agents_list = [
        ("🤖 Main Orchestrator (Buddy)", "main"),
        ("⚡ REST API Agent", "api"),
        ("🐙 GitHub Agent", "github"),
        ("📦 SAM CLI Deploy Agent", "sam"),
    ]

    for label, akey in agents_list:
        info = session.get_subagent_model_info(akey)
        topo_table.add_row(label, info["name"], info["provider"])

    console.print()
    console.print(topo_table)

    # 2. Available Satellite Models Matrix
    table = Table(
        title="🧠 [bold #00ff55]SATELLITE AI MODEL MATRIX[/bold #00ff55]",
        border_style=f"dim {COLOR_MUTED}",
        header_style=f"bold {COLOR_PEACH}",
        expand=True,
    )
    table.add_column("#", style=f"bold {COLOR_AMBER}", width=4)
    table.add_column("Provider", style=f"bold {COLOR_BLUE}", width=14)
    table.add_column("Full Designation", style=f"bold {COLOR_TEXT}", ratio=4)
    table.add_column("Model ID / Key", style=f"dim {COLOR_TEXT}", ratio=3)
    table.add_column("Status", style=f"bold {COLOR_MINT}", width=12)

    for m in MODELS_CATALOG:
        is_active = any(
            m["key"].lower() == session.subagent_models.get(k, "").lower()
            or m.get("model_id", "").lower() == session.subagent_models.get(k, "").lower()
            or (m["key"] == "groq" and session.subagent_models.get(k, "").lower() in ("groq", "qwen/qwen3.8-27b"))
            or (m["key"] == "ollama" and session.subagent_models.get(k, "").lower() in ("ollama", "llama3.1:8b"))
            or (m["key"] == "bedrock" and session.subagent_models.get(k, "").lower() in ("bedrock", "us.anthropic.claude-3-7-sonnet-20250219-v1:0"))
            for k in ("main", "api", "github", "sam")
        )
        status_str = f"[{COLOR_MINT}]● ACTIVE[/{COLOR_MINT}]" if is_active else "[dim]STANDBY[/dim]"
        table.add_row(f"[{m['id']}]", m["provider"], m["name"], m.get("model_id", m["key"]), status_str)

    console.print()
    console.print(table)
    console.print()

    # Agent target selection
    console.print(f"[{COLOR_PEACH}]Select Target Agent to Configure:[/{COLOR_PEACH}]")
    console.print(f"  [1] Main Orchestrator (Buddy)")
    console.print(f"  [2] REST API Agent")
    console.print(f"  [3] GitHub Agent")
    console.print(f"  [4] SAM CLI Deploy Agent")
    console.print(f"  [5] Synchronize All Agents")
    target_agent_choice = Prompt.ask(
        f"[{COLOR_AMBER}]Target Agent [1-5 or Enter to keep current][/{COLOR_AMBER}]",
        default=""
    ).strip()

    if not target_agent_choice:
        return

    agent_target_map = {
        "1": "main",
        "2": "api",
        "3": "github",
        "4": "sam",
        "5": "all",
    }
    agent_target = agent_target_map.get(target_agent_choice, "main")
    target_label = "All Agents" if agent_target == "all" else agent_target.upper()

    choice = Prompt.ask(
        f"[{COLOR_PEACH}]Select Model [1-{len(MODELS_CATALOG)}] for {target_label} or enter custom ID[/{COLOR_PEACH}]",
        default=""
    ).strip()

    if choice:
        # Check for BYOM selection
        if choice in ("8", "byom", "custom"):
            console.print(f"[{COLOR_PEACH}]🔧 Bring Your Own Model (BYOM) Setup for {target_label}:[/{COLOR_PEACH}]")
            prov = Prompt.ask("   Select Provider [1: Groq, 2: Ollama, 3: Bedrock]", default="1").strip()
            prov_key = "ollama" if prov in ("2", "ollama") else ("bedrock" if prov in ("3", "bedrock") else "groq")
            custom_id = Prompt.ask(f"   Enter Custom Model ID for {prov_key.upper()}").strip()
            if custom_id:
                full_key = f"{prov_key}:{custom_id}"
                session.switch_model(full_key, agent_name=agent_target)
                console.print(f"[{COLOR_MINT}]✨ {target_label} model switched to Custom: {full_key}[/{COLOR_MINT}]\n")
                return

        for m in MODELS_CATALOG:
            if (
                choice == m["id"]
                or choice.lower() == m["key"].lower()
                or choice.lower() == m.get("model_id", "").lower()
                or choice.lower() in m["name"].lower()
            ):
                session.switch_model(m["key"], agent_name=agent_target)
                console.print(f"[{COLOR_MINT}]✨ {target_label} model switched to: {m['name']}[/{COLOR_MINT}]\n")
                return

        # Direct model string input (e.g. "qwen:7b", "groq:my-model")
        session.switch_model(choice, agent_name=agent_target)
        console.print(f"[{COLOR_MINT}]✨ {target_label} model switched to: {choice}[/{COLOR_MINT}]\n")


def clean_session_id(s: str) -> str:
    """Cleans 0x prefix or extra whitespace from user-entered session IDs."""
    s = s.strip()
    if s.lower().startswith("0x") and len(s) > 2:
        s = s[2:]
    return s.strip()


def show_session_dialog(session: SessionState, console: Optional[Console] = None) -> None:
    """Shows session details and lets the user switch, resume, or paste a session ID."""
    if console is None:
        console = Console()

    stored_sessions: list[str] = []
    try:
        from agent.memory import list_stored_sessions
        stored_sessions = list_stored_sessions()
    except Exception:
        pass

    box_content = Text()
    box_content.append("🔑 ACTIVE SESSION UUID:\n", style="bold #facc15")
    box_content.append(f"{session.session_id}\n\n", style="bold #00ff55")
    box_content.append(f"🤖 Active Model: {session.model_key.upper()} | 📊 Telemetry: {session.messages_count} messages\n", style="bold #38bdf8")
    box_content.append(f"📥 In: {session.total_input_tokens:,} tokens | 📤 Out: {session.total_output_tokens:,} tokens\n\n", style="dim #94a3b8")
    box_content.append("💡 Copy the UUID above to resume this exact state anytime.", style="italic #38bdf8")

    console.print()
    console.print(Text("💾 BUDDY AGENT // SESSION CONTEXT", style="bold #00ff55", justify="center"))
    console.print(Text("─" * 78, style="dim #15803d", justify="center"))
    console.print(box_content)
    console.print(Text("─" * 78, style="dim #15803d", justify="center"))
    console.print()

    if stored_sessions:
        table = Table(
            title="📁 [bold #00ff55]STORED SESSIONS ARCHIVE (./agent/memory/sessions_data)[/bold #00ff55]",
            border_style=f"dim {COLOR_MUTED}",
            header_style=f"bold {COLOR_PEACH}",
            expand=True,
            padding=(0, 1),
        )
        table.add_column("#", style=f"bold {COLOR_AMBER}", width=4)
        table.add_column("Session UUID", style=f"bold {COLOR_TEXT}", ratio=6)
        table.add_column("Status", style=f"bold {COLOR_MINT}", width=12)

        for idx, sid in enumerate(stored_sessions[:8], 1):
            is_active = (sid.lower() == session.session_id.lower())
            status_str = f"[{COLOR_MINT}]● ACTIVE[/{COLOR_MINT}]" if is_active else "[dim]SAVED[/dim]"
            table.add_row(f"[{idx}]", sid, status_str)

        console.print(table)
        console.print()

    console.print(f"[{COLOR_PEACH}]Enter [bold]n[/bold] for new session, [bold]#[/bold] from list, paste [bold]Session UUID[/bold], or press [bold]Enter[/bold] to keep current:[/{COLOR_PEACH}]")
    raw_input = Prompt.ask("").strip()

    if not raw_input:
        console.print(f"[{COLOR_MUTED}]Keeping current session: {session.session_id}[/{COLOR_MUTED}]\n")
        return

    # Check for new session
    if raw_input.lower() in ("n", "new"):
        new_id = str(uuid.uuid4())
        session.session_id = new_id
        session.messages_count = 0
        session.total_input_tokens = 0
        session.total_output_tokens = 0
        session.history.clear()
        session.reset_agent()
        try:
            from agent.memory import set_current_session_id, set_session_model_key
            set_current_session_id(new_id)
            set_session_model_key(new_id, session.model_key)
        except Exception:
            pass
        console.print(f"[{COLOR_MINT}]✨ Started new session: {session.session_id} (Model: {session.model_key})[/{COLOR_MINT}]\n")
        return

    # Check for selection by number
    if raw_input.isdigit() and stored_sessions:
        idx = int(raw_input) - 1
        if 0 <= idx < len(stored_sessions):
            target_id = stored_sessions[idx]
            session.switch_session(target_id)
            console.print(f"[{COLOR_MINT}]🔄 Switched to session #{idx+1}: {session.session_id} (Model: {session.model_key})[/{COLOR_MINT}]\n")
            return

    # Check for 'r' or 'resume'
    if raw_input.lower() in ("r", "resume"):
        raw_input = Prompt.ask(f"[{COLOR_PEACH}]Paste Session UUID[/{COLOR_PEACH}]").strip()
        if not raw_input:
            return

    # Direct paste of session UUID
    target_id = clean_session_id(raw_input)
    if target_id:
        session.switch_session(target_id)
        console.print(f"[{COLOR_MINT}]🔄 Resumed session: {session.session_id} (Model: {session.model_key})[/{COLOR_MINT}]\n")


def show_tool_list_table(console: Optional[Console] = None) -> None:
    """Renders the 3-column MCP tools catalog for GitHub, SAM CLI, and Text Editor."""
    if console is None:
        console = Console()

    github_tools, sam_tools, text_tools = get_non_hardcoded_mcp_tools()

    table = Table(
        title="🛠️ [bold #00ff55]BUDDY AGENT // MCP TOOLS CATALOG[/bold #00ff55]",
        border_style=f"dim {COLOR_MUTED}",
        header_style=f"bold {COLOR_PEACH}",
        expand=True,
        padding=(0, 1),
    )

    table.add_column("🐙 GitHub MCP Tools", style=f"bold {COLOR_TEXT}", ratio=4)
    table.add_column("⚡ SAM CLI MCP Tools", style=f"bold {COLOR_TEXT}", ratio=4)
    table.add_column("📝 Text Editor MCP Tools", style=f"bold {COLOR_TEXT}", ratio=4)

    max_len = max(len(github_tools), len(sam_tools), len(text_tools))

    for i in range(max_len):
        col1 = f"• [bold {COLOR_BLUE}]{github_tools[i][0]}[/]\n  [dim]{github_tools[i][1]}[/]" if i < len(github_tools) else ""
        col2 = f"• [bold {COLOR_AMBER}]{sam_tools[i][0]}[/]\n  [dim]{sam_tools[i][1]}[/]" if i < len(sam_tools) else ""
        col3 = f"• [bold {COLOR_PURPLE}]{text_tools[i][0]}[/]\n  [dim]{text_tools[i][1]}[/]" if i < len(text_tools) else ""
        table.add_row(col1, col2, col3)

    console.print()
    console.print(table)
    console.print()


def show_readme_dialog(console: Optional[Console] = None) -> None:
    """Renders the Project I.G.I. tactical ReadMe and architecture manual."""
    if console is None:
        console = Console()

    table = Table.grid(padding=(0, 1), expand=True)
    table.add_column()

    table.add_row(Text("✦ BUDDY AGENT // SYSTEM MANUAL & ARCHITECTURE ✦\n", style=f"bold {IGI_GREEN_BRIGHT}", justify="center"))
    table.add_row(Text("─" * 78, style=f"dim {COLOR_MUTED}"))
    
    sections = [
        ("1. EXECUTIVE OVERVIEW", "Buddy Agent is an autonomous, production-grade agentic AI pair programmer built on Python 3.14 and the Strands Agents framework. It combines deep multi-agent delegation with a tactical Project I.G.I. HUD and real-time Btop++ system telemetry."),
        ("2. MULTI-AGENT TOPOLOGY", "• Master Orchestrator (Buddy Agent): Intent classification, semantic memory routing, and response synthesis.\n• API Manager: End-to-end REST/FastAPI microservice endpoint generation with strict Pydantic schemas.\n• SAM CLI Deploy Agent: CloudFormation infrastructure packaging, deployment, and sync.\n• GitHub Agent: Branching, pull request lifecycles, and code inspection."),
        ("3. MODEL CONTEXT PROTOCOL (MCP)", "Integrates dedicated MCP clients for GitHub, AWS SAM CLI, and atomic Text Editing with zero hardcoded tools, giving the agent deterministic environment control."),
        ("4. RESILIENT MEMORY ARCHITECTURE", "Multi-tier state persistence supporting session archiving, UUID hot-swapping, and sliding window context compression without loss of state across agent reloads."),
        ("5. TACTICAL HUD & TELEMETRY", "• Project I.G.I. 3D extruded menus and CRT green theme matrices.\n• Btop++ live per-core CPU braille curves, RSS memory meters, network I/O, process management, and 360° sonar radar."),
    ]

    for title, body in sections:
        table.add_row(Text(f"\n{title}", style=f"bold {COLOR_PEACH}"))
        table.add_row(Text(body, style=f"dim {COLOR_TEXT}"))

    table.add_row(Text("\n" + "─" * 78, style=f"dim {COLOR_MUTED}", justify="center"))
    table.add_row(Text("Press Enter or 'q' to return to tactical menu...", style=f"bold {COLOR_MINT}", justify="center"))

    console.print()
    console.print(table)
    console.print()
