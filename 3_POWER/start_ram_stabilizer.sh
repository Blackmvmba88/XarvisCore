#!/bin/bash

# 🦅 RAM Stabilizer - Lanzador del Sistema de Estabilización de RAM

echo "🦅 Xarvis RAM Stabilizer"
echo "========================"
echo ""

cd "$(dirname "$0")"

VENV="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"

# Menú de opciones
echo "Selecciona modo:"
echo "1) Limpieza profunda AHORA (cierra apps, purge, libera todo)"
echo "2) Activar RAM Guardian (monitoreo continuo automático)"
echo "3) Ambos (limpieza + guardian)"
echo ""
read -p "Opción [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🧹 Ejecutando limpieza profunda..."
        echo "⚠️  Esto cerrará Spotify, Slack, renderers de ChatGPT/VSCode, etc."
        echo ""
        $VENV deep_ram_cleaner.py
        ;;
    2)
        echo ""
        echo "🛡️ Activando RAM Guardian..."
        echo "El sistema monitoreará y liberará RAM automáticamente"
        echo "Presiona Ctrl+C para detener"
        echo ""
        $VENV ram_guardian.py
        ;;
    3)
        echo ""
        echo "🔥 Limpieza profunda + Guardian continuo"
        echo ""
        
        # Primero limpieza
        echo "Paso 1/2: Limpieza profunda..."
        $VENV deep_ram_cleaner.py --auto
        
        echo ""
        echo "Paso 2/2: Activando guardian..."
        sleep 2
        $VENV ram_guardian.py
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac
