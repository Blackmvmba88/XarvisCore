#!/usr/bin/env bash
set -e

# Ensure Ollama is installed
if ! command -v ollama >/dev/null 2>&1; then
  brew install ollama
fi

# Pull default model
ollama pull llama3.1:8b

echo "[OK] Ollama model ready."
