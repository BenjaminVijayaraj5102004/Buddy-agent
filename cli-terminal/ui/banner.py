"""
Banner & Tactical Header Layout for Buddy Agent
Provides clean, sleek, compact tactical status headers for the interactive shell.
"""

from typing import Optional
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from .theme import get_theme
from .state import SessionState


def render_banner(session: SessionState, theme_name: Optional[str] = None) -> Panel:
    """
    Renders a clean, compact tactical header for the interactive chat shell.
    """
    active_theme_name = theme_name or getattr(session, "theme", "igi")
    t = get_theme(active_theme_name)
    model_info = session.get_model_info()

    content = Table.grid(padding=(0, 1), expand=True)
    content.add_column(ratio=6)
    content.add_column(ratio=4, justify="right")

    left = Text()
    left.append("⚡ BUDDY AGENT ", style=f"bold {t['highlight']}")
    left.append("│ ", style=f"dim {t.get('box_border', t['box'])}")
    left.append("● ONLINE ", style=f"bold {t['meter_low']}")
    left.append(f"• 0x{session.session_id[:8].upper()} ", style=f"bold {t['dim_text']}")
    left.append(f"• Model: {model_info['name']}", style=f"dim {t['text']}")

    right = Text()
    right.append("Commands: ", style=f"dim {t['dim_text']}")
    right.append("/tools ", style=f"bold {t['highlight']}")
    right.append("• /menu • /top • /session • /help", style=f"dim {t['text']}")

    content.add_row(left, right)

    return Panel(
        content,
        border_style=f"dim {t['highlight']}",
        padding=(0, 1),
    )
