import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR_PATH = ROOT / "xarvis_supervisor.py"


def load_supervisor(monkeypatch, tmp_path):
    monkeypatch.setenv("XARVIS_BASE_DIR", str(ROOT))
    monkeypatch.setenv("XARVIS_LOG_DIR", str(tmp_path / "logs"))
    spec = importlib.util.spec_from_file_location("xarvis_supervisor_test", SUPERVISOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_supervisor_uses_repo_relative_paths(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)

    assert supervisor.BASE_DIR == ROOT
    assert supervisor.LOG_DIR == tmp_path / "logs"
    assert supervisor.PROCESSES["CORE_SOVEREIGN"]["path"] == ROOT / "1_CORE/xarvis_core.py"
    assert supervisor.PROCESSES["RAM_GUARDIAN"]["log"] == tmp_path / "logs" / "ram_guardian.log"


def test_supervisor_import_does_not_start_processes(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)

    assert all(config["proc"] is None for config in supervisor.PROCESSES.values())


def test_enabled_processes_are_sorted_by_priority(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    processes = {
        "LATE": {"priority": 9, "enabled": True},
        "EARLY_B": {"priority": 1, "enabled": True},
        "DISABLED": {"priority": 0, "enabled": False},
        "EARLY_A": {"priority": 1, "enabled": True},
    }

    names = [name for name, _ in supervisor.enabled_process_items(processes)]

    assert names == ["EARLY_A", "EARLY_B", "LATE"]


def test_runtime_processes_can_include_extended_modules(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)

    core_only = supervisor.runtime_processes(include_extended=False)
    with_extended = supervisor.runtime_processes(include_extended=True)

    assert "STATION_COMMAND" not in core_only
    assert "STATION_COMMAND" in with_extended
    assert with_extended["STATION_COMMAND"]["enabled"] is True
    assert all(config["proc"] is None for config in with_extended.values())


def test_start_process_disables_missing_scripts(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    config = {
        "path": tmp_path / "missing.py",
        "log": tmp_path / "logs" / "missing.log",
        "proc": None,
        "priority": 1,
        "enabled": True,
    }

    started = supervisor.start_process("MISSING_DOMAIN", config)

    assert started is False
    assert config["enabled"] is False
    assert config["proc"] is None


def test_positive_float_env_rejects_invalid_values(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    monkeypatch.setenv("INVALID_INTERVAL", "0")

    with pytest.raises(ValueError, match="INVALID_INTERVAL.*'0'"):
        supervisor.positive_float_env("INVALID_INTERVAL", 1.0)


def test_monitor_once_schedules_exponential_restart(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    messages = []
    monkeypatch.setattr(supervisor, "log_master", messages.append)
    monkeypatch.setattr(supervisor, "RESTART_BACKOFF_INITIAL", 2.0)
    monkeypatch.setattr(supervisor, "RESTART_BACKOFF_MAX", 10.0)
    config = {
        "enabled": True,
        "priority": 1,
        "proc": None,
        "restart_attempts": 0,
        "restart_at": 0.0,
    }

    monkeypatch.setattr(supervisor, "start_process", lambda name, current: False)
    supervisor.monitor_once({"CORE": config}, now=100.0)
    assert config["restart_attempts"] == 1
    assert config["restart_at"] == 102.0

    supervisor.monitor_once({"CORE": config}, now=102.0)
    assert config["restart_attempts"] == 2
    assert config["restart_at"] == 106.0
    assert any("reintentará en 4s" in message for message in messages)


def test_monitor_once_restarts_due_process(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    calls = []
    config = {
        "enabled": True,
        "priority": 1,
        "proc": None,
        "restart_attempts": 1,
        "restart_at": 50.0,
    }

    def start_process(name, current):
        calls.append(name)
        current["proc"] = object()
        current["restart_at"] = 0.0
        current["started_at"] = 50.0
        return True

    monkeypatch.setattr(supervisor, "start_process", start_process)
    monkeypatch.setattr(supervisor, "log_master", lambda message: None)

    supervisor.monitor_once({"CORE": config}, now=50.0)

    assert calls == ["CORE"]
    assert config["restart_attempts"] == 1
    assert config["restart_at"] == 0.0


def test_monitor_once_resets_backoff_after_stable_run(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    monkeypatch.setattr(supervisor, "RESTART_STABLE_AFTER", 30.0)

    class RunningProcess:
        @staticmethod
        def poll():
            return None

    config = {
        "enabled": True,
        "priority": 1,
        "proc": RunningProcess(),
        "restart_attempts": 3,
        "restart_at": 0.0,
        "started_at": 100.0,
    }

    supervisor.monitor_once({"CORE": config}, now=130.0)

    assert config["restart_attempts"] == 0


def test_kill_process_waits_for_graceful_shutdown(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    signals = []
    waits = []

    class Process:
        pid = 123

        @staticmethod
        def wait(timeout):
            waits.append(timeout)

    config = {"proc": Process()}
    monkeypatch.setattr(supervisor.os, "getpgid", lambda pid: 456)
    monkeypatch.setattr(supervisor.os, "killpg", lambda group, sent_signal: signals.append((group, sent_signal)))
    monkeypatch.setattr(supervisor, "log_master", lambda message: None)

    supervisor.kill_process("CORE", config)

    assert signals == [(456, supervisor.signal.SIGTERM)]
    assert waits == [supervisor.SHUTDOWN_TIMEOUT]
    assert config["proc"] is None


def test_kill_process_forces_shutdown_after_timeout(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    signals = []

    class Process:
        pid = 123
        wait_calls = 0

        @classmethod
        def wait(cls, timeout):
            cls.wait_calls += 1
            if cls.wait_calls == 1:
                raise supervisor.subprocess.TimeoutExpired(cmd="core", timeout=timeout)

    config = {"proc": Process()}
    monkeypatch.setattr(supervisor.os, "getpgid", lambda pid: 456)
    monkeypatch.setattr(supervisor.os, "killpg", lambda group, sent_signal: signals.append((group, sent_signal)))
    monkeypatch.setattr(supervisor, "log_master", lambda message: None)

    supervisor.kill_process("CORE", config)

    assert signals == [
        (456, supervisor.signal.SIGTERM),
        (456, supervisor.signal.SIGKILL),
    ]
    assert Process.wait_calls == 2
    assert config["proc"] is None


def test_kill_process_keeps_handle_when_shutdown_fails(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)

    class Process:
        pid = 123

    process = Process()
    config = {"proc": process}
    monkeypatch.setattr(supervisor.os, "getpgid", lambda pid: 456)
    monkeypatch.setattr(
        supervisor.os,
        "killpg",
        lambda group, sent_signal: (_ for _ in ()).throw(PermissionError("denied")),
    )
    monkeypatch.setattr(supervisor, "log_master", lambda message: None)

    supervisor.kill_process("CORE", config)

    assert config["proc"] is process


def test_monitor_once_attempts_immediate_start_without_backoff(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    calls = []
    config = {
        "enabled": True,
        "priority": 1,
        "proc": None,
        "restart_attempts": 0,
        "restart_at": 0.0,
    }
    monkeypatch.setattr(supervisor, "start_process", lambda name, current: calls.append(name) or True)
    monkeypatch.setattr(supervisor, "log_master", lambda message: None)

    supervisor.monitor_once({"CORE": config}, now=100.0)

    assert calls == ["CORE"]
    assert config["restart_attempts"] == 0
    assert config["restart_at"] == 0.0


def test_signal_handler_stops_higher_priority_processes_first(monkeypatch, tmp_path):
    supervisor = load_supervisor(monkeypatch, tmp_path)
    stopped = []
    supervisor.ACTIVE_PROCESSES = {
        "CORE": {"priority": 1, "enabled": True, "proc": object()},
        "POWER": {"priority": 2, "enabled": True, "proc": object()},
    }
    monkeypatch.setattr(supervisor, "kill_process", lambda name, config: stopped.append(name))
    monkeypatch.setattr(supervisor, "log_master", lambda message: None)

    with pytest.raises(SystemExit) as exit_info:
        supervisor.signal_handler(None, None)

    assert exit_info.value.code == 0
    assert stopped == ["POWER", "CORE"]
