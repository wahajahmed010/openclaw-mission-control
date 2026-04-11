#!/usr/bin/env python3
"""
Buck's Dashboard — Real-time OpenClaw Health Monitor
Built with Python stdlib + psutil (no Flask needed)
Serves at http://0.0.0.0:8080
"""

import http.server
import socketserver
import json
import os
import time
import socket
import sqlite3
import re
import glob
from datetime import datetime
from pathlib import Path
import psutil
import subprocess

PORT = 8080
BUFFER_SIZE = 100  # Circular buffer for activity log

# ─── Activity Logger ───────────────────────────────────────────────
activity_log = []

def log_activity(event_type, message):
    """Add entry to circular activity log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    activity_log.insert(0, {"time": timestamp, "type": event_type, "msg": message})
    if len(activity_log) > BUFFER_SIZE:
        activity_log.pop()

log_activity("system", "Dashboard initialized")

# ─── Metric Collectors ──────────────────────────────────────────────

def get_gateway_status():
    """Check if OpenClaw gateway is alive via host network namespace"""
    try:
        start = time.time()
        result = subprocess.run(
            ['curl', '-s', '--max-time', '3', 'http://127.0.0.1:18789/'],
            capture_output=True, text=True, timeout=5
        )
        latency_ms = round((time.time() - start) * 1000)
        if result.returncode == 0 and result.stdout.strip():
            # Try to get actual uptime from gateway API (expects JSON response)
            uptime_str = None
            try:
                uptime_result = subprocess.run(
                    ['curl', '-s', '--max-time', '2', 'http://127.0.0.1:18789/status'],
                    capture_output=True, text=True, timeout=4
                )
                if uptime_result.returncode == 0 and uptime_result.stdout.strip().startswith('{'):
                    uptime_data = json.loads(uptime_result.stdout)
                    process_start = uptime_data.get('process_start', 0)
                    if process_start:
                        uptime_s = int(time.time() - process_start)
                        h, rem = divmod(uptime_s, 3600)
                        m, s = divmod(rem, 60)
                        uptime_str = f"{h}h {m}m" if h > 0 else f"{m}m {s}s"
            except Exception:
                pass

            # Fallback: find openclaw-gateway process start time via psutil
            if not uptime_str:
                for proc in psutil.process_iter(['name', 'create_time']):
                    try:
                        name = proc.info['name'] or ''
                        if 'openclaw-gateway' in str(name) or 'openclaw' in str(name).lower():
                            create_time = proc.info['create_time']
                            if create_time:
                                uptime_s = int(time.time() - create_time)
                                h, rem = divmod(uptime_s, 3600)
                                m, s = divmod(rem, 60)
                                uptime_str = f"{h}h {m}m" if h > 0 else f"{m}m {s}s"
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            return {
                "status": "alive",
                "service": "openclaw-gateway",
                "version": "2026.4.9",
                "latency_ms": latency_ms,
                "uptime": uptime_str or "Active",
                "uptime_raw": uptime_str
            }
    except Exception:
        pass
    return {"status": "dead", "service": "openclaw-gateway", "version": "2026.4.9", "latency_ms": None}

def get_service_health():
    """Check health of key services: Gateway, Tailscale, SSH, DNS"""
    health = {
        "gateway": "unknown",
        "tailscale": "unknown",
        "ssh": "unknown",
        "dns": "unknown"
    }

    # Gateway
    gw = get_gateway_status()
    health["gateway"] = gw["status"]

    # SSH (port 22)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 22))
        sock.close()
        health["ssh"] = "alive" if result == 0 else "dead"
    except Exception:
        health["ssh"] = "unknown"

    # DNS (port 53)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 53))
        sock.close()
        health["dns"] = "alive" if result == 0 else "dead"
    except Exception:
        health["dns"] = "unknown"

    # Tailscale (port 41641 or service check)
    try:
        # Try connecting to Tailscale port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 41641))
        sock.close()
        if result == 0:
            health["tailscale"] = "alive"
        else:
            # Check if tailscaled process exists
            proc = subprocess.run(
                ["pgrep", "-x", "tailscaled"],
                capture_output=True, text=True, timeout=3
            )
            health["tailscale"] = "alive" if proc.returncode == 0 else "not_installed"
    except Exception:
        health["tailscale"] = "not_installed"

    # Overall health score (0-100) + weakest link
    alive_count = sum(1 for v in health.values() if v == "alive")
    # Denominator: only installed/expected services (exclude 'not_installed')
    installed_keys = [k for k, v in health.items() if k not in ('score', 'weakest') and v != 'not_installed']
    total_installed = len(installed_keys)
    health["score"] = round((alive_count / total_installed) * 100) if total_installed > 0 else 0

    # Find weakest service (dead > unknown)
    not_alive = {k: v for k, v in health.items() if k not in ('score',) and v not in ('alive', 'not_installed')}
    weakest = None
    for svc, status in not_alive.items():
        if status == 'dead':
            weakest = svc
            break
    if weakest is None and not_alive:
        weakest = list(not_alive.keys())[0]
    health["weakest"] = weakest

    return health

def get_system_metrics():
    """Collect CPU, RAM, Disk, Network metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        per_cpu = psutil.cpu_percent(interval=0.5, percpu=True)
        load = psutil.getloadavg()

        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "per_core": per_cpu,
                "load_1m": round(load[0], 2),
                "load_5m": round(load[1], 2),
                "load_15m": round(load[2], 2)
            },
            "ram": {
                "total_gb": round(mem.total / (1024**3), 1),
                "used_gb": round(mem.used / (1024**3), 1),
                "available_gb": round(mem.available / (1024**3), 1),
                "percent": mem.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 0),
                "used_gb": round(disk.used / (1024**3), 0),
                "free_gb": round(disk.free / (1024**3), 0),
                "percent": round(disk.percent, 1)
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        }
    except Exception as e:
        return {"error": str(e)}

