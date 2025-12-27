#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

# Start backend (uvicorn) in background
if [[ -d "$VENV_DIR" ]]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  echo "Starting backend (uvicorn)..."
  nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > "$ROOT_DIR/logs/uvicorn.out" 2>&1 &
else
  echo "Virtualenv not found at $VENV_DIR. Run scripts/bootstrap.sh first."
fi

# Start frontend (vite) in background (if exists)
if [[ -d "$ROOT_DIR/web" ]]; then
  if command -v npm >/dev/null 2>&1; then
    echo "Starting frontend (vite)..."
    (cd "$ROOT_DIR/web" && nohup npm run dev > "$ROOT_DIR/logs/vite.out" 2>&1 &)
  else
    echo "npm not found; frontend not started"
  fi
fi

echo "Services started (background). Check logs in $ROOT_DIR/logs/"
