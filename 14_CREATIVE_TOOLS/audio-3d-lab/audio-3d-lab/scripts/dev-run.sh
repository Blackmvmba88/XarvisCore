#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -d ".venv" ]]; then
  /opt/homebrew/bin/python3 -m venv .venv || /usr/local/bin/python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .

echo "[dev-run] Lanzando audio3d-cube..."
exec audio3d-cube "$@"
