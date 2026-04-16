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


def test_runs_export_json_stdout():
    db_path = ROOT / "logs" / "runs.sqlite3"
    if db_path.exists():
        db_path.unlink()

    run_xarvis("init")
    run_xarvis("run")

    export = run_xarvis("runs", "export", "--format", "json", "--limit", "5")
    payload = json.loads(export.stdout)
    assert isinstance(payload, list)
    assert payload[0]["command"] == "run"


def test_runs_export_csv_file(tmp_path):
    db_path = ROOT / "logs" / "runs.sqlite3"
    if db_path.exists():
        db_path.unlink()

    run_xarvis("init")
    run_xarvis("run")

    out = tmp_path / "runs.csv"
    result = run_xarvis("runs", "export", "--format", "csv", "--output", str(out), "--limit", "5")
    payload = json.loads(result.stdout)
    assert payload["exported"] is True
    assert out.exists()
    assert "command,status,decision,valid" in out.read_text(encoding="utf-8")
