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


def test_runs_stats_human_and_json():
    db_path = ROOT / "logs" / "runs.sqlite3"
    if db_path.exists():
        db_path.unlink()

    run_xarvis("init")
    run_xarvis("run")
    run_xarvis("run")

    human = run_xarvis("runs", "stats")
    assert "Total runs:" in human.stdout
    assert "By status:" in human.stdout
    assert "By decision:" in human.stdout

    payload = json.loads(run_xarvis("runs", "stats", "--json").stdout)
    assert payload["total_runs"] >= 2
    assert payload["by_status"]["processed"] >= 2
    assert payload["by_decision"]["MEDIUM"] >= 2
    assert len(payload["latest_runs"]) >= 1
