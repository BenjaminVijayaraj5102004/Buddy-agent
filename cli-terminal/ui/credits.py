"""
Movie End Credits & Black Aesthetic Portrait Engine for Buddy Agent
Authentic Borderless Cinema Movie Credits (Dune / Hollywood style) featuring:
- Black Aesthetic Portrait Rendering of Benjamin V
- Creator Profile: BENJAMIN V (AI Engineer | Backend Engineer)
- Summary, Technical Skills Matrix, Education, Certifications & Hackathons
- Featured GitHub Repositories (Web Design Agent, Software Agent, Engineering SDK, Open Contributions)
- System Architecture & Framework Credits
- Pure Cinema Scroll: Borderless, Full-Screen, Fluid Timing with Pause and Navigation
"""

import os
import sys
import time
from typing import List, Optional
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.align import Align

# Ensure UTF-8 output encoding for terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Black Aesthetic Palette (Monochrome / Titanium / Obsidian)
AESTHETIC_WHITE = "#ffffff"
AESTHETIC_SILVER = "#e4e4e7"
AESTHETIC_PLATINUM = "#d4d4d8"
AESTHETIC_GRAY_LIGHT = "#a1a1aa"
AESTHETIC_GRAY_MID = "#71717a"
AESTHETIC_GRAY_DARK = "#3f3f46"
AESTHETIC_OBSIDIAN = "#27272a"
AESTHETIC_ONYX = "#18181b"
AESTHETIC_EMERALD_GLOW = "#00ff66"
AESTHETIC_CYAN_DIM = "#38bdf8"


def get_benjamin_black_aesthetic_portrait(width: int = 42) -> List[Text]:
    """
    Renders Benjamin's photo as high-contrast Black Aesthetic character art.
    Uses multi-stage contrast stretching and platinum/obsidian shaded ramps.
    """
    asset_path = os.path.join(os.path.dirname(__file__), "assets", "benjamin.jpg")
    if not os.path.exists(asset_path):
        asset_path = os.path.join(
            os.path.expanduser("~"), ".gemini", "antigravity-ide", "brain",
            "72efcbfb-00eb-4129-8686-64e9af4bfc79", ".user_uploaded", "media_1789758888823.jpg"
        )

    if os.path.exists(asset_path):
        try:
            from PIL import Image, ImageEnhance
            img = Image.open(asset_path).convert("L")
            img = ImageEnhance.Contrast(img).enhance(2.2)
            img = ImageEnhance.Sharpness(img).enhance(2.0)

            aspect = (img.height / img.width) * 0.52
            height = int(width * aspect)
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)

            ASCII_RAMP = "   ..::--==++**##%%@@@@"
            portrait_lines: List[Text] = []

            for y in range(height):
                t = Text(justify="center")
                for x in range(width):
                    pixel = img_resized.getpixel((x, y))
                    if isinstance(pixel, (tuple, list)) and len(pixel) > 0:
                        val = pixel[0] if pixel[0] is not None else 0
                    elif isinstance(pixel, int):
                        val = pixel
                    elif isinstance(pixel, float):
                        val = int(pixel)
                    else:
                        val = 0
                    char_idx = int((val / 255) * (len(ASCII_RAMP) - 1))
                    char_idx = max(0, min(char_idx, len(ASCII_RAMP) - 1))
                    char = ASCII_RAMP[char_idx]

                    # High-contrast black aesthetic metallic gradient
                    if val > 210:
                        style = f"bold {AESTHETIC_WHITE}"
                    elif val > 165:
                        style = f"bold {AESTHETIC_SILVER}"
                    elif val > 125:
                        style = AESTHETIC_PLATINUM
                    elif val > 85:
                        style = AESTHETIC_GRAY_LIGHT
                    elif val > 50:
                        style = AESTHETIC_GRAY_MID
                    elif val > 25:
                        style = AESTHETIC_GRAY_DARK
                    else:
                        style = AESTHETIC_OBSIDIAN
                    t.append(char, style=style)
                portrait_lines.append(t)

            return portrait_lines
        except Exception:
            pass

    # Stylized fallback if Pillow is unavailable
    fallback = [
        Text("┌──────────────────────────────────┐", style=f"dim {AESTHETIC_GRAY_MID}", justify="center"),
        Text("│        [ BENJAMIN  V ]           │", style=f"bold {AESTHETIC_WHITE}", justify="center"),
        Text("│    AI & Backend Systems Eng.     │", style=f"bold {AESTHETIC_SILVER}", justify="center"),
        Text("│     ⚡ VIT-AP • B.Tech '27       │", style=f"dim {AESTHETIC_GRAY_LIGHT}", justify="center"),
        Text("└──────────────────────────────────┘", style=f"dim {AESTHETIC_GRAY_MID}", justify="center"),
    ]
    return fallback


