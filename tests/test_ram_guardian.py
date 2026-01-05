import importlib.util
import os
import textwrap
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
RG_PATH = os.path.join(REPO_ROOT, "5_INFRA", "ram_guardian.py")

spec = importlib.util.spec_from_file_location("ram_guardian", RG_PATH)
ram_guardian = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ram_guardian)


def test_parse_vm_stat():
    sample = textwrap.dedent("""
        Mach Virtual Memory Statistics: (page size of 4096 bytes)
        Pages free:                               100.
        Pages speculative:                         10.
        Pages inactive:                            50.
        Pages active:                              70.
    """)
    free, inactive = ram_guardian.parse_vm_stat(sample)
    assert free == 100
    assert inactive == 50


def test_available_fraction(monkeypatch):
    monkeypatch.setattr(ram_guardian, "total_memory_bytes", lambda: 1024 * 1024 * 1024)  # 1GB
    monkeypatch.setattr(ram_guardian, "free_inactive_bytes", lambda: 256 * 1024 * 1024)  # 256MB
    frac = ram_guardian.available_fraction()
    assert abs(frac - 0.25) < 0.001


def test_top_memory_procs_parsing(monkeypatch):
    ps_output = """
      PID COMM             RSS
      123 python3         500000
      456 Safari          300000
      789 Chrome          700000
    """
    monkeypatch.setattr(ram_guardian, "run_cmd", lambda cmd: ps_output)
    top = ram_guardian.top_memory_procs(3)
    assert len(top) == 3
    # Highest RSS is Chrome (700000 KB)
    assert top[0][1].strip() == "Chrome"
    assert top[0][0] == 789


def test_perform_action_and_measure(monkeypatch):
    pre_vm = """
        Pages free: 100.
        Pages inactive: 0.
    """
    post_vm = """
        Pages free: 200.
        Pages inactive: 0.
    """
    state = {"after": False}

    def fake_run(cmd):
        # cmd is a list; check vm_stat and sysctl
        if isinstance(cmd, list) and cmd and cmd[0] == "vm_stat":
            return post_vm if state["after"] else pre_vm
        if isinstance(cmd, list) and cmd and cmd[0] == "sysctl":
            return str(1024 * 1024 * 1024)
        return ""

    monkeypatch.setattr(ram_guardian, "run_cmd", fake_run)

    def action():
        state["after"] = True

    info = ram_guardian.perform_action_and_measure(action, timeout=2, poll_interval=0.05)
    assert info["pre_free_bytes"] == (100 + 0) * ram_guardian.PAGE_SIZE
    assert info["post_free_bytes"] == (200 + 0) * ram_guardian.PAGE_SIZE
    assert info["delta_bytes"] == (100) * ram_guardian.PAGE_SIZE
    assert info["success"] is True


def test_estimate_rss_sum():
    procs = [(1, "a", 1024), (2, "b", 2048)]
    assert ram_guardian.estimate_rss_sum(procs) == 3072

