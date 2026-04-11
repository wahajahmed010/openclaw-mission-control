# Council Design Review — Strategos
**Target:** Buck's Dashboard (server.py + index.html)
**Lens:** Information Architecture — hierarchy, priority, flow, signal-to-noise

---

## 1. What's Wrong (Identification)

### The Big ASCII Header Is Destructive
The massive ASCII art banner consumes the top 20-25% of the viewport with pure decoration. Nothing in it communicates operational state. On any laptop or smaller screen, the first thing a user sees is Buck's name rendered in green — not a single data point. This is the most visible element on the page by visual weight, and it conveys zero information.

### No System Health Overview
There is no single "is this system healthy?" signal at the top. A vignette effect changes color based on a services score, but:
- It requires the user to understand what the color means
- It's ambient/decorative, not a panel
- The score itself is never displayed numerically
The user must scan every single panel to assess system state. This is the core failure.

### Visual Hierarchy Is Inverted
The layout is a flat grid. The top row shows: System (CPU/RAM), Gateway, Docker, AdGuard. These are infrastructure metrics — not the most critical information. The most critical information — **what tasks are running, what agents are doing, what's failed** — is in panels near the bottom of the page.

For a personal assistant dashboard, the priority should be:
1. What is Buck doing right now? (agents + pipeline)
2. Is anything broken? (health score, errors, failed tasks)
3. How is the host behaving? (CPU, RAM, disk)

The current order puts #3 first and #1 last.

### Activity Log and Agents Panel Are Redundant
The "Active Agents" panel maps sessions data. The "Activity Log" also displays system events. But `gateway_uptime` in the Gateway panel just says "Active" — not an actual duration. Sessions count is shown in Gateway, but agent status is shown in Active Agents. The Docker panel shows container count as a number — not which containers or their states. These should be consolidated or the redundancy removed.

### Static Fake Data Is Noise
`AdGuard Home` → "Upstream DNS: dns10.quad9.net" is a hardcoded string, not live data. It's in the dashboard as if it's being monitored, but it's not. This creates false confidence.

### Docker Panel Is Almost Useless
It shows `Containers: X running` with no names, no images, no states. Compare to what it could show: which containers are present, which are unhealthy, memory/CPU per container.

### Task Pipeline Is Underemphasized
The pipeline is arguably the most operationally important panel — it shows what Buck is actively doing. It's in a `full-width` panel at the bottom, below Activity Log. This placement signals it's not primary information.

---

## 2. The ONE Change That Would Most Improve Communication

**Add a Health Score + Status Banner at the very top.**

Replace the ASCII header with a slim status bar that shows:
- System status: `ALL SYSTEMS NOMINAL` / `WARNINGS DETECTED` / `ISSUES FOUND`
- Numerical health score: `Score: 100/100`
- Quick alerts: `1 agent running | 0 failed | 2 containers healthy`

This single change transforms the dashboard from "decorated data grid" to "operational overview." Everything else follows from having a clear top-level status.

---

## 3. Redundant / Low-Value Data to Remove

| Item | Why Remove or Change |
|---|---|
| ASCII art banner | Decoration, costs 20% of viewport, communicates nothing |
| `{{cpu_count}} Cores` label | Static, not actionable, wastes panel space |
| `Gateway Uptime: Active` | "Active" is not uptime. Either show real duration or remove this line. |
| `Disk: Used X GB / Free Y GB` | The percentage + progress bar already conveys this. The GB numbers are redundant. |
| `AdGuard Upstream DNS` static string | Fake data — hardcoded, not live. Either pull real config or remove. |
| `DNS Errors (100 logs)` label | `dns_errors_100 logs` is a confusing key name. More importantly: show the error *rate* or trend, not a raw count from a 100-log window. |

---

## 4. Data Flow Assessment

```
Raw Data (psutil, SQLite, docker CLI, subprocess)
    → collect_all_metrics() — server-side aggregation ✓
    → /api/metrics JSON response
    → fetchMetrics() — client-side injection into DOM
```

The data pipeline itself is sound. The problem is after the data arrives in the browser: **injection is unselective**. All metrics are shown all the time regardless of severity. There's no conditional rendering — no emphasis on anomalies, no suppression of nominal data.

**Specific flow gaps:**
- Failed tasks don't get visual priority over completed tasks in the pipeline panel (both are equal-weight sections)
- No threshold alerting — if disk hits 95%, the panel turns green (no visual change from 50%)
- Agent status dot pulses for all agents — running and idle both pulse (idle should be static)

---

## Summary Scores

| Dimension | Rating | Notes |
|---|---|---|
| Priority hierarchy | ⚠️ Weak | Infrastructure over operations — inverted |
| Signal-to-noise | ⚠️ Low | ASCII art, static fake data, redundant metrics |
| At-a-glance comprehension | ❌ Poor | No top-level health signal |
| Information density | ⚠️ Medium | Right amount of data, wrong presentation order |
| Actionability | ⚠️ Limited | Refresh/Clear/View Memory — no alerting or intervention |

**Bottom line:** The data is there. The architecture of collecting and serving it is fine. The failure is in presentation priority — decorative elements crowd out operational ones, and there's no top-level status summary. Fix the header and add a health banner, and the dashboard becomes genuinely useful.
