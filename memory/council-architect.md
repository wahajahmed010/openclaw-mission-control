# Council: Architect's Analysis
## Turning the Dashboard into a Mission Control Center
**Role:** Systems Architect | **Date:** 2026-04-11

---

## Core Principle: Tiered Information Architecture

A mission control doesn't show everything — it surfaces what needs eyes now and archives what doesn't. Information has three tiers:

1. **CRITICAL** — Requires immediate human action. No ambient data here.
2. **IMPORTANT** — Worth watching, not urgent. Trends matter.
3. **AMBIENT** — Context and history. Informs but doesn't demand.

---

## 10 Concrete Proposals

### 1. Agent Health Grid (CRITICAL)
**What:** Live status panel showing every subagent — alive, working, stalled, dead.
**Why it matters:** A stalled agent silently failing is worse than a crashed service. You need to see at a glance which agents are actively working vs. idle vs. hung. This is the **house lights** panel — if everything is green, mission nominal. If something is red, eyes on it.
**Implementation:** heartbeat-state.json becomes a live grid. Add: last-task-start timestamp, task description, restart count.

---

### 2. System Resource Timeline (IMPORTANT → CRITICAL when spiked)
**What:** CPU, RAM, disk I/O plotted as a rolling 24h line. Not a snapshot — a trend.
**Why it matters:** Reactive "disk full" debugging is a bad look. A trendline showing disk growing at 1GB/hour 6 hours before crash is actionable. Same for RAM leaks creeping up over days.
**Action threshold:** Alert (not just show) when any resource exceeds 80% for >5 min.

---

### 3. Scheduled Jobs Monitor (IMPORTANT)
**What:** Visual list of all cron jobs — last run time, next run time, duration, exit code.
**Why it matters:** Scheduled jobs that silently fail are a class of failure that almost never surfaces until it's a problem. This is the **night shift** panel — it's watching the things that run when no one's looking.
**Bonus:** Flag jobs that have **never run** (misconfigured) vs. jobs that **missed their last window**.

---

### 4. Service Health Strip (CRITICAL)
**What:** A single horizontal strip — OpenClaw gateway, Tailscale, any SSH tunnels, cloud backups, anything that's a dependency. Green/Yellow/Red.
**Why it matters:** When the dashboard itself is the mission control, you need to know if the *monitoring* infrastructure is healthy. If Tailscale is down, your agent is still running but you can't reach it.
**This is the "are we even connected" check.**

---

### 5. Event Feed (Ambient / Forensic)
**What:** A scrolling, timestamped log of significant events: agent spawns, agent deaths, errors, file modifications, external API calls, message volumes.
**Why it matters:** When something goes wrong, you need to reconstruct what happened. A mission control without an event log is a car without a black box. Keep last 1000 events, searchable.
**Distinguish by type:** ERROR (red), WARNING (yellow), INFO (blue), AGENT (purple — make it pop).

---

### 6. Storage Breakdown by Category (IMPORTANT)
**What:** Pie/ring chart: how much space used by logs vs. memory files vs. workspace vs. agent state vs. skills.
**Why it matters:** "Disk at 90%" is useless without knowing *what* filled it. A 2GB log file is deletable. 2GB of agent memory is not. Knowing the composition changes the response.
**Add trend:** Show which category grew most in the last 7 days.

---

### 7. Communication Volume Chart (IMPORTANT — trending)
**What:** Messages handled per hour, per channel (Telegram, Discord, etc.), over a 7-day window.
**Why it matters:** A sudden spike in message volume can indicate a problem (spam, bot abuse) or an opportunity (engagement). A sudden drop can indicate a connectivity issue your human hasn't noticed yet.
**This is the "is the outside world reaching us" sensor.**

---

### 8. Active Task Pipeline (IMPORTANT)
**What:** What Buck is currently doing, queued next, and what just completed. Like a build pipeline but for cognitive work.
**Why it matters:** In a multi-agent system, tasks need to be serialized, prioritized, and tracked. If 3 subagents are working on 3 things, what are they? Which is blocking which?
**Actions possible from dashboard:** Cancel a running task, reprioritize queue, re-spawn a failed step.

---

### 9. Secrets / Credential Health (CRITICAL)
**What:** Which external services have valid auth tokens, which are expiring, which have failed.
**Why it matters:** An expired Telegram token silently breaks your bot with no error shown anywhere. A failed ElevenLabs auth silently breaks voice. This is the **dependency trust** panel — verify everything can talk to everything it needs to.
**Show:** Last successful API call per service, last failure, token expiry countdown if available.

---

### 10. Historical Uptime Ledger (Ambient → Important for reporting)
**What:** % uptime per day for the past 30 days, broken down by subsystem (gateway, agents, external APIs).
**Why it matters:** For personal use this is mostly vanity. But for system reliability over time, you want to see patterns — "every Sunday at 3am the gateway restarts" is the kind of thing you'd never catch without this.
**Make it a simple heatmap calendar.**

---

## Summary: What Makes This Actually Mission Control

| Tier | What to show |
|------|-------------|
| **CRITICAL** | Agent health, service strip, secrets health |
| **IMPORTANT** | Resources, cron jobs, task pipeline, comms volume |
| **AMBIENT** | Event feed, storage breakdown, uptime ledger |

**The test:** If you had to run this dashboard on a 5" phone screen, what do you put on that screen? Answer: Tier 1 only. That's your mission control. Everything else is available on demand.

**Actions from dashboard worth adding:**
- Kill / restart a specific agent
- Force-refresh a health check
- Clear a log file
- Trigger a manual cron run (with confirmation)
- Broadcast a test message to all channels

---
*Architect — Council Session 2026-04-11*
