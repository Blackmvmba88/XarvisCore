#!/bin/bash
# BlackMamba Music Performance Suite Launcher
# Dominio: 10_CULTURAL_RENAISSANCE

cd "$(dirname "$0")"

echo "🎵 BLACKMAMBA MUSIC PERFORMANCE SUITE"
echo "============================================================"
echo ""
echo "🚀 Iniciando servidor integrado..."
echo "   - VPA (Vocal Performance Analyzer)"
echo "   - BlackMamba Audio Detector"
echo "   - Music Library (194 canciones)"
echo ""
echo "📡 Servidor: http://localhost:9002"
echo "⌨️  Presiona Ctrl+C para detener"
echo ""
echo "============================================================"
echo ""

# Activar venv si existe
if [ -d "../../venv" ]; then
    source ../../venv/bin/activate
fi

# Iniciar servidor
python3 music_performance_suite.py
