#!/usr/bin/env bash
set -euo pipefail

# Run the RAM Guardian Web UI locally
PYTHON=${PYTHON:-python3}
PORT=${RAM_GUARDIAN_WEB_PORT:-8080}
$PYTHON 5_INFRA/ram_guardian_webui.py
