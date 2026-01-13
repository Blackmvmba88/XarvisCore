#!/usr/bin/env bash
# Wrapper simple para usar identify_processes.py
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/identify_processes.py"
python3 "$PY" "$@"
