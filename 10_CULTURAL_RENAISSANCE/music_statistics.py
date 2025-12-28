#!/usr/bin/env python3
"""
Analizador de Estadísticas Musical - BlackMamba
Estadísticas detalladas de tu colección
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

MUSIC_LIBRARY = Path(__file__).parent / "music_library.json"

def load_library():
    with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_statistics():
    """Calcula estadísticas completas."""
    print("📊 BLACKMAMBA MUSIC STATISTICS")
    print("=" * 60)
    
    library = load_library()
    
    # Básicas
    total_songs = len(library)
    mp3_count = len([s for s in library if s.get('formats', {}).get('mp3')])
    wav_count = len([s for s in library if s.get('formats', {}).get('wav')])
    complete_count = len([s for s in library if 
                          s.get('formats', {}).get('mp3') and 
                          s.get('formats', {}).get('wav')])
    
    print(f"\n📀 COLECCIÓN GENERAL")
    print(f"   Total canciones: {total_songs}")
    print(f"   Archivos MP3: {mp3_count}")
    print(f"   Archivos WAV: {wav_count}")
    print(f"   Completas (MP3+WAV): {complete_count}")
    
    # Tamaño total
    total_mb = sum(s.get('size_total_mb', 0) for s in library)
    total_gb = total_mb / 1024
    avg_mb = total_mb / total_songs if total_songs > 0 else 0
    
    print(f"\n💾 ALMACENAMIENTO")
    print(f"   Tamaño total: {total_gb:.2f} GB ({total_mb:.2f} MB)")
    print(f"   Promedio por canción: {avg_mb:.2f} MB")
    
    # Canción más grande/pequeña
    sizes = [(s.get('title', 'Unknown'), s.get('size_total_mb', 0)) for s in library]
    sizes.sort(key=lambda x: x[1], reverse=True)
    
    if sizes:
        print(f"   Más pesada: {sizes[0][0][:40]} ({sizes[0][1]:.2f} MB)")
        print(f"   Más ligera: {sizes[-1][0][:40]} ({sizes[-1][1]:.2f} MB)")
    
    # Por artista
    artists = Counter(s.get('artist', 'Unknown') for s in library)
    
    print(f"\n🎤 POR ARTISTA")
    print(f"   Artistas únicos: {len(artists)}")
    print(f"   Top 5 artistas:")
    for artist, count in artists.most_common(5):
        print(f"      • {artist}: {count} canciones")
    
    # Por ubicación
    all_locations = []
    for song in library:
        all_locations.extend(song.get('locations', []))
    
    locations = Counter(all_locations)
    
    print(f"\n📁 UBICACIONES")
    print(f"   Directorios: {len(locations)}")
    for location, count in locations.most_common(5):
        print(f"      • {location}: {count} archivos")
    
    # Por año
    years = Counter()
    for song in library:
        date_str = song.get('modified_date', '')
        if date_str:
            try:
                year = datetime.fromisoformat(date_str).year
                years[year] += 1
            except:
                years['unknown'] += 1
    
    print(f"\n📅 POR AÑO (última modificación)")
    for year in sorted(years.keys(), reverse=True):
        if year != 'unknown':
            print(f"      • {year}: {years[year]} canciones")
    if 'unknown' in years:
        print(f"      • Sin fecha: {years['unknown']} canciones")
    
    # Calidad/Estado
    statuses = Counter(s.get('status', 'unknown') for s in library)
    
    print(f"\n✨ CALIDAD")
    for status, count in statuses.most_common():
        emoji = {'complete': '💎', 'mp3_only': '💿', 'wav_only': '🎵'}.get(status, '❓')
        status_name = {
            'complete': 'Completas (MP3+WAV)',
            'mp3_only': 'Solo MP3',
            'wav_only': 'Solo WAV'
        }.get(status, status)
        print(f"      {emoji} {status_name}: {count} canciones")
    
    # Títulos interesantes
    print(f"\n🎯 CURIOSIDADES")
    
    # Títulos más largos
    longest = max(library, key=lambda s: len(s.get('title', '')))
    print(f"   Título más largo: {longest.get('title', '')[:50]}...")
    
    # Títulos más cortos
    shortest = min(library, key=lambda s: len(s.get('title', 'zzz')))
    print(f"   Título más corto: {shortest.get('title', '')}")
    
    # Detección de duplicados potenciales
    titles = [s.get('title', '').lower().strip() for s in library]
    duplicates = [title for title, count in Counter(titles).items() if count > 1]
    
    if duplicates:
        print(f"\n⚠️  POSIBLES DUPLICADOS")
        print(f"   Títulos repetidos: {len(duplicates)}")
        for dup in duplicates[:5]:
            print(f"      • {dup}")
    
    print("\n" + "=" * 60)
    print(f"✅ Análisis completado - {total_songs} canciones analizadas")

if __name__ == "__main__":
    calculate_statistics()
