#!/bin/bash

# 🦅 Network Optimizer Launcher
# Optimiza la red para Flight Simulator 2024

echo "🦅 Xarvis Network Priority Manager"
echo "===================================="
echo ""

cd "$(dirname "$0")"

VENV="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"

# Verificar si tenemos permisos de sudo
echo "⚠️  Este script requiere permisos de administrador"
echo "Se solicitará tu contraseña para configurar la red"
echo ""

# Opciones
echo "Selecciona modo:"
echo "1) Activar prioridad para Flight Simulator 2024"
echo "2) Monitoreo automático (activa cuando detecta el juego)"
echo "3) Desactivar prioridad de red"
echo ""
read -p "Opción [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Activando prioridad de red para Flight Simulator..."
        sudo $VENV network_priority_manager.py enable
        echo ""
        echo "✅ ¡Listo para volar con conexión optimizada!"
        echo ""
        echo "Para desactivar: bash start_network_optimizer.sh → opción 3"
        ;;
    2)
        echo ""
        echo "👁️ Iniciando monitoreo automático..."
        echo "El sistema activará prioridad cuando detecte Flight Simulator"
        echo "Presiona Ctrl+C para detener"
        echo ""
        sudo $VENV network_priority_manager.py monitor
        ;;
    3)
        echo ""
        echo "🔄 Desactivando prioridad de red..."
        sudo $VENV network_priority_manager.py disable
        echo ""
        echo "✅ Red en modo normal"
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac
