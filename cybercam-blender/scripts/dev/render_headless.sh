#!/usr/bin/env bash
set -euo pipefail

# Headless render wrapper for Cybercam
# Usage examples:
#   BLENDER_BIN=/opt/homebrew/bin/blender ./scripts/dev/render_headless.sh --preset mk1
#   BLENDER_BIN=/opt/homebrew/bin/blender ./scripts/dev/render_headless.sh --preset mk1 --frames 36 --render-preset final --width 2048 --height 2048
#   To skip rendering (only assemble + export GLB): add --no-render

# cybercam-blender root (this folder)
CYBERCAM_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# monorepo root (exports/, 20_BLENDER_INTEGRATION/, etc.)
REPO_ROOT="$(cd "$CYBERCAM_ROOT/.." && pwd)"
BLENDER_BIN="${BLENDER_BIN:-/opt/homebrew/bin/blender}"

# Defaults
PRESET="mk1"
SCREWS=8
CABLES=2
FRAMES=36
WIDTH=1024
HEIGHT=1024
RENDER_PRESET="preview"
IMAGE_FORMAT="PNG"
NO_RENDER=0
TIMESTAMP_OUTPUT=0
USE_GPU=0
LOG_FILE=""

# Simple arg parsing
while [[ $# -gt 0 ]]; do
  case "$1" in
    --preset) PRESET="$2"; shift 2;;
    --screws) SCREWS="$2"; shift 2;;
    --cables) CABLES="$2"; shift 2;;
    --frames) FRAMES="$2"; shift 2;;
    --width) WIDTH="$2"; shift 2;;
    --height) HEIGHT="$2"; shift 2;;
    --render-preset) RENDER_PRESET="$2"; shift 2;;
    --format) IMAGE_FORMAT="$2"; shift 2;;
    --no-render) NO_RENDER=1; shift 1;;
    --timestamped-output) TIMESTAMP_OUTPUT=1; shift 1;;
    --use-gpu) USE_GPU=1; shift 1;;
    --log-file) LOG_FILE="$2"; shift 2;;
    -h|--help) echo "Usage: $0 [--preset mk1] [--frames N] [--width W] [--height H] [--render-preset preview|final] [--no-render] [--timestamped-output] [--use-gpu] [--log-file /path/to/log]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

echo "Using Blender: $BLENDER_BIN"

# Build command parts; allow optional pre-scripts (GPU enabler)
ASSEMBLE_CMD=("$BLENDER_BIN" -b "$CYBERCAM_ROOT/blend/cybercam_master.blend")

# if requested, add GPU enabler script before the assemble script so it runs first
if [[ "$USE_GPU" -eq 1 ]]; then
  ENABLE_GPU_PY="$CYBERCAM_ROOT/scripts/dev/enable_cycles_gpu.py"
  if [[ -f "$ENABLE_GPU_PY" ]]; then
    ASSEMBLE_CMD+=(--python "$ENABLE_GPU_PY")
  else
    echo "Warning: --use-gpu requested but $ENABLE_GPU_PY not found; continuing without GPU enable step"
  fi
fi

# main assemble script
ASSEMBLE_CMD+=(--python "$CYBERCAM_ROOT/scripts/build/assemble_cam.py" -- --preset "$PRESET" --screws "$SCREWS" --cables "$CABLES")

if [[ "$NO_RENDER" -eq 0 ]]; then
  ASSEMBLE_CMD+=(--render --render-preset "$RENDER_PRESET" --render-frames "$FRAMES" --render-width "$WIDTH" --render-height "$HEIGHT" --render-format "$IMAGE_FORMAT")
else
  echo "--no-render set: will only assemble and export GLB"
fi

# If log file requested, redirect full stdout/stderr to it while still printing to console
if [[ -n "$LOG_FILE" ]]; then
  echo "Logging output to: $LOG_FILE"
fi

echo "Running assemble + optional render for preset: $PRESET"
# Print command for debugging
echo "Command: ${ASSEMBLE_CMD[*]}"

# Execute (optionally capture log)
if [[ -n "$LOG_FILE" ]]; then
  # tee both stdout and stderr
  "${ASSEMBLE_CMD[@]}" 2>&1 | tee "$LOG_FILE"
else
  "${ASSEMBLE_CMD[@]}"
fi

# Report output
OUT_DIR="$REPO_ROOT/exports/renders/$PRESET"
GLB_DIR="$REPO_ROOT/exports/gltf"

# If requested, timestamp the output dir (move it to preserve previous runs)
if [[ "$TIMESTAMP_OUTPUT" -eq 1 ]]; then
  TS=$(date -u +"%Y%m%dT%H%M%SZ")
  if [[ -d "$OUT_DIR" ]]; then
    NEW_OUT_DIR="${OUT_DIR}-${TS}"
    echo "Timestamping output: moving $OUT_DIR -> $NEW_OUT_DIR"
    mv "$OUT_DIR" "$NEW_OUT_DIR"
    OUT_DIR="$NEW_OUT_DIR"
  fi
  if [[ -d "$GLB_DIR" ]]; then
    # move any GLB exports for this preset into a timestamped subdir for traceability
    mkdir -p "$GLB_DIR/timestamped"
    for f in "$GLB_DIR/${PRESET}"*.glb; do
      [[ -e "$f" ]] || break
      mv "$f" "$GLB_DIR/timestamped/$(basename "$f" .glb)-${TS}.glb"
    done
  fi
fi

if [[ -d "$GLB_DIR" ]]; then
  echo "GLB exports (recent):"
  ls -la "$GLB_DIR" | sed -n '1,20p'
fi

if [[ "$NO_RENDER" -eq 0 ]]; then
  if [[ -d "$OUT_DIR" ]]; then
    echo "Rendered frames in: $OUT_DIR"
    ls -la "$OUT_DIR" | sed -n '1,20p'
  else
    echo "No render output found at: $OUT_DIR" >&2
  fi
fi

# macOS convenience: open the first PNG if available
if command -v open >/dev/null 2>&1; then
  if [[ -d "$OUT_DIR" ]] && compgen -G "$OUT_DIR/*.png" >/dev/null; then
    PNG=$(ls "$OUT_DIR"/*.png | head -n1)
    echo "Opening $PNG"
    open "$PNG"
  fi
fi
