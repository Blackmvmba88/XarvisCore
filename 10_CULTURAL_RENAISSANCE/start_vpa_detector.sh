#!/bin/bash
# Quick Start: VPA + BlackMamba Audio Detector
# Arquitecto: Iyari Cancino Gomez

echo "🎵 Iniciando VPA + BlackMamba Audio Detector"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$(dirname "$0")"

# Activar venv
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
else
    echo "❌ Virtual environment no encontrado"
    exit 1
fi

# Verificar dependencias
echo "🔍 Verificando dependencias..."

if ! command -v fpcalc &> /dev/null; then
    echo "⚠️  Chromaprint no instalado"
    echo "Instalar con: brew install chromaprint"
    exit 1
fi

if ! command -v rec &> /dev/null; then
    echo "⚠️  SoX no instalado"
    echo "Instalar con: brew install sox"
    exit 1
fi

# Verificar numpy
python3 -c "import numpy" 2>/dev/null || {
    echo "📦 Instalando numpy..."
    pip install numpy
}

echo ""
echo "✅ Dependencias OK"
echo ""

# Verificar si hay fingerprints indexados
if [ ! -f "audio_fingerprints.json" ]; then
    echo "⚠️  No hay fingerprints indexados"
    echo ""
    echo "¿Quieres indexar la biblioteca ahora? (S/n)"
    read -r response
    if [ "$response" != "n" ]; then
        echo "🔍 Indexando biblioteca..."
        python3 audio_detector.py --index
    fi
    echo ""
fi

# Iniciar servidor
echo "🚀 Iniciando servidor VPA + Detector en puerto 9001..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 vpa_with_detector.py
