"""
Theme definitions for Btop Telemetry Monitor & Project I.G.I. HUD
"""

THEMES = {
    # 1. Authentic Project I.G.I. (Tactical Phosphor Green HUD)
    "igi": {
        "name": "Project I.G.I. (Phosphor Green)",
        "box": "#00ff55",
        "title": "#22c55e",
        "text": "#f0fdf4",
        "dim_text": "#15803d",
        "highlight": "#00ff55",
        "meter_low": "#22c55e",
        "meter_mid": "#84cc16",
        "meter_high": "#facc15",
        "meter_crit": "#ef4444",
        "graph_cpu": "#00ff55",
        "graph_mem": "#22c55e",
        "graph_net_rx": "#38bdf8",
        "graph_net_tx": "#a855f7",
        "proc_selected": "#00ff55",
    },
    # 2. Matrix Cyber (Digital Rain)
    "matrix": {
        "name": "Matrix Cyber (Digital Rain)",
        "box": "#00ff41",
        "title": "#008f11",
        "text": "#d1fae5",
        "dim_text": "#003b00",
        "highlight": "#00ff41",
        "meter_low": "#008f11",
        "meter_mid": "#00ff41",
        "meter_high": "#a3e635",
        "meter_crit": "#ef4444",
        "graph_cpu": "#00ff41",
        "graph_mem": "#008f11",
        "graph_net_rx": "#22d3ee",
        "graph_net_tx": "#4ade80",
        "proc_selected": "#00ff41",
    },
    # 3. Tokyo Night (Stealth Cyberpunk Blue)
    "tokyo_night": {
        "name": "Tokyo Night (Cyberpunk Blue)",
        "box": "#7aa2f7",
        "title": "#bb9af7",
        "text": "#c0caf5",
        "dim_text": "#565f89",
        "highlight": "#7dcfff",
        "meter_low": "#73daca",
        "meter_mid": "#e0af68",
        "meter_high": "#ff9e64",
        "meter_crit": "#f7768e",
        "graph_cpu": "#7aa2f7",
        "graph_mem": "#bb9af7",
        "graph_net_rx": "#7dcfff",
        "graph_net_tx": "#b4f9f8",
        "proc_selected": "#7aa2f7",
    },
    # 4. Catppuccin Mocha (Soothing Pastel)
    "catppuccin": {
        "name": "Catppuccin Mocha (Soothing Pastel)",
        "box": "#89b4fa",
        "title": "#cba6f7",
        "text": "#cdd6f4",
        "dim_text": "#585b70",
        "highlight": "#a6e3a1",
        "meter_low": "#a6e3a1",
        "meter_mid": "#f9e2af",
        "meter_high": "#fab387",
        "meter_crit": "#f38ba8",
        "graph_cpu": "#89b4fa",
        "graph_mem": "#cba6f7",
        "graph_net_rx": "#94e2d5",
        "graph_net_tx": "#f5c2e7",
        "proc_selected": "#89b4fa",
    },
    # 5. Dracula (Crimson Gothic)
    "dracula": {
        "name": "Dracula (Crimson Gothic)",
        "box": "#bd93f9",
        "title": "#ff79c6",
        "text": "#f8f8f2",
        "dim_text": "#6272a4",
        "highlight": "#50fa7b",
        "meter_low": "#50fa7b",
        "meter_mid": "#f1fa8c",
        "meter_high": "#ffb86c",
        "meter_crit": "#ff5555",
        "graph_cpu": "#bd93f9",
        "graph_mem": "#ff79c6",
        "graph_net_rx": "#8be9fd",
        "graph_net_tx": "#50fa7b",
        "proc_selected": "#bd93f9",
    },
}

DEFAULT_THEME = "igi"


def get_theme(theme_name: str = "igi") -> dict:
    """Returns the color palette dictionary for a given theme name."""
    return THEMES.get(theme_name.lower(), THEMES["igi"])
