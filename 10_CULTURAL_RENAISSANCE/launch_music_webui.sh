#!/bin/bash
# Launcher para BlackMamba Music WebUI
# Dominio: 10_CULTURAL_RENAISSANCE

cd "$(dirname "$0")"

echo "🎵 BLACKMAMBA MUSIC WEBUI"
echo "============================================================"

# Verificar que existe music_library.json
if [ ! -f "music_library.json" ]; then
    echo "❌ Error: music_library.json no encontrado"
    exit 1
fi

# Contar canciones
TOTAL=$(cat music_library.json | grep -c '"song_name"')
echo "📚 Canciones en biblioteca: $TOTAL"

# Abrir en navegador
if command -v open &> /dev/null; then
    echo "🌐 Abriendo en navegador..."
    open music_webui.html
elif command -v xdg-open &> /dev/null; then
    xdg-open music_webui.html
else
    echo "📁 Archivo: $(pwd)/music_webui.html"
fi

echo "✅ WebUI iniciada"
echo ""
echo "💡 Para organizar tus canciones en una carpeta única:"
echo "   python3 organize_music.py"
