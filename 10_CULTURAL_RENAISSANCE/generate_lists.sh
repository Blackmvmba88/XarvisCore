#!/bin/bash
# Generador Rápido de Listas BlackMamba
# Dominio: 10_CULTURAL_RENAISSANCE

cd "$(dirname "$0")"

echo "🎵 BLACKMAMBA MUSIC - GENERADOR DE LISTAS"
echo "============================================================"

# Ejecutar analizador
python3 analyze_music_sources.py

echo ""
echo "✅ Listas generadas!"
echo ""
echo "📁 Ubicación: music_lists/"
echo "   • soundcloud_songs.txt - Canciones de SoundCloud"
echo "   • suno_songs.txt - Canciones de Suno"
echo "   • local_songs.txt - Canciones locales"
echo ""
echo "📊 Reporte completo: music_sources_report.json"
