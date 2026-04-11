# Council V3 — Analyticos Report
**Analyst:** Analyticos | **Date:** 2026-04-11 | **Subject:** Mission Control Dashboard — Second Review

---

## 1. What's Still Misleading or Could Create False Confidence?

### Score hides the panels you see
The health score only tracks 4 services: **gateway, SSH, DNS, Tailscale**. But the dashboard renders **6+ other panels** — Docker containers, AdGuard, Internet connectivity, Disk, CPU/RAM. AdGuard could be 100% dead, all Docker containers crashed, disk at 99% — score stays 100 and header says `NOMINAL` with green vignette. You're flying blind with a green cockpit.

### "not_installed" is silently excluded
Tailscale excluded from denominator when not installed. Fine in isolation. But: what if Tailscale was uninstalled accidentally? What if it's a critical remote access path? The dashboard shows "unknown" for Tailscale but it doesn't flag as a **missing dependency**. A blank is not the same as "intentionally absent."

### Internet = "connected" is too coarse
`internet: connected` only means `8.8.8.8:53` is reachable via TCP. It does NOT mean:
- DNS resolution works for your domains
- Web browsing works
- Tailscale VPN works
- AdGuard can reach upstream DNS
The "connected" green dot creates a false sense that everything network-related is fine.

### DNS check uses TCP port 53
`connect_ex(('127.0.0.1', 53))` — TCP only. Many DNS servers (including AdGuard) listen on UDP 53 primarily. If UDP is broken but TCP port 53 is up, DNS is effectively down. The check passes; DNS is not working.

### Gateway panel — two conflicting signals
`gateway_status` shows `ALIVE (XXms)` when latency is known, but the **Gateway Panel** title has a status dot that's either green (alive) or red (dead) — it never reflects degraded latency. High latency (say 2000ms) still shows a green pulsing dot. "Alive" ≠ "healthy."

### Activity Log is write-side only
The activity log only captures events that `log_activity()` explicitly records. It will never show you a Docker crash, a Python exception, a subagent that silently hung, or a cron that didn't fire. It's a self-reported log, not an objective system trace. You can't use it to detect what you didn't think to log.

---

## 2. What Data Is Still Missing?

| Gap | Why it matters |
|-----|----------------|
| **Per-container Docker health/CPU/memory** | "X running" with names is not health. A container can be "running" but OOM-killed or wedged. |
| **Disk I/O and per-mount usage** | Only `/` tracked. External mounts, Docker volumes, `/home` could all be full without warning. |
| **Docker daemon health** | `docker ps` fails gracefully to `[]` — no distinction between "Docker is down" and "no containers." |
| **AdGuard query volume + block rate** | DNS error count in last 100 logs is noise. Need queries/minute, blocked %, upstream latency. |
| **Network throughput trend (bytes sent/recv over time)** | Single snapshot, no history. Can't spot bandwidth-hogging subagents or leaks. |
| **Gateway child processes / thread count** | No visibility into OpenClaw subprocesses or memory of the gateway process itself. |
| **Scheduled cron jobs and their last run time** | Buck uses cron for heartbeats, reminders, morning reports. No panel shows if they fired. |
| **Companion/node device status** | If nodes (phone apps, companion devices) are paired/down, no visibility. |
| **Pipeline: which agent owns a running task** | Task shows as running but you can't tell which subagent is handling it. |
| **Last data freshness / stale data detection** | `as of HH:MM:SS` is shown but no alert if a panel hasn't updated in N minutes. |
| **RAM per process (OpenClaw gateway, Docker)** | Total RAM shown; gateway RAM growth (memory leak indicator) invisible. |
| **AdGuard upstream DNS actual response time** | Shows "dns10.quad9.net" hardcoded. No actual RTT measurement per query. |

---

## 3. What Assumption Is the Current Design Making That Could Be Wrong?

**The core assumption: "critical services = gateway + ssh + dns + tailscale."**

This omits AdGuard Home (DNS filtering), Docker daemon, and the host's network stack. AdGuard dying is treated the same as AdGuard running fine — it never affects the score.

**Second assumption: "port open = service healthy."**

`connect_ex` on a port returning 0 means the port is accepting connections. It does NOT mean the service is correctly configured, processing requests, or not silently failing. A misconfigured DNS server or a wedged Docker container can still have an open port.

**Third assumption: "not_installed = intentionally absent."**

Tailscale being absent might be a gap, not a preference. The design has no way to distinguish "Tailscale was never installed" from "Tailscale was uninstalled and remote access is now broken."

**Fourth assumption: "8.8.8.8 reachable = full internet connectivity."**

Google DNS being pingable is a narrow check. VPN tunnels, custom DNS routes, corporate firewalls, Tailscale netstack — none of these are tested. A user could have no web browsing but still show "connected."

**Fifth assumption: "the `/status` endpoint returns JSON."**

The uptime-fetching code checks `startswith('{')` but if the endpoint returns an error page or HTML (common for reverse-proxied services), the parse silently fails and `uptime_str` stays None. The code is fragile to API shape changes.

**Sixth assumption: "Docker commands always succeed or fail cleanly."**

`docker ps` returning non-zero exit code with no stderr could mean Docker daemon is down — but the error handling returns `{"containers": [], "error": ...}` and the panel just shows "0 running" with no alert that Docker itself might be dead.

---

## Verdict

The fixes (Tailscale exclusion, CRT overlay, font, weakest=None) are solid. But the dashboard is still primarily a **visibility layer for things that are working**. It has blind spots where things fail: AdGuard, Docker, cron jobs, network path quality, and anything not explicitly checked by `get_service_health()`. The score is optimistic by design — it reflects a narrow definition of "alive," not a definition of "operational."

**The most dangerous false confidence state:** Score 100, green vignette, all panels showing data — while AdGuard is down and cron heartbeats haven't fired in 4 hours.
