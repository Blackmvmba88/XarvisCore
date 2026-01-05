#!/bin/bash

echo "🦅 BlackMamba LocalTube"
echo "================================"
echo "Reproductor de Videos Sin Lag"
echo "================================"
echo ""

# Verificar USB
if [ ! -d "/Volumes/ADATA SC740" ]; then
    echo "❌ Error: USB no encontrado"
    echo "Conecta el USB y vuelve a intentar"
    exit 1
fi

# Activar venv
cd /Users/blackmamba/Desktop/XarvisCore
source venv/bin/activate

# Ir a directorio de herramientas
cd 14_CREATIVE_TOOLS

echo "🔍 Verificando servidor..."
if lsof -Pi :8888 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Servidor ya está corriendo en puerto 8888"
    echo "Abriendo interfaz..."
else
    echo "🚀 Iniciando servidor LocalTube..."
    python3 local_youtube_server.py &
    SERVER_PID=$!
    
    # Esperar a que el servidor inicie
    sleep 3
    
    echo "✅ Servidor iniciado (PID: $SERVER_PID)"
fi

echo ""
echo "🌐 Abriendo LocalTube en el navegador..."
sleep 1
open "http://localhost:8888"

echo ""
echo "================================"
echo "✅ LocalTube está funcionando!"
echo "================================"
echo ""
echo "📺 Interfaz: http://localhost:8888"
echo "🎬 Total de videos: ~4,000 en USB"
echo ""
echo "⌨️  Presiona Ctrl+C para detener"
echo ""

# Mantener el script corriendo
if [ ! -z "$SERVER_PID" ]; then
    wait $SERVER_PID
fi
