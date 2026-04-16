#!/bin/bash
# 🐂 BULL MARKET INTELLIGENCE - LAUNCHER OPTIMIZADO
# Sistema robusto de inversión con análisis de Nash

echo "🐂 BULL MARKET INTELLIGENCE SYSTEM"
echo "======================================"

BASE_DIR="/Users/blackmamba/Desktop/XarvisCore/12_SOVEREIGN_FINANCE"
VENV_PYTHON="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"
VENV_PIP="/Users/blackmamba/Desktop/XarvisCore/venv/bin/pip"

cd "$BASE_DIR" || exit 1

# Verificar que exista el script
if [ ! -f "bull_market_intelligence.py" ]; then
    echo "❌ Error: bull_market_intelligence.py no encontrado"
    exit 1
fi

# Verificar Python
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Python venv no encontrado"
    exit 1
fi

# Validación rápida de dependencias
echo "📦 Verificando dependencias..."

check_dependency() {
    if $VENV_PYTHON -c "import $1" 2>/dev/null; then
        echo "✅ $1"
        return 0
    else
        echo "⚠️ $1 no instalado"
        return 1
    fi
}

MISSING=0

check_dependency "flask" || MISSING=$((MISSING + 1))
check_dependency "flask_cors" || MISSING=$((MISSING + 1))
check_dependency "pandas" || MISSING=$((MISSING + 1))
check_dependency "numpy" || MISSING=$((MISSING + 1))
check_dependency "yfinance" || MISSING=$((MISSING + 1))

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "📥 Instalando $MISSING dependencias faltantes..."
    $VENV_PIP install --quiet flask flask-cors pandas numpy yfinance
    echo "✅ Dependencias instaladas"
fi

echo ""
echo "💰 Iniciando Bull Market Intelligence..."
echo "🎮 Análisis de Nash habilitado"
echo "📊 Indicadores técnicos: SMA, RSI, MACD, Bollinger"
echo "🌐 WebUI: http://localhost:7777"
echo "======================================"
echo ""

# Limpiar caché de puerto si existe
lsof -ti:7777 | xargs kill -9 2>/dev/null

# Iniciar servidor
$VENV_PYTHON bull_market_intelligence.py
