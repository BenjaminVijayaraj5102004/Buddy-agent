"""
Project I.G.I. Tactical HUD Menu & Interface Engine for Buddy Agent
Fully interactive configuration tabs (General, Session, Satellite AI, Themes, Radar),
Session Archive & Memory manager, MCP Tools Catalog, and live btop telemetry & radar integration.
"""

import time
import sys
import os
import uuid
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from rich.console import Console, Group
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.live import Live
from rich.align import Align

from .theme import get_theme, THEMES
from .monitor import get_key_non_blocking, flush_input, run_btop_monitor
from .ascii_art import render_igi_header
from .dialogs import show_tool_list_table, show_session_dialog, show_models_dialog, show_readme_dialog
from .credits import run_credits_movie_scroll, show_credits_dialog
from .config import (
    IGI_GREEN_BRIGHT, IGI_GREEN_MID, IGI_GREEN_DIM,
    IGI_METALLIC, IGI_WHITE, IGI_AMBER
)


def render_igi_main_menu(selected_idx: int = 0, theme_name: str = "igi", session_id: str = "") -> Table:
    """Renders the clean, borderless Project I.G.I. tactical main menu."""
    t_colors = get_theme(theme_name)
    color_bright = t_colors.get("highlight", IGI_GREEN_BRIGHT)
    color_mid = t_colors.get("title", IGI_GREEN_MID)
    color_white = t_colors.get("text", IGI_WHITE)

    sid_short = f"0x{session_id[:8].upper()}" if session_id else "0xNEW"

    menu_items = [
        ("Play Buddy Agent", f"Launch interactive AI pair programming tactical shell ({sid_short})"),
        ("Session Archive & Memory", f"View, switch, or paste session UUID to resume context"),
        ("MCP Tools Catalog", "Explore active GitHub, SAM CLI & Text Editor MCP tools"),
        ("Configuration", "Configure satellite AI models, sessions, HUD themes & radar"),
        ("Telemetry & Radar", "Full-screen live system resources, interactive processes & AI radar"),
        ("Mission Briefing", "View tactical keybindings and operations manual"),
        ("End Credits & Creator", "Cinematic Dune-style end credits & Anonymous AI profile"),
        ("Read Me & Manual", "System topology, MCP specifications & architecture overview"),
        ("Quit", "Abort mission and exit CLI"),
    ]
    
    content = Table.grid(padding=(0, 0), expand=True)
    content.add_column()
    
    hdr = Text("MAIN MENU", style=f"bold {color_white}", justify="center")
    content.add_row(hdr)
    content.add_row(Text("─" * 78, style=f"dim {color_mid}", justify="center"))
    content.add_row(Text(""))
    
    grid = Table.grid(padding=(0, 2), expand=True)
    grid.add_column(ratio=5)
    grid.add_column(ratio=6)
    
    for idx, (title, desc) in enumerate(menu_items):
        is_sel = (idx == selected_idx)
        if is_sel:
            t_title = Text(f"▶  {title}", style=f"bold reverse {color_bright}")
            t_desc = Text(f"◀ {desc}", style=f"bold {color_bright}")
        else:
            t_title = Text(f"   {title}", style=f"bold {color_white}")
            t_desc = Text(desc, style=f"dim {color_mid}")
        grid.add_row(t_title, t_desc)
        
    content.add_row(grid)
    content.add_row(Text(""))
    content.add_row(Text("─" * 78, style=f"dim {color_mid}", justify="center"))
    
    foot = Text("Read Me [r]   •   Credits [c]   •   ▲/▼ Navigate   •   Enter Select   •   q Quit", style=f"bold {color_mid}", justify="center")
    content.add_row(foot)
    
    return content


