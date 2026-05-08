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


def test_demo_init_run_status_inspect(tmp_path):
    output_path = ROOT / "examples" / "demo_full" / "output.json"
    log_path = ROOT / "logs" / "system.log"
    if output_path.exists():
        output_path.unlink()
    if log_path.exists():
        log_path.unlink()

    init = run_xarvis("init")
    assert "initialized" in init.stdout

    run = run_xarvis("run", "--json")
    payload = json.loads(run.stdout)
    assert payload["decision"] == "MEDIUM"
    assert payload["status"] == "processed"
    assert payload["valid"] is True

    status = run_xarvis("status")
    status_payload = json.loads(status.stdout)
    assert status_payload["output_exists"] is True

    inspect = run_xarvis("inspect")
    inspect_payload = json.loads(inspect.stdout)
    assert inspect_payload["decision"] == "MEDIUM"
    assert output_path.exists()


def test_validation_rejects_negative_value():
    from xarvis.guardian.validator import validate

    result = validate({"user_id": "u", "action": "process_data", "payload": {"value": -1}}, {})
    assert result["valid"] is False
    assert "Value must be >= 0" in result["errors"]
