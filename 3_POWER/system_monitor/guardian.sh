#!/bin/bash
# 🐍 MAMBA GUARDIAN - Launcher
# Inicia el sistema de monitoreo y mata procesos

cd "$(dirname "$0")"

echo "🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍"
echo "   MAMBA GUARDIAN - Protector del Sistema"
echo "🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍"
echo ""

case "$1" in
    start)
        echo "🚀 Iniciando guardian en background..."
        nohup python3 mamba_guardian.py daemon > guardian_output.log 2>&1 &
        echo $! > guardian.pid
        echo "✅ Guardian iniciado (PID: $(cat guardian.pid))"
        echo "📝 Logs en: guardian.log y guardian_output.log"
        ;;
    stop)
        if [ -f guardian.pid ]; then
            PID=$(cat guardian.pid)
            echo "🛑 Deteniendo guardian (PID: $PID)..."
            kill $PID 2>/dev/null
            rm guardian.pid
            echo "✅ Guardian detenido"
        else
            echo "⚠️ Guardian no está corriendo"
        fi
        ;;
    status)
        python3 mamba_guardian.py status
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    logs)
        echo "📜 Últimas 20 líneas del log:"
        echo "─────────────────────────────"
        tail -20 guardian.log 2>/dev/null || echo "(sin logs aún)"
        ;;
    watch)
        echo "👁️ Modo watch (Ctrl+C para salir):"
        watch -n 2 "python3 mamba_guardian.py status 2>/dev/null | head -30"
        ;;
    *)
        echo "Uso: $0 {start|stop|status|restart|logs|watch}"
        echo ""
        echo "  start   - Iniciar guardian en background"
        echo "  stop    - Detener guardian"
        echo "  status  - Ver estado del sistema"
        echo "  restart - Reiniciar guardian"
        echo "  logs    - Ver últimos logs"
        echo "  watch   - Monitoreo en tiempo real"
        ;;
esac
