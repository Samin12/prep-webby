#!/usr/bin/env python3
import json
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_DIR / "config.json"


def apple_string(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def run_applescript(script):
    subprocess.run(
        ["osascript", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )


def chrome_open_url(url, new_window, bounds):
    safe_url = apple_string(url)
    bounds_command = ""
    if bounds:
        bounds_command = (
            f'set bounds of front window to {{{bounds["x"]}, {bounds["y"]}, '
            f'{bounds["x"] + bounds["w"]}, {bounds["y"] + bounds["h"]}}}'
        )
    if new_window:
        script = f'''
        tell application "Google Chrome"
            activate
            make new window
            set URL of active tab of front window to "{safe_url}"
            delay 0.6
            {bounds_command}
        end tell
        '''
    else:
        script = f'''
        tell application "Google Chrome"
            activate
            if (count of windows) = 0 then
                make new window
            end if
            tell front window
                set newTab to make new tab with properties {{URL:"{safe_url}"}}
            end tell
            delay 0.6
            {bounds_command}
        end tell
        '''
    run_applescript(script)


def scroll_fast(times=5, interval=0.12, amount="page_down"):
    key_codes = {"page_down": 121, "down_arrow": 125, "space": 49}
    code = key_codes.get(amount, 121)
    for _ in range(times):
        run_applescript(f'tell application "System Events" to key code {code}')
        time.sleep(interval)


def open_app(app_name, bounds=None):
    safe_app_name = apple_string(app_name)
    run_applescript(f'tell application "{safe_app_name}" to activate')
    if bounds:
        time.sleep(0.6)
        run_applescript(
            f'tell application "System Events" to tell (first process whose frontmost is true) '
            f'to set position of front window to {{{bounds["x"]}, {bounds["y"]}}}'
        )


def reveal_in_finder(path):
    safe_path = apple_string(path)
    run_applescript(f'tell application "Finder" to reveal POSIX file "{safe_path}"')
    run_applescript('tell application "Finder" to activate')


def execute_cue(cue, screens):
    label = cue.get("label", cue.get("type"))
    print(f"[{time.strftime('%H:%M:%S')}] cue: {label}", flush=True)
    bounds = screens.get(cue.get("screen", ""), None)
    ctype = cue["type"]
    if ctype == "chrome_url":
        chrome_open_url(cue["url"], cue.get("new_window", False), bounds)
        scroll = cue.get("scroll")
        if scroll:
            scroll_fast(
                times=scroll.get("times", 5),
                interval=scroll.get("interval", 0.12),
                amount=scroll.get("amount", "page_down"),
            )
    elif ctype == "app":
        open_app(cue["app"], bounds)
    elif ctype == "finder_reveal":
        reveal_in_finder(cue["path"])
    else:
        print(f"  unknown cue type: {ctype}", file=sys.stderr)


def main():
    mute = "--mute" in sys.argv
    config = load_config()
    audio_path = config["audio"]
    screens = config["screens"]
    cues = sorted(config["cues"], key=lambda c: c["time"])

    player = None
    if mute:
        print("Starting cue timeline (muted — audio plays elsewhere)")
    else:
        print(f"Starting playback: {audio_path}")
        player = subprocess.Popen(["afplay", audio_path])
    start = time.monotonic()

    for cue in cues:
        target = start + cue["time"]
        now = time.monotonic()
        if target > now:
            time.sleep(target - now)
        execute_cue(cue, screens)

    if player is not None:
        player.wait()
    print("Done.")


if __name__ == "__main__":
    main()
