#!/bin/bash

# 🦅 SUNO AUTOPIPELINE LAUNCHER
# Lanza el pipeline automático de procesamiento de canciones Suno

echo "🦅 BlackMamba Suno AutoPipeline"
echo "================================"
echo ""

cd "$(dirname "$0")"

# Verificar venv
VENV="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"
if [ ! -f "$VENV" ]; then
    echo "❌ Entorno virtual no encontrado"
    echo "Ejecuta: python3 -m venv /Users/blackmamba/Desktop/XarvisCore/venv"
    exit 1
fi

# Ejecutar pipeline
echo "🚀 Iniciando pipeline..."
echo ""

$VENV suno_autopipeline.py

echo ""
echo "✅ Pipeline completado"
echo "Ver logs en: suno_pipeline.log"
