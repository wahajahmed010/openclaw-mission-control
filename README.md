# Buck's Mission Control Center 🦌

> A personal homelab project for managing a capable team of AI agents — with a council of 3 LLMs deliberating and improving the system in real time.

---

## What is this?

**Mission Control Center** is Buck's dashboard — a real-time monitoring and management interface for a multi-agent system running on a home server. It monitors system health, tracks agent pipelines, visualizes service status, and provides controls for spawning and managing sub-agents.

The defining feature: **a council of 3 specialized LLMs** that meet periodically to review the dashboard, debate improvements, and stress-test the design. Each council member uses a different model with a different perspective:

| Member | Model | Role |
|--------|-------|------|
| **Strategos** | minimax-m2.7:cloud | Reasoning, planning, risk assessment |
| **Analyticos** | kimi-k2.5:cloud | Analysis, data integrity, stress testing |
| **Creativos** | gemma4:31b-cloud | Creativity, visual design, out-of-the-box thinking |

The council doesn't just advise — it actively critiques every decision, finds blind spots, and forces better answers.

---

## Features

### Real-Time Monitoring
- **System metrics** — CPU, RAM, disk, load average
- **Service Health Strip** — Gateway, SSH, DNS, AdGuard, Docker, Tailscale at a glance
- **Docker containers** — running containers with status
- **Gateway status** — latency + uptime monitoring
- **Network info** — LAN IP, open ports, DNS status

### Agent Pipeline
- **Active Task Pipeline** — running, pending, completed, failed tasks
- **Full task visibility** — prompt, model, duration, timestamps
- **Expandable task rows** — click to see full task description
- **Agent heartbeats** — running agents with state pulses

### Visual Design
- **Mission Control aesthetic** — dark theme, CRT scanline overlay, Fira Code font
- **Color-temperature vignette** — ambient background shifts with system health
- **Agent state animations** — pulsing borders indicate running/idle/completed/error
- **Service Health Strip** — power-bus style horizontal status indicator

### Actions
- **Refresh All** — force refresh all dashboard data
- **Clear Logs** — reset the activity log
- **View Memory** — browse memory files in a modal

---

## Architecture

```
Browser (dashboard)
    ↓ HTTP
Python HTTP Server (dashboard/server.py)
    ↓
├── System metrics (psutil)
├── Docker status (docker CLI)
├── OpenClaw Gateway (curl)
├── SQLite task database (~/.openclaw/tasks/runs.sqlite)
└── Memory files (~/.openclaw/workspace/memory/)
```

### Technology
- **Dashboard** — Python stdlib http.server, vanilla JS, CSS animations
- **Container** — Docker with --network=host for localhost access
- **Data** — SQLite for task history, psutil for system metrics
- **Font** — Fira Code / SF Mono stack (monospace)

---

## Setup

### Prerequisites
- Docker
- Python 3.13+ (for local dev)
- OpenClaw running on the same host

### Running

```bash
# Build and run container
cd dashboard
docker build -t buck-dashboard:latest .
docker run -d \
  --name buck-dashboard \
  --restart unless-stopped \
  --network=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/wahaj/.openclaw:/home/wahaj/.openclaw:ro \
  buck-dashboard:latest
```

**Access:** `http://localhost:8080` or `http://<your-ip>:8080`

### Development

```bash
# Run locally without Docker
cd dashboard
python3 server.py
```

---

## The Council Protocol

When a significant change is needed, Buck spins the council:

1. **Each member reads the current state** — server.py, index.html, recent memory files
2. **Each member debates from their angle** — Strategos on architecture, Analyticos on data integrity, Creativos on visuals
3. **Disagreement is surfaced** — if one member disagrees, they say why
4. **Synthesis** — the findings are combined into actionable priorities

The council prevents:
- Building features that sound good but fail in practice
- Visual changes that are decorative but misleading
- Data that creates false confidence
- Assumption blindness

---

## Project Structure

```
workspace/
├── AGENTS.md          — Workspace management protocol
├── IDENTITY.md       — Buck's persona and thinking protocol
├── SOUL.md           — Buck's soul
├── USER.md           — About the human
├── TOOLS.md          — Local notes and tool config
├── HEARTBEAT.md      — Periodic check reminders
├── dashboard/
│   ├── server.py     — Python HTTP server + all API endpoints
│   ├── index.html    — Dashboard UI (HTML/CSS/JS)
│   ├── Dockerfile    — Container build
│   └── BUILD.md      — Build history
└── memory/
    ├── council-*.md — Council review reports
    ├── scout-findings.md
    └── *.md          — Daily memory and reports
```

---

## Stats

- **Models available:** minimax-m2.7:cloud, kimi-k2.5:cloud, gemma4:31b-cloud, glm-5:cloud
- **Council cadence:** runs on demand, 3-5 minutes per session
- **Dashboard refresh:** 30s polling interval
- **Host:** Dell OptiPlex, Ubuntu 25.10, 6-core i5-8600, 32GB RAM
- **Location:** Frankfurt am Main, Germany

---

*Self-evolving. Always learning. Creative with subagents.*
