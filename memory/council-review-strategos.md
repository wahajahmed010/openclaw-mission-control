# Council Review: Strategos — Mission Control Dashboard

**Date:** 2026-04-11
**Review:** Post-design-fix re-audit of dashboard/server.py + dashboard/index.html

---

## 1. ONE Most Critical Information Architecture Issue

**The health score conflates two distinct domains without separation.**

The vignette color, health status text, and score all mix:
- OpenClaw infrastructure health (gateway alive/dead, sessions)
- Generic system services (SSH, DNS, Tailscale)
- Docker/AdGuard container state

This means: "NOMINAL" can be true while your OpenClaw agents are hung or the task pipeline is broken. The health score measures the wrong thing for a dashboard whose persona is "Buck's Mission Control." It tells you if port 22 is open, not if the mission is succeeding.

The gateway latency display is also ambiguous — it now appends `(XXXms)` directly to the status word "ALIVE", making the label `gateway_status` element look like "ALIVE (47ms)" which reads like a status + metric mashup, not a clean label/value separation.

---

## 2. What to Kill

1. **AdGuard DNS Errors (100 logs)** — Raw log tail count is meaningless without baseline. Shows an integer with no context. Either show query volume + block rate (real metrics) or kill the panel entirely.

2. **Load averages in header** (`X/Y/Z` in a status strip) — The System panel already shows load_1m in context with CPU cores and a chart. The header version is redundant noise.

3. **Gateway Uptime → "Active"** — The backend returns `uptime_raw` as null/undefined, so it always shows "Unknown" or "Active." Dead UI element. Either wire it up properly or remove the row.

---

## 3. The ONE Thing to Improve

**Separate "System Health" from "Mission Health."**

The vignette and score should answer: *"Is Buck's work getting done?"*

Add a distinct `mission_score` (0-100) alongside the existing `services.score`:
- Active agents running vs. expected
- Tasks in pipeline (running + pending vs. completed recently)
- Session continuity

Keep `services.score` as a secondary indicator for infrastructure. Then the header becomes genuinely useful — you glance at it and immediately know if the human's work is progressing or stalled, not whether port 53 is responding.

This is the single change that makes the dashboard earn its "Mission Control" title.

---

**Verdict:** Solid foundation. The data collection is thorough. The rendering is clean and responsive. The gap is semantic — it looks like a health monitor but actually measures the wrong things for its name.
