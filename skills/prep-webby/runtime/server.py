#!/usr/bin/env python3
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PROJECT_DIR = Path(__file__).resolve().parent
PORT = 8765

runner_process = None
# Performance phase shown by the app orb: idle | listening | speaking
phase = "idle"
last_run = {"status": "never", "returncode": None}
phase_lock = threading.Lock()
cancel_event = threading.Event()


def audio_path():
    with open(PROJECT_DIR / "config.json") as f:
        return Path(json.load(f)["audio"])


def set_phase(value):
    global phase
    with phase_lock:
        phase = value


def run_performance(listen_seconds, mute):
    """listening glow -> (user says their line) -> runner speaks -> idle."""
    global last_run, runner_process
    cancel_event.clear()
    with phase_lock:
        last_run = {"status": "running", "returncode": None}
    set_phase("listening")
    if cancel_event.wait(listen_seconds):
        with phase_lock:
            last_run = {"status": "cancelled", "returncode": None}
        set_phase("idle")
        return
    cmd = [sys.executable, str(PROJECT_DIR / "runner.py")]
    if mute:
        cmd.append("--mute")
    runner_process = subprocess.Popen(cmd)
    set_phase("speaking")
    runner_process.wait()
    if cancel_event.is_set():
        status = "cancelled"
    else:
        status = "complete" if runner_process.returncode == 0 else "failed"
    with phase_lock:
        last_run = {
            "status": status,
            "returncode": runner_process.returncode,
        }
    set_phase("idle")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, "text/plain", b"")

    def do_GET(self):
        global runner_process
        if self.path == "/":
            html = (PROJECT_DIR / "index.html").read_bytes()
            self._send(200, "text/html; charset=utf-8", html)
        elif self.path == "/config":
            data = (PROJECT_DIR / "config.json").read_bytes()
            self._send(200, "application/json", data)
        elif self.path == "/audio":
            try:
                data = audio_path().read_bytes()
                self._send(200, "audio/mpeg", data)
            except OSError:
                self._send(404, "text/plain", b"audio file not found")
        elif self.path == "/status":
            running = runner_process is not None and runner_process.poll() is None
            with phase_lock:
                p = phase
                result = dict(last_run)
            body = json.dumps({"running": running, "phase": p, "last_run": result}).encode()
            self._send(200, "application/json", body)
        elif self.path == "/test-keys":
            # Sends a harmless Shift key event to check Accessibility permission
            # for the scroll cues, without touching any window.
            r = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to key code 56'],
                capture_output=True,
                text=True,
            )
            ok = r.returncode == 0
            body = json.dumps({"keystrokesAllowed": ok, "error": r.stderr.strip() or None}).encode()
            self._send(200, "application/json", body)
        else:
            self._send(404, "text/plain", b"not found")

    def _busy(self):
        with phase_lock:
            p = phase
        running = runner_process is not None and runner_process.poll() is None
        return running or p != "idle"

    def do_POST(self):
        global last_run, runner_process
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/perform":
            # Full choreography: listening glow, then the briefing.
            if self._busy():
                self._send(200, "application/json", b'{"started": false, "reason": "already running"}')
                return
            listen = float(query.get("listen", ["4"])[0])
            mute = query.get("mute", ["0"])[0] in ("1", "true")
            threading.Thread(target=run_performance, args=(listen, mute), daemon=True).start()
            self._send(200, "application/json", json.dumps({"started": True, "listen": listen, "mute": mute}).encode())
        elif parsed.path == "/start":
            # Immediate briefing, no listening phase.
            mute = "mute" in self.path
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                try:
                    body = json.loads(self.rfile.read(length))
                    mute = mute or bool(body.get("mute"))
                except (ValueError, KeyError):
                    pass
            if self._busy():
                self._send(200, "application/json", b'{"started": false, "reason": "already running"}')
                return
            threading.Thread(target=run_performance, args=(0, mute), daemon=True).start()
            self._send(200, "application/json", json.dumps({"started": True, "mute": mute}).encode())
        elif parsed.path == "/stop":
            was_busy = self._busy()
            cancel_event.set()
            if runner_process is not None and runner_process.poll() is None:
                runner_process.terminate()
            subprocess.run(["pkill", "-f", "afplay"], capture_output=True)
            if was_busy:
                with phase_lock:
                    last_run = {"status": "cancelled", "returncode": None}
            set_phase("idle")
            self._send(200, "application/json", b'{"stopped": true}')
        else:
            self._send(404, "text/plain", b"not found")

    def log_message(self, format, *args):
        pass


def main():
    try:
        server = HTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"Cue server already running on port {PORT} — nothing to do.")
        return
    print(f"Jarvis Reel Director dashboard: http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
