#!/bin/zsh
# Install one verified briefing and cue timeline.
# Usage: jarvis-day.sh <audio.mp3> <calendar-url> <skool-seconds> <friday-url> <friday-seconds>
set -euo pipefail

if (( $# < 5 )); then
  print -u2 "usage: $0 <audio.mp3> <calendar-url> <skool-seconds> <friday-url> <friday-seconds>"
  exit 2
fi

AUDIO="$1"
CAL="$2"
SKOOL_T="$3"
FRIDAY_URL="$4"
FRIDAY_T="$5"
CONFIG_PATH="${JARVIS_CONFIG:-$HOME/Downloads/jarvis-reel-director/config.json}"

if [[ ! -f "$AUDIO" ]]; then
  print -u2 "audio file not found: $AUDIO"
  exit 1
fi

python3 - "$CONFIG_PATH" "$AUDIO" "$CAL" "$SKOOL_T" "$FRIDAY_URL" "$FRIDAY_T" <<'PY'
import json
import math
import sys
from pathlib import Path
from urllib.parse import urlparse

config_path = Path(sys.argv[1]).expanduser()
audio_path = str(Path(sys.argv[2]).expanduser().resolve())
calendar_url = sys.argv[3]
skool_time = float(sys.argv[4])
friday_url = sys.argv[5]
friday_time = float(sys.argv[6])

if not config_path.is_file():
    raise SystemExit(f"config file not found: {config_path}")
if not all(math.isfinite(value) for value in (skool_time, friday_time)):
    raise SystemExit("cue times must be finite numbers")
if not (3.5 < skool_time < friday_time):
    raise SystemExit("cue times must be ordered: Skool (3.5) < Calendar < Friday")

parsed_calendar = urlparse(calendar_url)
if (
    parsed_calendar.scheme != "https"
    or parsed_calendar.hostname != "calendar.google.com"
    or parsed_calendar.username
    or parsed_calendar.password
    or parsed_calendar.port not in (None, 443)
    or not parsed_calendar.path.startswith("/calendar/")
):
    raise SystemExit("calendar URL must use https://calendar.google.com")
if friday_url != "http://127.0.0.1:8794/stage.html":
    raise SystemExit("Friday URL must be http://127.0.0.1:8794/stage.html")

with config_path.open() as handle:
    config = json.load(handle)

required_screens = {"ROG", "ROG-left", "ROG-right"}
missing = required_screens.difference(config.get("screens", {}))
if missing:
    raise SystemExit(f"missing calibrated screens: {', '.join(sorted(missing))}")

config["audio"] = audio_path
config["cues"] = [
    {
        "time": skool_time,
        "label": "Calendar",
        "type": "chrome_url",
        "url": calendar_url,
        "new_window": True,
        "screen": "ROG-left",
    },
    {
        "time": 3.5,
        "label": "Skool community",
        "type": "chrome_url",
        "url": "https://www.skool.com/claude",
        "new_window": True,
        "screen": "ROG-right",
    },
    {
        "time": friday_time,
        "label": "Friday reveal",
        "type": "chrome_url",
        "url": friday_url,
        "new_window": True,
        "screen": "ROG",
    },
]

temporary = config_path.with_suffix(".json.tmp")
with temporary.open("w") as handle:
    json.dump(config, handle, indent=2)
    handle.write("\n")
temporary.replace(config_path)
print(json.dumps({"config": str(config_path), "audio": audio_path, "cues": config["cues"]}, indent=2))
PY

if [[ "${JARVIS_CONFIG_ONLY:-0}" == "1" ]]; then
  print "Jarvis config updated without starting services."
  exit 0
fi

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
print "Jarvis day armed. Run 'jarvis' when it is time to perform."