def get_docker_status():
    """Get Docker container status"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True, text=True, timeout=5
        )
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    obj = json.loads(line)
                    containers.append({
                        "name": obj.get("Names", "unknown"),
                        "status": obj.get("Status", "unknown"),
                        "state": obj.get("State", "unknown"),
                        "image": obj.get("Image", "unknown")[:40]
                    })
                except:
                    pass
        return {"containers": containers, "count": len(containers)}
    except Exception as e:
        return {"containers": [], "error": str(e)}

def get_service_strip():
    """Get service health strip data for the power-bus display"""
    services = []

    # Gateway
    gw = get_gateway_status()
    latency = gw.get("latency_ms")
    services.append({
        "name": "Gateway",
        "status": gw["status"],
        "latency_ms": latency
    })

    # SSH (port 22)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 22))
        sock.close()
        ssh_status = "alive" if result == 0 else "dead"
    except Exception:
        ssh_status = "dead"
    services.append({"name": "SSH", "status": ssh_status, "latency_ms": None})

    # DNS (port 53 UDP/TCP)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 53))
        sock.close()
        dns_status = "alive" if result == 0 else "dead"
    except Exception:
        dns_status = "dead"
    services.append({"name": "DNS", "status": dns_status, "latency_ms": None})

    # AdGuard — check if container is running, try API
    adguard_status = "not_installed"
    adguard_latency = None
    try:
        check = subprocess.run(
            ["docker", "ps", "--filter", "name=adguardhome", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5
        )
        if "adguardhome" in check.stdout:
            # Try API on port 3000
            try:
                start = time.time()
                ag_res = subprocess.run(
                    ["curl", "-s", "--max-time", "2", "http://127.0.0.1:3000/status"],
                    capture_output=True, text=True, timeout=3
                )
                adguard_latency = round((time.time() - start) * 1000)
                if ag_res.returncode == 0 and ag_res.stdout.strip().startswith('{'):
                    adguard_status = "alive"
                else:
                    adguard_status = "alive"  # container running, API not responding
            except Exception:
                adguard_status = "alive"  # container alive but API unreachable
        else:
            adguard_status = "not_installed"
    except Exception:
        adguard_status = "not_installed"
    services.append({"name": "AdGuard", "status": adguard_status, "latency_ms": adguard_latency})

    # Docker
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=5
        )
        docker_status = "alive" if result.returncode == 0 else "dead"
    except Exception:
        docker_status = "dead"
    services.append({"name": "Docker", "status": docker_status, "latency_ms": None})

    # Tailscale
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 41641))
        sock.close()
        if result == 0:
            ts_status = "alive"
        else:
            proc = subprocess.run(
                ["pgrep", "-x", "tailscaled"],
                capture_output=True, text=True, timeout=3
            )
            ts_status = "alive" if proc.returncode == 0 else "not_installed"
    except Exception:
        ts_status = "not_installed"
    services.append({"name": "Tailscale", "status": ts_status, "latency_ms": None})

    return services

def get_adguard_status():
    """Get AdGuard DNS stats — clean version, no fake parsing"""
    try:
        check = subprocess.run(
            ["docker", "ps", "--filter", "name=adguardhome", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5
        )
        is_running = "adguardhome" in check.stdout

        if not is_running:
            return {"status": "not_installed", "version": None, "blocked": 0}

        # Try to get real stats from AdGuard API
        try:
            ag_res = subprocess.run(
                ["curl", "-s", "--max-time", "3", "http://127.0.0.1:3000/status"],
                capture_output=True, text=True, timeout=5
            )
            if ag_res.returncode == 0 and ag_res.stdout.strip().startswith('{'):
                data = json.loads(ag_res.stdout)
                return {
                    "status": "alive",
                    "version": data.get("version", "unknown"),
                    "blocked": data.get("blocked", 0),
                    "upstream": data.get("upstream_dns", ["unknown"])[0] if data.get("upstream_dns") else "unknown"
                }
        except Exception:
            pass

        return {"status": "alive", "version": "unknown", "blocked": 0, "upstream": "unknown"}
    except Exception as e:
        return {"status": "not_installed", "version": None, "blocked": 0, "error": str(e)}

def get_network_info():
    """Get LAN and connectivity info"""
    try:
        hostname = socket.gethostname()
        lan_ip = subprocess.run(
            ["hostname", "-I"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip().split()[0] if subprocess.run(
            ["which", "hostname"], capture_output=True
        ).returncode == 0 else "unknown"

        internet_ok = False
        try:
            sock = socket.create_connection(("8.8.8.8", 53), timeout=3)
            sock.close()
            internet_ok = True
        except:
            pass

        return {
            "hostname": hostname,
            "lan_ip": lan_ip,
            "internet": "connected" if internet_ok else "disconnected"
        }
    except Exception as e:
        return {"error": str(e)}

def get_openclaw_sessions():
    """Get active and recent OpenClaw agents from SQLite database"""
    try:
        db_path = '/home/wahaj/.openclaw/tasks/runs.sqlite'
        if not os.path.exists(db_path):
            return []

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Active subagents (no end time)
        c.execute('''
            SELECT run_id, child_session_key, task, status, started_at, label
            FROM task_runs
            WHERE child_session_key LIKE "%subagent%" AND ended_at IS NULL
            ORDER BY started_at DESC
        ''')
        active_rows = c.fetchall()

        # Recently ended subagents (last 30 min)
        cutoff = (time.time() - 1800) * 1000
        c.execute('''
            SELECT run_id, child_session_key, task, status, ended_at, label, terminal_outcome
            FROM task_runs
            WHERE child_session_key LIKE "%subagent%" AND ended_at > ?
            ORDER BY ended_at DESC
        ''', (cutoff,))
        recent_rows = c.fetchall()
        conn.close()

        agents = []
        seen = set()

        for row in active_rows:
            run_id, child_sk, task, status, started, label = row
            if child_sk in seen:
                continue
            seen.add(child_sk)
            name_match = re.search(r'You are "(\w+)"', task or '')
            agent_name = name_match.group(1) if name_match else 'Unknown'
            started_ts = datetime.fromtimestamp(started/1000).strftime('%H:%M:%S') if started else '?'
            agents.append({
                "name": agent_name,
                "session_key": child_sk,
                "status": "running",
                "started": started_ts,
                "ended": None,
                "task_preview": (task or '')[:120].replace('\n', ' ')
            })

        for row in recent_rows:
            run_id, child_sk, task, status, ended, label, outcome = row
            if child_sk in seen:
                continue
            seen.add(child_sk)
            name_match = re.search(r'You are "(\w+)"', task or '')
            agent_name = name_match.group(1) if name_match else 'Unknown'
            ended_ts = datetime.fromtimestamp(ended/1000).strftime('%H:%M:%S') if ended else '?'
            agents.append({
                "name": agent_name,
                "session_key": child_sk,
                "status": "idle",
                "started": None,
                "ended": ended_ts,
                "task_preview": (task or '')[:120].replace('\n', ' ')
            })

        return agents
    except Exception as e:
        return []

def get_load_averages():
    """Get system load averages"""
    try:
        load = psutil.getloadavg()
        return {
            "1min": round(load[0], 2),
            "5min": round(load[1], 2),
            "15min": round(load[2], 2)
        }
    except:
        return {"1min": 0, "5min": 0, "15min": 0}

def get_task_pipeline():
    """Get task pipeline state from SQLite"""
    def fmt_duration(started_ms, ended_ms):
        """Format duration in human readable format"""
        if not started_ms:
            return "?"
        end = ended_ms if ended_ms else time.time() * 1000
        elapsed_s = int((end - started_ms) / 1000)
        if elapsed_s < 60:
            return f"{elapsed_s}s"
        m, s = divmod(elapsed_s, 60)
        if m < 60:
            return f"{m}m {s}s"
        h, m = divmod(m, 60)
        return f"{h}h {m}m {s}s"

    def fmt_time(ts_ms):
        """Format timestamp to HH:MM:SS"""
        if not ts_ms:
            return "?"
        return datetime.fromtimestamp(ts_ms/1000).strftime('%H:%M:%S')

    try:
        db_path = '/home/wahaj/.openclaw/tasks/runs.sqlite'
        if not os.path.exists(db_path):
            return {"running": [], "pending": [], "completed": [], "failed": [], "error": "DB not found"}

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Active running tasks (deduplicated by run_id)
        c.execute('''
            SELECT run_id, task, label, status, delivery_status, started_at, terminal_outcome
            FROM task_runs
            WHERE status = 'running' AND delivery_status = 'not_applicable'
            ORDER BY started_at DESC
        ''')
        running = []
        seen_running = set()
        for row in c.fetchall():
            run_id, task, label, status, ds, started, outcome = row
            if run_id in seen_running:
                continue
            seen_running.add(run_id)
            running.append({
                "run_id": run_id,
                "task": task or "",
                "label": label or "Unnamed task",
                "status": outcome or "running",
                "terminal_outcome": outcome or "running",
                "started_at": fmt_time(started),
                "started_at_raw": started,
                "ended_at": None,
                "duration": fmt_duration(started, None),
                "delivery_status": ds
            })

        # Pending delivery tasks (running but not yet delivered)
        c.execute('''
            SELECT run_id, task, label, status, delivery_status, started_at, terminal_outcome
            FROM task_runs
            WHERE status = 'running' AND delivery_status = 'pending'
            ORDER BY started_at DESC
        ''')
        pending = []
        seen_pending = set()
        for row in c.fetchall():
            run_id, task, label, status, ds, started, outcome = row
            if run_id in seen_pending:
                continue
            seen_pending.add(run_id)
            pending.append({
                "run_id": run_id,
                "task": task or "",
                "label": label or "Queued task",
                "status": outcome or "pending",
                "terminal_outcome": outcome or "pending",
                "started_at": fmt_time(started),
                "started_at_raw": started,
                "ended_at": None,
                "duration": fmt_duration(started, None),
                "delivery_status": ds
            })

        # Recently completed (succeeded, deduplicated)
        c.execute('''
            SELECT run_id, task, label, status, started_at, ended_at, terminal_outcome
            FROM task_runs
            WHERE status = 'succeeded' AND delivery_status = 'not_applicable'
            ORDER BY ended_at DESC
            LIMIT 10
        ''')
        completed = []
        seen_comp = set()
        for row in c.fetchall():
            run_id, task, label, status, started, ended, outcome = row
            if run_id in seen_comp:
                continue
            seen_comp.add(run_id)
            completed.append({
                "run_id": run_id,
                "task": task or "",
                "label": label or "Completed task",
                "status": outcome or "done",
                "terminal_outcome": outcome or "done",
                "started_at": fmt_time(started),
                "started_at_raw": started,
                "ended_at": fmt_time(ended),
                "duration": fmt_duration(started, ended)
            })

        # Failed/timed out (deduplicated)
        c.execute('''
            SELECT run_id, task, label, status, started_at, ended_at, terminal_outcome, error
            FROM task_runs
            WHERE status IN ('timed_out', 'failed') AND delivery_status = 'not_applicable'
            ORDER BY ended_at DESC
            LIMIT 10
        ''')
        failed = []
        seen_failed = set()
        for row in c.fetchall():
            run_id, task, label, status, started, ended, outcome, error = row
            if run_id in seen_failed:
                continue
            seen_failed.add(run_id)
            failed.append({
                "run_id": run_id,
                "task": task or "",
                "label": label or "Failed task",
                "status": outcome or "error",
                "terminal_outcome": outcome or "error",
                "started_at": fmt_time(started),
                "started_at_raw": started,
                "ended_at": fmt_time(ended),
                "duration": fmt_duration(started, ended),
                "error": error[:80] if error else None
            })

        conn.close()
        return {"running": running, "pending": pending, "completed": completed, "failed": failed}
    except Exception as e:
        return {"running": [], "pending": [], "completed": [], "failed": [], "error": str(e)}

def get_memory_files():
    """Get list of memory files for View Memory action"""
    memory_files = []
    base_path = '/home/wahaj/.openclaw'
    
    # Memory directory
    mem_dir = os.path.join(base_path, 'memory')
    if os.path.exists(mem_dir):
        for f in sorted(Path(mem_dir).glob('*.md')):
            try:
                with open(f, 'r') as fh:
                    content = fh.read()[:500]  # First 500 chars
                memory_files.append({
                    "path": str(f).replace(base_path, ''),
                    "name": f.name,
                    "preview": content[:200]
                })
            except:
                pass
    
    # MEMORY.md
    mem_md = os.path.join(base_path, 'MEMORY.md')
    if os.path.exists(mem_md):
        try:
            with open(mem_md, 'r') as fh:
                content = fh.read()
            memory_files.append({
                "path": "/MEMORY.md",
                "name": "MEMORY.md",
                "preview": content[:200]
            })
        except:
            pass
    
    return memory_files

# ─── API Handler ──────────────────────────────────────────────────

def collect_all_metrics():
    """Collect all metrics in one call"""
    return {
        "timestamp": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "gateway": get_gateway_status(),
        "services": get_service_health(),
        "system": get_system_metrics(),
        "docker": get_docker_status(),
        "adguard": get_adguard_status(),
        "network": get_network_info(),
        "load": get_load_averages(),
        "activity": activity_log[:20],
        "sessions": get_openclaw_sessions(),
        "memory_files": get_memory_files()
    }

# ─── HTTP Handler ──────────────────────────────────────────────────

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for dashboard"""

    def do_GET(self):
        if self.path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            metrics = collect_all_metrics()
            self.wfile.write(json.dumps(metrics, indent=2).encode())

        elif self.path == '/api/clear-logs':
            global activity_log
            cleared_count = len(activity_log)
            activity_log = []
            log_activity("system", "Activity log cleared by dashboard")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "cleared": cleared_count}).encode())

        elif self.path == '/api/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(get_task_pipeline(), indent=2).encode())

        elif self.path == '/api/service-strip':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(get_service_strip()).encode())

        elif self.path == '/api/memory':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"files": get_memory_files()}, indent=2).encode())

        elif self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/api/clear-logs':
            global activity_log
            activity_log = []
            log_activity("system", "Activity log cleared by dashboard")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Logs cleared"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

# ─── Entry Point ──────────────────────────────────────────────────

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReusableTCPServer(("0.0.0.0", PORT), DashboardHandler) as httpd:
    print(f"🚀 Buck's Dashboard running at http://localhost:{PORT}")
    print(f"   Also accessible from: http://192.168.0.105:{PORT}")
    log_activity("dashboard", f"Dashboard started on port {PORT}")
    httpd.serve_forever()
