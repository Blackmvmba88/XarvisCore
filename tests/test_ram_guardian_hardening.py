import json
import os
import tempfile
import textwrap
import time

import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
RG_PATH = os.path.join(REPO_ROOT, "5_INFRA", "ram_guardian.py")

spec = importlib.util.spec_from_file_location("ram_guardian", RG_PATH)
ram_guardian = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ram_guardian)


def test_append_metric_entry_writes_file(tmp_path):
    path = tmp_path / "metrics.jsonl"
    entry = {"a": 1}
    ram_guardian.append_metric_entry(entry, path=str(path))
    with open(str(path), "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["a"] == 1


def test_get_memory_snapshot_handles_errors(monkeypatch):
    monkeypatch.setattr(ram_guardian, "free_inactive_bytes", lambda: (_ for _ in ()).throw(Exception("boom")))
    assert ram_guardian.get_memory_snapshot_bytes() == 0


def test_notify_handles_missing_osascript(monkeypatch):
    def fake_call(cmd):
        raise FileNotFoundError()
    monkeypatch.setattr(ram_guardian.subprocess, "call", fake_call)
    assert ram_guardian.notify("hello") is False


def test_perform_action_and_measure_timeout(monkeypatch):
    # action does nothing and vm stat doesn't change
    monkeypatch.setattr(ram_guardian, "get_memory_snapshot_bytes", lambda: 1000)

    def action():
        pass

    info = ram_guardian.perform_action_and_measure(action, timeout=0.2, poll_interval=0.05)
    assert info["success"] is False
    assert info["post_free_bytes"] == 1000
