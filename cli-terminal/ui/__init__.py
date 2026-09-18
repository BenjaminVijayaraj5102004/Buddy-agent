"""
Buddy Agent UI Package
Modular terminal UI/UX architecture for Buddy Agent:
- Tactical Project I.G.I. HUD & Menus
- Session Archive & Memory Switcher
- Btop++ Live Hardware Telemetry & Sonar Radar
- MCP Tools Governance & Non-Hardcoded Filtering
- Interactive REPL & Task Executor
"""

import os
import sys

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from .config import (
    APP_NAME, VERSION, MODELS_CATALOG,
    COLOR_PEACH, COLOR_AMBER, COLOR_MINT, COLOR_BLUE,
    COLOR_PURPLE, COLOR_ROSE, COLOR_TEXT, COLOR_MUTED,
    IGI_GREEN_BRIGHT, IGI_GREEN_MID, IGI_GREEN_DIM,
    IGI_METALLIC, IGI_WHITE, IGI_AMBER,
    get_random_champ_compliment
)
from .state import SessionState, active_session
from .theme import get_theme, THEMES, DEFAULT_THEME
from .graphs import (
    generate_braille_graph, generate_meter,
    generate_sparkline, generate_tactical_radar_art
)
from .ascii_art import (
    render_igi_header, render_word_sculpted_title,
    WORD_SILHOUETTE_MASK, FULL_WORDINGS_CORPUS
)
from .animations import BuddyEmpathyComplimentsAnimation
from .tools_catalog import get_non_hardcoded_mcp_tools
from .dialogs import (
    show_help_table, show_models_dialog,
    show_session_dialog, show_tool_list_table
)
from .executor import execute_agent_task
from .banner import render_banner
from .collector import SystemCollector, format_bytes
from .renderer import BtopRenderer
from .monitor import run_btop_monitor, get_key_non_blocking, flush_input
from .menu import (
    render_igi_main_menu, render_igi_options_menu,
    render_igi_help_modal, run_btop_game_interface
)
from .repl import run_interactive_shell

__all__ = [
    "APP_NAME",
    "VERSION",
    "MODELS_CATALOG",
    "SessionState",
    "active_session",
    "get_theme",
    "THEMES",
    "DEFAULT_THEME",
    "generate_braille_graph",
    "generate_meter",
    "generate_sparkline",
    "generate_tactical_radar_art",
    "render_igi_header",
    "render_word_sculpted_title",
    "BuddyEmpathyComplimentsAnimation",
    "get_non_hardcoded_mcp_tools",
    "show_help_table",
    "show_models_dialog",
    "show_session_dialog",
    "show_tool_list_table",
    "execute_agent_task",
    "render_banner",
    "SystemCollector",
    "format_bytes",
    "BtopRenderer",
    "run_btop_monitor",
    "get_key_non_blocking",
    "flush_input",
    "render_igi_main_menu",
    "render_igi_options_menu",
    "render_igi_help_modal",
    "run_btop_game_interface",
    "run_interactive_shell",
]
