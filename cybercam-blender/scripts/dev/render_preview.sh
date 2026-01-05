#!/usr/bin/env bash
set -euo pipefail

# Quick preview render (Eevee, 1 frame)
# Usage: BLENDER_BIN=/opt/homebrew/bin/blender ./scripts/dev/render_preview.sh [preset]

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BLENDER_BIN="${BLENDER_BIN:-/opt/homebrew/bin/blender}"
PRESET="${1:-mk1}"

echo "Using blender: $BLENDER_BIN"

$BLENDER_BIN -b "$REPO_ROOT/blend/cybercam_master.blend" --python "$REPO_ROOT/scripts/build/assemble_cam.py" -- --preset "$PRESET" --screws 8 --cables 2 --render --render-preset preview --render-frames 1 --render-width 1024 --render-height 1024

OUT_DIR="$REPO_ROOT/exports/renders/$PRESET"
if [ -d "$OUT_DIR" ]; then
  echo "Preview rendered to: $OUT_DIR"
  ls -la "$OUT_DIR" | sed -n '1,10p'
  # Try to open the generated PNG on macOS
  if command -v open >/dev/null 2>&1; then
    PNG=$(ls "$OUT_DIR"/*.png 2>/dev/null | head -n1 || true)
    if [ -n "$PNG" ]; then
      echo "Opening $PNG"
      open "$PNG"
    fi
  fi
else
  echo "No output directory found: $OUT_DIR" >&2
  exit 1
fi
