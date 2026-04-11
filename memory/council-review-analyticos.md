# Council Review — Analyticos
**Subagent:** Analyticos | **Model:** kimi-k2.5:cloud | **Date:** 2026-04-11

---

## 1. What metric or display is still misleading?

**Gateway Uptime → always shows "Unknown"**
`get_gateway_status()` never returns `uptime_raw` — the field is absent from the returned object. The HTML reads `data.gateway.uptime_raw ? 'Active' : 'Unknown'` and will **always** fall through to 'Unknown', giving the false impression that uptime data isn't available. It should either be populated in the backend or removed from the UI to avoid confusion.

**Gateway Status — latency overwrites the status line**
The gateway panel sets `gateway_status` to `"ALIVE (XXms)"` after the second fetch block, replacing the plain status. This is fine for "alive" — but if the gateway were dead, the latency check would return `null` and the second block wouldn't fire, leaving a stale `"ALIVE"` visible while the dot correctly goes red. The status text and the dot are now logically disconnected.

**Activity Log freshness timestamp is misleading**
`fetchMetrics()` stamps **all** `.freshness` elements with the same `/api/metrics` timestamp. But the activity log is a circular buffer of in-process server events — it has its own independent freshness (it's updated in-memory on every log_activity call). A panel-level timestamp on the activity log implies that log entries were fetched from a data source, which is wrong. The timestamp is accurate for every other panel but actively wrong for the activity log.

---

## 2. What data is still missing that would increase confidence?

- **Gateway actual uptime** — the gateway knows how long it's been running; the dashboard doesn't ask for it
- **Gateway response content check** — a 200 with an empty or malformed body still counts as "alive"; the code checks `result.stdout.strip()` but doesn't validate the response shape
- **Docker container states beyond running** — stopped/paused/exited containers are invisible; the count only shows running
- **Network I/O rates** — `bytes_sent/bytes_recv` are collected but never displayed; raw counters without deltas are meaningless
- **Swap usage** — if RAM fills, swap is the next failure vector; it's not shown
- **Disk I/O / mount-level breakdown** — single `/` partition assumption; `/home` or other mounts are invisible
- **Per-service error detail** — a service being "dead" shows no reason; SSH failing vs. AdGuard failing carry different urgency
- **Historical health score** — one snapshot doesn't show degradation trends; a 10-second health score is noise

---

## 3. What assumption is the current design making that could be wrong?

**Health score weights Tailscale equally with SSH and DNS.**
`not_installed` (Tailscale on a non-Tailscale machine) counts as "not alive" and drags the score down, while simultaneously being treated as a weaker signal than "dead" in the `weakest` selection. This means: (a) a machine without Tailscale installed starts with a maximum achievable score of 75, and (b) if all other services are alive, the weakest will be Tailscale and displayed as a concern — even though it's not installed by design. The score is structurally broken for any machine that doesn't run Tailscale.

**Docker container count implies health without state.**
`container_count` shows "N running" but never reveals whether the right containers are running. `adguardhome` could be stopped and the panel would show `0 running` without distinguishing which service matters vs. which is just absent.

**Latency is measured as curl round-trip time, not gateway processing latency.**
`curl --max-time 3 http://127.0.0.1:18789/` measures full HTTP response time including any internal pipeline processing. A slow gateway (subagent spawn, DB lock) will show high latency that doesn't reflect network or service availability. It's not wrong, but it's labeled "latency_ms" in a context where users will interpret it as round-trip network latency.

---

**Summary verdict:** The three most actionable fixes are (1) exclude `not_installed` from the health score denominator, (2) show a meaningful uptime field or remove the placeholder, and (3) display Docker container states — not just a running count.
