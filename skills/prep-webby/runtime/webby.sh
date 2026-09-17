#!/bin/zsh
# WEBBY — full Jarvis demo startup. Spins up Friday, the cue server, and Agent Club,
# pre-warms the Chrome tabs, then waits for your line + Enter to fire the briefing.

step() { printf "\033[36m▸ %s\033[0m\n" "$1"; }
ok()   { printf "  \033[32m✓ %s\033[0m\n" "$1"; }

step "Friday (the assistant)"
curl -s -m1 -o /dev/null http://127.0.0.1:8794/stage.html || (cd ~/friday && nohup python3 server.py >/dev/null 2>&1 &); sleep 1
ok "http://127.0.0.1:8794/stage.html"

step "Jarvis cue server"
curl -s -m1 -o /dev/null http://127.0.0.1:8765/status || (cd ~/Downloads/jarvis-reel-director && nohup python3 server.py >/dev/null 2>&1 &); sleep 1
curl -s -X POST http://127.0.0.1:8765/stop >/dev/null 2>&1
ok "port 8765 — briefing loaded: $(python3 -c "import json;print(json.load(open('$HOME/Downloads/jarvis-reel-director/config.json'))['audio'].split('/')[-1])")"

step "Agent Club"
if pgrep -f "electron-vite dev" >/dev/null; then ok "already running"
else
  (cd ~/Downloads/Agent-Club && npm start > /tmp/agent-club-start.log 2>&1 &)
  for i in {1..40}; do grep -q "Showing main window" /tmp/agent-club-start.log 2>/dev/null && break; sleep 1; done
  ok "window up"
fi

step "Chrome — pre-warming tabs"
open -a "Google Chrome" "https://calendar.google.com/calendar/u/1/r/day/2026/9/17" "https://www.skool.com/claude" "http://127.0.0.1:8794/stage.html" >/dev/null 2>&1
ok "calendar · skool · friday"

echo
echo "── JARVIS armed. Type your line and HIT ENTER to start ──"
printf "You: "
read -r line
curl -s -X POST http://127.0.0.1:8765/start >/dev/null
echo "Jarvis: ..."
