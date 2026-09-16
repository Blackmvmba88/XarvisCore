import importlib.util
from pathlib import Path

import xarvis.integrations.warpblack as warpblack


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "3_POWER"
    / "system_monitor"
    / "mamba_guardian.py"
)
SPEC = importlib.util.spec_from_file_location("mamba_guardian_test_target", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mamba_guardian = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mamba_guardian)


def test_parse_disk_used_reads_last_df_row():
    output = "Filesystem Size Used Avail Capacity Mounted on\n/dev/disk3s1 460Gi 200Gi 250Gi 45% /\n"
    assert mamba_guardian.MambaGuardian._parse_disk_used(output) == "45%"


def test_disk_usage_prefers_warpblack_when_configured(monkeypatch):
    calls = []

    class FakeAdapter:
        @classmethod
        def from_env(cls):
            return cls()

        def execute(self, argv, *, cwd, timeout_s, approved):
            calls.append((argv, cwd, timeout_s, approved))
            return {
                "ok": True,
                "stdout": (
                    "Filesystem Size Used Avail Capacity Mounted on\n"
                    "/dev/disk3s1 460Gi 200Gi 250Gi 45% /workspace\n"
                ),
            }

    monkeypatch.setenv("WARPBLACK_TOKEN", "x" * 24)
    monkeypatch.setattr(warpblack, "WarpBlackAdapter", FakeAdapter)

    guardian = mamba_guardian.MambaGuardian()
    assert guardian.get_disk_usage() == "45%"
    assert calls == [(["df", "-h", "."], ".", 10.0, False)]


def test_disk_usage_local_fallback_uses_structured_argv(monkeypatch):
    class Result:
        stdout = (
            "Filesystem Size Used Avail Capacity Mounted on\n"
            "/dev/disk3s1 460Gi 210Gi 240Gi 47% /\n"
        )

    seen = {}

    def fake_run(argv, *, capture_output, text, check):
        seen["argv"] = argv
        seen["capture_output"] = capture_output
        seen["text"] = text
        seen["check"] = check
        return Result()

    monkeypatch.delenv("WARPBLACK_TOKEN", raising=False)
    monkeypatch.setattr(mamba_guardian.subprocess, "run", fake_run)

    guardian = mamba_guardian.MambaGuardian()
    assert guardian.get_disk_usage() == "47%"
    assert seen == {
        "argv": ["df", "-h", "/"],
        "capture_output": True,
        "text": True,
        "check": False,
    }
