# Creativos — Council Position
**Model:** gemma4:31b-cloud

## Domain Patterns to Steal

1. **Bloomberg Terminal** — dense, information-first. No decorative chrome. Every pixel earns its place.
2. **NASA Mission Control** — status strips at top, critical info front-center, ambient awareness through color zones.
3. **SOC (Security Operations)** — alert severity hierarchy through color temperature, not just labels.
4. **Trading floor** — the "something feels wrong" sense comes from ambient cues before any specific alert fires.

## The Obvious Trap

**Auto-refresh dashboards.** They create jitter, burn resources, and train you to ignore the screen. The moment everything flashes red simultaneously (because multiple things happened at once), you've learned to distrust the dashboard. A "pull to refresh" or "refresh on focus" model is more honest about information freshness.

## Non-Obvious Data Source

**Cron job history / scheduled task patterns.** Most dashboards monitor "now." But the most predictive data is "what was supposed to run vs what actually ran?" Missed cron jobs in the last 24h are an early warning system for system drift.

## What Makes This Different

The question isn't "what does this dashboard show?" It's "what does this dashboard *feel like*?" If it feels like a website with metrics, you've failed. If it feels like you're sitting at a live operations center — calm, ordered, in control — then it works.

---

## Specific Ideas (from creative synthesis)

1. **Chyron ticker** — scrolling live event feed at top edge, color-coded [OK]/[WARN]/[CRIT]
2. **Radial gauge cluster** — like cockpit instruments, needle animates smoothly to convey rate of change
3. **Blinking border pulses** — peripheral vision reads agent state without looking directly
4. **Color-temperature zones** — background shifts from cool blue (healthy) to amber (warning) to red (critical)
5. **Connection topology map** — animated particles on lines showing agent relationships
6. **CRT scanline overlay** — subtle, 3% opacity, psychological "live feed" framing
7. **Priority stack** — spatial depth = urgency hierarchy
8. **Heatmap grid** — 24h activity density like GitHub contributions
9. **Alert toasts with screen-edge flash** — theatrical entry, clean exit
10. **Ambient particle field** — density/speed reflects system load

**Core philosophy:** The dashboard should feel like watching Earth from orbit. Calm and ordered until it isn't.
