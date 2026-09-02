# prep-webby

A Claude Code skill that preps a webinar day with the full **Jarvis** rig:

- Organizes and **color-codes today's Google Calendar** around your meetings (blue = deep work, green = community/webinar, orange = admin, yellow = personal), with the webinar as `🟢 MAIN PRIORITY`
- Generates a **Jarvis voice briefing** with ElevenLabs (community "Jarvis AI Assistant" voice) that walks the real agenda — and ends with the *"Check out Friday — the assistant"* reveal
- Installs it into the **cue server** so Calendar, Skool, and Friday open on the right monitor at the right words
- Spins up **Agent Club** (the dashboard with the glowing orb) and **Friday**

## Install

```bash
git clone https://github.com/Samin12/prep-webby.git
mkdir -p ~/.claude/skills
cp -R prep-webby/skills/prep-webby ~/.claude/skills/
bash ~/.claude/skills/prep-webby/scripts/setup.sh
```

The setup script auto-clones [Agent Club](https://github.com/AI-Answer/Agent-Club) and [Friday](https://github.com/Samin12/friday) if you don't have them, installs the Jarvis runtime, and checks dependencies (`ffmpeg`, `whisper-cli`, `node`, `python3`).

You'll also need:
- An **ElevenLabs** API key in `$ELEVENLABS_API_KEY` (or the ElevenLabs Player desktop extension configured)
- The **Google Calendar** MCP connected in Claude Code

## Use

Say to Claude Code:

> prep webby for the day

Then run `jarvis` in a terminal, type your line, hit Enter — Jarvis speaks, the orb glows, and your screens choreograph themselves.
