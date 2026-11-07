import json
import sqlite3
from datetime import datetime, timezone

from xarvis.guardian.validator import validate
from xarvis.memory.runs import ensure_db, summarize_runs
from xarvis.core.engine import XarvisEngine


def test_validator_rejects_nonfinite_and_boolean_values():
    for value in (float("nan"), float("inf"), float("-inf"), True, False):
        result = validate({"user_id": "test", "action": "process_data", "payload": {"value": value}})
        assert not result["valid"], value


def test_run_statistics_include_more_than_ten_thousand(tmp_path):
    db = tmp_path / "runs.sqlite3"
    ensure_db(db)
    now = datetime.now(timezone.utc).isoformat()
    rows = [(now, "run", "processed", "LOW", 1, "{}", "{}")] * 10001
    with sqlite3.connect(db) as conn:
        conn.executemany(
            "INSERT INTO runs (created_at, command, status, decision, valid, input_json, output_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
    result = summarize_runs(db, limit=2)
    assert result["total_runs"] == 10001
    assert len(result["latest_runs"]) == 2


def test_engine_uses_custom_runs_database(tmp_path):
    inp = tmp_path / "input.json"
    rules = tmp_path / "rules.json"
    inp.write_text(json.dumps({"user_id": "u", "action": "process_data", "payload": {"value": 12}}))
    rules.write_text(json.dumps({"allowed_actions": ["process_data"]}))
    db = tmp_path / "custom.sqlite3"
    engine = XarvisEngine(input_path=inp, rules_path=rules, output_path=tmp_path / "output.json", log_path=tmp_path / "system.log", runs_db_path=db)
    assert engine.run_demo()["valid"]
    assert db.exists()
    assert engine.status()["runs_db_exists"]
