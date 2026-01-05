#!/bin/bash
# 🎬 BlackMamba Cinema AI - Launcher con Inteligencia Real
# Arquitecto: Iyari Cancino Gomez

echo "🎬 BlackMamba Cinema AI - Iniciando sistema inteligente..."

# Verificar Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instalando..."
    brew install python3
fi

# Verificar ffprobe (parte de ffmpeg) - CRÍTICO para análisis
if ! command -v ffprobe &> /dev/null; then
    echo "⚡ ffprobe no encontrado. Instalando ffmpeg..."
    brew install ffmpeg
fi

# Instalar dependencias
echo "📦 Verificando dependencias..."
pip3 install flask flask-cors --quiet

# Verificar/crear catálogo
CATALOG_FILE="cinema_catalog_ai.json"
if [ ! -f "$CATALOG_FILE" ]; then
    echo "📁 Primera ejecución - escaneando biblioteca..."
    echo "⏳ Esto puede tomar varios minutos (analizando calidad de cada video)..."
fi

# Lanzar servidor AI
echo "🚀 Iniciando BlackMamba Cinema AI..."
echo ""
echo "✨ CAPA DE INTELIGENCIA ACTIVADA:"
echo "   • Análisis de duración (>60 min = película)"
echo "   • Detección de calidad (resolución, bitrate)"
echo "   • Identificación de idioma y subtítulos"
echo "   • Clasificación automática (película/serie/corto)"
echo ""
echo "🌐 Abre: http://localhost:5001"
echo "🎯 API: http://localhost:5001/api/movies/valid (solo películas reales)"
echo ""

python3 blackmamba_cinema_ai.py
