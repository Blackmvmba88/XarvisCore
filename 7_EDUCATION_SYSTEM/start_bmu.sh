#!/bin/bash
# BlackMamba University Platform Launcher
# Arquitecto: Iyari Cancino Gomez

BASE_DIR="/Users/blackmamba/Desktop/XarvisCore"
BMU_DIR="$BASE_DIR/7_EDUCATION_SYSTEM"
VENV_PYTHON="$BASE_DIR/venv/bin/python3"
LOG_FILE="$BMU_DIR/bmu_server.log"

echo "🎓 BlackMamba University Platform"
echo "=" * 60
echo "Iniciando servidor en puerto 7000..."
echo "Accede en: http://localhost:7000"
echo "=" * 60

cd "$BMU_DIR" && "$VENV_PYTHON" bmu_platform.py
