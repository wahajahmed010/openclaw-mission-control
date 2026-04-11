# Strategos — Council Position
## Mission Control Dashboard & Agent System Design
**Date:** 2026-04-11

---

## Preliminary Assessment

I've read all four council positions. Architect has rigor. Devil has skepticism worth listening to. Futurist is dreaming in color. Visualist is making it pretty. None of them are wrong. None of them are fully right. Here's where I push back.

---

## 1. The ONE Most Critical Feature Missing

**Active Task Pipeline is the spine. Nobody has made it load-bearing enough.**

Architect mentions it (#8) and calls it IMPORTANT. Devil correctly flags scope creep everywhere else but doesn't touch this. Futurist's "neural map" is a prettier version of the same thing. Visualist's "priority stack" is a cosmetic layer on top.

But here's the problem: **every other panel is theater without task pipeline visibility.**

You can show me a green Agent Health Grid, a beautiful radial gauge cluster, a live event feed with color-coded entries — and Buck could be stuck in a loop, two subagents deadlocked on the same file, a task queue 40 deep with no one working it. I'd have no way to know from those panels alone.

The single most important thing to know at any moment: **what is working, what is queued, what is blocked, what failed.**

Everything else is nice-to-have context. Task state is the signal.

---

## 2. The Biggest Risk in the Current Architecture

**The data sources are unverified. The entire dashboard is built on assumptions.**

Devil flagged AdGuard API validation — correct, but that's one example of a systemic problem. The healthcheck skill, agent heartbeat-state, system metrics (CPU/RAM/disk), Docker stats, cron job status — none of these have been confirmed as stable, parseable, and accessible from a single entry point.

The risk isn't the design. The risk is that you build a beautiful Mission Control Center and then discover:
- `heartbeat-state.json` doesn't have the fields the Architect's spec assumes
- The cron job that polls metrics doesn't exist yet
- The system metrics require a daemon that isn't installed
- The " Secrets Health" panel requires API keys that aren't configured

**Every panel in the Architect's spec is a promise that requires a data contract.** Those contracts don't exist yet. You are designing a dashboard for systems that haven't been instrumented yet.

The biggest risk: treating v1 as "build the UI, the data will follow." It won't. The data infrastructure has to come first, or you're painting a beautiful facade on an empty building.

---

## 3. Three Things to Build in the Next Session

**Priority 1: Define and instrument the data contracts.**
Before any dashboard UI: define what data each panel needs, verify it exists in accessible form, and build the collection layer if it doesn't. This means:
- `heartbeat-state.json` schema confirmed — what fields exist, what's missing
- System metrics collection — what command gives you CPU/RAM/disk in a parseable format
- Cron job status — how do you programmatically query "did this job run, did it succeed"
- Docker container state — confirmed accessible without root

This is not glamorous. It is the only foundation the rest of the work stands on.

**Priority 2: Task Pipeline visibility — the actual working state of Buck's mind.**
The Active Task Pipeline is the most important panel. Build this with minimal UI first: a list of running agents, their status, what they're blocked by, what's queued next. No radial gauges, no particle fields. A text table with color-coded status. Prove the data flows first, then make it pretty.

**Priority 3: Secrets and Credential Health — silent failures are the worst failures.**
The Architect is right to call this CRITICAL. An expired Telegram token, a failed ElevenLabs auth, an AdGuard API that's silently returning errors — these break the assistant without any visible crash. Build the credential health panel first among the "infrastructure" panels. If you can only see one thing besides task state, see this.

---

## 4. The Assumption Everyone Is Making That I Think Is Wrong

**That v1 can be a single HTML file with existing tools.**

Devil attacks the historical graphs ("will drag you into backend hell") — correct. But the implicit assumption everyone is making is that the path to a shipped v1 is: pick a frontend, wire it to existing shell commands, done.

This is wrong because **the data layer doesn't exist yet in the form the dashboard needs.** You can't just `cat /proc/meminfo` your way to a Mission Control. The Architect's spec requires:
- A live agent heartbeat tracker with structured JSON
- Cron job state persistence (not just "did it run" but "last 10 runs with exit codes")
- Credential health polling with expiry tracking
- A structured event log with searchable history

These aren't commands you run once. They're services that run continuously and maintain state. That is a backend. Not a full database — SQLite handles it fine — but a backend nonetheless.

**The assumption that v1 is a pure frontend project is how the Futurist's concern becomes real.** "Historical graphs will drag you into backend hell" is true IF you try to add them later. But if you plan for a minimal backend from the start (SQLite + a few collection scripts), v2's "historical data" is just querying the same database with a time filter.

Design for the backend you know you'll need, even in v1. The cost of adding it later is 10x.

---

## Where I Agree — And Where I Push Back

**Agree with Architect:** Tiered information architecture (Critical/Important/Ambient) is the right mental model. Ship it.

**Agree with Devil:** Cut bandwidth. Cut SSH theater panel. 30s refresh, not 10s. Validate APIs before promising them. These are correct calls.

**Agree with Visualist:** The theatrical elements (scanlines, ambient particles, blinking borders) are v2 polish, not v1 scope. BUT — the radial gauge for the single health score headline metric is worth doing in v1 if data contract is simple. It communicates state faster than a number.

**Agree with Futurist:** The vision is right. The timing is wrong. Neural map, voice control, gesture UI — these are the reasons to build the foundation well. Don't skip to chapter 10 because it looks cool. But let the Futurist's list be the 6-month roadmap, not the backlog.

---

## Summary Position

| Question | Strategos Says |
|---|---|
| Most critical missing feature | Active Task Pipeline — know what Buck is actually doing |
| Biggest architectural risk | Unverified data contracts — building on assumptions |
| Top 3 builds | (1) Data contracts + instrumentation, (2) Task pipeline, (3) Secrets health |
| Everyone's wrong assumption | That v1 is a pure frontend project — a minimal backend is required |

Build the spine first. Everything else is muscle and skin.

---

*Strategos — Council Session 2026-04-11*
*3 minutes. Direct. Done.*
