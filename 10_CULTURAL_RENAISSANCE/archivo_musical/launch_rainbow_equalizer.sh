#!/bin/zsh
# 🌈 BLACKMAMBA RAINBOW EQUALIZER LAUNCHER
# Lanza el ecualizador visual con onda sinusoidal rainbow
# ¿No crees que el audio merece ser arte visual?

echo "🌈 INICIANDO BLACKMAMBA RAINBOW EQUALIZER 🎵"
echo "============================================="

# Configuración
HTML_FILE="/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/rainbow_equalizer.html"
URL="file://$HTML_FILE"

# Verificar archivo
if [[ ! -f "$HTML_FILE" ]]; then
    echo "❌ Error: Archivo del ecualizador no encontrado"
    echo "📁 Buscando en: $HTML_FILE"
    exit 1
fi

echo "🎤 Ecualizador: Rainbow Sinusoidal"
echo "🎨 Modos: Ondas, Barras, Círculo, Espiral"
echo "⚡ Velocidades: Lento, Normal, Rápido, Turbo"
echo "🔊 Fuente: Micrófono Studio Mac"
echo ""

# Abrir en el navegador preferido
if command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" >/dev/null 2>&1; then
    echo "🌐 Abriendo en Google Chrome..."
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --new-window "$URL" --allow-running-insecure-content --disable-web-security --user-data-dir=/tmp/chrome-audio &
elif command -v "/Applications/Safari.app/Contents/MacOS/Safari" >/dev/null 2>&1; then
    echo "🌐 Abriendo en Safari..."
    open -a Safari "$URL" &
elif command -v firefox >/dev/null 2>&1; then
    echo "🌐 Abriendo en Firefox..."
    firefox "$URL" &
else
    echo "🌐 Abriendo en navegador por defecto..."
    open "$URL" &
fi

echo ""
echo "🎵 INSTRUCCIONES:"
echo "================="
echo "1️⃣  Haz clic en '🎤 Iniciar Micrófono'"
echo "2️⃣  Permite acceso al micrófono cuando aparezca"
echo "3️⃣  ¡Habla, canta o reproduce música!"
echo "4️⃣  Cambia modos con '🌊 Modo'"
echo "5️⃣  Ajusta velocidad con '⚡ Velocidad'"
echo ""
echo "🎨 MODOS DISPONIBLES:"
echo "===================="
echo "🌊 Ondas     - Ondas sinusoidales rainbow clásicas"
echo "📊 Barras    - Barras de frecuencia coloridas"
echo "⭕ Círculo   - Visualización circular"
echo "🌀 Espiral   - Espiral hipnótica"
echo ""
echo "⚠️  IMPORTANTE: Permite acceso al micrófono para ver la magia"
echo "🎧 CONSEJO: Usa auriculares para evitar retroalimentación"
echo ""
echo "🎵 ¡Disfruta tu ecualizador rainbow sinusoidal!"