# Council V3 — Strategos: Dashboard Re-Review

## What Works Well

- **Health score is now correct** — Tailscale excluded from denominator. Score hits 100 when all installed services alive. No phantom deaths from `not_installed` entries polluting the count.
- **Vignette transitions** — green/yellow/red based on score is solid UX. Not overdone.
- **CRT scanlines** — subtle, atmospheric. Right call.
- **Font stack** — Fira Code / SF Mono is the right aesthetic. Monospace everywhere reinforces the terminal-ops vibe.
- **Task deduplication** — `seen_running` / `seen_pending` / `seen_comp` / `seen_failed` is correct. No more duplicate task entries.
- **Gateway latency display** — `ALIVE (47ms)` in the status panel is genuinely useful.
- **Weakest service** correctly shows `None` when all services are alive.

## ONE Most Critical Issue

**Active count in header is wrong on first load.**

`fetchMetrics()` reads `window._pipelineCache` to compute `activeTasks`, but `fetchPipeline()` (which populates that cache) runs AFTER `fetchMetrics()` on page load. Result: initial render shows `0 ACTIVE` even when tasks are running. Fix: call `fetchPipeline()` first, or `await` it before the first `fetchMetrics()`, or just fetch pipeline data inside `fetchMetrics()` and eliminate the separate polling entirely.

This is a correctness bug, not cosmetic.

## What to Kill

1. **The duplicate `fetchMetrics` function** — there are two `async function fetchMetrics()` definitions in the `<script>` block. The second one wins, the first is dead code. Looks like sloppy merge leftover. Clean it up.

2. **`gateway_uptime` display** — it always shows "Active" or "Unknown" because the ternary always evaluates the truthy path. The actual formatted uptime (e.g., `2h 14m`) computed in Python never makes it to the display. Either wire it properly or remove the uptime field entirely — dead UI is worse than no UI.

3. **`load_avg` element** — referenced in JS but doesn't exist in the HTML. It's a ghost reference.

## What to Add or Improve

1. **Fix initial load ordering** — as noted above. Pipeline data should be fetched before metrics on first load, or merged into a single `/api/all` endpoint that returns everything in one round-trip.

2. **Per-service latency in the health panel** — Gateway shows latency. SSH, DNS, Tailscale don't. Add `latency_ms` to each service check so you can see which is slow before it dies.

3. **AdBlock/DNS stats** — AdGuard panel shows DNS error count from 100 log lines. That's noisy and imprecise. Either wire to actual AdGuard API (port 3000) or remove the metric. At minimum, show query count or blocked count if available.

4. **Panel collapse state** — some panels are always full-width (Activity Log, Agents, Pipeline). Let users collapse sections they don't care about. Small QoL improvement.

5. **Alert log** — failed tasks should surface as a dedicated alert banner at the top, not buried in the Pipeline panel. If something fails, the human should notice immediately.

6. **Disk I/O or network throughput** — currently showing bytes sent/received as raw counters. Show rates (MB/s) or at least format the numbers so they're human-readable (KB/MB/GB).

---

**Bottom line:** It's functionally solid. The four fixes (Tailscale denominator, CRT, fonts, weakest=None) all landed correctly. The remaining issues are minor but concrete: initial load ordering, dead code cleanup, and ghost references. Fix those and it's done.