def render_igi_options_menu(active_tab: int, selected_opt: int, session_obj) -> Table:
    """Renders the clean, borderless 5-tab tactical configuration screen (General, Session, Satellite AI, Theme, Radar)."""
    theme_name = getattr(session_obj, "theme", "igi")
    t_colors = get_theme(theme_name)
    color_bright = t_colors.get("highlight", IGI_GREEN_BRIGHT)
    color_mid = t_colors.get("title", IGI_GREEN_MID)
    color_white = t_colors.get("text", IGI_WHITE)
    color_steel = t_colors.get("dim_text", IGI_METALLIC)

    tabs = ["General", "Session", "Satellite AI", "HUD Theme", "Radar"]
    
    content = Table.grid(padding=(0, 0), expand=True)
    content.add_column()
    
    tab_hdr = Text()
    for idx, tab_name in enumerate(tabs):
        if idx == active_tab:
            tab_hdr.append(f"  [ {tab_name} ]  ", style=f"bold reverse {color_bright}")
        else:
            tab_hdr.append(f"    {tab_name}    ", style=f"bold {color_steel}")
    
    content.add_row(Text(f"CONFIGURATION OPTIONS\n", style=f"bold {color_white}", justify="center"))
    content.add_row(Align.center(tab_hdr))
    content.add_row(Text("─" * 78, style=f"dim {color_mid}", justify="center"))
    content.add_row(Text(""))

    grid = Table.grid(padding=(0, 2), expand=True)
    grid.add_column(ratio=5)
    grid.add_column(ratio=6)

    # Tab 0: General
    if active_tab == 0:
        opts = [
            ("Empathy Compliments", "[ENABLED]" if getattr(session_obj, "empathy_enabled", True) else "[DISABLED]"),
            ("Default Mission", f"[{getattr(session_obj, 'default_mission', 'FastAPI')}]"),
            ("Sound Effects / Chime", "[ENABLED]" if getattr(session_obj, "sound_enabled", True) else "[DISABLED]"),
        ]
    # Tab 1: Session
    elif active_tab == 1:
        cur_sid = getattr(session_obj, "session_id", "none")
        stored_count = 0
        try:
            from agent.memory import list_stored_sessions
            stored_count = len(list_stored_sessions())
        except Exception:
            pass
        opts = [
            ("Active Session UUID", f"[{cur_sid[:16]}...]"),
            ("Generate New Session", "[PRESS ENTER]"),
            ("Paste / Switch Session", f"[{stored_count} stored in archive]"),
            ("Session Auto-Save", "[ENABLED]" if getattr(session_obj, "autosave_enabled", True) else "[DISABLED]"),
        ]
    # Tab 2: Satellite AI
    elif active_tab == 2:
        main_inf = session_obj.get_subagent_model_info("main")
        api_inf = session_obj.get_subagent_model_info("api")
        gh_inf = session_obj.get_subagent_model_info("github")
        sam_inf = session_obj.get_subagent_model_info("sam")
        opts = [
            ("🤖 Main Buddy Agent", f"[{main_inf['name']}]"),
            ("⚡ REST API Agent", f"[{api_inf['name']}]"),
            ("🐙 GitHub Agent", f"[{gh_inf['name']}]"),
            ("📦 SAM CLI Deploy Agent", f"[{sam_inf['name']}]"),
            ("🔄 Sync All Agents to Main", "[PRESS ENTER]"),
            ("🧠 Satellite Model Matrix Dialog", "[OPEN DIALOG]"),
        ]
    # Tab 3: HUD Theme
    elif active_tab == 3:
        current_t = getattr(session_obj, "theme", "igi")
        opts = [
            ("Project I.G.I. (Phosphor Green)", "[ACTIVE]" if current_t == "igi" else "[STANDBY]"),
            ("Matrix Cyber (Digital Rain)", "[ACTIVE]" if current_t == "matrix" else "[STANDBY]"),
            ("Tokyo Night (Cyberpunk Blue)", "[ACTIVE]" if current_t == "tokyo_night" else "[STANDBY]"),
            ("Catppuccin Mocha (Soothing Pastel)", "[ACTIVE]" if current_t == "catppuccin" else "[STANDBY]"),
            ("Dracula Gothic (Vampire Purple)", "[ACTIVE]" if current_t == "dracula" else "[STANDBY]"),
        ]
    # Tab 4: Radar
    else:
        opts = [
            ("Radar Scan Rate", f"[{getattr(session_obj, 'radar_interval', 1.0)}s]"),
            ("Braille Topography Curves", "[ACTIVE]" if getattr(session_obj, "braille_graphs", True) else "[OFF]"),
            ("Per-Core Threat Analysis", "[ACTIVE]" if getattr(session_obj, "per_core_threat", True) else "[OFF]"),
            ("Bandwidth Sonar Ping", "[ACTIVE]" if getattr(session_obj, "bandwidth_telemetry", True) else "[OFF]"),
        ]

    for idx, (label, val) in enumerate(opts):
        is_sel = (idx == selected_opt)
        if is_sel:
            t_label = Text(f"▶  {label}", style=f"bold reverse {color_bright}")
            t_val = Text(f"◀ {val}", style=f"bold {color_bright}")
        else:
            t_label = Text(f"   {label}", style=f"bold {color_white}")
            t_val = Text(val, style=f"dim {color_mid}")
        grid.add_row(t_label, t_val)

    content.add_row(grid)
    content.add_row(Text(""))
    content.add_row(Text("─" * 78, style=f"dim {color_mid}", justify="center"))
    foot = Text("Tab Switch Category   •   ▲/▼ Navigate   •   Enter Toggle/Select   •   q / Esc Return", style=f"bold {color_mid}", justify="center")
    content.add_row(foot)

    return content


