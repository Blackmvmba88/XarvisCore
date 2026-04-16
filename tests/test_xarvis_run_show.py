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


def test_runs_show_returns_full_record():
    db_path = ROOT / "logs" / "runs.sqlite3"
    if db_path.exists():
        db_path.unlink()

    run_xarvis("init")
    run_xarvis("run")

    listed = json.loads(run_xarvis("runs", "list", "--limit", "1").stdout)
    run_id = listed["runs"][0]["id"]

    payload = json.loads(run_xarvis("runs", "show", str(run_id)).stdout)
    assert payload["id"] == run_id
    assert payload["command"] == "run"
    assert payload["decision"] == "MEDIUM"
    assert payload["valid"] is True
    assert "input_json" in payload
    assert "output_json" in payload


def test_runs_show_missing_id_returns_error():
    db_path = ROOT / "logs" / "runs.sqlite3"
    if db_path.exists():
        db_path.unlink()

    payload = json.loads(run_xarvis("runs", "show", "9999").stdout)
    assert payload["error"] == "run_not_found"
    assert payload["run_id"] == 9999
