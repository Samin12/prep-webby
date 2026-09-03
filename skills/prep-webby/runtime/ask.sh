#!/bin/zsh
# Type your line to Jarvis, hit Enter, and the briefing starts.
set -euo pipefail

ensure_cue_server() {
  if curl -fsS -m 1 http://127.0.0.1:8765/status >/dev/null 2>&1; then
    return 0
  fi

  (cd "$HOME/Downloads/jarvis-reel-director" && nohup python3 server.py >/dev/null 2>&1 &)
  for _ in {1..20}; do
    curl -fsS -m 1 http://127.0.0.1:8765/status >/dev/null 2>&1 && return 0
    sleep 0.25
  done

  print -u2 "cue server did not become ready at http://127.0.0.1:8765/status"
  return 1
}

ensure_cue_server

curl -fsS -X POST http://127.0.0.1:8765/stop >/dev/null

print "Type your line and HIT ENTER to start:"
printf "You: "
read -r line
[[ -n "$line" ]] || { print -u2 "No line entered; Jarvis was not started."; exit 1; }

response=$(curl -fsS -X POST http://127.0.0.1:8765/start)
if [[ "$response" != *'"started": true'* ]]; then
  print -u2 "Jarvis did not start: $response"
  exit 1
fi

print "Jarvis: ..."
