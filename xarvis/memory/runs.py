from __future__ import annotations

import sqlite3
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    command TEXT NOT NULL,
    status TEXT NOT NULL,
    decision TEXT NOT NULL,
    valid INTEGER NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT NOT NULL
);
"""


def ensure_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(SCHEMA)
        conn.commit()


def record_run(path: Path, *, command: str, status: str, decision: str, valid: bool, input_json: str, output_json: str) -> None:
    ensure_db(path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO runs (created_at, command, status, decision, valid, input_json, output_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                command,
                status,
                decision,
                1 if valid else 0,
                input_json,
                output_json,
            ),
        )
        conn.commit()


def list_runs(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, created_at, command, status, decision, valid
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "command": row["command"],
            "status": row["status"],
            "decision": row["decision"],
            "valid": bool(row["valid"]),
        }
        for row in rows
    ]


def get_run(path: Path, run_id: int) -> dict[str, Any] | None:
    if not path.exists():
        return None

    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT id, created_at, command, status, decision, valid, input_json, output_json
            FROM runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "command": row["command"],
        "status": row["status"],
        "decision": row["decision"],
        "valid": bool(row["valid"]),
        "input_json": row["input_json"],
        "output_json": row["output_json"],
    }


def export_runs(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    return list_runs(path, limit=limit)


def export_runs_json(path: Path, limit: int = 20) -> str:
    return json.dumps(export_runs(path, limit=limit), indent=2, ensure_ascii=False)


def export_runs_csv(path: Path, limit: int = 20) -> str:
    rows = export_runs(path, limit=limit)
    if not rows:
        return ""

    fieldnames = ["id", "created_at", "command", "status", "decision", "valid"]
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def _parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _filter_since(rows: list[dict[str, Any]], since: str | None) -> list[dict[str, Any]]:
    if not since:
        return rows

    since = since.strip().lower()
    if since.endswith("h") and since[:-1].isdigit():
        cutoff = datetime.now(timezone.utc) - timedelta(hours=int(since[:-1]))
    elif since.endswith("d") and since[:-1].isdigit():
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(since[:-1]))
    else:
        cutoff = _parse_utc(since)

    filtered: list[dict[str, Any]] = []
    for row in rows:
        created_at = row.get("created_at")
        if not created_at:
            continue
        if _parse_utc(created_at) >= cutoff:
            filtered.append(row)
    return filtered


def summarize_runs(path: Path, limit: int = 20, since: str | None = None) -> dict[str, Any]:
    rows = export_runs(path, limit=10_000)
    rows = _filter_since(rows, since)
    total = len(rows)

    status_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        decision_counts[row["decision"]] = decision_counts.get(row["decision"], 0) + 1

    latest = rows[:limit]
    return {
        "db_path": str(path),
        "total_runs": total,
        "since": since,
        "by_status": status_counts,
        "by_decision": decision_counts,
        "latest_runs": latest,
    }


def db_health(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "reachable": False, "table_exists": False}

    try:
        with sqlite3.connect(path) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
            ).fetchone()
    except sqlite3.Error as exc:
        return {"exists": True, "reachable": False, "table_exists": False, "error": str(exc)}

    return {
        "exists": True,
        "reachable": True,
        "table_exists": row is not None,
    }
