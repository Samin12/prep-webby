---
name: prep-webby
description: Prepare Samin's target webinar day with his saved Chrome tab-group workspace, a conflict-safe Google Calendar plan, a personalized ElevenLabs Jarvis briefing, and verified Calendar/Skool/Friday screen cues. Use for "prep webby", "webinar prep", "set up my webinar day", or requests to restore Samin's webinar workspace and Jarvis demo.
---

# Prep Webby

Prepare the target webinar day end to end. The result is not complete until the
calendar, Chrome groups, briefing audio, cue configuration, and local services
have each been read back or health-checked.

Default timezone: `America/New_York`.

## Resolve the target webinar

1. Prefer a date and time explicitly supplied by the user.
2. Otherwise search the primary Google Calendar for the next 90 days using
   `webinar`, `webby`, and the named event or community.
3. If overlapping candidates occur on one date, prefer the specific,
   non-placeholder event with the longer duration. Report the other candidate;
   never delete it without a direct request.
4. If no match exists, ask for the date. Do not silently turn "prep webby" into
   a plan for today.

Read the complete target day before changing it. Never move, rename, delete, or
change attendees on an event organized by someone else. A declined or
needs-action invitation is still protected; do not change its response status.

## Phase 0: Check the machine

Run `scripts/setup.sh` from this skill directory on first use and after pulling
an update. It installs the checked-in Jarvis runtime while preserving the live
`config.json`, and checks `ffmpeg`, `whisper-cli`, `python3`, and `node`.

If a dependency is missing, report the exact missing command and suggested
installation command. Do not claim the rig is ready.

## Phase 1: Build the target day's calendar

Use Google Calendar's event palette. Confirm the current palette before writes;
the expected event colors are blue `9`, green `10`, orange `6`, and yellow `5`.

Start from the actual event times and existing busy windows. Upsert solo blocks,
never blindly create duplicates. Managed blocks must contain this description
marker:

```text
prep-webby-managed:v2
```

On the first v2 run, also treat an existing same-day event with the same title
and time as an upsert candidate. Add the marker to a user-owned solo event
instead of creating a duplicate.

Default blocks, fitted around existing meetings:

- `🟢 Skool Community — Morning Replies`, 8:00–9:00 AM, green.
- `🔵 Webinar Rehearsal + Tech Check`, 60 minutes, ending at least 60 minutes
  before the webinar, blue.
- Canonical webinar interval, green. When allowed, change only the event color
  on the user's calendar copy. Never create a second busy hold on top of an
  existing webinar. If the event cannot be colored safely, preserve it and
  report that limitation.
- `🟠 Webinar Follow-ups + Emails`, starting 15 minutes after the webinar and
  lasting 60 minutes, orange.

Only add film, packing, errands, meals, or other personal blocks when the user
mentioned them or they already exist. Do not invent a full life schedule.

After writes, search the date again and read back every managed block's title,
start, end, color, and event URL. Report conflicts rather than stacking blocks
on top of meetings.

## Phase 2: Restore the Chrome workspace

Read [references/browser-workspace.md](references/browser-workspace.md). It is
the human-readable source of truth for group order, colors, collapsed state,
and URLs; `runtime/browser-workspace.json` contains the same snapshot for
machine checks.

Operate the user's existing Chrome profile, not a fresh automation browser.
Prefer the saved tab-group buttons because Chrome preserves the group's name,
color, order, and tabs:

1. Inspect the live Chrome tab inventory and saved tab-group toolbar.
2. For each required group, do nothing when it is already open. If its saved
   button says `Closed`, open it once. Never duplicate an open group.
3. If a saved group is missing, rebuild only that group from the reference.
   Keep unrelated tabs and groups untouched.
4. Restore the captured left-to-right group order and collapsed state.
5. Re-read the live tab inventory. Verify every required group name and URL.

The duplicate `scroll-world` URL in both `Skills` and `Website` is intentional.
Do not add ungrouped research, inbox, or email-thread tabs to this workspace.

## Phase 3: Personalize the briefing

Read [references/samin-profile.md](references/samin-profile.md). Use only the
public professional facts relevant to the audience. Prefer the live calendar,
the user's stated topic, and the current project over generic biography.

Never put private email content, street addresses, phone numbers, browser
history, or calendar attendee details into the script or the public repository.

Write a 25–40 second briefing using the real target-day events. Keep this shape:

> "Good morning, sir. Here is your <weekday>. First up: your Skool community —
> I am opening it now for your morning replies. At <time>, <rehearsal or deep
> work>. <Protected meetings>. Then your main event: <webinar title>, from
> <start> to <end>. Good luck up there, sir. <Follow-ups>. And… I see you are in
> the middle of the webinar, sir. Hello, everyone. I think you might want to see
> this. Check out Friday — the assistant."

Keep the Friday reveal only for a webinar demo. Do not claim capabilities that
the rig will not visibly demonstrate.

## Phase 4: Generate and align Jarvis audio

Use ElevenLabs voice `sI8FqE1zOcqXDhRwCwAx` ("Jarvis AI Assistant"), model
`eleven_multilingual_v2`, and settings
`{"stability":0.5,"similarity_boost":0.75,"style":0.3}`.

Read the API key from `ELEVENLABS_API_KEY`; otherwise read `api_key` from:

```text
~/Library/Application Support/Claude/Claude Extensions Settings/ant.dir.gh.elevenlabs.elevenlabs-player.json
```

Never print, log, or commit the key. Save the MP3 as
`~/Downloads/jarvis_<YYYY-MM-DD>_briefing.mp3` and verify it with `afinfo` or
`ffprobe`.

Determine cue times from the generated audio. Prefer timestamped transcription
from `whisper-cli`; fall back to proportional word-position estimates. Confirm
that cue times are ordered and less than the audio duration.

## Phase 5: Install the screen cues

Update `~/Downloads/jarvis-reel-director/config.json` without overwriting its
screen calibration:

1. Around 1 second: target-date Google Calendar day view on `ROG-left`.
2. At "opening it now": `https://www.skool.com/claude` on `ROG-right`.
3. At "you might want to see this": `http://127.0.0.1:8794/stage.html` on the
   full `ROG` screen.

Use `runtime/jarvis-day.sh` with the verified audio path, target-date Calendar
URL, and cue seconds. Read back the resulting JSON and confirm the audio path,
three URLs, screen assignments, and ordered cue times.

## Phase 6: Arm the rig

- Cue server: start `server.py` if `http://127.0.0.1:8765/status` is
  unavailable. If the endpoint lacks `last_run`, restart that listener once so
  the updated status contract is active.
- Friday: start its server only if `http://127.0.0.1:8794/stage.html` is
  unavailable.
- Agent Club: start it only if no `electron-vite dev` process is running.
- Update Agent Club's
  `src/renderer/pages/jarvis/components/DailyBrief.tsx` and
  `src/renderer/pages/jarvis/services/demoDirector.ts` from the same frozen
  briefing text so the orb UI and audio agree.

Health-check both HTTP endpoints and confirm Agent Club reached `Showing main
window`. Do not trigger the performance early when preparing a future date.

## Handoff

On the webinar day, tell the user to run `jarvis` (or `~/jarvis/ask.sh`), type
`hey jarvis hows my day looking`, and press Enter.

Report separately:

- target webinar and any overlapping candidate;
- calendar blocks created, updated, unchanged, or conflicted;
- Chrome groups opened, already open, rebuilt, or missing;
- audio path and duration;
- cue readback;
- service health.

Prepared is not performed. Only say the Jarvis demo ran after `/status` reports
`last_run.status` as `complete`; report `failed` or `cancelled` exactly.
