#!/bin/bash
# prep-webby onboarding — idempotent. Installs Agent Club, Friday, and the Jarvis runtime.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }

echo "── prep-webby setup ──"

# 1. Agent Club
if [ ! -d "$HOME/Downloads/Agent-Club" ]; then
  git clone https://github.com/AI-Answer/Agent-Club.git "$HOME/Downloads/Agent-Club" && ok "Agent Club cloned"
else ok "Agent Club present"; fi
if [ -d "$HOME/Downloads/Agent-Club" ] && [ ! -d "$HOME/Downloads/Agent-Club/node_modules" ]; then
  (cd "$HOME/Downloads/Agent-Club" && npm install --silent) && ok "Agent Club deps installed"
fi

# 2. Friday (the assistant)
if [ ! -d "$HOME/friday" ]; then
  git clone https://github.com/Samin12/friday.git "$HOME/friday" && ok "Friday cloned"
else ok "Friday present"; fi

# 3. Jarvis runtime (cue server + launcher scripts)
mkdir -p "$HOME/Downloads/jarvis-reel-director" "$HOME/jarvis"
for f in server.py runner.py; do
  install -m 0644 "$HERE/runtime/$f" "$HOME/Downloads/jarvis-reel-director/$f"
done
[ -f "$HOME/Downloads/jarvis-reel-director/config.json" ] || cp "$HERE/runtime/config.template.json" "$HOME/Downloads/jarvis-reel-director/config.json"
install -m 0755 "$HERE/runtime/ask.sh" "$HERE/runtime/jarvis-day.sh" "$HOME/jarvis/"
install -m 0644 "$HERE/assets/greeting.mp3" "$HOME/jarvis/greeting.mp3"
ok "Jarvis runtime updated; live config.json preserved"

# 4. jarvis alias
grep -q 'alias jarvis=' "$HOME/.zshrc" 2>/dev/null || { echo 'alias jarvis="$HOME/jarvis/ask.sh"' >> "$HOME/.zshrc"; ok "jarvis alias added to ~/.zshrc"; }

# 5. Dependencies
for dep in ffmpeg whisper-cli python3 node; do
  command -v "$dep" >/dev/null 2>&1 && ok "$dep" || warn "$dep missing — brew install $dep"
done

echo "── setup complete ──"
