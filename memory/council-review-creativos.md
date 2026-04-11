# Council Review — Creativos
**Subject:** Mission Control Dashboard (Post-Fix Re-Review)
**Date:** 2026-04-11
**Verdict:** Solid bones. Functional. But it still looks like a *website pretending* to be a dashboard. Here's what's missing and what to fix.

---

## 1. What visual element would make this feel like a real mission control?

**A live telemetry event ticker.** Not the activity log — a real-time *event stream* that scrolls like a trading floor or NASA flight control. Every state change, every ping, every agent spawn should punch through as a timestamped event with color-coded severity.

Right now the activity log is a static scrollable list. Boring. A mission control ticker breathes — it shows you the system is *alive* and *responding*, not just displaying static data someone refreshed.

---

## 2. What looks amateurish or cheap that should be improved?

- **`Courier New` as the font.** This is the single most "amateur dashboard" signal you can send. It says "I made this in Notepad." Switch to `JetBrains Mono` or `IBM Plex Mono` from Google Fonts. Costs nothing, transforms everything.

- **The "Loading..." states are jarring.** "Loading pipeline data..." and "Loading agents..." in plain gray text against a black background looks like a broken page, not a live system waiting for data. Use pulsing dots or skeleton shimmer panels.

- **The panels are visually disconnected islands.** No shared visual logic, no unified glow hierarchy. When everything lights up green on hover, it feels like a generic Bootstrap card. Mission control panels share a *coat of arms* — a family resemblance through consistent accent treatment.

- **The freshness timestamps** ("as of 20:06:12") are a great addition but they're buried and tiny. Make them part of the panel header aesthetic — right-aligned, monospace, same color as the border accent.

---

## 3. What ONE visual change would have the most impact?

**Add a subtle CRT/scanline overlay + bloom glow on text.** Just a CSS effect — faint horizontal scanlines over the entire viewport + a slight text-shadow bloom on bright elements (the green numbers, the cyan panel titles). This is the psychological switch that flips "website" to "terminal." It says: *this is a live operations interface, not a webpage.*

Specifically:
- Scanlines: `background: repeating-linear-gradient` at ~2px intervals, 3-5% opacity
- Text bloom: `text-shadow: 0 0 8px currentColor` on `.metric-value`, `.big-number`, `.panel-title`
- Optional: slight `border-radius: 2px` micro-chamfer on panels instead of the soft 8px — sharper = more ops-center

That's it. One CSS layer. Changes everything.

---

## Summary

| # | Item | Priority |
|---|------|----------|
| 1 | Live telemetry ticker (not static log) | Medium |
| 2 | Replace Courier New with JetBrains Mono | High |
| 3 | Fix "Loading..." state presentation | Medium |
| 4 | CRT scanline + bloom glow | **Critical** |

One change: **CRT overlay + text bloom.** Do that first. Everything else falls into place around it.
