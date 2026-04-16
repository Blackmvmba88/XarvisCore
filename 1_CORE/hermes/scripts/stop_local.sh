#!/usr/bin/env bash
pkill -f "services/api/app.py" || true
pkill -f "services/webui/server.py" || true
if command -v docker >/dev/null; then
  docker compose stop qdrant || true
fi
