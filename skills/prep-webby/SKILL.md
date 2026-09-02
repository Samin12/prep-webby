---
name: prep-webby
description: Prep the day for a webinar ("webby") with the full Jarvis rig. Use when the user says "prep webby", "prep webby for the day", "webby prep", or wants the Jarvis morning-briefing demo set up for a webinar day. Organizes and color-codes today's Google Calendar, generates the ElevenLabs Jarvis briefing audio, installs it into the cue server with screen choreography, and spins up Agent Club + Friday.
---

# Prep Webby — Jarvis webinar-day rig

You are prepping Samin's day for a webinar and arming the Jarvis voice demo.
Follow the phases in order. Everything is idempotent — safe to re-run.

## Phase 0 — Onboarding check (first run on a new machine)

Run `scripts/setup.sh` from this skill's directory. It:
- clones **Agent Club** (`https://github.com/AI-Answer/Agent-Club.git`) into `~/Downloads/Agent-Club` and runs `npm install` if missing
- clones **Friday** (`https://github.com/Samin12/friday.git`) into `~/friday` if missing
- installs the Jarvis runtime (`server.py`, `runner.py`, `config.template.json`) into `~/Downloads/jarvis-reel-director/` and the launcher scripts (`ask.sh`, `jarvis-day.sh`) + `greeting.mp3` into `~/jarvis/`
- adds the `jarvis` alias to `~/.zshrc`
- checks deps: `ffmpeg`, `whisper-cli`, `python3`, `node`

If setup.sh reports a missing dependency, tell the user the brew command to fix it.

## Phase 1 — Calendar for today

Use the Google Calendar MCP (list_events for today, then create/update).

1. List today's events. Identify the webinar — an event named like "webby"/"webinar". If the user gave a time (default 1:00–3:00 PM America/New_York), make sure it exists at that time; rename it to `🟢 Webinar — MAIN PRIORITY`, colorId 10.
2. Fill the day around existing meetings, color-coded:
   - `🟢 Skool Community — Morning Replies` 8:00–9:00, colorId 10
   - `🔵 Film — <current course/video>` mid-morning block, colorId 9 (ask nothing; pick the project the user mentioned, or a generic deep-work film block)
   - `🟠 Webinar Follow-ups + Emails` 15 min after the webinar ends, 1h, colorId 6
   - Personal blocks (packing, errands) colorId 5 with 🟡
3. Never move or delete meetings with attendees. Fit blocks around them.
4. Color convention: blue 9 = deep work, green 10 = community/webinar, orange 6 = admin/email, yellow 5 = personal.

## Phase 2 — ElevenLabs Jarvis briefing

- Voice ID: `sI8FqE1zOcqXDhRwCwAx` ("Jarvis AI Assistant"), model `eleven_multilingual_v2`, voice_settings `{"stability":0.5,"similarity_boost":0.75,"style":0.3}`.
- API key: `$ELEVENLABS_API_KEY`, else read the `api_key` from `~/Library/Application Support/Claude/Claude Extensions Settings/ant.dir.gh.elevenlabs.elevenlabs-player.json`. Never commit or print the key.
- Script template (~25–35s). Weave in the REAL events from Phase 1:

> "Good morning, sir. Here is your <weekday>. First up: your Skool community — I am opening it now for your morning replies. At <time>, <deep work block>. <Meetings>. Then your main event: the webinar, from <start> to <end>. Good luck up there, sir. <Follow-ups / personal blocks>. Dinner at <time>. And… I see you are in the middle of the webinar, sir. Hello, everyone. I think you might want to see this. Check out Friday — the assistant."

Keep the Friday reveal ending only on webinar-demo days (default: keep it).
- Generate with curl `POST https://api.elevenlabs.io/v1/text-to-speech/<voice>?output_format=mp3_44100_128`, save to `~/Downloads/jarvis_<day>_briefing.mp3`, check duration with `afinfo`.

## Phase 3 — Install into the cue server

Edit `~/Downloads/jarvis-reel-director/config.json`:
- `audio`: today's mp3
- Screens must include `ROG` plus virtual halves `ROG-left`/`ROG-right` (half width each). Detect the ROG monitor origin if needed.
- Cues (times estimated from the script wording, ~2.6 words/sec):
  1. ~1.0s → today's Google Calendar day view (`https://calendar.google.com/calendar/u/1/r/day/YYYY/M/D`), screen `ROG-left`, new_window true
  2. when "opening it now" is said (~4.5s) → `https://www.skool.com/claude`, screen `ROG-right`, new_window true
  3. when "you might want to see this" is said (near the end) → `http://127.0.0.1:8794/stage.html` (Friday), screen `ROG` full, new_window true

## Phase 4 — Spin everything up

- Cue server: `cd ~/Downloads/jarvis-reel-director && nohup python3 server.py &` if `curl -m1 http://127.0.0.1:8765/status` fails.
- Friday: `cd ~/friday && nohup python3 server.py &` if `curl -m1 http://127.0.0.1:8794/stage.html` fails.
- Agent Club: `cd ~/Downloads/Agent-Club && npm start &` if no `electron-vite dev` process. Confirm "Showing main window" in its log.
- Sync Agent Club's demo UI to today's briefing: update `TOP_THREE`/`AGENDA` in `src/renderer/pages/jarvis/components/DailyBrief.tsx` and `DEMO_BRIEFING_TEXT` in `src/renderer/pages/jarvis/services/demoDirector.ts` (dev mode hot-reloads).

## Phase 5 — Hand off

Tell the user: run `jarvis` (or `~/jarvis/ask.sh`), type the line ("hey jarvis hows my day looking"), **hit Enter**, and Jarvis speaks with the orb glowing while Calendar/Skool/Friday fire on the ROG monitor at their cue times. Warn if Friday's server was down when checked.
