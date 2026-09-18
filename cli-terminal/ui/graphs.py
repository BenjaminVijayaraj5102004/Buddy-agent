"""
Braille, Block Graph, and Tactical Radar generator matching btop++ and Project I.G.I.
"""

from typing import List
from rich.text import Text

LEFT_DOTS = [0x00, 0x40, 0x40 | 0x04, 0x40 | 0x04 | 0x02, 0x40 | 0x04 | 0x02 | 0x01]
RIGHT_DOTS = [0x00, 0x80, 0x80 | 0x20, 0x80 | 0x20 | 0x10, 0x80 | 0x20 | 0x10 | 0x08]
BLOCK_CHARS = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


def generate_braille_graph(
    data: List[float],
    width: int,
    height: int = 4,
    color_low: str = "#00ff55",
    color_mid: str = "#facc15",
    color_high: str = "#fb923c",
    color_crit: str = "#ef4444",
) -> List[Text]:
    """Generates a multi-line braille line graph matching btop++."""
    required_points = width * 2
    padded_data = [0.0] * required_points
    if data:
        slice_data = data[-required_points:]
        padded_data[-len(slice_data):] = slice_data

    total_dots = height * 4
    lines: List[Text] = []
    
    for row in range(height):
        row_min_dots = (height - 1 - row) * 4
        line_text = Text()
        
        for col in range(width):
            val1 = padded_data[col * 2]
            val2 = padded_data[col * 2 + 1]
            
            dots1 = int((val1 / 100.0) * total_dots + 0.5)
            dots2 = int((val2 / 100.0) * total_dots + 0.5)
            
            d1_in_row = max(0, min(4, dots1 - row_min_dots))
            d2_in_row = max(0, min(4, dots2 - row_min_dots))
            
            if d1_in_row == 0 and d2_in_row == 0:
                char = " "
            else:
                code = 0x2800 | LEFT_DOTS[d1_in_row] | RIGHT_DOTS[d2_in_row]
                char = chr(code)
                
            avg_val = (val1 + val2) / 2.0
            if avg_val >= 85.0:
                style = f"bold {color_crit}"
            elif avg_val >= 65.0:
                style = color_high
            elif avg_val >= 35.0:
                style = color_mid
            else:
                style = color_low
                
            line_text.append(char, style=style if char != " " else "")
            
        lines.append(line_text)
        
    return lines


def generate_meter(
    percent: float,
    width: int = 15,
    style_low: str = "#00ff55",
    style_mid: str = "#facc15",
    style_high: str = "#fb923c",
    style_crit: str = "#ef4444",
    empty_style: str = "dim #14532d",
) -> Text:
    """Generates a btop-style segmented meter bar [■■■■■░░░░░]"""
    clamped = max(0.0, min(100.0, percent))
    filled_chars = int((clamped / 100.0) * width + 0.5)
    empty_chars = width - filled_chars
    
    t = Text()
    for i in range(filled_chars):
        pos_pct = (i + 1) / width * 100.0
        if pos_pct >= 85.0:
            c = style_crit
        elif pos_pct >= 65.0:
            c = style_high
        elif pos_pct >= 35.0:
            c = style_mid
        else:
            c = style_low
        t.append("■", style=f"bold {c}")
        
    t.append("░" * empty_chars, style=empty_style)
    return t


def generate_sparkline(data: List[float], width: int = 20, color: str = "#00ff55", style_color: str | None = None) -> Text:
    """Generates a single-line unicode sparkline [ ▂▃▅▆▇█]"""
    actual_color = style_color or color
    t = Text()
    if not data:
        return Text(" " * width)
    recent = data[-width:]
    if len(recent) < width:
        recent = [0.0] * (width - len(recent)) + recent
    
    for val in recent:
        idx = max(0, min(len(BLOCK_CHARS) - 1, int((val / 100.0) * (len(BLOCK_CHARS) - 1) + 0.5)))
        t.append(BLOCK_CHARS[idx], style=f"bold {actual_color}")
    return t


def generate_tactical_radar_art(
    step: int,
    threat_level: str = "SECURE",
    color_bright: str = "#00ff55",
    color_dim: str = "#14532d",
    color_alert: str = "#facc15",
    radar_color: str | None = None,
    blip_color: str | None = None,
) -> List[Text]:
    """Renders an animated 360° tactical circular sonar radar HUD matching Project I.G.I."""
    bright = radar_color or color_bright
    alert = blip_color or color_alert
    beam_frames = [
        ["      ▲ [N]      ", "    .---│---.    ", "   /    │    \\   ", "  |─────┼─────|  ", "   \\    │    /   ", "    '---│---'    ", "      ▼ [S]      "],
        ["     ▲ [N]       ", "    .---/---.    ", "   /   /     \\   ", "  |───┼───────|  ", "   \\ /       /   ", "    '---/---'    ", "      ▼ [S]      "],
        ["       [N]       ", "    .───────.    ", "   /         \\   ", "  |─────┼─────►  ", "   \\         /   ", "    '───────'    ", "       [S]       "],
        ["       [N]       ", "    .───\\───.    ", "   /     \\   \\   ", "  |───────┼───|  ", "   \\       \\ /   ", "    '───\\───'    ", "       [S]       "],
        ["      ▲ [N]      ", "    .---│---.    ", "   /    │    \\   ", "  |─────┼─────|  ", "   \\    │    /   ", "    '---│---'    ", "      ▼ [S]      "],
        ["       [N]       ", "    .───/───.    ", "   /   /     \\   ", "  |───┼───────|  ", "   \\ /       /   ", "    '───/───'    ", "       [S]       "],
        ["       [N]       ", "    .───────.    ", "   /         \\   ", "  ◄─────┼─────|  ", "   \\         /   ", "    '───────'    ", "       [S]       "],
        ["     ▲ [N]       ", "    .───\\───.    ", "   /     \\   \\   ", "  |───────┼───|  ", "   \\       \\ /   ", "    '───\\───'    ", "      ▼ [S]      "],
    ]
    frame_idx = step % len(beam_frames)
    frame = beam_frames[frame_idx]
    
    blip_char = "●" if (step % 2 == 0) else "◉"
    res: List[Text] = []
    
    for line_idx, line_str in enumerate(frame):
        t = Text()
        if line_idx == 2 and (frame_idx in (1, 2)):
            line_str = line_str[:6] + blip_char + line_str[7:]
        elif line_idx == 4 and (frame_idx in (4, 5)):
            line_str = line_str[:12] + blip_char + line_str[13:]
            
        for ch in line_str:
            if ch in ("●", "◉"):
                t.append(ch, style=f"bold {alert}")
            elif ch in ("│", "─", "┼", "/", "\\", "◄", "►", "▲", "▼"):
                t.append(ch, style=f"bold {bright}")
            elif ch in (".", "'", "(", ")"):
                t.append(ch, style=f"dim {color_dim}")
            else:
                t.append(ch, style=f"bold {bright}")
        res.append(t)
        
    return res
