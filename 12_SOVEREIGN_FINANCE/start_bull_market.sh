#!/bin/bash

# 🐂 BULL MARKET INTELLIGENCE LAUNCHER
# Sistema de Inversión Inteligente

echo "🐂 BULL MARKET INTELLIGENCE SYSTEM"
echo "======================================"

cd "$(dirname "$0")"

VENV_PYTHON="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"

# Instalar/verificar dependencias
echo "📦 Instalando dependencias financieras..."

$VENV_PYTHON -m pip install --quiet --upgrade pip

# Dependencias core
$VENV_PYTHON -m pip install --quiet yfinance pandas numpy flask flask-cors

echo "✅ Dependencias instaladas"
echo ""
echo "💰 Iniciando Sistema de Inversión..."
echo "🌐 WebUI: http://localhost:7777"
echo "======================================"
echo ""

# Lanzar sistema
$VENV_PYTHON bull_market_intelligence.py
