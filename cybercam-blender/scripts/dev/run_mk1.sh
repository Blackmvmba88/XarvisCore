#!/usr/bin/env bash
set -euo pipefail

# Wrapper para crear plantilla y ensamblar MK1 headless
# Uso:
#   BLENDER_BIN=/opt/homebrew/bin/blender ./cybercam-blender/scripts/dev/run_mk1.sh
# O sin variable si Blender está en /opt/homebrew/bin/blender

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CYBERCAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPO_ROOT="$(cd "$CYBERCAM_ROOT/.." && pwd)"
BLENDER_BIN="${BLENDER_BIN:-/opt/homebrew/bin/blender}"
VENV_ACTIVATE="${VENV_ACTIVATE:-}"

if [ -n "$VENV_ACTIVATE" ] && [ -f "$VENV_ACTIVATE" ]; then
  echo "Activando venv: $VENV_ACTIVATE"
  # shellcheck source=/dev/null
  source "$VENV_ACTIVATE"
fi

echo "Usando blender: $BLENDER_BIN"

echo "1) Generando plantilla de piezas (cybercam_parts.blend)..."
"$BLENDER_BIN" --background --python "$CYBERCAM_ROOT/blend/create_parts_template.py" -- --output "$CYBERCAM_ROOT/blend/cybercam_parts.blend"

if [ ! -f "$CYBERCAM_ROOT/blend/cybercam_parts.blend" ]; then
  echo "ERROR: No se generó cybercam_parts.blend. Revisa errores anteriores." >&2
  exit 2
fi

echo "2) Ensamblando MK1 desde master (asegúrate que cybercam_master.blend contiene los ANCHOR_*)..."
if [ ! -f "$CYBERCAM_ROOT/blend/cybercam_master.blend" ]; then
  echo "ERROR: No se encontró cybercam_master.blend. Crea o añade el master en blend/cybercam_master.blend" >&2
  exit 3
fi
"$BLENDER_BIN" -b "$CYBERCAM_ROOT/blend/cybercam_master.blend" --python "$CYBERCAM_ROOT/scripts/build/assemble_cam.py" -- --preset=mk1 --screws=8 --cables=2 --render

echo "Hecho. Revisa $REPO_ROOT/exports/gltf para el .glb y $REPO_ROOT/exports/renders para renders (si se generaron)."
