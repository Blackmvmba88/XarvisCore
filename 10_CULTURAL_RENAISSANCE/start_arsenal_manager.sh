#!/bin/bash

# 🦅 BLACKMAMBA ARSENAL MANAGER LAUNCHER
# Lanzador con instalación automática de dependencias

echo "🦅 BLACKMAMBA ARSENAL MANAGER"
echo "======================================"

cd "$(dirname "$0")"

VENV_PYTHON="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"

# Verificar/instalar dependencias
echo "📦 Verificando dependencias..."

if ! $VENV_PYTHON -c "import mutagen" 2>/dev/null; then
    echo "⚙️  Instalando mutagen..."
    $VENV_PYTHON -m pip install mutagen --quiet
fi

if ! $VENV_PYTHON -c "import flask" 2>/dev/null; then
    echo "⚙️  Instalando Flask..."
    $VENV_PYTHON -m pip install flask flask-cors --quiet
fi

echo "✅ Dependencias listas"
echo ""
echo "🌐 Iniciando WebUI en http://localhost:8888"
echo "======================================"
echo ""

# Lanzar servidor
$VENV_PYTHON arsenal_manager_webui.py
