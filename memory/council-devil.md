# 🐃 Council — Devil's Objections
**Dashboard v1 — Adversarial Review**
_Round 1, 2026-04-11_

---

## Objection 1: Kill "Bandwidth" Metrics Entirely

**Verdict: Cut it.**

Getting real bandwidth (upload/download bytes/sec) on a plain Linux box requires either `nload`, `bwm-ng`, parsing `/proc/net/dev`, or嫁给 `vnstat`. None of these are installed by default. If the engineer has to install packages, configure a daemon, and parse a new data source just to show "bandwidth" — that's scope creep on a v1 that was supposed to be a single HTML file with existing tools. The engineer will either hardcode garbage values or spend 3 hours on something that could be a line chart showing bytes/sec for 5 minutes before it floors anyway. **If you can't get it with `cat /proc/net/dev` in 2 commands, it doesn't ship in v1.**

---

## Objection 2: "Quick Action Links" Is a Security Landmine

**Verdict: Dangerous, cut or heavily gate.**

"Quick actions" on a dashboard that anyone who can hit the page can see. If these are actual links to stop containers, restart services, or open UFW logs — you're building a control panel without authentication. This is fine if it's localhost-only, but if it ever becomes accessible over the network (port forwarding, VPN), you've handed anyone a root shell. Either these links do read-only things (open AdGuard admin, open portainer) — in which case they're just browser bookmarks, not a feature — or they do actual actions, in which case you need auth. **Pick one. If it's read-only bookmarks, don't pretend it's a "quick actions" feature.**

---

## Objection 3: Auto-Refresh Every 10 Seconds Will Age Poorly

**Verdict: Make it configurable or drop the frequency.**

10s is aggressive for a server dashboard. CPU and RAM don't change that fast under normal operation. What you'll get is a page that flashes DOM updates every 10 seconds for zero useful information change, burning browser resources and making the page feel jittery. The moment Docker containers start/stop, the whole layout shifts and redraws. **Default should be 30s or 60s. Or better: refresh on visibility change (tab comes into focus). If the user has multiple tabs open, they don't need this thing polling constantly.**

---

## Objection 4: Phase 2 "Historical Graphs" Will Drag You Into Backend Hell

**Verdict: This is how projects die.**

Historical data implies persistence. You'll need:
- A database (SQLite? InfluxDB? Prometheus?)
- A cron job to poll and store
- A graphing library (Chart.js? Recharts?)
- A data retention policy

Suddenly v1's "single HTML file" becomes a system that needs Docker Compose, a volume mount, and maintenance. If the goal is a quick local dashboard that shows you the current state, historical graphs are a completely different project. **Don't call it "Phase 2." Call it "Project: Metrics History" and start it as a separate initiative with its own spec. Mixing it in as a natural "next step" is how you never finish v1.**

---

## Objection 5: AdGuard Stats Might Be a Moving Target

**Verdict: Validate the API before promising it.**

AdGuard Home has an API (`http://localhost:3000/control/stats.txt` or `/api/stats`). But API changes between versions, and some AdGuard setups expose this differently. If AdGuard is running in Docker vs. bare metal, the endpoint might be different. The engineer should be testing the actual AdGuard API right now — not assuming it returns JSON. If it returns plain text or a different format, the whole "AdGuard Stats" panel becomes a research task. **Don't let the spec claim "queries, blocked, ratio" without confirming the API returns those fields in a parseable format.**

---

## Objection 6: SSH "Security" Panel Is Theater

**Verdict: Useless feature.**

Showing "SSH: active" or "last login: user from IP" on a dashboard is noise. SSH being "active" is the default state — of course it's running. The actual security value would be alerting on failed login attempts, new key additions, or unusual source IPs. But that would require parsing `auth.log` or setting up `fail2ban` integration, which is another rabbit hole. **A panel that shows "SSH: active ✓" tells the user nothing they don't already know. Cut it. If you want real SSH security monitoring, that's a separate alerting system, not a dashboard widget.**

---

## Objection 7: "Load" Average Without Context Is Misleading

**Verdict: Context required or cut it.**

Showing "Load: 1.42" means nothing to a non-technical user. On a 4-core machine, 1.42 is fine. On a 1-core machine, it's a problem. If you show load, you need to show it relative to core count, or show per-core breakdown. Otherwise you're just displaying a number that will cause anxiety without information. **If CPU % and core count are already shown, load average is redundant. If you keep it, normalize it: "Load: 1.42 / 4 cores" so it's immediately readable.**

---

## Objection 8: Phase 2 "Mobile Layout" Is a Trap

**Verdict: Defers the hard work with a false promise.**

Adding "mobile layout" to a dashboard that's supposed to be a quick terminal-style single-page tool is how you go from 1 day of work to 1 week. Mobile layout means:
- Responsive CSS breakpoints
- Touch-friendly targets
- Possibly a hamburger menu or collapsed panels
- Testing on real devices

And for what? A local server dashboard that will be viewed on a phone occasionally. The user is sitting at their desk. They're not managing their server from a phone in bed. **Mobile layout is a nice-to-have that will be promised in Phase 2 and never actually built. If the designer wants to do it, they can do it in v1 as a nice touch — but don't put it in the spec as a Phase 2 deliverable. That's how you write a spec that's never finished.**

---

## Summary: What Ships in v1

| Feature | Verdict |
|---|---|
| System Overview (CPU%, RAM%, Disk%, Uptime) | ✅ Keep |
| Docker Status (count + list) | ✅ Keep |
| Network (LAN IP, open ports) | ✅ Keep — but DROP bandwidth |
| AdGuard Stats | ⚠️ Keep — validate API first |
| Security (UFW status, SSH) | ⚠️ UFW status OK, SSH panel = cut |
| Quick actions | 🔒 Read-only bookmarks only, or cut |
| Auto-refresh | ✅ 30s default, not 10s |
| Historical graphs | 🚫 Cut from this project entirely |
| Mobile layout | 🚫 Don't spec it as Phase 2 |
| Authentication | ⏸️ Not needed if localhost-only |

**Core v1 is 4 panels + Docker. Everything else is fighting for attention on a 10-second refresh cycle nobody asked for.**
