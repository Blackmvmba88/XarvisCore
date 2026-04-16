import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_xarvis(*args):
    return subprocess.run(
        [sys.executable, "-m", "xarvis", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_doctor_reports_healthy_state():
    run_xarvis("init")
    run_xarvis("run")

    payload = json.loads(run_xarvis("doctor").stdout)
    assert payload["ok"] is True
    names = {check["name"] for check in payload["checks"]}
    assert "python_version" in names
    assert "runs_db_reachable" in names
    assert "runs_table_exists" in names
