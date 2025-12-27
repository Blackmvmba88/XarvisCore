#!/usr/bin/env bash
set -euo pipefail
# Rotate today’s telemetry to dated file (if not already) and keep last symlink
DIR="${1:-data/memory}"
STAMP=$(date +%Y%m%d)
DAILY="$DIR/telemetry-$STAMP.jsonl"
CURRENT="$DIR/telemetry.jsonl"
mkdir -p "$DIR"
# If current exists and daily doesn’t, move current to daily and recreate current
if [ -f "$CURRENT" ] && [ ! -f "$DAILY" ]; then
  cp "$CURRENT" "$DAILY"
fi
ln -sf "telemetry-$STAMP.jsonl" "$DIR/telemetry-latest.jsonl"
echo "Telemetry rotated/symlinked: $DAILY"