def build_credits_corpus() -> List[Text]:
    """Assembles the complete cinematic movie end credits stream."""
    lines: List[Text] = []

    def blank(n: int = 1):
        for _ in range(n):
            lines.append(Text(""))

    def centered(text: str, style: str):
        lines.append(Text(text, style=style, justify="center"))

    def role_pair(role: str, person: str, role_width: int = 32, val_width: int = 46):
        t = Text(justify="center")
        t.append(role.rjust(role_width) + "   ", style=f"dim {AESTHETIC_GRAY_LIGHT}")
        t.append(person.ljust(val_width), style=f"bold {AESTHETIC_WHITE}")
        lines.append(t)

    def section_header(title: str):
        blank(2)
        centered(title.upper(), style=f"bold {AESTHETIC_SILVER}")
        blank(1)

    blank(3)
    centered("B U D D Y   A G E N T", f"bold {AESTHETIC_WHITE}")
    centered("A U T O N O M O U S   A I   S Y S T E M S", f"dim {AESTHETIC_GRAY_LIGHT}")
    blank(1)
    centered("OFFICIAL PROJECT CREDITS", f"dim {AESTHETIC_GRAY_MID}")
    blank(3)

    # 2. Creator Card & Black Aesthetic Photo Portrait
    section_header("CREATOR & LEAD ARCHITECT")
    centered("B E N J A M I N   V", f"bold {AESTHETIC_WHITE}")
    centered("AI Engineer  •  Backend Engineer  •  Systems Architect", f"bold {AESTHETIC_SILVER}")
    blank(1)
    centered("Email: benjaminvijayaraj5102004@gmail.com   │   Mobile: +91 8637630867", f"dim {AESTHETIC_GRAY_LIGHT}")
    centered("GitHub: github.com/BenjaminVijayaraj5102004", f"bold {AESTHETIC_CYAN_DIM}")
    blank(2)

    # Embed Black Aesthetic Photo Portrait directly in the scroll
    portrait_lines = get_benjamin_black_aesthetic_portrait(width=42)
    for p_line in portrait_lines:
        lines.append(p_line)
    blank(2)

    # 3. Professional Summary
    section_header("EXECUTIVE SUMMARY")
    centered("AI and Backend Engineer (B.Tech, 2027) building production-grade agentic AI systems and asynchronous backends.", f"dim {AESTHETIC_SILVER}")
    centered("Specializes in LangGraph multi-agent architectures, Model Context Protocol (MCP) integrations, custom RAG pipelines,", f"dim {AESTHETIC_SILVER}")
    centered("and high-performance FastAPI microservices. Experienced in containerized local model inference, automated CI/CD,", f"dim {AESTHETIC_SILVER}")
    centered("and secure stateful persistence across cloud and air-gapped environments.", f"dim {AESTHETIC_SILVER}")
    blank(2)

    # 4. Technical Skills Matrix (Dune Left Role / Right Name format)
    section_header("TECHNICAL SKILLS")
    role_pair("AI & Agentic Systems", "LangGraph • LangChain • MCP • Deep-Agents • RAG • Prompt Eng.")
    role_pair("Observability & Tracing", "LangSmith • OpenTelemetry • Execution Logging")
    role_pair("Languages & Frameworks", "Python • SQL • FastAPI • Pydantic • SQLAlchemy 2.0 • Alembic")
    role_pair("Databases & Security", "PostgreSQL • OAuth2 • JWT • Argon2 • Stateful Storage")
    role_pair("CS Fundamentals & Patterns", "Object-Oriented Design • Factory & Singleton • Algorithms • DBMS")
    role_pair("DevOps & Tooling", "Docker (Multi-stage) • Docker Compose • GitHub Actions • Linux • UV")
    role_pair("Testing & Quality", "Pytest • Unit & Integration Testing • Test Automation")
    blank(2)

    # 5. Education
    section_header("EDUCATION")
    role_pair("Degree Program", "B.Tech — Electronics and Communication Engineering")
    role_pair("Academic Timeline", "2023 – 2027")
    role_pair("Institution", "Vellore Institute of Technology (VIT-AP)")
    blank(2)

    # 6. Certifications & Hackathon Honors
    section_header("CERTIFICATIONS & HACKATHON HONORS")
    role_pair("NVIDIA Deep Learning", "Building LLM Applications with Prompt Engineering")
    role_pair("IBM Cognitive Class", "Artificial Intelligence Fundamentals")
    role_pair("MSME Hackathon 2024", "Smart Mirror IoT System with Real-Time Health Dashboard (Honored)")
    role_pair("ChatBot Hackathon 2025", "LangChain + RAG First-Aid Guidance Assistant with Auto-Scheduling")
    blank(2)

    # 7. Featured GitHub Repositories
    section_header("FEATURED GITHUB PROJECTS")
    role_pair("Web Design Agent", "github.com/BenjaminVijayaraj5102004/web-design-agent")
    role_pair("Software Agent", "github.com/BenjaminVijayaraj5102004/software-agent")
    role_pair("Engineering SDK", "github.com/BenjaminVijayaraj5102004/engineering-sdk")
    role_pair("Open Contributed Repositories", "Agentic AI, MCP Tooling & Open-Source Cloud Ecosystem")
    blank(2)

    # 8. Buddy Agent System Credits
    section_header("BUDDY AGENT SYSTEM CREDITS")
    role_pair("Lead System Architect", "BENJAMIN V")
    role_pair("Agent Orchestration Framework", "Strands Agents SDK (Python 3.14)")
    role_pair("Sub-Agent Delegation Layer", "API Manager • SAM CLI Deploy Agent • GitHub Agent")
    role_pair("Model Context Protocol (MCP)", "GitHub MCP Client • SAM CLI MCP • Text Editor MCP")
    role_pair("Tactical Interface Engine", "Project I.G.I. Tactical HUD • Black Aesthetic Character Matrix")
    role_pair("Telemetry & Sonar Radar", "Btop++ Real-Time Hardware & CPU Braille Monitor")
    role_pair("Interactive REPL & Hotkeys", "Prompt-Toolkit 3.0 • Rich Interactive TUI Engine")
    role_pair("Session & Memory Architecture", "Resilient Session Manager • Multi-Tier Conversation Archive")
    blank(2)

    # 9. Satellite AI Providers
    section_header("SATELLITE AI INFERENCE ENGINES")
    role_pair("Groq Cloud Engine", "Llama 3.3 70B Versatile (Ultra-Fast Inference)")
    role_pair("Local Host Air-Gapped", "Ollama Local Engine (Llama 3.1 8B)")
    role_pair("AWS Cloud Engine", "Amazon Bedrock (Claude 3.7 Sonnet)")
    blank(2)

    # 10. Acknowledgements & Special Thanks
    section_header("SPECIAL THANKS & ACKNOWLEDGEMENTS")
    role_pair("Academic Institution", "Vellore Institute of Technology, AP")
    role_pair("Open-Source AI Community", "Anthropic • Meta AI • AWS Cloud • Groq • Strands SDK")
    role_pair("Tribute & Inspiration", "Project I.G.I. (Innerloop Studios) • Btop++ (Aristocratos)")
    role_pair("Dedication", "To the Future of Autonomous Multi-Agent Systems")
    blank(3)

    # 11. Final End Card
    centered("✦  COPYRIGHT © 2026 BENJAMIN V  ✦", f"bold {AESTHETIC_WHITE}")
    centered("ALL RIGHTS RESERVED • OPEN-SOURCE INNOVATION", f"dim {AESTHETIC_GRAY_LIGHT}")
    blank(4)

    return lines


