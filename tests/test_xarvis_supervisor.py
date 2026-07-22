import importlib.util
from pathlib import Path


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
