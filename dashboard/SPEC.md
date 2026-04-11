# Dashboard Spec — Buck's Home Lab Command Center

## Purpose
Single-page dashboard for Wahaj to monitor his home lab at a glance.

## System Context
- **Host:** Dell OptiPlex, Ubuntu 25.10, 14GB RAM (upgrading to 32GB)
- **IP:** 192.168.0.105 (LAN)
- **Services:** AdGuard Home (port 3000), Docker
- **Security:** UFW firewall, SSH restricted to LAN

## Dashboard Must-Haves

### 1. System Overview Panel
- CPU usage (current % + graph)
- RAM usage (used/total GB + %)
- Disk usage (root volume)
- Uptime
- Load average (1m, 5m, 15m)

### 2. Docker Status Panel
- Running containers count
- List of running containers with status
- Total CPU/memory used by Docker

### 3. Network Panel
- LAN IP address
- Active connections count
- Bandwidth (RX/TX)

### 4. AdGuard Home Stats
- DNS queries today
- Blocked today
- Block ratio %

### 5. Security Status Panel
- Firewall (UFW) status: active/inactive
- SSH allowed IPs
- Open ports list

### 6. Quick Actions (links)
- AdGuard Admin → http://192.168.0.105:3000
- OpenClaw Gateway

## Tech Stack
- Single HTML file with vanilla JS
- Fetch data from shell commands or API endpoints
- Auto-refresh every 10 seconds
- Dark theme (matches terminal/hacker aesthetic)

## Design Direction
- Dark mode, monospace font, terminal-inspired
- Color accents: green (good), amber (warning), red (alert)
- Minimal, information-dense, no fluff

## Out of Scope (for v1)
- Historical graphs (just current values)
- Authentication (internal network only)
- Mobile optimization