def run_credits_movie_scroll(console: Optional[Console] = None) -> None:
    """
    Runs an authentic, borderless cinematic scrolling movie end-credits presentation.
    Clean black background with cinema typography and zero bounding boxes.
    """
    if console is None:
        console = Console()

    corpus = build_credits_corpus()

    # Non-blocking keypress helper
    def get_key():
        if sys.platform == "win32":
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    code = msvcrt.getwch()
                    if code == 'H': return 'up'
                    if code == 'P': return 'down'
                return ch.lower()
        return None

    term_height = console.height or 32
    view_height = max(18, term_height - 3)
    
    total_lines = len(corpus)
    scroll_pos = 0.0
    scroll_speed = 0.5  # lines per tick
    is_paused = False

    console.clear()

    # Render directly to screen in Live mode without ANY panel or box borders
    with Live(console=console, screen=True, auto_refresh=False) as live:
        while True:
            k = get_key()
            if k in ('q', '\x1b'):
                break
            elif k == ' ':
                is_paused = not is_paused
            elif k in ('+', '='):
                scroll_speed = min(2.5, scroll_speed + 0.2)
            elif k in ('-', '_'):
                scroll_speed = max(0.2, scroll_speed - 0.2)
            elif k == 'up':
                scroll_pos = max(0.0, scroll_pos - 3)
            elif k == 'down':
                scroll_pos = min(float(total_lines - view_height), scroll_pos + 3)

            # Advance scrolling position
            if not is_paused:
                scroll_pos += scroll_speed
                if scroll_pos >= total_lines:
                    scroll_pos = 0.0  # Loop back to top

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

            # Minimal, discrete bottom footer with zero box borders
            status_text = "PAUSED" if is_paused else f"{scroll_speed:.1f}x"
            hud_footer = Text(
                f"   [Space] {status_text}   •   [+/-] Speed   •   [▲/▼] Scroll   •   [q] Return",
                style=f"dim {AESTHETIC_GRAY_DARK}",
                justify="center"
            )
            grid.add_row(hud_footer)

            live.update(grid, refresh=True)
            time.sleep(0.06)


def show_credits_dialog(console: Optional[Console] = None) -> None:
    """Entrypoint to launch the full interactive credits screen."""
    run_credits_movie_scroll(console)
