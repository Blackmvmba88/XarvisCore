#!/usr/bin/env python3
"""
Analizador de Origen de Canciones - BlackMamba
Identifica qué canciones vienen de SoundCloud, Suno u otras fuentes
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import json
from pathlib import Path
from collections import Counter

# === CONFIGURACIÓN ===
MUSIC_LIBRARY = Path(__file__).parent / "music_library.json"
OUTPUT_FILE = Path(__file__).parent / "music_sources_report.json"

# Patrones para identificar origen
SOUNDCLOUD_PATTERNS = [
    'soundcloud',
    'SC-',  # Prefix común de descargas de SoundCloud
]

SUNO_PATTERNS = [
    'suno',
    'Suno',
    '(Intro)',
    '(Verse',
    '(Chorus',
    '(Bridge',
    '(Outro',
]

def detect_source(song):
    """Detecta el origen de una canción."""
    title = song.get('title', '').lower()
    song_name = song.get('song_name', '').lower()
    
    # Buscar en rutas de archivos
    paths = []
    for format_type, format_data in song.get('formats', {}).items():
        if isinstance(format_data, dict):
            paths.append(format_data.get('path', '').lower())
    
    all_text = f"{title} {song_name} {' '.join(paths)}"
    
    # Detectar SoundCloud
    for pattern in SOUNDCLOUD_PATTERNS:
        if pattern.lower() in all_text:
            return 'soundcloud'
    
    # Detectar Suno
    for pattern in SUNO_PATTERNS:
        if pattern.lower() in all_text:
            return 'suno'
    
    # Por defecto: local/desconocido
    return 'local'

def analyze_library():
    """Analiza la biblioteca completa."""
    print("🔍 ANALIZADOR DE ORIGEN - BLACKMAMBA MUSIC")
    print("=" * 60)
    
    # Cargar biblioteca
    with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
        library = json.load(f)
    
    print(f"📚 Analizando {len(library)} canciones...\n")
    
    # Clasificar por origen
    by_source = {
        'soundcloud': [],
        'suno': [],
        'local': []
    }
    
    for song in library:
        source = detect_source(song)
        song['source'] = source  # Agregar campo
        by_source[source].append(song)
    
    # Estadísticas
    print("📊 RESULTADOS:")
    print("=" * 60)
    print(f"🔊 SoundCloud: {len(by_source['soundcloud'])} canciones")
    print(f"🎵 Suno: {len(by_source['suno'])} canciones")
    print(f"💿 Local/Otras: {len(by_source['local'])} canciones")
    print(f"\n📀 Total: {len(library)} canciones")
    
    # Generar reporte
    report = {
        'total_songs': len(library),
        'by_source': {
            'soundcloud': {
                'count': len(by_source['soundcloud']),
                'songs': [
                    {
                        'title': s['title'],
                        'artist': s['artist'],
                        'formats': list(s.get('formats', {}).keys())
                    }
                    for s in by_source['soundcloud']
                ]
            },
            'suno': {
                'count': len(by_source['suno']),
                'songs': [
                    {
                        'title': s['title'],
                        'artist': s['artist'],
                        'formats': list(s.get('formats', {}).keys())
                    }
                    for s in by_source['suno']
                ]
            },
            'local': {
                'count': len(by_source['local']),
                'songs': [
                    {
                        'title': s['title'],
                        'artist': s['artist'],
                        'formats': list(s.get('formats', {}).keys())
                    }
                    for s in by_source['local']
                ]
            }
        }
    }
    
    # Guardar reporte
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Reporte guardado: {OUTPUT_FILE}")
    
    # Actualizar music_library.json con campo 'source'
    update_library = input("\n¿Actualizar music_library.json con campo 'source'? (s/n): ")
    if update_library.lower() == 's':
        with open(MUSIC_LIBRARY, 'w', encoding='utf-8') as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
        print("✅ music_library.json actualizado")
    
    # Mostrar algunas canciones de ejemplo
    print("\n" + "=" * 60)
    print("📋 EJEMPLOS DE CANCIONES:")
    print("=" * 60)
    
    if by_source['soundcloud']:
        print(f"\n🔊 SoundCloud (primeras 5):")
        for song in by_source['soundcloud'][:5]:
            print(f"   • {song['title']} - {song['artist']}")
    
    if by_source['suno']:
        print(f"\n🎵 Suno (primeras 5):")
        for song in by_source['suno'][:5]:
            print(f"   • {song['title']} - {song['artist']}")
    
    return report

def generate_lists():
    """Genera listas en formato texto."""
    print("\n" + "=" * 60)
    print("📝 GENERANDO LISTAS...")
    print("=" * 60)
    
    with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
        library = json.load(f)
    
    # Listas por origen
    lists = {
        'soundcloud': [],
        'suno': [],
        'local': []
    }
    
    for song in library:
        source = song.get('source', detect_source(song))
        lists[source].append(f"{song['title']} - {song['artist']}")
    
    # Guardar listas
    lists_dir = Path(__file__).parent / "music_lists"
    lists_dir.mkdir(exist_ok=True)
    
    for source, songs in lists.items():
        list_file = lists_dir / f"{source}_songs.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write(f"# BlackMamba Music - {source.upper()} ({len(songs)} canciones)\n")
            f.write("=" * 60 + "\n\n")
            for song in sorted(songs):
                f.write(f"{song}\n")
        print(f"✅ {list_file.name} - {len(songs)} canciones")
    
    print(f"\n📁 Listas guardadas en: {lists_dir}")

if __name__ == "__main__":
    report = analyze_library()
    
    generate = input("\n¿Generar listas en archivos .txt? (s/n): ")
    if generate.lower() == 's':
        generate_lists()
    
    print("\n✅ Análisis completado")
