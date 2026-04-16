#!/usr/bin/env bash
set -e

if ! command -v brew >/dev/null; then
  echo "Instala Homebrew primero: https://brew.sh"; exit 1
fi

# Base
brew install python@3.11 cmake pkg-config ffmpeg || true

# (Opcional) Qdrant local con Docker
if ! command -v docker >/dev/null; then
  echo "Docker no detectado. Puedes instalar Docker Desktop para usar Qdrant en contenedor."
fi

# Ollama para modelos locales
if ! command -v ollama >/dev/null; then
  brew install ollama || true
fi

# Modelos base mínimos
ollama pull llama3.1:8b || true

# Venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r services/api/requirements.txt
pip install -r services/rag/requirements.txt

echo "[OK] Bootstrap completado."
