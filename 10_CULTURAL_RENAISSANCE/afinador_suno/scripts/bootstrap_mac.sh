#!/usr/bin/env bash
set -euo pipefail

# Bootstrap macOS for Afinador Suno
# NOTA: revisa cada paso antes de ejecutarlo

# Requisitos nativos
if ! command -v brew >/dev/null 2>&1; then
  echo "[!] Homebrew no está instalado. Instálalo desde https://brew.sh/"
  exit 1
fi

echo "[+] Instalando ffmpeg y libsndfile (si falta)"
brew list --formula ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list --formula libsndfile >/dev/null 2>&1 || brew install libsndfile

# Python venv
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -d .venv ]; then
  echo "[+] Creando venv"
  python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install -U pip wheel setuptools

# Instalación editable del proyecto (pyproject)
pip install -e .

echo "[✓] Listo. Para lanzar la UI:"
echo "    source .venv/bin/activate && python -m afinador_suno.ui.app"
