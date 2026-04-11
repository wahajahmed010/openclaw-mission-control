# Designer — Dashboard Task

Read SPEC.md first.

## Your Job
Make the dashboard beautiful. You own the visual layer.

## Deliverables

1. **index.html** — Full single-page dashboard
   - Dark terminal-inspired theme (black/dark-gray background)
   - Font: JetBrains Mono or Fira Code (Google Fonts)
   - Grid layout: 2-3 column responsive grid for panels
   - Each panel should be a card with subtle border/shadow

2. **Style requirements:**
   - Color palette: bg #0d1117, cards #161b22, borders #30363d
   - Text: #c9d1d9 (muted), #f0f6fc (bright)
   - Accent: #58a6ff (links), #3fb950 (good), #f0883e (warn), #f85149 (bad)
   - Smooth transitions on hover
   - No external CSS frameworks (vanilla only)

3. **Panels to include (matching SPEC.md):**
   - System Overview (CPU, RAM, Disk, Uptime, Load)
   - Docker Status (container count + list)
   - Network Info (IP, connections, bandwidth)
   - AdGuard Stats (queries, blocked, ratio)
   - Security Status (UFW, SSH, ports)

4. **Layout:**
   - Header with machine name + refresh indicator
   - 2-column grid on desktop, 1-column on mobile
   - Each panel has a title + live data area
   - Footer with last-updated timestamp

5. **Interactions:**
   - Auto-refresh every 10 seconds
   - Subtle pulse animation when refreshing
   - Panels should show "—" while loading

## Important
- Do NOT hardcode dynamic values (CPU %, RAM %, etc.)
- Just put placeholder spans like `{{cpu}}`, `{{ram}}` — Engineer will wire them up
- Or use IDs that Engineer will target with JS

## Place to save files
`/home/wahaj/.openclaw/workspace/dashboard/index.html`

Start now. Save your work to that path.
