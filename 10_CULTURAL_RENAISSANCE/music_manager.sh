#!/bin/bash
# BlackMamba Music Manager - Todo en Uno
# Dominio: 10_CULTURAL_RENAISSANCE

cd "$(dirname "$0")"

echo "🎵 BLACKMAMBA MUSIC MANAGER"
echo "============================================================"
echo ""
echo "📚 Tu Colección Musical: 194 canciones"
echo ""
echo "Selecciona una opción:"
echo ""
echo "  1) 🌐 Ver WebUI (navegador)"
echo "  2) 🎼 Generar Playlists básicas (M3U/M3U8/PLS)"
echo "  3) 🎲 Generar Playlists avanzadas (Shuffle, Año, Temas)"
echo "  4) 📋 Analizar origen (SoundCloud/Suno/Local)"
echo "  5) 📊 Ver estadísticas detalladas"
echo "  6) 📁 Organizar en carpeta única"
echo "  7) �️ Gestión de backups"
echo "  8) 🎧 Analizar calidad de audio"
echo "  9) 🔍 Buscar duplicados"
echo "  10) �🚪 Salir"
echo ""
read -p "Opción: " option

case $option in
    1)
        echo ""
        echo "🌐 Abriendo WebUI..."
        open music_webui.html
        echo "✅ WebUI iniciada"
        ;;
    2)
        echo ""
        python3 generate_playlists.py
        echo ""
        echo "📁 Abriendo carpeta de playlists..."
        open playlists/
        ;;
    3)
        echo ""
        python3 generate_advanced_playlists.py
        echo ""
        echo "📁 Abriendo carpeta de playlists..."
        open playlists/
        ;;
    4)
        echo ""
        python3 analyze_music_sources.py
        ;;
    5)
        echo ""
        python3 music_statistics.py
        ;;
    6)
        echo ""
        python3 organize_music.py
        ;;
    7)
        echo ""
        python3 music_backup_manager.py
        ;;
    8)
        echo ""
        python3 music_quality_analyzer.py
        ;;
    9)
        echo ""
        python3 music_duplicate_finder.py
        ;;
    10)
        echo ""
        echo "👋 ¡Hasta pronto!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "✅ Proceso completado"
echo ""
echo "💡 Tip: Ejecuta este script de nuevo para más opciones"
