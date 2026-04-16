#!/usr/bin/env bash
set -euo pipefail

# Hero render (Cycles final preset) — single high-res frame for screenshots
# Usage: BLENDER_BIN=/opt/homebrew/bin/blender ./scripts/dev/render_hero.sh [preset]

# cybercam-blender root (this folder)
CYBERCAM_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# monorepo root (exports/, 20_BLENDER_INTEGRATION/, etc.)
REPO_ROOT="$(cd "$CYBERCAM_ROOT/.." && pwd)"
BLENDER_BIN="${BLENDER_BIN:-/opt/homebrew/bin/blender}"
PRESET="${1:-mk1}"

echo "Using blender: $BLENDER_BIN"

$BLENDER_BIN -b "$CYBERCAM_ROOT/blend/cybercam_master.blend" --python "$CYBERCAM_ROOT/scripts/build/assemble_cam.py" -- --preset "$PRESET" --screws 12 --cables 3 --render --render-preset final --render-frames 1 --render-width 2048 --render-height 2048

OUT_DIR="$REPO_ROOT/exports/renders/$PRESET"
if [ -d "$OUT_DIR" ]; then
  echo "Hero render produced: $OUT_DIR"
  ls -la "$OUT_DIR" | sed -n '1,10p'
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
