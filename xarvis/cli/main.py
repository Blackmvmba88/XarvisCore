from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import sqlite3
import sys

from xarvis.config import DEMO_DIR, INPUT_PATH, RULES_PATH, OUTPUT_PATH, RUNS_DB_PATH
from xarvis.core.engine import XarvisEngine
from xarvis.memory.runs import db_health, export_runs_csv, export_runs_json, get_run, list_runs, summarize_runs


DEFAULT_INPUT = {
    "user_id": "demo_user",
    "action": "process_data",
    "payload": {"value": 42},
}

DEFAULT_RULES = {
    "min_value": 0,
    "allowed_actions": ["process_data"],
}


def init_demo() -> dict:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_PATH.exists():
        INPUT_PATH.write_text(json.dumps(DEFAULT_INPUT, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not RULES_PATH.exists():
        RULES_PATH.write_text(json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    return {"initialized": True, "demo_dir": str(DEMO_DIR)}


def run_doctor() -> dict:
    checks = []

    checks.append({"name": "python_version", "ok": sys.version_info >= (3, 10), "value": platform.python_version()})
    checks.append({"name": "package_import", "ok": True, "value": "xarvis importable"})
    checks.append({"name": "input_exists", "ok": INPUT_PATH.exists(), "value": str(INPUT_PATH)})
    checks.append({"name": "rules_exists", "ok": RULES_PATH.exists(), "value": str(RULES_PATH)})
    checks.append({"name": "output_dir_writable", "ok": _check_writable(OUTPUT_PATH.parent), "value": str(OUTPUT_PATH.parent)})
    checks.append({"name": "logs_dir_writable", "ok": _check_writable(RUNS_DB_PATH.parent), "value": str(RUNS_DB_PATH.parent)})

    try:
        with INPUT_PATH.open("r", encoding="utf-8") as handle:
            json.load(handle)
        input_read_ok = True
    except Exception as exc:  # noqa: BLE001
        input_read_ok = False
        checks.append({"name": "input_readable", "ok": False, "value": str(exc)})
    else:
        checks.append({"name": "input_readable", "ok": input_read_ok, "value": str(INPUT_PATH)})

    try:
        with RULES_PATH.open("r", encoding="utf-8") as handle:
            json.load(handle)
        rules_read_ok = True
    except Exception as exc:  # noqa: BLE001
        rules_read_ok = False
        checks.append({"name": "rules_readable", "ok": False, "value": str(exc)})
    else:
        checks.append({"name": "rules_readable", "ok": rules_read_ok, "value": str(RULES_PATH)})

    db = db_health(RUNS_DB_PATH)
    checks.append({"name": "runs_db_exists", "ok": db["exists"], "value": str(RUNS_DB_PATH)})
    checks.append({"name": "runs_db_reachable", "ok": db.get("reachable", False), "value": db})
    checks.append({"name": "runs_table_exists", "ok": db.get("table_exists", False), "value": db})

    all_ok = all(check["ok"] for check in checks)
    return {
        "ok": all_ok,
        "checks": checks,
    }


def _check_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".xarvis_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:  # noqa: BLE001
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xarvis")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("run")
    sub.add_parser("status")
    sub.add_parser("inspect")
    runs_parser = sub.add_parser("runs")
    runs_sub = runs_parser.add_subparsers(dest="runs_command", required=True)
    list_parser = runs_sub.add_parser("list")
    list_parser.add_argument("--limit", type=int, default=20)
    show_parser = runs_sub.add_parser("show")
    show_parser.add_argument("run_id", type=int)
    export_parser = runs_sub.add_parser("export")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")
    export_parser.add_argument("--limit", type=int, default=20)
    export_parser.add_argument("--output", type=str, default=None)
    stats_parser = runs_sub.add_parser("stats")
    stats_parser.add_argument("--limit", type=int, default=10)
    stats_parser.add_argument("--since", type=str, default=None)
    stats_parser.add_argument("--json", action="store_true")
    sub.add_parser("doctor")

    args = parser.parse_args(argv)
    engine = XarvisEngine()

    if args.command == "init":
        result = init_demo()
    elif args.command == "run":
        result = engine.run_demo()
    elif args.command == "status":
        result = engine.status()
    elif args.command == "runs":
        if args.runs_command == "list":
            result = {
                "db_path": str(RUNS_DB_PATH),
                "count": len(list_runs(RUNS_DB_PATH, limit=args.limit)),
                "runs": list_runs(RUNS_DB_PATH, limit=args.limit),
            }
        elif args.runs_command == "show":
            run = get_run(RUNS_DB_PATH, args.run_id)
            result = run if run is not None else {"error": "run_not_found", "run_id": args.run_id}
        elif args.runs_command == "export":
            if args.format == "csv":
                payload = export_runs_csv(RUNS_DB_PATH, limit=args.limit)
            else:
                payload = export_runs_json(RUNS_DB_PATH, limit=args.limit)

            if args.output:
                Path(args.output).write_text(payload, encoding="utf-8")
                result = {"exported": True, "format": args.format, "output": args.output}
            else:
                print(payload)
                return 0
        elif args.runs_command == "stats":
            result = summarize_runs(RUNS_DB_PATH, limit=args.limit, since=args.since)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return 0
            print(f"Total runs: {result['total_runs']}")
            print("")
            print("By status:")
            for key, value in sorted(result["by_status"].items()):
                print(f"  {key}: {value}")
            print("")
            print("By decision:")
            for key, value in sorted(result["by_decision"].items()):
                print(f"  {key}: {value}")
            print("")
            print("Latest runs:")
            for row in result["latest_runs"]:
                print(f"  #{row['id']} {row['created_at']} {row['status']} {row['decision']} valid={row['valid']}")
            return 0
        else:
            result = {"error": "unknown_runs_command"}
    elif args.command == "doctor":
        result = run_doctor()
    else:
        result = engine.inspect()

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
