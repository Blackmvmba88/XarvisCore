#!/bin/bash

# 🦅 Preparación de Raspberry Pi - Launcher
# Prepara microSD con Arsenal Portátil de Xarvis

echo "🦅 XarvisCore - Preparación de Raspberry Pi"
echo "============================================"
echo ""

cd "$(dirname "$0")"

VENV="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"

if [ ! -f "$VENV" ]; then
    echo "❌ Entorno virtual no encontrado"
    exit 1
fi

echo "⚠️  ADVERTENCIA:"
echo "Este script va a:"
echo "  1. Detectar tu microSD"
echo "  2. FORMATEARLA (borrando todo)"
echo "  3. Copiar módulos de XarvisCore"
echo "  4. Preparar instalador para Raspberry Pi"
echo ""
echo "Asegúrate de tener la microSD correcta insertada"
echo ""

read -p "¿Continuar? (si/no): " confirm

if [ "$confirm" != "si" ] && [ "$confirm" != "SI" ]; then
    echo "Operación cancelada"
    exit 0
fi

echo ""
echo "🚀 Iniciando preparación..."
echo ""

sudo $VENV raspberry_pi_setup.py

echo ""
echo "✅ Proceso completado"
echo "Ver log completo en: logs/raspberry_setup.log"
