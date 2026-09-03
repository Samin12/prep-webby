import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "prep-webby"
RUNTIME = SKILL / "runtime"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_module("prep_webby_runner", RUNTIME / "runner.py")

    def test_apple_string_escapes_script_delimiters(self):
        self.assertEqual(self.runner.apple_string('a"b\\c\nd'), 'a\\"b\\\\c\\nd')

    def test_chrome_url_without_bounds_is_supported(self):
        scripts = []
        with mock.patch.object(self.runner, "run_applescript", scripts.append):
            self.runner.chrome_open_url("https://example.com", True, None)

        self.assertEqual(len(scripts), 1)
        self.assertIn('set URL of active tab of front window to "https://example.com"', scripts[0])
        self.assertNotIn("set bounds of front window", scripts[0])


class ServerStateTests(unittest.TestCase):
    def setUp(self):
        self.server = load_module("prep_webby_server", RUNTIME / "server.py")

    def test_successful_run_is_recorded(self):
        process = mock.Mock(returncode=0)
        process.wait.return_value = 0
        with mock.patch.object(self.server.subprocess, "Popen", return_value=process):
            self.server.run_performance(0, False)

        self.assertEqual(self.server.phase, "idle")
        self.assertEqual(self.server.last_run, {"status": "complete", "returncode": 0})

    def test_failed_run_is_recorded(self):
        process = mock.Mock(returncode=1)
        process.wait.return_value = 1
        with mock.patch.object(self.server.subprocess, "Popen", return_value=process):
            self.server.run_performance(0, False)

        self.assertEqual(self.server.last_run, {"status": "failed", "returncode": 1})

    def test_cancelled_run_is_not_reported_as_failed(self):
        process = mock.Mock(returncode=-15)
        process.wait.side_effect = self.server.cancel_event.set
        with mock.patch.object(self.server.subprocess, "Popen", return_value=process):
            self.server.run_performance(0, False)

        self.assertEqual(self.server.last_run, {"status": "cancelled", "returncode": -15})


class JarvisDayTests(unittest.TestCase):
    def run_config(self, calendar_url, skool_time="4.5", friday_time="24"):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.json"
            config_path.write_text((RUNTIME / "config.template.json").read_text())
            env = os.environ.copy()
            env.update(JARVIS_CONFIG=str(config_path), JARVIS_CONFIG_ONLY="1")
            result = subprocess.run(
                [
                    "zsh",
                    str(RUNTIME / "jarvis-day.sh"),
                    str(SKILL / "assets" / "greeting.mp3"),
                    calendar_url,
                    skool_time,
                    "http://127.0.0.1:8794/stage.html",
                    friday_time,
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            config = json.loads(config_path.read_text())
            return result, config

    def test_writes_three_ordered_cues_and_preserves_screens(self):
        result, config = self.run_config(
            "https://calendar.google.com/calendar/u/1/r/day/2026/9/17"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([cue["time"] for cue in config["cues"]], [1.0, 4.5, 24.0])
        self.assertEqual([cue["screen"] for cue in config["cues"]], ["ROG-left", "ROG-right", "ROG"])
        self.assertIn("MacBook", config["screens"])

    def test_rejects_non_calendar_host(self):
        result, config = self.run_config("https://example.com/calendar")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("calendar URL must use", result.stderr)
        self.assertEqual(config["audio"], "REPLACED_BY_SKILL_EACH_DAY.mp3")

    def test_rejects_unordered_cues(self):
        result, _ = self.run_config(
            "https://calendar.google.com/calendar/u/1/r/day/2026/9/17",
            skool_time="30",
            friday_time="24",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cue times must be ordered", result.stderr)


class WorkspaceSnapshotTests(unittest.TestCase):
    def test_snapshot_has_expected_groups_and_tab_count(self):
        workspace = json.loads((RUNTIME / "browser-workspace.json").read_text())

        self.assertEqual(
            [group["name"] for group in workspace["groups"]],
            ["Skills", "Insta", "Website", "Content Pipeline", "Trading"],
        )
        self.assertEqual(sum(len(group["urls"]) for group in workspace["groups"]), 17)


if __name__ == "__main__":
    unittest.main()
