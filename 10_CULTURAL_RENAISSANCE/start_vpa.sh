#!/bin/bash
# Script de inicio rápido para Vocal Performance Analyzer
# Autor: Iyari Cancino Gomez
# Dominio: 10_CULTURAL_RENAISSANCE

echo "🎤 Iniciando Vocal Performance Analyzer..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar dependencias
echo "📋 Verificando dependencias..."

# Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 OK"

# Shazam Desktop
if [ ! -d "$HOME/Library/Application Support/Shazam" ]; then
    echo -e "${YELLOW}⚠️  Shazam Desktop no encontrado${NC}"
    echo "   Descarga de: https://www.shazam.com/apps"
    echo "   O continúa sin detección automática"
else
    echo -e "${GREEN}✓${NC} Shazam Desktop OK"
fi

# Activar venv si existe
if [ -d "../../venv" ]; then
    source ../../venv/bin/activate
    echo -e "${GREEN}✓${NC} Entorno virtual activado"
else
    echo -e "${YELLOW}⚠️  No se encontró venv, usando Python del sistema${NC}"
fi

# Verificar e instalar dependencias Python
echo ""
echo "📦 Verificando paquetes Python..."
pip3 list | grep -q flask || pip3 install flask flask-cors requests
echo -e "${GREEN}✓${NC} Paquetes instalados"

# Crear directorios necesarios
mkdir -p lyrics_cache
mkdir -p performance_logs
echo -e "${GREEN}✓${NC} Directorios creados"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🚀 Lanzando VPA Server en puerto 9000...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard: http://localhost:9000/status"
echo "🎨 WebUI: Abre vpa_dashboard.html en tu navegador"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Iniciar servidor
python3 vocal_performance_analyzer.py
