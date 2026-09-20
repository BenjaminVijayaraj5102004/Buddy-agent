"""
Btop UI Renderer for Buddy Agent & Project I.G.I.
Renders high-fidelity game-inspired terminal boxes, braille graphs,
per-core meters, disk IO, network sparklines, process table, and Tactical Radar HUD.
"""

import time
import sys
import os
from typing import Dict, Any, List, Optional


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from typing import Dict, Any, List, Optional
from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align

from .theme import get_theme
from .graphs import generate_braille_graph, generate_meter, generate_sparkline, generate_tactical_radar_art
from .collector import format_bytes


class BtopRenderer:
    def __init__(self, theme_name: str = "igi"):
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)
        self.show_cpu = True
        self.show_mem = True
        self.show_net = True
        self.show_proc = True
        self.show_buddy = True
        self.show_radar = True
        self.sort_by = "cpu"
        self.selected_proc_idx = 0
        self.filter_text = ""
        self.step = 0
        self.inspecting_proc: Optional[Dict[str, Any]] = None
        self.kill_confirm_proc: Optional[Dict[str, Any]] = None
        self.status_notification: str = ""
        self.status_notification_time: float = 0.0

    def set_theme(self, theme_name: str):
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)

    def set_notification(self, msg: str):
        self.status_notification = msg
        self.status_notification_time = time.time()

    def render_header(self, metrics: Dict[str, Any], refresh_rate: float = 1.0) -> Text:
        t = self.theme
        hdr = Text()
        
        keys = [
            ("1", "cpu", self.show_cpu),
            ("2", "mem", self.show_mem),
            ("3", "net", self.show_net),
            ("4", "proc", self.show_proc),
            ("5", "ai", self.show_buddy),
            ("6", "radar", self.show_radar),
            ("t", "theme", True),
            ("s", "sort", True),
            ("f", "filter", True),
            ("r", f"{refresh_rate}s", True),
            ("h", "help", True),
            ("q", "quit", True),
        ]
        
        for k, name, active in keys:
            if active:
                hdr.append(f"[{k}:", style=f"bold {t.get('dim_text', '#15803d')}")
                hdr.append(name, style=f"bold {t.get('highlight', '#00ff55')}")
                hdr.append("] ", style=f"bold {t.get('dim_text', '#15803d')}")
            else:
                hdr.append(f"[{k}:{name}] ", style=f"dim {t.get('dim_text', '#15803d')}")
                
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        hdr.append("│ ", style=f"dim {border_col}")
        hdr.append("⚡ BUDDY // BTOP++ TELEMETRY", style=f"bold {t.get('title', '#22c55e')}")
        hdr.append(" │ ", style=f"dim {border_col}")
        
        threat = metrics.get("threat_level", "SECURE")
        threat_col = t.get('meter_low', '#22c55e') if threat == "SECURE" else (t.get('meter_high', '#facc15') if threat == "ELEVATED" else t.get('meter_crit', '#ef4444'))
        hdr.append(f"DEFCON: {threat} ", style=f"bold {threat_col}")
        
        uptime = metrics.get("uptime_str", "0h 0m")
        hdr.append(f"• UPTIME: {uptime} ", style=f"dim {t.get('text', '#f0fdf4')}")
        
        batt = metrics.get("battery_pct")
        if batt is not None:
            charging = "⚡" if metrics.get("battery_charging") else "🔋"
            hdr.append(f"• {charging}{int(batt)}% ", style=f"bold {t.get('highlight', '#00ff55')}")
            
        return hdr

    def render_cpu_box(self, metrics: Dict[str, Any]) -> Panel:
        t = self.theme
        cpu_total = metrics.get("cpu_total", 0.0)
        per_core = metrics.get("per_core", [])
        cpu_history = metrics.get("cpu_history", [])
        freq = metrics.get("cpu_freq_ghz", 2.8)
        
        box_col = t.get('cpu_box', t.get('box', '#00ff55'))
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column(ratio=6)
        grid.add_column(ratio=4)
        
        left = Table.grid(padding=(0, 0), expand=True)
        left.add_column()
        
        sum_line = Text()
        sum_line.append("CPU Total: ", style=f"bold {t.get('text', '#f0fdf4')}")
        sum_line.append(f"{cpu_total:5.1f}% ", style=f"bold {box_col}")
        sum_line.append(f"[{freq:.2f} GHz] ", style=f"dim {t.get('dim_text', '#15803d')}")
        meter = generate_meter(cpu_total, width=16, style_low=t.get("meter_low", "#22c55e"), style_mid=t.get("meter_mid", "#84cc16"), style_high=t.get("meter_high", "#facc15"), style_crit=t.get("meter_crit", "#ef4444"), empty_style=f"dim {border_col}")
        sum_line.append_text(meter)
        left.add_row(sum_line)
        left.add_row(Text("─" * 48, style=f"dim {border_col}"))
        
        graph_lines = generate_braille_graph(cpu_history, width=48, height=4, color_low=t.get("meter_low", "#22c55e"), color_mid=t.get("meter_mid", "#84cc16"), color_high=t.get("meter_high", "#facc15"), color_crit=t.get("meter_crit", "#ef4444"))
        for gl in graph_lines:
            left.add_row(gl)
            
        right = Table.grid(padding=(0, 1), expand=True)
        right.add_column()
        right.add_column(justify="right")
        
        for idx, core_val in enumerate(per_core[:8]):
            c_label = Text(f"Core {idx}: ", style=f"dim {t.get('text', '#f0fdf4')}")
            c_val_str = f"{core_val:4.1f}% "
            c_meter = generate_meter(core_val, width=10, style_low=t.get("meter_low", "#22c55e"), style_mid=t.get("meter_mid", "#84cc16"), style_high=t.get("meter_high", "#facc15"), style_crit=t.get("meter_crit", "#ef4444"), empty_style=f"dim {border_col}")
            c_bar = Text(c_val_str, style=f"bold {box_col}")
            c_bar.append_text(c_meter)
            right.add_row(c_label, c_bar)
            
        grid.add_row(left, right)
        
        return Panel(
            grid,
            title=f"[bold {box_col}] CPU // Hardware Telemetry [/]",
            title_align="left",
            border_style=box_col,
            padding=(0, 1),
        )

    def render_mem_disk_box(self, metrics: Dict[str, Any]) -> Panel:
        t = self.theme
        mem_used = metrics.get("mem_used", 0)
        mem_total = metrics.get("mem_total", 1)
        mem_free = metrics.get("mem_free", 0)
        mem_cached = metrics.get("mem_cached", 0)
        mem_pct = metrics.get("mem_percent", 0.0)
        
        swap_used = metrics.get("swap_used", 0)
        swap_total = metrics.get("swap_total", 1)
        swap_pct = metrics.get("swap_percent", 0.0)
        
        box_col = t.get('mem_box', t.get('title', '#22c55e'))
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        rx_col = t.get('graph_net_rx', '#38bdf8')
        tx_col = t.get('graph_net_tx', '#a855f7')
        
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column()
        
        ram_line = Text()
        ram_line.append("RAM:  ", style=f"bold {box_col}")
        ram_line.append(f"{format_bytes(mem_used)} / {format_bytes(mem_total)} ({mem_pct:4.1f}%) ", style=f"bold {t.get('text', '#f0fdf4')}")
        ram_meter = generate_meter(mem_pct, width=14, style_low=t.get("meter_low", "#22c55e"), style_mid=t.get("meter_mid", "#84cc16"), style_high=t.get("meter_high", "#facc15"), style_crit=t.get("meter_crit", "#ef4444"), empty_style=f"dim {border_col}")
        ram_line.append_text(ram_meter)
        grid.add_row(ram_line)
        
        ram_sub = Text()
        ram_sub.append(f"Free: {format_bytes(mem_free)}  Cached: {format_bytes(mem_cached)}", style=f"dim {t.get('dim_text', '#15803d')}")
        grid.add_row(ram_sub)
        
        if swap_total > 0:
            swap_line = Text()
            swap_line.append("SWAP: ", style=f"bold {t.get('dim_text', '#15803d')}")
            swap_line.append(f"{format_bytes(swap_used)} / {format_bytes(swap_total)} ({swap_pct:4.1f}%) ", style=f"dim {t.get('text', '#f0fdf4')}")
            swap_meter = generate_meter(swap_pct, width=14, style_low=t.get("meter_low", "#22c55e"), style_mid=t.get("meter_mid", "#84cc16"), style_high=t.get("meter_high", "#facc15"), style_crit=t.get("meter_crit", "#ef4444"), empty_style=f"dim {border_col}")
            swap_line.append_text(swap_meter)
            grid.add_row(swap_line)
            
        grid.add_row(Text("─" * 40, style=f"dim {border_col}"))
        
        disks = metrics.get("disks", [])
        for d in disks[:2]:
            d_line = Text()
            d_line.append(f"Disk ({d['mount']}): ", style=f"bold {t.get('text', '#f0fdf4')}")
            d_line.append(f"{format_bytes(d['used'])} / {format_bytes(d['total'])} ", style=f"dim {t.get('text', '#f0fdf4')}")
            d_meter = generate_meter(d['percent'], width=10, style_low=t.get("meter_low", "#22c55e"), style_mid=t.get("meter_mid", "#84cc16"), style_high=t.get("meter_high", "#facc15"), style_crit=t.get("meter_crit", "#ef4444"), empty_style=f"dim {border_col}")
            d_line.append_text(d_meter)
            grid.add_row(d_line)
            
        dio_line = Text()
        dio_line.append(f"IO R: {format_bytes(metrics.get('disk_read_speed', 0.0))}/s  ", style=f"bold {rx_col}")
        dio_line.append(f"IO W: {format_bytes(metrics.get('disk_write_speed', 0.0))}/s", style=f"bold {tx_col}")
        grid.add_row(dio_line)
        
        return Panel(
            grid,
            title=f"[bold {box_col}] MEM & DISK [/]",
            title_align="left",
            border_style=box_col,
            padding=(0, 1),
        )

    def render_net_box(self, metrics: Dict[str, Any]) -> Panel:
        t = self.theme
        rx_speed = metrics.get("rx_speed", 0.0)
        tx_speed = metrics.get("tx_speed", 0.0)
        net_rx_total = metrics.get("net_rx_total", 0)
        net_tx_total = metrics.get("net_tx_total", 0)
        rx_hist = metrics.get("net_rx_history", [])
        tx_hist = metrics.get("net_tx_history", [])
        
        rx_col = t.get('graph_net_rx', '#38bdf8')
        tx_col = t.get('graph_net_tx', '#a855f7')
        box_col = t.get('net_box', rx_col)
        
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column()
        
        rx_line = Text()
        rx_line.append("▼ RX: ", style=f"bold {rx_col}")
        rx_line.append(f"{format_bytes(rx_speed)}/s ", style=f"bold {t.get('text', '#f0fdf4')}")
        rx_line.append(f"(Total: {format_bytes(net_rx_total)})", style=f"dim {t.get('dim_text', '#15803d')}")
        grid.add_row(rx_line)
        
        rx_spark = generate_sparkline(rx_hist[-25:], style_color=rx_col)
        grid.add_row(rx_spark)
        
        tx_line = Text()
        tx_line.append("▲ TX: ", style=f"bold {tx_col}")
        tx_line.append(f"{format_bytes(tx_speed)}/s ", style=f"bold {t.get('text', '#f0fdf4')}")
        tx_line.append(f"(Total: {format_bytes(net_tx_total)})", style=f"dim {t.get('dim_text', '#15803d')}")
        grid.add_row(tx_line)
        
        tx_spark = generate_sparkline(tx_hist[-25:], style_color=tx_col)
        grid.add_row(tx_spark)
        
        ifaces = metrics.get("interfaces", [])
        if ifaces:
            if_line = Text("Interfaces: ", style=f"dim {t.get('dim_text', '#15803d')}")
            for ifc in ifaces:
                if_line.append(f"{ifc['name']}[{ifc['ip']}] ", style=f"bold {t.get('highlight', '#00ff55')}")
            grid.add_row(if_line)
            
        return Panel(
            grid,
            title=f"[bold {box_col}] NET // Real-Time I/O [/]",
            title_align="left",
            border_style=box_col,
            padding=(0, 1),
        )

    def render_radar_box(self, metrics: Dict[str, Any], collector_obj: Optional[Any] = None) -> Panel:
        t = self.theme
        self.step += 1
        
        highlight_col = t.get('highlight', '#00ff55')
        crit_col = t.get('meter_crit', '#ef4444')
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column(ratio=4)
        grid.add_column(ratio=6)
        
        radar_lines = generate_tactical_radar_art(self.step, radar_color=highlight_col, blip_color=crit_col)
        radar_text = Text("\n").join(radar_lines)
        
        targets_table = Table(
            box=None,
            expand=True,
            header_style=f"bold {highlight_col}",
            border_style=f"dim {border_col}",
            padding=(0, 1),
        )
        targets_table.add_column("TYPE", style=f"bold {t.get('cpu_box', highlight_col)}", width=6)
        targets_table.add_column("RADAR VECTOR / ENDPOINT", style=f"bold {t.get('text', '#f0fdf4')}")
        targets_table.add_column("STATUS", justify="right", style=f"bold {t.get('meter_low', '#22c55e')}", width=12)
        
        radar_targets: List[Dict[str, Any]] = collector_obj.get_radar_targets() if collector_obj else []
        if not radar_targets:
            radar_targets = [
                {"type": "UPLINK", "label": "Groq Satellite Llama-3.3 (US-CENTRAL)", "status": "ONLINE", "pid": 4096},
                {"type": "RADAR", "label": "Localhost Port 8000 (FastAPI Service)", "status": "ACTIVE", "pid": 1024},
                {"type": "COMMS", "label": "Telemetry Sonar Ping // 280 t/s", "status": "CONNECTED", "pid": 8192},
            ]
            
        for tgt in radar_targets[:5]:
            targets_table.add_row(
                str(tgt["type"]),
                str(tgt["label"]),
                str(tgt["status"]),
            )
            
        grid.add_row(radar_text, targets_table)
        
        return Panel(
            grid,
            title=f"[bold {highlight_col}] 🛰️ TACTICAL RADAR // Active Neural & Network Sonar [/]",
            title_align="left",
            border_style=highlight_col,
            padding=(0, 1),
        )

    def render_proc_box(self, procs: List[Dict[str, Any]]) -> Panel:
        t = self.theme
        highlight_col = t.get('highlight', '#00ff55')
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        mem_col = t.get('mem_box', t.get('title', '#22c55e'))
        cpu_col = t.get('cpu_box', highlight_col)
        proc_box_col = t.get('proc_box', highlight_col)
        
        tbl = Table(
            box=None,
            expand=True,
            header_style=f"bold {highlight_col}",
            border_style=f"dim {border_col}",
            padding=(0, 1),
        )
        tbl.add_column("PID", justify="right", style=f"dim {t.get('dim_text', '#15803d')}", width=7)
        tbl.add_column("Program Name", justify="left", style=f"bold {t.get('text', '#f0fdf4')}")
        tbl.add_column("User", justify="left", style=f"dim {t.get('dim_text', '#15803d')}", width=10)
        tbl.add_column("Threads", justify="right", style=f"dim {t.get('text', '#f0fdf4')}", width=7)
        tbl.add_column("Mem RSS", justify="right", style=f"bold {mem_col}", width=10)
        tbl.add_column("Mem %", justify="right", style=f"bold {mem_col}", width=7)
        tbl.add_column("CPU %", justify="right", style=f"bold {cpu_col}", width=7)

        for idx, p in enumerate(procs):
            is_sel = (idx == self.selected_proc_idx)
            pid_str = f"▶ {p['pid']}" if is_sel else str(p['pid'])
            p_style = f"bold reverse {highlight_col}" if is_sel else f"bold {t.get('text', '#f0fdf4')}"
            rss_str = format_bytes(p.get("mem_rss", 0))
            
            tbl.add_row(
                pid_str,
                Text(p["name"][:20], style=p_style),
                p.get("user", "user")[:10],
                str(p.get("threads", 1)),
                rss_str,
                f"{p['mem']:4.1f}%",
                f"{p['cpu']:4.1f}%",
            )

        sort_info = f" [Sorted by: {self.sort_by.upper()} (s)] "
        if self.filter_text:
            sort_info += f"[Filter: '{self.filter_text}' (c:clear)] "
        sort_info += "[k: Kill | i: Inspect]"

        return Panel(
            tbl,
            title=f"[bold {proc_box_col}] PROC // Interactive Process Manager {sort_info}[/]",
            title_align="left",
            border_style=proc_box_col,
            padding=(0, 1),
        )

    def render_buddy_box(self, agent_state: Optional[Dict[str, Any]] = None) -> Panel:
        t = self.theme
        buddy_col = t.get('buddy_box', t.get('title', '#22c55e'))
        highlight_col = t.get('highlight', '#00ff55')
        crit_col = t.get('meter_crit', '#ef4444')
        low_col = t.get('meter_low', '#22c55e')
        
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column(ratio=2)
        grid.add_column(ratio=6)

        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spin = spinners[self.step % len(spinners)]

        teddy = Text()
        teddy.append("  ʕ•ᴥ•ʔ  \n", style=f"bold {buddy_col}")
        teddy.append("  (づ♥⊂) \n", style=f"bold {crit_col}")
        teddy.append("  /\"\"\"\"\\ \n", style=f"dim {buddy_col}")

        ai_info = Table.grid(padding=(0, 1), expand=True)
        ai_info.add_column()

        model_name = agent_state.get("model_name", "Groq Satellite (Llama 3.3 70B)") if agent_state else "Groq Satellite (Llama 3.3 70B)"
        speed = agent_state.get("speed", "⚡ 280 t/s") if agent_state else "⚡ 280 t/s"
        latency = agent_state.get("latency", "135 ms") if agent_state else "135 ms"
        status_msg = agent_state.get("status_msg", "Hey Champ! Pair programming ready. Telemetry online!") if agent_state else "Hey Champ! Pair programming ready. Telemetry online!"

        l1 = Text()
        l1.append(f"{spin} ", style=f"bold {buddy_col}")
        l1.append("Satellite Neural Uplink: ", style=f"bold {t.get('text', '#f0fdf4')}")
        l1.append(f"{model_name} ", style=f"bold {low_col}")
        l1.append(f"• {speed} • Latency: {latency}", style=f"dim {t.get('dim_text', '#15803d')}")
        ai_info.add_row(l1)

        l2 = Text()
        l2.append(" Buddy says: ", style=f"bold {buddy_col}")
        l2.append(f"\"{status_msg}\"", style=f"italic {highlight_col}")
        ai_info.add_row(l2)

        grid.add_row(teddy, ai_info)

        return Panel(
            grid,
            title=f"[bold {buddy_col}] BUDDY AGENT // Satellite AI Telemetry & Empathy Companion [/]",
            title_align="left",
            border_style=buddy_col,
            padding=(0, 1),
        )

    def render_process_inspect_modal(self, p_details: Dict[str, Any]) -> Panel:
        t = self.theme
        highlight_col = t.get('highlight', '#00ff55')
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        
        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column(style=f"bold {highlight_col}", width=18)
        table.add_column(style=f"bold {t.get('text', '#f0fdf4')}")

        table.add_row("Process Name:", p_details.get("name", "N/A"))
        table.add_row("Process ID (PID):", str(p_details.get("pid", "N/A")))
        table.add_row("Owner / User:", p_details.get("user", "N/A"))
        table.add_row("Execution Status:", p_details.get("status", "N/A"))
        table.add_row("CPU Utilization:", f"{p_details.get('cpu_percent', 0.0):.1f}%")
        table.add_row("Resident Memory (RSS):", format_bytes(p_details.get("memory_rss", 0)))
        table.add_row("Virtual Memory (VMS):", format_bytes(p_details.get("memory_vms", 0)))
        table.add_row("Active Threads:", str(p_details.get("threads", 1)))
        table.add_row("Start Time:", p_details.get("create_time", "N/A"))
        table.add_row("Full Command Line:", p_details.get("cmdline", "N/A"))

        content = Table.grid(padding=(0, 0), expand=True)
        content.add_column()
        content.add_row(table)
        content.add_row(Text("─" * 70, style=f"dim {border_col}"))
        content.add_row(Text("Press Enter or Esc to return to telemetry dashboard", style=f"bold {highlight_col}", justify="center"))

        return Panel(
            content,
            title=f"[bold {highlight_col}]  Tactical Process Inspector // PID {p_details.get('pid')} [/]",
            border_style=highlight_col,
            padding=(1, 2),
        )

    def render_kill_confirm_modal(self, p_info: Dict[str, Any]) -> Panel:
        t = self.theme
        crit_col = t.get('meter_crit', '#ef4444')
        border_col = t.get('box_border', t.get('dim_text', '#15803d'))
        highlight_col = t.get('highlight', '#00ff55')
        
        content = Table.grid(padding=(0, 1), expand=True)
        content.add_column()

        content.add_row(Text(" CONFIRM TACTICAL PROCESS TERMINATION", style=f"bold {crit_col}", justify="center"))
        content.add_row(Text("─" * 60, style=f"dim {border_col}"))
        content.add_row(Text(f"Process Name : {p_info.get('name')}", style=f"bold {t.get('text', '#f0fdf4')}"))
        content.add_row(Text(f"Process PID  : {p_info.get('pid')}", style=f"bold {t.get('text', '#f0fdf4')}"))
        content.add_row(Text(f"User Owner   : {p_info.get('user')}", style=f"dim {t.get('dim_text', '#15803d')}"))
        content.add_row(Text(""))
        content.add_row(Text("Press [Y] to terminate or [N / Esc] to cancel", style=f"bold {highlight_col}", justify="center"))

        return Panel(
            content,
            title=f"[bold {crit_col}] 🛑 Terminate Process [/]",
            border_style=crit_col,
            padding=(1, 2),
        )

    def render_dashboard(
        self,
        metrics: Dict[str, Any],
        procs: List[Dict[str, Any]],
        agent_state: Optional[Dict[str, Any]] = None,
        collector_obj: Optional[Any] = None,
        refresh_rate: float = 1.0,
    ) -> Group:
        elements: List[RenderableType] = []

        elements.append(self.render_header(metrics, refresh_rate))
        elements.append(Text(""))

        if self.status_notification and (time.time() - self.status_notification_time < 3.0):
            elements.append(Panel(
                Text(f"{self.status_notification}", style=f"bold {self.theme.get('highlight', '#00ff55')}"),
                border_style=f"bold {self.theme.get('highlight', '#00ff55')}",
                padding=(0, 1),
            ))

        if self.show_cpu:
            elements.append(self.render_cpu_box(metrics))

        mid_table = Table.grid(padding=(0, 1), expand=True)
        mid_table.add_column(ratio=1)
        mid_table.add_column(ratio=1)

        mem_panel = self.render_mem_disk_box(metrics) if self.show_mem else Text("")
        net_panel = self.render_net_box(metrics) if self.show_net else Text("")
        mid_table.add_row(mem_panel, net_panel)
        elements.append(mid_table)

        if self.show_radar:
            elements.append(self.render_radar_box(metrics, collector_obj))

        if self.show_buddy:
            elements.append(self.render_buddy_box(agent_state))

        if self.show_proc:
            elements.append(self.render_proc_box(procs))

        return Group(*elements)
