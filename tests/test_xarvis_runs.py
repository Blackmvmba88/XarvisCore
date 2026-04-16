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


def test_runs_list_records_history():
    db_path = ROOT / "logs" / "runs.sqlite3"
    if db_path.exists():
        db_path.unlink()

    run_xarvis("init")
    run_xarvis("run")
    run_xarvis("run")

    runs = run_xarvis("runs", "list", "--limit", "10")
    payload = json.loads(runs.stdout)
    assert payload["count"] >= 2
    assert payload["runs"][0]["command"] == "run"
    assert payload["runs"][0]["decision"] == "MEDIUM"
    assert payload["runs"][0]["valid"] is True