def render_igi_help_modal(theme_name: str = "igi") -> Table:
    """Renders the Mission Briefing & Tactical Operations Manual borderless."""
    t_colors = get_theme(theme_name)
    color_bright = t_colors.get("highlight", IGI_GREEN_BRIGHT)
    color_mid = t_colors.get("title", IGI_GREEN_MID)
    color_white = t_colors.get("text", IGI_WHITE)
    color_amber = t_colors.get("meter_high", IGI_AMBER)

    content = Table.grid(padding=(0, 2), expand=True)
    content.add_column(style=f"bold {color_amber}", width=22)
    content.add_column(style=f"bold {color_white}")

    content.add_row("MISSION OBJECTIVE:", "Autonomous AI Pair Programming & Tactical Infrastructure")
    content.add_row("TACTICAL SHELL:", "Type code prompts, FastAPI scaffolds, SAM builds, or GitHub actions")
    content.add_row("SESSION MEMORY:", "View or paste session UUID to resume context across runs")
    content.add_row("MCP TOOLS CATALOG:", "View /tools or tool_list for non-hardcoded MCP operations")
    content.add_row("BTOP++ TELEMETRY:", "Live CPU per-core braille curves, RAM RSS, network IO & radar")
    content.add_row("KEYBINDINGS:", "")
    content.add_row("  • ▲ / ▼ / w / j", "Navigate menu options and process cursor")
    content.add_row("  • Tab / ◄ / ►", "Switch configuration tabs (General, Session, AI, Theme, Radar)")
    content.add_row("  • Enter / Space", "Execute selected tactical action or toggle setting")
    content.add_row("  • /session, /tools, /help", "Interactive commands available inside AI shell")
    content.add_row("  • q / Esc", "Return to main HUD / Abort mission")

    wrapper = Table.grid(padding=(0, 0), expand=True)
    wrapper.add_column()
    wrapper.add_row(Text("📖 PROJECT BUDDY // MISSION BRIEFING\n", style=f"bold {color_bright}", justify="center"))
    wrapper.add_row(Text("─" * 78, style=f"dim {color_mid}", justify="center"))
    wrapper.add_row(content)
    wrapper.add_row(Text("─" * 78, style=f"dim {color_mid}", justify="center"))
    wrapper.add_row(Text("Press 'q' or Esc to return to Main Menu", style=f"bold {color_mid}", justify="center"))
    return wrapper


