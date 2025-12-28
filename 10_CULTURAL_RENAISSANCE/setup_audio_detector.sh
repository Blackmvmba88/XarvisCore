#!/bin/bash
# Setup BlackMamba Audio Detector
# Arquitecto: Iyari Cancino Gomez

echo "🎵 BlackMamba Audio Detector - Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$(dirname "$0")"

# Activar venv
source ../venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install numpy

# Verificar chromaprint
if ! command -v fpcalc &> /dev/null; then
    echo "⚠️  Chromaprint no encontrado"
    echo "📦 Instalando chromaprint (audio fingerprinting)..."
    brew install chromaprint
fi

# Verificar sox (para grabar)
if ! command -v rec &> /dev/null; then
    echo "📦 Instalando sox (audio recording)..."
    brew install sox
fi

echo ""
echo "✅ Setup completo"
echo ""
echo "Uso:"
echo "  1. Indexar biblioteca:"
echo "     python3 audio_detector.py --index"
echo ""
echo "  2. Detectar canción (graba 10 seg):"
echo "     python3 audio_detector.py --detect 10"
echo ""
