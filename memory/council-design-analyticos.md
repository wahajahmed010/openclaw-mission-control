# Analyticos — Design Review: Data Integrity & Clarity
**Model:** kimi-k2.5:cloud

## Most Misleading Display

**The health score (services.score = 75).**

A single number that aggregates DNS, SSH, Gateway, Tailscale into one score. But what does 75 actually mean? Which service is at 25? A user seeing 75 has no idea if it's DNS failing or Tailscale being absent. The score smooths over the one thing that might actually be broken.

**Verdict:** The score is useful for at-a-glance trending, but it should be accompanied by the lowest-scoring service explicitly labeled. "Score: 75 — DNS is the weak link."

---

## Information Pattern That Creates False Confidence

**"Gateway: alive" status.**

This tells you the gateway process is responding to a curl request. It does NOT tell you:
- Whether it's processing messages correctly
- Whether Telegram is connected
- Whether agents are spawning properly
- Whether the session store is functioning

A gateway that responds "alive" but can't route messages is functionally dead. The status indicator says alive. The user trusts it. It's lying.

**Verdict:** "Alive" is a green dot that means almost nothing. At minimum, show latency (how fast does it respond?) and a timestamp of last successful communication.

---

## What Should Be Labeled or Annotated That Isn't

1. **CPU percentage without context.** "CPU: 8%" means nothing without knowing load average and core count. A 8% CPU on a 6-core machine under normal load is fine. But there's no load average shown, so you can't tell.

2. **Memory in bytes without conversion.** `mem_used: 8589934592` is technically correct but practically useless. Show GB with 1 decimal. Show percentage. Show available.

3. **Disk "Used: X / Y" without context.** Without knowing what the partition is for, whether it's system or data, and what the growth rate is — "90% full" could be urgent or could be normal.

4. **Activity log with no timestamps.** Events fire, but the log shows relative positions, not absolute times. "When did that error actually happen?" Can't answer from the dashboard.

5. **No indication of data freshness.** When was each metric last updated? If the dashboard is polling every 30s and one metric hasn't changed in 10 minutes — is that because nothing changed, or because the collection broke?

---

## Summary

| Problem | Impact | Fix |
|---------|--------|-----|
| Health score hides the weak link | User trusts score, misses failing service | Show score + lowest service explicitly |
| "Alive" = responsive, not functional | False confidence in gateway health | Show latency + last comms timestamp |
| CPU without load average | Can't assess if system is actually busy | Add load average |
| Memory in raw bytes | Unreadable at a glance | Convert to GB + % |
| No data freshness indicators | Can't tell if metric collection broke | Show "as of HH:MM:SS" per metric |

**Core principle:** Every metric should answer "is this actually working right now?" not just "does this number exist?"
