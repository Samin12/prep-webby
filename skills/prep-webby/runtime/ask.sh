#!/bin/zsh
# Type your line to Jarvis, hit Enter, and the briefing starts (with orb glows).

# Make sure the cue server is up
if ! curl -s -m 1 http://127.0.0.1:8765/status >/dev/null 2>&1; then
  (cd ~/Downloads/jarvis-reel-director && nohup python3 server.py >/dev/null 2>&1 &)
  sleep 1
fi

# Clear any stuck run from before
curl -s -X POST http://127.0.0.1:8765/stop >/dev/null 2>&1

echo "Type your line and HIT ENTER to start:"
printf "You: "
read -r line   # e.g. "hey jarvis hows my day looking"

curl -s -X POST http://127.0.0.1:8765/start >/dev/null
echo "Jarvis: ..."
