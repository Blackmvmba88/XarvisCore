#!/usr/bin/env python3
"""
Generador Avanzado de Playlists - BlackMamba
Playlists shuffle, por año, por tamaño, mejores canciones
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import json
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MUSIC_LIBRARY = Path(__file__).parent / "music_library.json"
PLAYLISTS_DIR = Path(__file__).parent / "playlists"

def load_library():
    with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_m3u8(songs, title):
    """Genera contenido M3U8."""
    lines = [
        "#EXTM3U",
        f"# {title}",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Total tracks: {len(songs)}",
        ""
    ]
    
    for song in songs:
        path = (song.get('formats', {}).get('mp3') or 
                song.get('formats', {}).get('wav', {})).get('path')
        if path:
            title = f"{song.get('artist', 'Unknown')} - {song.get('title', 'Unknown')}"
            lines.append(f"#EXTINF:-1,{title}")
            lines.append(path)
    
    return '\n'.join(lines)

def create_shuffle_playlists():
    """Crea playlists aleatorias."""
    print("🎲 Creando playlists shuffle...")
    
    library = load_library()
    
    # Shuffle completo
    shuffled = library.copy()
    random.shuffle(shuffled)
    
    shuffle_file = PLAYLISTS_DIR / "BlackMamba_SHUFFLE_ALL.m3u8"
    content = generate_m3u8(shuffled, "BlackMamba SHUFFLE - Todas las canciones")
    shuffle_file.write_text(content, encoding='utf-8')
    print(f"✅ {shuffle_file.name} ({len(shuffled)} canciones)")
    
    # Top 50 aleatorio
    top50 = random.sample(library, min(50, len(library)))
    top50_file = PLAYLISTS_DIR / "BlackMamba_RANDOM_50.m3u8"
    content = generate_m3u8(top50, "BlackMamba - 50 Canciones Aleatorias")
    top50_file.write_text(content, encoding='utf-8')
    print(f"✅ {top50_file.name} (50 canciones)")
    
    # Mini mix (20 canciones)
    mini = random.sample(library, min(20, len(library)))
    mini_file = PLAYLISTS_DIR / "BlackMamba_MINI_MIX.m3u8"
    content = generate_m3u8(mini, "BlackMamba Mini Mix - 20 canciones")
    mini_file.write_text(content, encoding='utf-8')
    print(f"✅ {mini_file.name} (20 canciones)")

def create_by_year_playlists():
    """Crea playlists por año de modificación."""
    print("\n📅 Creando playlists por año...")
    
    library = load_library()
    by_year = defaultdict(list)
    
    for song in library:
        date_str = song.get('modified_date', '')
        if date_str:
            try:
                year = datetime.fromisoformat(date_str).year
                by_year[year].append(song)
            except:
                by_year['unknown'].append(song)
    
    for year, songs in sorted(by_year.items(), reverse=True):
        if songs:
            year_file = PLAYLISTS_DIR / f"BlackMamba_{year}.m3u8"
            content = generate_m3u8(songs, f"BlackMamba {year} - {len(songs)} canciones")
            year_file.write_text(content, encoding='utf-8')
            print(f"✅ {year_file.name} ({len(songs)} canciones)")

def create_by_size_playlists():
    """Crea playlists por tamaño (pequeñas vs grandes)."""
    print("\n💾 Creando playlists por tamaño...")
    
    library = load_library()
    
    # Ordenar por tamaño
    sorted_by_size = sorted(library, key=lambda s: s.get('size_total_mb', 0), reverse=True)
    
    # Top 30 más grandes
    biggest = sorted_by_size[:30]
    big_file = PLAYLISTS_DIR / "BlackMamba_HEAVIEST_30.m3u8"
    content = generate_m3u8(biggest, "BlackMamba - 30 Canciones Más Pesadas")
    big_file.write_text(content, encoding='utf-8')
    total_mb = sum(s.get('size_total_mb', 0) for s in biggest)
    print(f"✅ {big_file.name} (30 canciones, {total_mb:.1f} MB)")
    
    # 30 más ligeras
    lightest = sorted_by_size[-30:]
    light_file = PLAYLISTS_DIR / "BlackMamba_LIGHTEST_30.m3u8"
    content = generate_m3u8(lightest, "BlackMamba - 30 Canciones Más Ligeras")
    light_file.write_text(content, encoding='utf-8')
    total_mb = sum(s.get('size_total_mb', 0) for s in lightest)
    print(f"✅ {light_file.name} (30 canciones, {total_mb:.1f} MB)")

def create_workout_playlists():
    """Crea playlists temáticas para diferentes momentos."""
    print("\n💪 Creando playlists temáticas...")
    
    library = load_library()
    
    # Workout Mix (canciones más pesadas/grandes, probablemente más intensas)
    sorted_by_size = sorted(library, key=lambda s: s.get('size_total_mb', 0), reverse=True)
    workout = sorted_by_size[:50]
    random.shuffle(workout)
    
    workout_file = PLAYLISTS_DIR / "BlackMamba_WORKOUT.m3u8"
    content = generate_m3u8(workout, "BlackMamba WORKOUT Mix - 50 canciones")
    workout_file.write_text(content, encoding='utf-8')
    print(f"✅ {workout_file.name} (50 canciones)")
    
    # Chill Mix (canciones más ligeras)
    chill = sorted_by_size[-50:]
    random.shuffle(chill)
    
    chill_file = PLAYLISTS_DIR / "BlackMamba_CHILL.m3u8"
    content = generate_m3u8(chill, "BlackMamba CHILL Mix - 50 canciones")
    chill_file.write_text(content, encoding='utf-8')
    print(f"✅ {chill_file.name} (50 canciones)")
    
    # Focus Mix (sample aleatorio)
    focus = random.sample(library, min(40, len(library)))
    focus_file = PLAYLISTS_DIR / "BlackMamba_FOCUS.m3u8"
    content = generate_m3u8(focus, "BlackMamba FOCUS Mix - 40 canciones")
    focus_file.write_text(content, encoding='utf-8')
    print(f"✅ {focus_file.name} (40 canciones)")

def create_alphabetical_playlists():
    """Crea playlists ordenadas alfabéticamente."""
    print("\n🔤 Creando playlists alfabéticas...")
    
    library = load_library()
    
    # Por título
    by_title = sorted(library, key=lambda s: s.get('title', '').lower())
    title_file = PLAYLISTS_DIR / "BlackMamba_A-Z_BY_TITLE.m3u8"
    content = generate_m3u8(by_title, "BlackMamba A-Z por Título")
    title_file.write_text(content, encoding='utf-8')
    print(f"✅ {title_file.name} ({len(by_title)} canciones)")
    
    # Por artista
    by_artist = sorted(library, key=lambda s: s.get('artist', '').lower())
    artist_file = PLAYLISTS_DIR / "BlackMamba_A-Z_BY_ARTIST.m3u8"
    content = generate_m3u8(by_artist, "BlackMamba A-Z por Artista")
    artist_file.write_text(content, encoding='utf-8')
    print(f"✅ {artist_file.name} ({len(by_artist)} canciones)")

def export_to_text():
    """Exporta lista simple para Spotify/Apple Music."""
    print("\n📝 Exportando listas de texto...")
    
    library = load_library()
    
    # Lista simple
    simple_file = PLAYLISTS_DIR / "BlackMamba_TRACK_LIST.txt"
    with open(simple_file, 'w', encoding='utf-8') as f:
        f.write("# BlackMamba Music Collection\n")
        f.write(f"# Total: {len(library)} canciones\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        for song in sorted(library, key=lambda s: s.get('title', '').lower()):
            f.write(f"{song.get('artist', 'Unknown')} - {song.get('title', 'Unknown')}\n")
    
    print(f"✅ {simple_file.name} (formato texto simple)")
    
    # Con metadata
    detailed_file = PLAYLISTS_DIR / "BlackMamba_DETAILED_LIST.txt"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        f.write("# BlackMamba Music Collection - Detailed\n")
        f.write(f"# Total: {len(library)} canciones\n")
        f.write("=" * 60 + "\n\n")
        
        for song in sorted(library, key=lambda s: s.get('title', '').lower()):
            f.write(f"🎵 {song.get('title', 'Unknown')}\n")
            f.write(f"   Artista: {song.get('artist', 'Unknown')}\n")
            
            formats = list(song.get('formats', {}).keys())
            if formats:
                f.write(f"   Formatos: {', '.join(formats).upper()}\n")
            
            size = song.get('size_total_mb', 0)
            if size:
                f.write(f"   Tamaño: {size:.2f} MB\n")
            
            f.write("\n")
    
    print(f"✅ {detailed_file.name} (con metadata)")

if __name__ == "__main__":
    print("🎼 BLACKMAMBA ADVANCED PLAYLIST GENERATOR")
    print("=" * 60)
    
    PLAYLISTS_DIR.mkdir(exist_ok=True)
    
    create_shuffle_playlists()
    create_by_year_playlists()
    create_by_size_playlists()
    create_workout_playlists()
    create_alphabetical_playlists()
    export_to_text()
    
    print("\n" + "=" * 60)
    print("✅ Playlists avanzadas generadas!")
    print(f"📁 Ubicación: {PLAYLISTS_DIR}")
    print("\n💡 Nuevas playlists:")
    print("   🎲 SHUFFLE_ALL, RANDOM_50, MINI_MIX")
    print("   📅 Por año (2025, 2024, etc.)")
    print("   💾 HEAVIEST_30, LIGHTEST_30")
    print("   💪 WORKOUT, CHILL, FOCUS")
    print("   🔤 A-Z por título/artista")
    print("   📝 Listas de texto para Spotify/Apple Music")
