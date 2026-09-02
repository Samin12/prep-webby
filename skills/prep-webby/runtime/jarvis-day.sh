#!/bin/zsh
# Shared Jarvis day runner.
# Usage: jarvis-day.sh <audio.mp3> <cal-url> <skool-cue-seconds> [extra-url] [extra-cue-seconds]
# The optional extra cue opens a third page on the ROG left half late in the
# briefing (e.g. "let me show you Friday" -> Friday's calendar view).
AUDIO="$1"; CAL="$2"; SKOOL_T="${3:-13}"; EXTRA_URL="${4:-}"; EXTRA_T="${5:-0}"

# Install this day's briefing + cues into the reel-director config
python3 - "$AUDIO" "$CAL" "$SKOOL_T" "$EXTRA_URL" "$EXTRA_T" <<'EOF'
import json, sys
p = '/Users/saminyasar/Downloads/jarvis-reel-director/config.json'
c = json.load(open(p))
c['audio'] = sys.argv[1]
c['cues'] = c['cues'][:2]
c['cues'][0].update(time=1.0, label='Calendar', url=sys.argv[2], screen='ROG-left', new_window=True)
c['cues'][1].update(time=float(sys.argv[3]), label='Skool community', screen='ROG-right')
if sys.argv[4]:
    c['cues'].append({'time': float(sys.argv[5]), 'label': 'Showcase (extra page)',
                      'type': 'chrome_url', 'url': sys.argv[4], 'new_window': True, 'screen': 'ROG'})
json.dump(c, open(p, 'w'), indent=2)
EOF

# Make sure the cue server is up, clear any stuck run
if ! curl -s -m 1 http://127.0.0.1:8765/status >/dev/null 2>&1; then
  (cd ~/Downloads/jarvis-reel-director && nohup python3 server.py >/dev/null 2>&1 &)
  sleep 1
fi
curl -s -X POST http://127.0.0.1:8765/stop >/dev/null 2>&1

echo "Type your line and HIT ENTER to start:"
printf "You: "
read -r line

curl -s -X POST http://127.0.0.1:8765/start >/dev/null
echo "Jarvis: ..."