def run_btop_game_interface(session_obj, console_obj: Optional[Console] = None):
    """
    Main interactive loop providing the authentic Project I.G.I. tactical HUD interface.
    """
    if console_obj is None:
        console_obj = Console()

    current_screen = "main_menu"
    main_menu_idx = 0
    options_tab = 0
    options_opt_idx = 0

    missions_list = ["FastAPI", "SAM-Serverless", "GitHub-Action"]
    mission_idx = 0
    intervals_list = [0.5, 1.0, 2.0, 3.0]
    interval_idx = 1

    console_obj.clear()
    is_screen = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True

    with Live(console=console_obj, screen=is_screen, refresh_per_second=20) as live:
        while True:
            active_theme = getattr(session_obj, "theme", "igi")
            header = render_igi_header(theme_name=active_theme)

            # Render according to current screen state
            if current_screen == "main_menu":
                body = render_igi_main_menu(main_menu_idx, theme_name=active_theme, session_id=session_obj.session_id)
            elif current_screen == "options":
                body = render_igi_options_menu(options_tab, options_opt_idx, session_obj)
            elif current_screen == "help":
                body = render_igi_help_modal(theme_name=active_theme)
            else:
                body = render_igi_main_menu(main_menu_idx, theme_name=active_theme, session_id=session_obj.session_id)

            live.update(Group(header, body))

            # Non-blocking key check
            key = get_key_non_blocking()
            if key:
                if key in ('q', '\x1b'):
                    if current_screen != "main_menu":
                        current_screen = "main_menu"
                    else:
                        break  # exit program cleanly
                elif key in ('k', 'up', 'w'):
                    if current_screen == "main_menu":
                        main_menu_idx = max(0, main_menu_idx - 1)
                    elif current_screen == "options":
                        max_opt = {0: 2, 1: 3, 2: 5, 3: 4, 4: 3}.get(options_tab, 3)
                        options_opt_idx = max(0, options_opt_idx - 1)
                elif key in ('j', 'down', 's_key'):
                    if current_screen == "main_menu":
                        main_menu_idx = min(8, main_menu_idx + 1)
                    elif current_screen == "options":
                        max_opt = {0: 2, 1: 3, 2: 5, 3: 4, 4: 3}.get(options_tab, 3)
                        options_opt_idx = min(max_opt, options_opt_idx + 1)
                elif key == '\t' or key in ('l', 'right'):
                    if current_screen == "options":
                        options_tab = (options_tab + 1) % 5
                        options_opt_idx = 0
                elif key in ('h', 'left'):
                    if current_screen == "options":
                        options_tab = (options_tab - 1) % 5
                        options_opt_idx = 0
                    elif current_screen == "main_menu" and key == 'h':
                        current_screen = "help"
                elif key == 'c' and current_screen == "main_menu":
                    live.stop()
                    flush_input()
                    run_credits_movie_scroll(console_obj)
                    flush_input()
                    console_obj.clear()
                    live.start()
                elif key == 'r' and current_screen == "main_menu":
                    live.stop()
                    flush_input()
                    show_readme_dialog(console_obj)
                    flush_input()
                    console_obj.clear()
                    live.start()
                elif key == 'm':
                    current_screen = "main_menu"
                elif key in ('\r', '\n', ' '):  # Enter or Space
                    if current_screen == "main_menu":
                        if main_menu_idx == 0:  # PLAY BUDDY AGENT
                            live.stop()
                            console_obj.clear()
                            from .repl import run_interactive_shell
                            run_interactive_shell(session_obj, console_obj)
                            console_obj.clear()
                            live.start()
                        elif main_menu_idx == 1:  # SESSION ARCHIVE & MEMORY
                            live.stop()
                            console_obj.clear()
                            show_session_dialog(session_obj, console_obj)
                            console_obj.input("\n[bold #00ff55]Press Enter to return to Project I.G.I. tactical menu...[/]")
                            console_obj.clear()
                            live.start()
                        elif main_menu_idx == 2:  # MCP TOOLS CATALOG
                            live.stop()
                            console_obj.clear()
                            show_tool_list_table(console_obj)
                            console_obj.input("\n[bold #00ff55]Press Enter to return to Project I.G.I. tactical menu...[/]")
                            console_obj.clear()
                            live.start()
                        elif main_menu_idx == 3:  # CONFIGURATION
                            current_screen = "options"
                            options_tab = 0
                            options_opt_idx = 0
                        elif main_menu_idx == 4:  # TELEMETRY & RADAR (ACTUAL FULL BTOP FEATURES)
                            live.stop()
                            flush_input()
                            active_theme = getattr(session_obj, "theme", "igi")
                            run_btop_monitor(
                                console_obj,
                                theme_name=active_theme,
                                initial_refresh_rate=getattr(session_obj, "radar_interval", 1.0),
                                session_obj=session_obj
                            )
                            flush_input()
                            if hasattr(console_obj, "clear") and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                                console_obj.clear()
                            live.start()
                        elif main_menu_idx == 5:  # MISSION BRIEFING
                            current_screen = "help"
                        elif main_menu_idx == 6:  # END CREDITS & CREATOR
                            live.stop()
                            flush_input()
                            run_credits_movie_scroll(console_obj)
                            flush_input()
                            console_obj.clear()
                            live.start()
                        elif main_menu_idx == 7:  # READ ME & MANUAL
                            live.stop()
                            flush_input()
                            show_readme_dialog(console_obj)
                            flush_input()
                            console_obj.clear()
                            live.start()
                        elif main_menu_idx == 8:  # QUIT
                            break
                    elif current_screen == "options":
                        if options_tab == 0:  # General
                            if options_opt_idx == 0:
                                session_obj.empathy_enabled = not getattr(session_obj, "empathy_enabled", True)
                            elif options_opt_idx == 1:
                                mission_idx = (mission_idx + 1) % len(missions_list)
                                session_obj.default_mission = missions_list[mission_idx]
                            elif options_opt_idx == 2:
                                session_obj.sound_enabled = not getattr(session_obj, "sound_enabled", True)
                        elif options_tab == 1:  # Session
                            if options_opt_idx == 0:
                                live.stop()
                                console_obj.clear()
                                show_session_dialog(session_obj, console_obj)
                                console_obj.input("\n[bold #00ff55]Press Enter to return to options...[/]")
                                console_obj.clear()
                                live.start()
                            elif options_opt_idx == 1:
                                new_id = str(uuid.uuid4())
                                session_obj.session_id = new_id
                                session_obj.messages_count = 0
                                session_obj.total_input_tokens = 0
                                session_obj.total_output_tokens = 0
                                session_obj.reset_agent()
                                try:
                                    from agent.memory import set_current_session_id
                                    set_current_session_id(new_id)
                                except Exception:
                                    pass
                            elif options_opt_idx == 2:
                                live.stop()
                                console_obj.clear()
                                show_session_dialog(session_obj, console_obj)
                                console_obj.input("\n[bold #00ff55]Press Enter to return to options...[/]")
                                console_obj.clear()
                                live.start()
                            elif options_opt_idx == 3:
                                session_obj.autosave_enabled = not getattr(session_obj, "autosave_enabled", True)
                        elif options_tab == 2:  # Satellite AI
                            if options_opt_idx in (0, 1, 2, 3, 5):
                                live.stop()
                                console_obj.clear()
                                show_models_dialog(session_obj, console_obj)
                                console_obj.input("\n[bold #00ff55]Press Enter to return to options...[/]")
                                console_obj.clear()
                                live.start()
                            elif options_opt_idx == 4:  # Sync all agents to main
                                session_obj.switch_model(session_obj.model_key, agent_name="all")
                        elif options_tab == 3:  # HUD Theme
                            theme_keys = ["igi", "matrix", "tokyo_night", "catppuccin", "dracula"]
                            session_obj.theme = theme_keys[options_opt_idx % len(theme_keys)]
                        elif options_tab == 4:  # Radar
                            if options_opt_idx == 0:
                                interval_idx = (interval_idx + 1) % len(intervals_list)
                                session_obj.radar_interval = intervals_list[interval_idx]
                            elif options_opt_idx == 1:
                                session_obj.braille_graphs = not getattr(session_obj, "braille_graphs", True)
                            elif options_opt_idx == 2:
                                session_obj.per_core_threat = not getattr(session_obj, "per_core_threat", True)
                            elif options_opt_idx == 3:
                                session_obj.bandwidth_telemetry = not getattr(session_obj, "bandwidth_telemetry", True)

            time.sleep(0.04)
