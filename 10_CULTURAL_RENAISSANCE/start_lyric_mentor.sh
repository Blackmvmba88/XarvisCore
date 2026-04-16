#!/bin/bash
# 🎤 BlackMamba Lyric Mentor Launcher
# Arquitecto: Iyari Cancino Gomez

echo "🎤 BlackMamba Lyric Mentor"
echo "=========================="

cd "$(dirname "$0")"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python3 -c "import requests, langdetect" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias..."
    pip3 install requests langdetect
fi

# Verificar perfiles
if [ ! -f "lyric_style_profile_multi.json" ]; then
    echo ""
    echo "📚 Primera ejecución: Se necesita analizar tu estilo"
    echo "Esto estudiará tus canciones y tomará ~5-10 minutos"
    echo ""
    read -p "¿Ejecutar análisis ahora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        python3 lyric_mentor.py --analyze
    else
        echo "⚠️  Ejecuta: python3 lyric_mentor.py --analyze"
        exit 0
    fi
fi

# Ejecutar mentor
echo "🚀 Iniciando mentor interactivo..."
python3 lyric_mentor.py
