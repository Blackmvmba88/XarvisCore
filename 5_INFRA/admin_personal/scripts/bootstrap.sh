#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON=$(command -v python3 || command -v python)

echo "[bootstrap] root: $ROOT_DIR"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python not found. Install Python 3 and re-run."
  exit 1
fi

# Create virtualenv
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtualenv at $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
fi

# Activate and install
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
if [[ -f "$ROOT_DIR/requirements.txt" ]]; then
  pip install -r "$ROOT_DIR/requirements.txt"
else
  echo "No requirements.txt found"
fi

# Frontend deps
if [[ -d "$ROOT_DIR/web" ]]; then
  if command -v npm >/dev/null 2>&1; then
    echo "Installing web dependencies (npm install)"
    (cd "$ROOT_DIR/web" && npm install)
  else
    echo "npm not found. Install Node.js / npm to use the WebUI."
  fi
fi

echo "Bootstrap complete. To activate env: source $VENV_DIR/bin/activate"
