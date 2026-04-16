#!/bin/bash
# 🎬 BlackMamba Cinema Launcher
# Netflix para Pobres con Inteligencia
# Arquitecto: Iyari Cancino Gomez

echo "🎬 BlackMamba Cinema"
echo "Netflix para Pobres con Inteligencia"
echo "======================================"

cd "$(dirname "$0")"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python3 -c "import flask, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias..."
    pip3 install flask flask-cors
fi

# Verificar si hay catálogo
if [ ! -f "cinema_catalog.json" ]; then
    echo ""
    echo "📚 Primera ejecución: Escaneando tu biblioteca de películas..."
    python3 blackmamba_cinema.py --scan
    echo ""
fi

# Iniciar servidor
echo "🚀 Iniciando BlackMamba Cinema..."
echo "🌐 Abre tu navegador en: http://localhost:5001"
echo ""
echo "💡 Después del trabajo, relájate y disfruta tus películas"
echo "   Presiona Ctrl+C para detener"
echo ""

python3 blackmamba_cinema.py
