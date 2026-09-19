"""
ASCII Art, 3D Typography, and Mascot definitions for Buddy Agent UI
"""

from typing import List
from rich.text import Text
from .config import (
    IGI_GREEN_BRIGHT, IGI_GREEN_DIM, IGI_METALLIC, IGI_WHITE,
    COLOR_PEACH
)
from .theme import get_theme


def render_igi_header(version="V1.2.0", theme_name: str = "igi") -> Text:
    """Renders the iconic Project I.G.I. 3D extruded military HUD header cleanly centered."""
    t_colors = get_theme(theme_name)
    color_bright = t_colors.get("highlight", IGI_GREEN_BRIGHT)
    color_dim = t_colors.get("box_border", IGI_GREEN_DIM)
    color_white = t_colors.get("text", IGI_WHITE)
    color_steel = t_colors.get("dim_text", IGI_METALLIC)

    t = Text(justify="center")
    # P R O J E C T
    t.append("P   R   O   J   E   C   T\n", style=f"bold {color_steel}")
    
    # 3D Steel / Night-Vision Letters: B U D D Y . A G E N T
    logo_lines = [
        ("█▀▀▄ █░░█ █▀▀▄ █▀▀▄ █░░█ ▄  █▀▀█ █▀▀▀ █▀▀▀ █▄░░█ ▀▀█▀▀", f"bold {color_white}"),
        ("█▀▀▄ █░░█ █░░█ █░░█ █▄▄█ ▄  █▄▄█ █░▀█ █▀▀▀ █░█░█ ░░█░░", f"bold {color_bright}"),
        ("▀▀▀░ ░▀▀▀ ▀▀▀░ ▀▀▀░ ▄▄▄█ ░  ▀░░▀ ▀▀▀▀ ▀▀▀▀ ▀░░▀▀ ░░▀░░", f"bold {color_dim}"),
    ]
    for row_text, color in logo_lines:
        t.append(row_text + "\n", style=color)
    t.append(f"{version}\n", style=f"dim {color_steel}")
    return t


WORD_SILHOUETTE_MASK = [
    "00000000000000000000000000000000000000000000000000000000000000000000",
    "00000111111110000110000001100111111100000111111100000110000001100000",
    "00000110000001100110000001100110000011000110000011000110000001100000",
    "00000111111110000110000001100110000001100110000001100011000011000000",
    "00000110000001100110000001100110000001100110000001100001111110000000",
    "00000110000001100110000001100110000011000110000011000000011000000000",
    "00000111111110000011111111000111111100000111111100000000011000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000",
    "00000001111110000011111111000111111111100110000001100111111111100000",
    "00000011000000110110000000000110000000000111000000110000011000000000",
    "00000110000000110110001111100111111110000110110000110000011000000000",
    "00000111111111110110000000110110000000000110011000110000011000000000",
    "00000110000000110110000000110110000000000110001100110000011000000000",
    "00000110000000110011111111000111111111100110000011100000011000000000",
    "00000000000000000000000000000000000000000000000000000000000000000000",
]

FULL_WORDINGS_CORPUS = (
    "We are Buddy Agent • Autonomous AI Pair Programmer • Benjamin & Developer Companion • "
    "Code with Passion • Ship with Speed • We do not fear bugs • We debug relentlessly • "
    "Clean code, elegant architecture • Groq Cloud ultra-fast inference, AWS Bedrock, Ollama Local • "
    "High performance terminal companion • Pair programming reimagined with empathy, speed, and intelligence • "
    "Always by your side • We are Buddy Agent • Expect excellence • "
)


def render_word_sculpted_title(mask_rows: List[str] = WORD_SILHOUETTE_MASK, phrase: str = FULL_WORDINGS_CORPUS) -> Text:
    """Renders BUDDY AGENT carved out of a continuous stream of repeated full wordings."""
    res = Text()
    char_counter = 0
    clean_phrase = phrase.strip()
    for r in mask_rows:
        for ch in r:
            word_ch = clean_phrase[char_counter % len(clean_phrase)]
            char_counter += 1
            if ch == "1":
                res.append(word_ch, style="bold #4ade80")
            else:
                res.append(word_ch, style="dim #334155")
        res.append("\n")
    return res
