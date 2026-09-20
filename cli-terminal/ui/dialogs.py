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


from rich.markdown import Markdown


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
        ("/readme, /manual", "Manual", "Interactive system documentation, architecture & manual reader"),
        ("/tools, /tool_list", "Governance", "List active MCP tools (GitHub, SAM CLI, Text Editor)"),
        ("/top, /monitor", "Telemetry", "Launch interactive btop++ live system & AI radar"),
        ("/menu", "Interface", "Open Project I.G.I. 3D tactical HUD configuration menu"),
        ("/model, /models", "AI Satellite", "Switch LLM satellite models per agent or synchronized"),
        ("/session", "Memory", "View, paste, or switch session UUID and context"),
        ("/demo", "Mission", "Run automated FastAPI endpoint scaffolding demonstration"),
        ("/clear", "Display", "Clear screen and redraw tactical HUD banner"),
        ("/help", "Manual", "Display this tactical command reference"),
        ("/exit, /quit", "System", "Save session and exit tactical shell cleanly"),
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
        ("Main Orchestrator (Buddy)", "main"),
        ("REST API Agent", "api"),
        (" GitHub Agent", "github"),
        ("SAM CLI Deploy Agent", "sam"),
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
            m["key"] == session.subagent_models.get(k, "")
            or m.get("model_id", "") == session.subagent_models.get(k, "")
            or (m["key"] == "groq" and session.subagent_models.get(k, "") in ("groq", "qwen/qwen3.8-27b"))
            or (m["key"] == "ollama" and session.subagent_models.get(k, "") in ("ollama", "llama3.1:8b"))
            or (m["key"] == "bedrock" and session.subagent_models.get(k, "") in ("bedrock", "us.anthropic.claude-3-7-sonnet-20250219-v1:0"))
            for k in ("main", "api", "github", "sam")
        )
        status_str = f"[{COLOR_MINT}]● ACTIVE[/{COLOR_MINT}]" if is_active else "[dim]STANDBY[/dim]"
        table.add_row(
            f"[{m['id']}]",
            str(m["provider"]),
            str(m["name"]),
            str(m.get("model_id", m["key"])),
            status_str,
        )




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
    box_content.append("ACTIVE SESSION UUID:\n", style="bold #facc15")
    box_content.append(f"{session.session_id}\n\n", style="bold #00ff55")
    box_content.append(f"Active Model: {session.model_key.upper()} |  Telemetry: {session.messages_count} messages\n", style="bold #38bdf8")
    box_content.append(f" In: {session.total_input_tokens:,} tokens |  Out: {session.total_output_tokens:,} tokens\n\n", style="dim #94a3b8")
    box_content.append(" Copy the UUID above to resume this exact state anytime.", style="italic #38bdf8")

    console.print()
    console.print(Text("BUDDY AGENT // SESSION CONTEXT", style="bold #00ff55", justify="center"))
    console.print(Text("─" * 78, style="dim #15803d", justify="center"))
    console.print(box_content)
    console.print(Text("─" * 78, style="dim #15803d", justify="center"))
    console.print()

    if stored_sessions:
        table = Table(
            title=" [bold #00ff55]STORED SESSIONS ARCHIVE (./agent/memory/sessions_data)[/bold #00ff55]",
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
        console.print(f"[{COLOR_MINT}]Started new session: {session.session_id} (Model: {session.model_key})[/{COLOR_MINT}]\n")
        return

    # Check for selection by number
    if raw_input.isdigit() and stored_sessions:
        idx = int(raw_input) - 1
        if 0 <= idx < len(stored_sessions):
            target_id = stored_sessions[idx]
            session.switch_session(target_id)
            console.print(f"[{COLOR_MINT}] Switched to session #{idx+1}: {session.session_id} (Model: {session.model_key})[/{COLOR_MINT}]\n")
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
        console.print(f"[{COLOR_MINT}] Resumed session: {session.session_id} (Model: {session.model_key})[/{COLOR_MINT}]\n")


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

    table.add_column("GitHub MCP Tools", style=f"bold {COLOR_TEXT}", ratio=4)
    table.add_column("SAM CLI MCP Tools", style=f"bold {COLOR_TEXT}", ratio=4)
    table.add_column("Text Editor MCP Tools", style=f"bold {COLOR_TEXT}", ratio=4)

    max_len = max(len(github_tools), len(sam_tools), len(text_tools))

    for i in range(max_len):
        col1 = f"• [bold {COLOR_BLUE}]{github_tools[i][0]}[/]\n  [dim]{github_tools[i][1]}[/]" if i < len(github_tools) else ""
        col2 = f"• [bold {COLOR_AMBER}]{sam_tools[i][0]}[/]\n  [dim]{sam_tools[i][1]}[/]" if i < len(sam_tools) else ""
        col3 = f"• [bold {COLOR_PURPLE}]{text_tools[i][0]}[/]\n  [dim]{text_tools[i][1]}[/]" if i < len(text_tools) else ""
        table.add_row(col1, col2, col3)

    console.print()
    console.print(table)
    console.print()


import time
from rich.live import Live


def build_readme_movie_corpus() -> list[Text]:
    """Assembles the cinematic scrolling movie end-card for Buddy Agent documentation and manual."""
    lines: list[Text] = []

    # Typography & Palette
    COLOR_TITLE = "#ffffff"
    COLOR_SUB = "#e4e4e7"
    COLOR_PLATINUM = "#d4d4d8"
    COLOR_GREEN = "#00ff66"
    COLOR_CYAN = "#38bdf8"
    COLOR_AMBER = "#facc15"
    COLOR_PURPLE_SOFT = "#c084fc"
    COLOR_GRAY_LIGHT = "#a1a1aa"
    COLOR_GRAY_MID = "#71717a"
    COLOR_GRAY_DARK = "#3f3f46"

    def blank(n: int = 1):
        for _ in range(n):
            lines.append(Text(""))

    def centered(text: str, style: str):
        lines.append(Text(text, style=style, justify="center"))

    def role_pair(label: str, val: str, left_w: int = 30, right_w: int = 48):
        t = Text(justify="center")
        t.append(label.rjust(left_w) + "   ", style=f"dim {COLOR_GRAY_LIGHT}")
        t.append(val.ljust(right_w), style=f"bold {COLOR_SUB}")
        lines.append(t)

    def section_header(title: str):
        blank(2)
        centered("═" * 68, f"dim {COLOR_GRAY_DARK}")
        centered(title.upper(), f"bold {COLOR_GREEN}")
        centered("═" * 68, f"dim {COLOR_GRAY_DARK}")
        blank(1)

    # 1. Opening Header / Title Card
    blank(3)
    centered("B U D D Y   A G E N T", f"bold {COLOR_TITLE}")
    centered("AUTONOMOUS PAIR PROGRAMMING & CLOUD INFRASTRUCTURE ORCHESTRATION", f"bold {COLOR_CYAN}")
    blank(1)
    centered("SYSTEM ARCHITECTURE & TECHNICAL OPERATIONS MANUAL", f"dim {COLOR_GRAY_LIGHT}")
    centered("Release: 2026.09-LTS • Python 3.14 • Strands Agents SDK", f"dim {COLOR_GRAY_MID}")
    blank(3)

    # 2. Executive Overview
    section_header("1. EXECUTIVE OVERVIEW")
    centered("Buddy Agent is an autonomous, production-grade pair programming and infrastructure orchestrator.", f"bold {COLOR_SUB}")
    centered("It eliminates context fatigue by distributing backend engineering across specialized micro-agents.", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("Runtime Engine", "Python 3.14 + Strands Agents SDK")
    role_pair("Core Architecture", "Hierarchical Micro-Agent Delegation")
    role_pair("Model Layer", "Dynamic Multi-Provider Model Routing & BYOM")
    role_pair("Tool Standard", "Standardized Model Context Protocol (MCP)")
    role_pair("Memory Persistence", "Multi-Tier Session UUIDs + S3 + Knowledge Base")
    role_pair("Interface HUD", "Project I.G.I. Night-Vision + Btop++ Live Telemetry")
    blank(2)

    # 3. System Architecture & Topology
    section_header("2. SYSTEM ARCHITECTURE & TOPOLOGY")
    centered("The system decomposes high-level user intent into structured, bounded execution plans:", f"dim {COLOR_PLATINUM}")
    blank(1)
    centered("┌─────────────────────────────────────────────────────────────┐", f"dim {COLOR_GRAY_MID}")
    centered("│                   BUDDY ORCHESTRATOR                        │", f"bold {COLOR_CYAN}")
    centered("│           (Master Planner & Intent Classifier)              │", f"dim {COLOR_GRAY_LIGHT}")
    centered("└──────────────┬──────────────────────────────┬───────────────┘", f"dim {COLOR_GRAY_MID}")
    centered("               │                              │                ", f"dim {COLOR_GRAY_MID}")
    centered("      ┌────────┴─────────┐           ┌────────┴────────┐       ", f"dim {COLOR_GRAY_MID}")
    centered("      │   API MANAGER    │           │  GITHUB AGENT   │       ", f"bold {COLOR_AMBER}")
    centered("      │  (Schema Design) │           │ (PRs & Issues)  │       ", f"dim {COLOR_GRAY_LIGHT}")
    centered("      └────────┬─────────┘           └─────────────────┘       ", f"dim {COLOR_GRAY_MID}")
    centered("               │                                               ", f"dim {COLOR_GRAY_MID}")
    centered("      ┌────────┴─────────┐           ┌─────────────────┐       ", f"dim {COLOR_GRAY_MID}")
    centered("      │    REST AGENT    │           │  SAM CLI AGENT  │       ", f"bold {COLOR_PURPLE_SOFT}")
    centered("      │ (FastAPI & Text) │           │(AWS Deploy/Sync)│       ", f"dim {COLOR_GRAY_LIGHT}")
    centered("      └──────────────────┘           └─────────────────┘       ", f"dim {COLOR_GRAY_MID}")
    blank(1)
    role_pair("Buddy Orchestrator", "Top-level intent classification, multi-phase plans, agent routing")
    role_pair("API Manager", "REST route architecture, strict Pydantic schemas, parameter validation")
    role_pair("REST Agent", "FastAPI microservice implementation and atomic code editing")
    role_pair("GitHub Agent", "Automated commits, branch management, issue tracking, and PR reviews")
    role_pair("SAM CLI Agent", "Builds, packages, validates, and deploys CloudFormation templates")
    blank(2)

    # 4. Dynamic Model Routing & BYOM
    section_header("3. DYNAMIC MODEL ROUTING & BYOM")
    centered("Supports independent per-agent LLM allocation across high-speed LPUs, local weights, and cloud:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("Groq Cloud (Default)", "qwen/qwen3.8-27b  (High-Throughput Intent Classification)")
    role_pair("Groq Cloud (Large)", "openai/gpt-oss-120b  (Context-Heavy Analysis)")
    role_pair("Groq Cloud (Guard)", "meta-llama/llama-prompt-guard-2-22m  (Prompt Security)")
    role_pair("Ollama Local (Default)", "llama3.1:8b  (Local Air-Gapped Execution)")
    role_pair("Ollama Local (Coder)", "qwen2.5-coder:32b  (Precision Code Syntax & Pydantic)")
    role_pair("Ollama Local (Compact)", "qwen:7b  (Low-Latency Lightweight Scaffolding)")
    role_pair("AWS Bedrock (Cloud)", "us.anthropic.claude-3-7-sonnet-20250219-v1:0  (Complex Infra)")
    role_pair("Bring Your Own Model", "Custom syntax: groq:<model_id> or ollama:<model_id>")
    blank(2)

    # 5. Model Context Protocol (MCP) Integration
    section_header("4. MODEL CONTEXT PROTOCOL (MCP) INTEGRATION")
    centered("All external interactions execute via non-hardcoded MCP stdio servers:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("GitHub MCP Client", "create_pull_request • merge_pull_request • create_issue")
    role_pair("", "list_issues • get_issue • update_issue • create_branch")
    role_pair("", "list_branches • create_commit • fork_repository")
    blank(1)
    role_pair("SAM CLI MCP Client", "sam deploy • sam sync • sam build • sam package")
    role_pair("", "sam validate • sam logs • sam list • sam delete")
    blank(1)
    role_pair("Text Editor MCP Client", "create_or_update_file • replace_file_content")
    role_pair("", "multi_replace_file_content • delete_text_file_contents")
    role_pair("", "view_file_contents • list_directory_contents")
    blank(2)

    # 6. Memory Architecture & State Persistence
    section_header("5. MEMORY ARCHITECTURE & PERSISTENCE")
    centered("Multi-tier memory guarantees session continuity and prevents catastrophic forgetting:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("Session UUID Archive", "Disk & Amazon S3 storage preserving turns & subagent models")
    role_pair("UUID Hot-Swapping", "Paste or select any historic UUID to resume full context")
    role_pair("Sliding Window Compression", "SafeSlidingWindow preserves system guardrails & active tools")
    role_pair("Long-Term Vector Memory", "AWS Bedrock Knowledge Base semantic retrieval across sessions")
    blank(2)

    # 7. Main Menu Operations Manual & How It Works
    section_header("6. MAIN MENU OPERATIONS MANUAL")
    centered("Comprehensive guide to each Project I.G.I. HUD menu option and operational workflow:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("1. Play Buddy Agent", "Launches interactive AI pair programming shell.")
    role_pair("", "Accepts natural language prompts, creates FastAPI endpoints,")
    role_pair("", "invokes MCP tools, and preserves session state upon exit.")
    blank(1)
    role_pair("2. Session Archive", "Displays all past conversation sessions by UUID.")
    role_pair("", "Allows switching active context, generating fresh UUIDs,")
    role_pair("", "or pasting past IDs to restore message history and models.")
    blank(1)
    role_pair("3. MCP Tools Catalog", "Inspects active tools across GitHub, SAM CLI, and Editor.")
    role_pair("", "Shows parameter definitions and tool execution scopes.")
    blank(1)
    role_pair("4. Configuration", "5-tab tactical configuration screen:")
    role_pair("  • Tab 0 (General)", "Toggle empathy compliments, sound chimes & default missions.")
    role_pair("  • Tab 1 (Session)", "Inspect active UUID, regenerate sessions, toggle autosave.")
    role_pair("  • Tab 2 (Satellite AI)", "Configure models per sub-agent or synchronize all to master.")
    role_pair("  • Tab 3 (HUD Theme)", "Switch CRT themes (Phosphor Green, Matrix, Tokyo Night, etc.)")
    role_pair("  • Tab 4 (Radar)", "Configure radar refresh rates, braille curves & telemetry.")
    blank(1)
    role_pair("5. Telemetry & Radar", "Full-screen live Btop++ monitoring interface.")
    role_pair("", "Renders per-core CPU braille curves, RSS memory breakdown,")
    role_pair("", "interactive process manager, and 360-degree sonar radar.")
    blank(1)
    role_pair("6. Mission Briefing", "Displays tactical keybindings and keyboard shortcuts manual.")
    blank(1)
    role_pair("7. End Credits & Creator", "Dune-style movie end credits for lead architect Benjamin V.")
    blank(1)
    role_pair("8. Read Me & Manual", "Launches this cinematic full documentation & manual scroll.")
    blank(1)
    role_pair("9. Quit", "Flushes active session memory and exits CLI cleanly.")
    blank(2)

    # 8. Tactical CLI Reference
    section_header("7. CLI REFERENCE & COMMAND MANUAL")
    centered("Available hotkeys and interactive commands:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("/help", "Displays tactical command reference")
    role_pair("/readme  /manual", "Launches this cinematic documentation movie scroll")
    role_pair("/tools  /tool_list", "Lists active non-hardcoded MCP tools")
    role_pair("/top  /monitor", "Launches live Btop++ system telemetry and radar")
    role_pair("/menu", "Opens Project I.G.I. tactical configuration menu")
    role_pair("/model  /models", "Opens multi-agent satellite model assignment matrix")
    role_pair("/session", "Opens session archive, switch, or paste UUID")
    role_pair("/demo", "Runs automated FastAPI scaffolding demonstration")
    role_pair("/clear  /cls", "Clears terminal screen and redraws tactical HUD banner")
    role_pair("/exit  /quit", "Saves session and exits tactical shell cleanly")
    blank(2)

    # 9. Engineering & Model Stack
    section_header("8. ENGINEERING & FOUNDATION MODEL STACK")
    centered("Architected and engineered using modern foundation models aligned to specific tasks:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("Gemini 3.7 Flash", "Interface design, Project I.G.I. HUD, palette systems,")
    role_pair("", "and real-time high-throughput telemetry rendering.")
    blank(1)
    role_pair("Gemini 3.7", "Complex multi-agent orchestration architecture, state persistence,")
    role_pair("", "sliding-window context management, and MCP client protocols.")
    blank(2)

    # 10. Installation & Quickstart
    section_header("9. INSTALLATION & QUICKSTART")
    centered("Simple setup workflow with Python 3.14 and uv:", f"dim {COLOR_PLATINUM}")
    blank(1)
    role_pair("1. Clone Repository", "git clone https://github.com/BenjaminVijayaraj5102004/Buddy-agent.git")
    role_pair("2. Install Dependencies", "cd Buddy-agent && uv sync")
    role_pair("3. Configure Env", "cp .env.example .env (Set GROQ_API_KEY, GITHUB_PAT, OLLAMA_BASE_URL)")
    role_pair("4. Launch HUD Menu", "uv run python cli-terminal/cli.py")
    role_pair("5. Interactive REPL", "uv run python -m buddy.buddy")
    role_pair("6. One-Shot Command", "uv run python cli-terminal/cli.py ask \"Create a FastAPI endpoint\"")
    blank(3)

    # 11. Closing Signature Card
    centered("✦  BUDDY AGENT // MISSION STATUS: OPERATIONAL  ✦", f"bold {COLOR_TITLE}")
    centered("LEAD ARCHITECT: BENJAMIN V  •  B.TECH 2027", f"bold {COLOR_GREEN}")
    centered("github.com/BenjaminVijayaraj5102004/Buddy-agent", f"bold {COLOR_CYAN}")
    centered("COPYRIGHT © 2026 BENJAMIN V • ALL RIGHTS RESERVED", f"dim {COLOR_GRAY_LIGHT}")
    blank(4)

    return lines


def run_readme_movie_scroll(console: Optional[Console] = None) -> None:
    """
    Runs an authentic cinematic scrolling movie end-card for Buddy Agent documentation.
    Features smooth continuous scrolling, pause/speed controls, and keyboard navigation.
    """
    if console is None:
        console = Console()

    corpus = build_readme_movie_corpus()

    # Non-blocking keypress helper
    def get_key():
        if sys.platform == "win32":
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    code = msvcrt.getwch()
                    if code in ('H', 'w', 'k'): return 'up'
                    if code in ('P', 's', 'j'): return 'down'
                return ch.lower()
        return None

    term_height = console.height or 32
    view_height = max(18, term_height - 3)

    total_lines = len(corpus)
    scroll_pos = 0.0
    scroll_speed = 0.45  # lines per tick
    is_paused = False

    console.clear()

    with Live(console=console, screen=True, auto_refresh=False) as live:
        while True:
            k = get_key()
            if k in ('q', '\x1b', '\r', '\n'):
                break
            elif k == ' ':
                is_paused = not is_paused
            elif k in ('+', '='):
                scroll_speed = min(2.5, scroll_speed + 0.15)
            elif k in ('-', '_'):
                scroll_speed = max(0.15, scroll_speed - 0.15)
            elif k in ('up', 'w', 'k'):
                scroll_pos = max(0.0, scroll_pos - 3)
            elif k in ('down', 's', 'j'):
                scroll_pos = min(float(total_lines - view_height), scroll_pos + 3)

            # Advance scrolling position
            if not is_paused:
                scroll_pos += scroll_speed
                if scroll_pos >= total_lines:
                    scroll_pos = 0.0  # Loop back smoothly

            # Extract window of lines
            start_idx = int(scroll_pos)
            end_idx = min(total_lines, start_idx + view_height)
            visible_lines = corpus[start_idx:end_idx]

            # Build borderless grid
            grid = Table.grid(padding=(0, 0), expand=True)
            grid.add_column()

            for line in visible_lines:
                grid.add_row(line)

            # Fill remaining rows if needed
            for _ in range(view_height - len(visible_lines)):
                grid.add_row(Text(""))

            # Discrete bottom HUD controls
            status_str = "PAUSED" if is_paused else f"{scroll_speed:.2f}x"
            hud_footer = Text(
                f"   [Space] {status_str}   •   [+/-] Speed   •   [▲/▼] Scroll   •   [q / Enter] Return",
                style="dim #3f3f46",
                justify="center"
            )
            grid.add_row(hud_footer)

            live.update(grid, refresh=True)
            time.sleep(0.06)


def show_readme_dialog(console: Optional[Console] = None) -> None:
    """Entrypoint to launch the cinematic README & Manual movie end-card scroll."""
    run_readme_movie_scroll(console)

