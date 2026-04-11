# Engineer — Dashboard Task

Read SPEC.md first.

## Your Job
Make the dashboard live. You own the data layer and logic.

## Deliverables

1. **scripts/metrics.sh** — Shell script that outputs all metrics as JSON
   ```bash
   # Must output valid JSON to stdout
   # Include: cpu, ram (used/total), disk (used/total), uptime, load (1m,5m,15m)
   # Docker: running_containers, container_list (name + status for each)
   # Network: lan_ip, active_connections, bandwidth_rx, bandwidth_tx
   # AdGuard: queries_today, blocked_today, block_ratio
   # Security: ufw_status, open_ports
   ```
   Save to: `/home/wahaj/.openclaw/workspace/dashboard/scripts/metrics.sh`

2. **js/dashboard.js** — JavaScript to fetch and update metrics
   - Fetch `metrics.sh` output (or hardcoded simulation for now)
   - Parse JSON and update DOM elements by ID
   - Auto-refresh every 10 seconds
   - Handle errors gracefully (show "—" on failure)
   - Save to: `/home/wahaj/.openclaw/workspace/dashboard/js/dashboard.js`

3. **Wire up index.html** — If Designer hasn't created it yet, create a basic version with:
   - Proper `<script>` and `<style>` tags
   - All the panel IDs that dashboard.js will target
   - Refresh indicator

## Testing
- Run `bash scripts/metrics.sh` and verify JSON output
- Check the JSON is valid
- Test that dashboard.js updates the DOM correctly

## Context for commands
```bash
# CPU/RAM/Uptime/Load
top -bn1 | head -5
free -m
uptime
cat /proc/loadavg

# Docker
docker ps --format "{{.Names}}|{{.Status}}"

# Network
ip addr show | grep "inet "  # LAN IP
ss -tun | wc -l              # connection count
# Bandwidth: parse /proc/net/dev

# AdGuard Home API (if running)
curl -s http://localhost:3000/stats/querylog/count 2>/dev/null || echo '{"queries":0,"blocked":0}'
# Or use: curl -s http://localhost:3000/stats/today

# UFW
ufw status verbose
```

## Important
- Make metrics.sh work even if some services are down
- Always output valid JSON even on error (use fallback values)
- Comment your code

## Place to save files
- `/home/wahaj/.openclaw/workspace/dashboard/scripts/metrics.sh`
- `/home/wahaj/.openclaw/workspace/dashboard/js/dashboard.js`

Start now. Save your work to those paths.
