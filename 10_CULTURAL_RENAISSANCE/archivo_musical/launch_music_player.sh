#!/bin/zsh
# 🎼 LANZADOR BLACKMAMBA MUSIC PLAYER
# Script para iniciar el reproductor musical web
# ¿No crees que mereces un lanzador profesional?

echo "🎼 BLACKMAMBA MUSIC PLAYER LAUNCHER 🐍"
echo "======================================="

# Verificar que el USB está conectado
if [[ ! -d "/Volumes/ADATA SC740" ]]; then
    echo "❌ USB ADATA SC740 no detectado"
    echo "🔌 Asegúrate de que tu USB esté conectado"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado"
    echo "📦 Instala Python 3 para continuar"
    exit 1
fi

# Función para verificar puerto disponible
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 1  # Puerto ocupado
    else
        return 0  # Puerto disponible
    fi
}

# Buscar puerto disponible
MUSIC_PORT=8888
while ! check_port $MUSIC_PORT; do
    echo "⚠️ Puerto $MUSIC_PORT ocupado, probando $(($MUSIC_PORT + 1))..."
    MUSIC_PORT=$(($MUSIC_PORT + 1))
done

echo "✅ Usando puerto: $MUSIC_PORT"
echo ""

# Mostrar información del sistema
echo "📊 INFORMACIÓN DEL SISTEMA"
echo "--------------------------"
echo "🎵 Total MP3: $(find '/Volumes/ADATA SC740' -name '*.mp3' 2>/dev/null | wc -l | tr -d ' ')"
echo "💎 Total WAV: $(find '/Volumes/ADATA SC740' -name '*.wav' 2>/dev/null | wc -l | tr -d ' ')"
echo "🎛️ Total MIDI: $(find '/Volumes/ADATA SC740' -name '*.mid*' 2>/dev/null | wc -l | tr -d ' ')"
echo ""

# Función para cleanup al salir
cleanup() {
    echo ""
    echo "🧹 Cerrando servidor de música..."
    jobs -p | xargs kill 2>/dev/null
    echo "👋 ¡Hasta la vista!"
}

trap cleanup EXIT INT TERM

echo "🚀 INICIANDO REPRODUCTOR MUSICAL..."
echo "===================================="
echo ""
echo "🎧 El reproductor se abrirá automáticamente en tu navegador"
echo "🌐 URL: http://localhost:$MUSIC_PORT"
echo ""
echo "⌨️  CONTROLES:"
echo "   • Barra espaciadora = Play/Pausa"
echo "   • ← → = Canción anterior/siguiente"
echo "   • Ctrl+C = Cerrar reproductor"
echo ""
echo "🔄 Presiona Ctrl+C para detener..."
echo ""

# Cambiar al directorio del servidor
cd "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA"

# Iniciar servidor de música
python3 music_server.py &
SERVER_PID=$!

# Esperar a que termine el servidor o reciba señal
wait $SERVER_PID