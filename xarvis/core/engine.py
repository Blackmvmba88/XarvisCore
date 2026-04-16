from __future__ import annotations

from dataclasses import asdict

import json

from xarvis.config import INPUT_PATH, LOG_PATH, OUTPUT_PATH, RULES_PATH, RUNS_DB_PATH
from xarvis.core.decision import decide
from xarvis.core.models import ExecutionResult
from xarvis.guardian.validator import validate
from xarvis.logs.logger import log_event
from xarvis.memory.runs import record_run
from xarvis.memory.store import load_json, save_output


class XarvisEngine:
    def __init__(self, input_path=INPUT_PATH, rules_path=RULES_PATH, output_path=OUTPUT_PATH, log_path=LOG_PATH):
        self.input_path = input_path
        self.rules_path = rules_path
        self.output_path = output_path
        self.log_path = log_path

    def run_demo(self) -> dict:
        input_data = load_json(self.input_path)
        rules = load_json(self.rules_path) if self.rules_path.exists() else {}

        validation = validate(input_data, rules)
        if not validation["valid"]:
            result = ExecutionResult(
                input=input_data,
                decision="REJECTED",
                status="validation_failed",
                valid=False,
                errors=validation["errors"],
                timestamp="",
            )
            payload = asdict(result)
            log_event("validation_failed", {"input": input_data, "errors": validation["errors"]}, self.log_path)
            record_run(
                RUNS_DB_PATH,
                command="run",
                status=result.status,
                decision=result.decision,
                valid=result.valid,
                input_json=json.dumps(input_data, ensure_ascii=False),
                output_json=json.dumps(payload, ensure_ascii=False),
            )
            return payload

        decision = decide(input_data)
        result = ExecutionResult(
            input=input_data,
            decision=decision,
            status="processed",
            valid=True,
            errors=[],
            timestamp="",
        )
        persisted = save_output(asdict(result), self.output_path)
        log_event("execution_success", persisted, self.log_path)
        record_run(
            RUNS_DB_PATH,
            command="run",
            status=persisted["status"],
            decision=persisted["decision"],
            valid=persisted["valid"],
            input_json=json.dumps(input_data, ensure_ascii=False),
            output_json=json.dumps(persisted, ensure_ascii=False),
        )
        return persisted

    def status(self) -> dict:
        return {
            "system": "XarvisCore",
            "demo_ready": self.input_path.exists(),
            "input_exists": self.input_path.exists(),
            "rules_exists": self.rules_path.exists(),
            "output_exists": self.output_path.exists(),
            "runs_db_exists": RUNS_DB_PATH.exists(),
        }

    def inspect(self) -> dict:
        if not self.output_path.exists():
            return {"error": "output_not_found", "path": str(self.output_path)}
        return load_json(self.output_path)
