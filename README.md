# prep-webby

A reusable webinar-day skill for Samin's full Jarvis rig.

It now handles the whole setup as one verified workflow:

- finds the correct upcoming webinar date instead of assuming "today";
- safely upserts color-coded Google Calendar prep blocks without moving or
  rewriting attendee-owned meetings;
- restores the saved Chrome workspace with the captured `Skills`, `Insta`,
  `Website`, `Content Pipeline`, and `Trading` groups;
- personalizes the voice briefing with public professional context and the real
  target-day agenda;
- generates the ElevenLabs Jarvis audio and aligns cues to the finished file;
- arms Calendar, Skool, Agent Club, and Friday, then reads the live setup back.

## Install

```bash
git clone https://github.com/Samin12/prep-webby.git
mkdir -p ~/.claude/skills
cp -R prep-webby/skills/prep-webby ~/.claude/skills/
bash ~/.claude/skills/prep-webby/scripts/setup.sh
```

The setup script installs the checked-in runtime into
`~/Downloads/jarvis-reel-director` and `~/jarvis`, preserving the machine's live
screen calibration and cue config. It also clones
[Agent Club](https://github.com/AI-Answer/Agent-Club) and
[Friday](https://github.com/Samin12/friday) when missing.

Requirements:

- `ffmpeg`, `whisper-cli`, `python3`, and `node`;
- an ElevenLabs API key in `ELEVENLABS_API_KEY`, or the configured ElevenLabs
  Player extension;
- Google Calendar access;
- access to the existing Chrome profile and its saved tab groups.

## Use

Ask Codex or Claude Code:

> prep webby for my next webinar

or:

> prep webby for September 17

The skill resolves the date, prepares that day's calendar, restores the browser
workspace, builds the briefing and cue timeline, and health-checks the rig.

On the webinar day, run `jarvis`, type your line, and press Enter. Calendar and
Skool open on the ROG halves, then Friday takes the full screen at the reveal.

## Validate

```bash
python3 -m unittest discover -s tests -v
```
