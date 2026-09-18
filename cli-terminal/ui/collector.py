"""
System and Agent Telemetry Collector for Btop Resource Monitor & IGI Tactical HUD
Uses psutil with robust fallback, history tracking, process control, and network interface scanning.
"""

import time
import os
import sys
from typing import List, Dict, Any, Optional, Tuple

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class SystemCollector:
    def __init__(self, history_len: int = 120):
        self.history_len = history_len
        self.cpu_history: List[float] = []
        self.net_rx_history: List[float] = []
        self.net_tx_history: List[float] = []
        
        self.last_net_io = None
        self.last_net_time = time.time()
        self.rx_speed = 0.0  # bytes / sec
        self.tx_speed = 0.0  # bytes / sec
        
        self.last_disk_io = None
        self.last_disk_time = time.time()
        self.disk_read_speed = 0.0  # bytes / sec
        self.disk_write_speed = 0.0 # bytes / sec
        
        self.boot_time = psutil.boot_time() if HAS_PSUTIL else time.time() - 3600
        
        # Prime psutil cpu measurements
        if HAS_PSUTIL:
            try:
                psutil.cpu_percent(interval=None)
                psutil.cpu_percent(interval=None, percpu=True)
            except Exception:
                pass

    def update_metrics(self) -> Dict[str, Any]:
        """Collects latest system snapshots and updates histories."""
        now = time.time()
        
        # 1. CPU
        if HAS_PSUTIL:
            try:
                cpu_total = psutil.cpu_percent(interval=None)
                per_core = psutil.cpu_percent(interval=None, percpu=True)
                cpu_count = psutil.cpu_count(logical=True) or 4
                
                # Frequency
                freq = psutil.cpu_freq()
                cpu_freq_ghz = (freq.current / 1000.0) if freq and freq.current else 2.8
            except Exception:
                cpu_total = 15.0
                per_core = [15.0] * 4
                cpu_count = 4
                cpu_freq_ghz = 2.8
        else:
            cpu_total = 22.0
            per_core = [20.0, 25.0, 18.0, 26.0]
            cpu_count = 4
            cpu_freq_ghz = 3.2
            
        self.cpu_history.append(cpu_total)
        if len(self.cpu_history) > self.history_len:
            self.cpu_history.pop(0)

        # 2. Memory & Swap
        if HAS_PSUTIL:
            try:
                vmem = psutil.virtual_memory()
                mem_total = vmem.total
                mem_used = vmem.used
                mem_avail = vmem.available
                mem_free = getattr(vmem, "free", mem_avail)
                mem_percent = vmem.percent
                mem_cached = getattr(vmem, "cached", 0)
                
                smem = psutil.swap_memory()
                swap_total = smem.total
                swap_used = smem.used
                swap_free = smem.free
                swap_percent = smem.percent
            except Exception:
                mem_total = 16 * 1024**3
                mem_used = 8 * 1024**3
                mem_avail = 8 * 1024**3
                mem_free = 4 * 1024**3
                mem_percent = 50.0
                mem_cached = 2 * 1024**3
                swap_total = 8 * 1024**3
                swap_used = 1 * 1024**3
                swap_free = 7 * 1024**3
                swap_percent = 12.5
        else:
            mem_total = 16 * 1024**3
            mem_used = 8 * 1024**3
            mem_avail = 8 * 1024**3
            mem_free = 4 * 1024**3
            mem_percent = 50.0
            mem_cached = 2 * 1024**3
            swap_total = 8 * 1024**3
            swap_used = 1 * 1024**3
            swap_free = 7 * 1024**3
            swap_percent = 12.5

        # 3. Disks
        disks_info = []
        if HAS_PSUTIL:
            try:
                partitions = psutil.disk_partitions(all=False)
                for part in partitions:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        disks_info.append({
                            "device": part.device,
                            "mount": part.mountpoint,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                        })
                    except Exception:
                        continue
                
                # Disk IO
                dio = psutil.disk_io_counters()
                if dio and self.last_disk_io:
                    dt = max(0.001, now - self.last_disk_time)
                    self.disk_read_speed = max(0.0, (dio.read_bytes - self.last_disk_io.read_bytes) / dt)
                    self.disk_write_speed = max(0.0, (dio.write_bytes - self.last_disk_io.write_bytes) / dt)
                if dio:
                    self.last_disk_io = dio
                    self.last_disk_time = now
            except Exception:
                pass
        
        if not disks_info:
            disks_info = [{
                "device": "C:" if sys.platform == "win32" else "/",
                "mount": "C:" if sys.platform == "win32" else "/",
                "total": 512 * 1024**3,
                "used": 240 * 1024**3,
                "free": 272 * 1024**3,
                "percent": 46.8,
            }]

        # 4. Network
        net_rx_total = 0
        net_tx_total = 0
        interfaces_list = []
        if HAS_PSUTIL:
            try:
                nio = psutil.net_io_counters()
                if nio:
                    net_rx_total = nio.bytes_recv
                    net_tx_total = nio.bytes_sent
                    if self.last_net_io:
                        dt = max(0.001, now - self.last_net_time)
                        self.rx_speed = max(0.0, (nio.bytes_recv - self.last_net_io.bytes_recv) / dt)
                        self.tx_speed = max(0.0, (nio.bytes_sent - self.last_net_io.bytes_sent) / dt)
                    self.last_net_io = nio
                    self.last_net_time = now
                
                # Network interfaces
                addrs = psutil.net_if_addrs()
                stats = psutil.net_if_stats()
                for iface_name, addr_list in addrs.items():
                    ip_addr = "N/A"
                    for addr in addr_list:
                        if addr.family.name == "AF_INET":
                            ip_addr = addr.address
                            break
                    is_up = stats[iface_name].isup if iface_name in stats else True
                    if ip_addr != "N/A" and not ip_addr.startswith("127."):
                        interfaces_list.append({
                            "name": iface_name,
                            "ip": ip_addr,
                            "is_up": is_up,
                        })
            except Exception:
                pass
                
        # Normalize network history as percentage of peak bandwidth (e.g. 10 MB/s scale)
        max_bw = 10 * 1024 * 1024 # 10 MiB/s reference scale
        rx_pct = min(100.0, (self.rx_speed / max_bw) * 100.0)
        tx_pct = min(100.0, (self.tx_speed / max_bw) * 100.0)
        
        self.net_rx_history.append(rx_pct)
        if len(self.net_rx_history) > self.history_len:
            self.net_rx_history.pop(0)
            
        self.net_tx_history.append(tx_pct)
        if len(self.net_tx_history) > self.history_len:
            self.net_tx_history.pop(0)

        # 5. Uptime & Battery
        uptime_sec = int(now - self.boot_time)
        hours = uptime_sec // 3600
        mins = (uptime_sec % 3600) // 60
        uptime_str = f"{hours}h {mins}m"
        
        battery_pct = None
        battery_charging = False
        if HAS_PSUTIL:
            try:
                batt = psutil.sensors_battery()
                if batt:
                    battery_pct = batt.percent
                    battery_charging = batt.power_plugged
            except Exception:
                pass

        # 6. Threat assessment
        threat_level = "SECURE"
        if cpu_total > 85.0 or mem_percent > 90.0:
            threat_level = "CRITICAL"
        elif cpu_total > 60.0 or mem_percent > 75.0:
            threat_level = "ELEVATED"

        return {
            "cpu_total": cpu_total,
            "per_core": per_core,
            "cpu_count": cpu_count,
            "cpu_freq_ghz": cpu_freq_ghz,
            "cpu_history": self.cpu_history,
            "mem_total": mem_total,
            "mem_used": mem_used,
            "mem_avail": mem_avail,
            "mem_free": mem_free,
            "mem_cached": mem_cached,
            "mem_percent": mem_percent,
            "swap_total": swap_total,
            "swap_used": swap_used,
            "swap_free": swap_free,
            "swap_percent": swap_percent,
            "disks": disks_info,
            "disk_read_speed": self.disk_read_speed,
            "disk_write_speed": self.disk_write_speed,
            "rx_speed": self.rx_speed,
            "tx_speed": self.tx_speed,
            "net_rx_total": net_rx_total,
            "net_tx_total": net_tx_total,
            "net_rx_history": self.net_rx_history,
            "net_tx_history": self.net_tx_history,
            "interfaces": interfaces_list[:2],
            "uptime_str": uptime_str,
            "battery_pct": battery_pct,
            "battery_charging": battery_charging,
            "threat_level": threat_level,
        }

    def get_process_list(self, sort_by: str = "cpu", filter_text: str = "", limit: int = 15) -> List[Dict[str, Any]]:
        """Returns sorted and filtered running processes with memory RSS details."""
        procs = []
        if not HAS_PSUTIL:
            dummy_list = [
                {"pid": 1024, "name": "python.exe", "user": "agent", "cpu": 14.5, "mem": 4.2, "mem_rss": 145 * 1024**2, "threads": 12, "status": "running", "cmd": "uv run python cli.py"},
                {"pid": 4096, "name": "groq_worker", "user": "agent", "cpu": 8.2, "mem": 2.1, "mem_rss": 78 * 1024**2, "threads": 8, "status": "running", "cmd": "groq-stream --model llama-3.3"},
                {"pid": 8192, "name": "ollama.exe", "user": "system", "cpu": 2.1, "mem": 12.4, "mem_rss": 512 * 1024**2, "threads": 16, "status": "running", "cmd": "ollama serve"},
                {"pid": 9821, "name": "code.exe", "user": "developer", "cpu": 1.5, "mem": 6.8, "mem_rss": 340 * 1024**2, "threads": 32, "status": "sleeping", "cmd": "code e:\\Hackathon"},
            ]
            if filter_text:
                dummy_list = [p for p in dummy_list if filter_text.lower() in p["name"].lower()]
            return dummy_list

        try:
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'memory_info', 'num_threads', 'status']):
                try:
                    info = p.info
                    name = info.get('name') or "unknown"
                    if filter_text and filter_text.lower() not in name.lower():
                        continue
                    
                    mem_info = info.get('memory_info')
                    mem_rss = mem_info.rss if mem_info else 0
                    
                    procs.append({
                        "pid": info.get('pid', 0),
                        "name": name,
                        "user": (info.get('username') or "").split("\\")[-1] or "user",
                        "cpu": info.get('cpu_percent') or 0.0,
                        "mem": info.get('memory_percent') or 0.0,
                        "mem_rss": mem_rss,
                        "threads": info.get('num_threads') or 1,
                        "status": info.get('status') or "running",
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass

        # Dynamic Sorting
        if sort_by == "mem":
            procs.sort(key=lambda x: x["mem"], reverse=True)
        elif sort_by == "rss":
            procs.sort(key=lambda x: x["mem_rss"], reverse=True)
        elif sort_by == "pid":
            procs.sort(key=lambda x: x["pid"])
        elif sort_by == "name":
            procs.sort(key=lambda x: x["name"].lower())
        elif sort_by == "user":
            procs.sort(key=lambda x: x["user"].lower())
        else: # default cpu
            procs.sort(key=lambda x: x["cpu"], reverse=True)

        return procs[:limit]

    def get_process_details(self, pid: int) -> Optional[Dict[str, Any]]:
        """Retrieves in-depth tactical telemetry on a specific process."""
        if not HAS_PSUTIL:
            return {
                "pid": pid,
                "name": "python.exe",
                "user": "developer",
                "status": "running",
                "cpu_percent": 12.5,
                "memory_rss": 145 * 1024**2,
                "memory_vms": 320 * 1024**2,
                "threads": 12,
                "cmdline": "uv run python cli.py",
                "create_time": time.ctime(time.time() - 1800),
            }
        try:
            p = psutil.Process(pid)
            mem = p.memory_info()
            return {
                "pid": pid,
                "name": p.name(),
                "user": (p.username() or "").split("\\")[-1],
                "status": p.status(),
                "cpu_percent": p.cpu_percent(),
                "memory_rss": mem.rss,
                "memory_vms": mem.vms,
                "threads": p.num_threads(),
                "cmdline": " ".join(p.cmdline()) if p.cmdline() else p.name(),
                "create_time": time.ctime(p.create_time()),
            }
        except Exception:
            return None

    def terminate_process(self, pid: int) -> Tuple[bool, str]:
        """Terminates or kills a process by PID."""
        if not HAS_PSUTIL:
            return True, f"Simulated termination of process {pid} successful."
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True, f"Process {pid} ({p.name()}) terminated."
        except psutil.NoSuchProcess:
            return False, f"Process {pid} does not exist."
        except psutil.AccessDenied:
            try:
                p = psutil.Process(pid)
                p.kill()
                return True, f"Process {pid} forcefully killed."
            except Exception:
                return False, f"Access denied terminating process {pid}."
        except Exception as e:
            return False, f"Error terminating {pid}: {str(e)}"

    def get_radar_targets(self) -> List[Dict[str, Any]]:
        """Collects tactical radar targets (network connections and active threads)."""
        targets = []
        if HAS_PSUTIL:
            try:
                conns = psutil.net_connections(kind="inet")
                for c in conns[:6]:
                    if c.status in ("ESTABLISHED", "LISTEN"):
                        l_addr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "local"
                        r_addr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "listen"
                        targets.append({
                            "type": "NET",
                            "label": f"{l_addr} -> {r_addr}",
                            "status": c.status,
                            "pid": c.pid or 0,
                        })
            except Exception:
                pass
        if not targets:
            targets = [
                {"type": "UPLINK", "label": "Groq Satellite Llama-3.3 (US-CENTRAL)", "status": "CONNECTED", "pid": 4096},
                {"type": "RADAR", "label": "Localhost Port 8000 (FastAPI Service)", "status": "LISTEN", "pid": 1024},
                {"type": "COMMS", "label": "Telemetry Sonar Ping // 280 t/s", "status": "ACTIVE", "pid": 8192},
            ]
        return targets


def format_bytes(num_bytes: float) -> str:
    """Formats bytes to B, KiB, MiB, GiB, TiB."""
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PiB"
