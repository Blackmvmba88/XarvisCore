#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export HOMEBREW_NO_AUTO_UPDATE=1

echo "[bundle] Instalando fórmulas del Brewfile..."
brew bundle --file=Brewfile

echo "[bundle] Verificando librerías clave..."
brew list --versions portaudio libsndfile qt || true

echo "[bundle] Preparando entorno Python..."
if [[ ! -d ".venv" ]]; then
  /opt/homebrew/bin/python3 -m venv .venv || /usr/local/bin/python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .

echo "[bundle] Sanity check de imports..."
python - <<'PY'
import sys
mods = ["soundfile","sounddevice","librosa","PyQt6","pyqtgraph","OpenGL"]
for m in mods:
    try:
        __import__(m)
        print(f"[ok] {m}")
    except Exception as e:
        print(f"[faltante] {m}", e, file=sys.stderr)
PY

echo "[bundle] Listo."
