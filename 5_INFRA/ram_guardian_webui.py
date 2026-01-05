#!/usr/bin/env python3
"""Lightweight Flask Web UI for RAM Guardian

Features:
- /api/status -> current available fraction, top processes
- /api/metrics -> recent metrics JSON lines
- /api/action -> trigger estimate or (with approval) perform action and measure
- static UI at / (index.html) that displays status and allows actions
Security:
- If env var RAM_GUARDIAN_WEB_SECRET is set, POST actions must provide Authorization: Bearer <secret>
- For destructive actions (quit/kill), an approval file must exist (env var RAM_GUARDIAN_APPROVAL_FILE, default /tmp/ram_guardian_approval)

Run: python3 5_INFRA/ram_guardian_webui.py
"""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory, abort

BASE_DIR = Path(__file__).resolve().parent
RG_PATH = str(BASE_DIR / "ram_guardian.py")

# load ram_guardian module via importlib to avoid package naming issues
spec = importlib.util.spec_from_file_location("ram_guardian", RG_PATH)
ram_guardian = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ram_guardian)

app = Flask(__name__, static_folder=str(BASE_DIR / "webui"))

METRICS_PATH = os.environ.get("RAM_GUARDIAN_METRICS_PATH", "/tmp/ram_guardian_metrics.jsonl")
WEB_SECRET = os.environ.get("RAM_GUARDIAN_WEB_SECRET", "")
APPROVAL_FILE = os.environ.get("RAM_GUARDIAN_APPROVAL_FILE", "/tmp/ram_guardian_approval")


def check_auth_required() -> bool:
    return bool(WEB_SECRET)


def is_authorized(req) -> bool:
    if not check_auth_required():
        return True
    auth = req.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        return token == WEB_SECRET
    return False


def require_approval() -> bool:
    return os.path.exists(APPROVAL_FILE)


@app.route("/api/status")
def status() -> Any:
    try:
        frac = ram_guardian.available_fraction()
        procs = ram_guardian.top_memory_procs(10)
        procs_out = [{"pid": p[0], "comm": p[1], "rss_bytes": p[2]} for p in procs]
        total = ram_guardian.total_memory_bytes()
        return jsonify({"available_fraction": frac, "total_bytes": total, "top_processes": procs_out})
    except Exception:
        return jsonify({"error": "failed to gather status"}), 500


@app.route("/api/metrics")
def metrics() -> Any:
    limit = int(request.args.get("limit", "50"))
    out = []
    if not os.path.exists(METRICS_PATH):
        return jsonify([])
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        for l in lines:
            try:
                out.append(json.loads(l))
            except Exception:
                continue
        return jsonify(out)
    except Exception:
        return jsonify({"error": "failed to read metrics"}), 500


@app.route("/api/action", methods=["POST"])
def action():
    payload = request.get_json() or {}
    kind = payload.get("action")
    target = payload.get("target")

    if kind not in ("estimate", "quit_app", "kill_pid"):
        return jsonify({"error": "unsupported action"}), 400

    if kind in ("quit_app", "kill_pid") and not is_authorized(request):
        return jsonify({"error": "unauthorized"}), 403

    if kind in ("quit_app", "kill_pid") and not require_approval():
        return jsonify({"error": "approval required (approval file missing)"}), 403

    # estimate (dry-run) path
    if kind == "estimate":
        procs = ram_guardian.top_memory_procs(20)
        est = ram_guardian.estimate_rss_sum(procs)
        return jsonify({"estimated_free_bytes": est, "by_kb": est // 1024})

    # quit app
    if kind == "quit_app":
        if not target:
            return jsonify({"error": "target missing"}), 400
        info = ram_guardian.perform_action_and_measure(lambda: ram_guardian.quit_app_by_name(target), timeout=payload.get("timeout", 10))
        info["action"] = "quit_app"
        info["target"] = target
        ram_guardian.append_metric_entry(info, path=METRICS_PATH)
        return jsonify(info)

    # kill pid
    if kind == "kill_pid":
        try:
            pid = int(target)
        except Exception:
            return jsonify({"error": "invalid pid"}), 400
        info = ram_guardian.perform_action_and_measure(lambda: ram_guardian.kill_pid(pid), timeout=payload.get("timeout", 10))
        info["action"] = "kill_pid"
        info["target"] = pid
        ram_guardian.append_metric_entry(info, path=METRICS_PATH)
        return jsonify(info)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/static/<path:path>")
def static_path(path):
    return send_from_directory(app.static_folder, path)


def main():
    port = int(os.environ.get("RAM_GUARDIAN_WEB_PORT", "8080"))
    print(f"Starting RAM Guardian WebUI on http://localhost:{port}")
    app.run(host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
