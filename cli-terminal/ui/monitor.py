"""
Interactive Real-Time Btop Monitor & Radar for Buddy Agent & Project I.G.I.
Provides live full-screen dashboard with instant non-blocking keyboard navigation,
module toggling, theme switching, process sorting, process inspection, process termination,
and authentic Project I.G.I. tactical sonar radar HUD.
"""

import time
import sys
import os
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .theme import THEMES, DEFAULT_THEME
from .collector import SystemCollector
from .renderer import BtopRenderer


def flush_input():
    """Flushes any pending keypresses in the input stream."""
    if sys.platform == "win32":
        import msvcrt
        while msvcrt.kbhit():
            try:
                msvcrt.getwch()
            except Exception:
                pass
    else:
        import select
        try:
            while True:
                dr, _, _ = select.select([sys.stdin], [], [], 0.0)
                if dr:
                    sys.stdin.read(1)
                else:
                    break
        except Exception:
            pass


def get_key_non_blocking() -> Optional[str]:
    """Non-blocking key reader for Windows and POSIX."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            try:
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):  # Special extended keys (arrows, fn keys)
                    code = msvcrt.getwch()
                    if code in ('H', 'w'): return 'up'
                    if code in ('P', 'z'): return 'down'
                    if code == 'K': return 'left'
                    if code == 'M': return 'right'
                    if code == 'I': return 'pgup'
                    if code == 'Q': return 'pgdn'
                    if code == 'S': return 'delete'
                    return None
                return ch.lower()
            except Exception:
                return None
        return None
    else:
        import select
        try:
            dr, _, _ = select.select([sys.stdin], [], [], 0.0)
            if dr:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    dr2, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if dr2:
                        seq = sys.stdin.read(2)
                        if seq == '[A': return 'up'
                        if seq == '[B': return 'down'
                        if seq == '[C': return 'right'
                        if seq == '[D': return 'left'
                    return 'escape'
                return ch.lower()
        except Exception:
            pass
        return None


def run_btop_monitor(
    console: Optional[Console] = None,
    theme_name: str = "igi",
    initial_refresh_rate: float = 1.0,
    session_obj: Optional[Any] = None,
    max_loops: Optional[int] = None,
):
    """
    Runs the authentic full-screen interactive btop resource & tactical radar monitor.
    """
    if console is None:
        console = Console()

    flush_input()

    collector = SystemCollector()
    renderer = BtopRenderer(theme_name=theme_name)
    
    # Sync with session_obj settings if present
    if session_obj:
        if hasattr(session_obj, "theme") and session_obj.theme:
            renderer.set_theme(session_obj.theme)
        if hasattr(session_obj, "radar_interval"):
            initial_refresh_rate = session_obj.radar_interval

    themes_list = list(THEMES.keys())
    current_theme_idx = themes_list.index(renderer.theme_name) if renderer.theme_name in themes_list else 0
    
    sort_options = ["cpu", "mem", "rss", "pid", "name", "user"]
    current_sort_idx = 0
    
    refresh_rates = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
    current_refresh_idx = 2
    for idx, r in enumerate(refresh_rates):
        if abs(r - initial_refresh_rate) < 0.1:
            current_refresh_idx = idx
            break

    show_help_modal = False
    paused = False
    in_filter_mode = False
    filter_buffer = ""
    loop_count = 0
    modal_opened_time = 0.0
    
    last_metrics_update = 0.0
    cached_metrics = collector.update_metrics()
    cached_procs = collector.get_process_list(sort_by=renderer.sort_by, filter_text=renderer.filter_text, limit=10)

    if hasattr(console, "clear") and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        console.clear()

    # Agent telemetry live state
    model_name = "Groq Satellite (Llama 3.3 70B)"
    if session_obj and hasattr(session_obj, "model_key"):
        if session_obj.model_key == "bedrock":
            model_name = "AWS Bedrock (Claude 3.7 Sonnet)"
        elif session_obj.model_key == "ollama":
            model_name = "Ollama Localhost (Llama 3.1 8B)"

    agent_state = {
        "model_name": model_name,
        "speed": "⚡ 280 t/s",
        "latency": "135 ms",
        "status_msg": "Hey Champ! Pair programming ready. System running smooth as butter! 🐾",
    }

    is_screen = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True

    try:
        with Live(console=console, screen=is_screen, refresh_per_second=25) as live:
            while True:
                if max_loops is not None and loop_count >= max_loops:
                    break
                loop_count += 1
                now = time.time()
                current_refresh_rate = refresh_rates[current_refresh_idx]

                # Check keyboard inputs immediately
                key = get_key_non_blocking()
                if key:
                    if renderer.kill_confirm_proc is not None:
                        if now - modal_opened_time > 0.15:
                            if key in ('y', '\r', '\n'):
                                target_pid = renderer.kill_confirm_proc.get("pid")
                                assert target_pid is not None
                                ok, msg = collector.terminate_process(target_pid)
                                renderer.set_notification(f"TERMINATE: {msg}")
                                renderer.kill_confirm_proc = None
                                flush_input()
                                last_metrics_update = 0
                            elif key in ('n', 'q', '\x1b', 'escape'):
                                renderer.kill_confirm_proc = None
                                flush_input()
                        continue

                    if renderer.inspecting_proc is not None:
                        if now - modal_opened_time > 0.15:
                            if key in ('\r', '\n', ' ', 'q', '\x1b', 'escape', 'i'):
                                renderer.inspecting_proc = None
                                flush_input()
                        continue

                    if show_help_modal:
                        if now - modal_opened_time > 0.15:
                            if key in ('h', 'q', '\x1b', 'escape', ' ', '\r', '\n'):
                                show_help_modal = False
                                flush_input()
                        continue

                    if in_filter_mode:
                        if key in ('\r', '\n'):
                            renderer.filter_text = filter_buffer
                            in_filter_mode = False
                            renderer.selected_proc_idx = 0
                            flush_input()
                            last_metrics_update = 0
                        elif key in ('\x1b', 'escape'):
                            in_filter_mode = False
                            filter_buffer = ""
                            flush_input()
                        elif key == '\x08':
                            filter_buffer = filter_buffer[:-1]
                        elif len(key) == 1 and key.isprintable():
                            filter_buffer += key
                        continue

                    if key in ('q', '\x1b', 'escape'):
                        flush_input()
                        break

                    elif key == '1':
                        renderer.show_cpu = not renderer.show_cpu
                        renderer.set_notification(f"CPU Box: {'ENABLED' if renderer.show_cpu else 'HIDDEN'}")

                    elif key == '2':
                        renderer.show_mem = not renderer.show_mem
                        renderer.set_notification(f"MEM/Disk Box: {'ENABLED' if renderer.show_mem else 'HIDDEN'}")

                    elif key == '3':
                        renderer.show_net = not renderer.show_net
                        renderer.set_notification(f"Network Box: {'ENABLED' if renderer.show_net else 'HIDDEN'}")

                    elif key == '4':
                        renderer.show_proc = not renderer.show_proc
                        renderer.set_notification(f"Process Box: {'ENABLED' if renderer.show_proc else 'HIDDEN'}")

                    elif key == '5':
                        renderer.show_buddy = not renderer.show_buddy
                        renderer.set_notification(f"AI Box: {'ENABLED' if renderer.show_buddy else 'HIDDEN'}")

                    elif key in ('6', 'r'):
                        renderer.show_radar = not renderer.show_radar
                        renderer.set_notification(f"Radar Box: {'ENABLED' if renderer.show_radar else 'HIDDEN'}")

                    elif key == 't':
                        current_theme_idx = (current_theme_idx + 1) % len(themes_list)
                        chosen_theme = themes_list[current_theme_idx]
                        renderer.set_theme(chosen_theme)
                        if session_obj:
                            session_obj.theme = chosen_theme
                        renderer.set_notification(f"🎨 HUD Theme: {chosen_theme.upper()}")

                    elif key == 'h':
                        show_help_modal = True
                        modal_opened_time = now
                        flush_input()

                    elif key in ('k', 'd', 'delete'):
                        if cached_procs and 0 <= renderer.selected_proc_idx < len(cached_procs):
                            renderer.kill_confirm_proc = cached_procs[renderer.selected_proc_idx]
                            modal_opened_time = now
                            flush_input()

                    elif key in ('i', '\r', '\n'):
                        if cached_procs and 0 <= renderer.selected_proc_idx < len(cached_procs):
                            sel_p = cached_procs[renderer.selected_proc_idx]
                            details = collector.get_process_details(sel_p["pid"])
                            renderer.inspecting_proc = details or sel_p
                            modal_opened_time = now
                            flush_input()

                    elif key == 's':
                        current_sort_idx = (current_sort_idx + 1) % len(sort_options)
                        renderer.sort_by = sort_options[current_sort_idx]
                        renderer.selected_proc_idx = 0
                        renderer.set_notification(f"Sort Processes by: {renderer.sort_by.upper()}")
                        last_metrics_update = 0

                    elif key in ('up', 'w'):
                        renderer.selected_proc_idx = max(0, renderer.selected_proc_idx - 1)

                    elif key in ('down', 'j'):
                        renderer.selected_proc_idx = min(len(cached_procs) - 1, renderer.selected_proc_idx + 1)

                    elif key in ('pgup',):
                        renderer.selected_proc_idx = max(0, renderer.selected_proc_idx - 5)

                    elif key in ('pgdn',):
                        renderer.selected_proc_idx = min(len(cached_procs) - 1, renderer.selected_proc_idx + 5)

                    elif key in ('f', '/'):
                        in_filter_mode = True
                        filter_buffer = renderer.filter_text
                        flush_input()

                    elif key == 'c':
                        renderer.filter_text = ""
                        renderer.selected_proc_idx = 0
                        renderer.set_notification("Process Filter Cleared")
                        last_metrics_update = 0

                    elif key in ('+', '='):
                        current_refresh_idx = max(0, current_refresh_idx - 1)
                        new_r = refresh_rates[current_refresh_idx]
                        if session_obj:
                            session_obj.radar_interval = new_r
                        renderer.set_notification(f"Radar Frequency: {new_r:.2f}s")

                    elif key in ('-', '_'):
                        current_refresh_idx = min(len(refresh_rates) - 1, current_refresh_idx + 1)
                        new_r = refresh_rates[current_refresh_idx]
                        if session_obj:
                            session_obj.radar_interval = new_r
                        renderer.set_notification(f"Radar Frequency: {new_r:.2f}s")

                    elif key == ' ':
                        paused = not paused
                        renderer.set_notification("STREAM PAUSED" if paused else "STREAM RESUMED")

                # Update system metrics if interval elapsed
                if not paused and (now - last_metrics_update >= current_refresh_rate):
                    cached_metrics = collector.update_metrics()
                    cached_procs = collector.get_process_list(sort_by=renderer.sort_by, filter_text=renderer.filter_text, limit=10)
                    last_metrics_update = now

                # Render active state
                if renderer.kill_confirm_proc is not None:
                    live.update(renderer.render_kill_confirm_modal(renderer.kill_confirm_proc))
                elif renderer.inspecting_proc is not None:
                    live.update(renderer.render_process_inspect_modal(renderer.inspecting_proc))
                elif show_help_modal:
                    t = renderer.theme
                    help_content = Table.grid(padding=(0, 2), expand=True)
                    help_content.add_column(style=f"bold {t.get('highlight', '#00ff55')}", width=18)
                    help_content.add_column(style=f"bold {t.get('text', '#f0fdf4')}")
                    
                    help_content.add_row("1 - 6", "Toggle CPU, MEM, NET, PROC, AI, RADAR modules")
                    help_content.add_row("▲ / ▼ (or w/j)", "Navigate interactive process table selection")
                    help_content.add_row("PgUp / PgDn", "Jump 5 processes up or down")
                    help_content.add_row("s", "Cycle Process Sort (CPU%, MEM%, RSS MB, PID, Name, User)")
                    help_content.add_row("f or /", "Filter / Search running processes by keyword")
                    help_content.add_row("c", "Clear active process filter")
                    help_content.add_row("i or Enter", "Inspect detailed process memory, threads & commandline")
                    help_content.add_row("k / d / Delete", "Terminate / Kill selected process (with confirmation)")
                    help_content.add_row("t", "Switch Themes (I.G.I. Green, Matrix, Tokyo Night, Dracula, etc.)")
                    help_content.add_row("+ / -", "Increase / decrease telemetry radar scanning speed")
                    help_content.add_row("Space", "Pause / Freeze live telemetry streams")
                    help_content.add_row("h", "Close this Mission Briefing help overlay")
                    help_content.add_row("q / Esc", "Return to Project I.G.I. Main Menu HUD")
                    
                    modal_panel = Panel(
                        help_content,
                        title=f"[bold {t.get('title', '#22c55e')}] 📖 Tactical Telemetry & Radar Operations Manual [/]",
                        border_style=t.get('highlight', '#00ff55'),
                        padding=(1, 2),
                    )
                    live.update(modal_panel)
                elif in_filter_mode:
                    t = renderer.theme
                    filter_box = Panel(
                        Text(f"Filter Keyword: {filter_buffer}█", style=f"bold {t.get('highlight', '#00ff55')}"),
                        title=f"[bold {t.get('highlight', '#00ff55')}] 🔍 Search Processes (Enter to apply, Esc to cancel) [/]",
                        border_style=t.get('highlight', '#00ff55'),
                        padding=(1, 2),
                    )
                    dash = renderer.render_dashboard(
                        cached_metrics,
                        cached_procs,
                        agent_state=agent_state,
                        collector_obj=collector,
                        refresh_rate=current_refresh_rate,
                    )
                    live.update(Group(dash, filter_box))
                else:
                    dash = renderer.render_dashboard(
                        cached_metrics,
                        cached_procs,
                        agent_state=agent_state,
                        collector_obj=collector,
                        refresh_rate=current_refresh_rate,
                    )
                    live.update(dash)

                time.sleep(0.04)

    except KeyboardInterrupt:
        pass
    finally:
        flush_input()
