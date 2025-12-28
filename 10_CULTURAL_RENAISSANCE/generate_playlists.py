#!/usr/bin/env python3
"""
Generador de Playlists BlackMamba
Crea listas M3U/M3U8/PLS para reproductores estándar
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import json
from pathlib import Path
from datetime import datetime

# === CONFIGURACIÓN ===
MUSIC_LIBRARY = Path(__file__).parent / "music_library.json"
PLAYLISTS_DIR = Path(__file__).parent / "playlists"

def detect_source(song):
    """Detecta el origen de una canción."""
    title = (song.get('title', '') or '').lower()
    song_name = (song.get('song_name', '') or '').lower()
    
    paths = []
    for format_type, format_data in song.get('formats', {}).items():
        if isinstance(format_data, dict):
            paths.append(format_data.get('path', '').lower())
    
    all_text = f"{title} {song_name} {' '.join(paths)}"
    
    # SoundCloud
    if 'soundcloud' in all_text or 'sc-' in all_text:
        return 'soundcloud'
    
    # Suno
    if any(p in all_text for p in ['intro)', 'verse', 'chorus', 'bridge', 'outro', 'suno']):
        return 'suno'
    
    return 'local'

def generate_m3u_playlist(songs, filename, extended=True):
    """Genera playlist M3U/M3U8."""
    content = []
    
    if extended:
        content.append("#EXTM3U")
        content.append(f"# BlackMamba Music Collection - {filename}")
        content.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"# Total tracks: {len(songs)}")
        content.append("")
    
    for song in songs:
        # Obtener ruta del archivo (priorizar MP3)
        audio_path = None
        duration = -1
        
        if song.get('formats', {}).get('mp3'):
            audio_path = song['formats']['mp3'].get('path')
        elif song.get('formats', {}).get('wav'):
            audio_path = song['formats']['wav'].get('path')
        
        if not audio_path:
            continue
        
        if extended:
            # Formato EXTINF: duración en segundos, artista - título
            title = song.get('title', 'Unknown')
            artist = song.get('artist', 'Unknown')
            content.append(f"#EXTINF:{duration},{artist} - {title}")
        
        content.append(audio_path)
    
    return '\n'.join(content)

def generate_pls_playlist(songs, filename):
    """Genera playlist PLS."""
    content = [
        "[playlist]",
        f"; BlackMamba Music Collection - {filename}",
        f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    valid_tracks = []
    for song in songs:
        audio_path = None
        
        if song.get('formats', {}).get('mp3'):
            audio_path = song['formats']['mp3'].get('path')
        elif song.get('formats', {}).get('wav'):
            audio_path = song['formats']['wav'].get('path')
        
        if audio_path:
            valid_tracks.append(song)
    
    content.append(f"NumberOfEntries={len(valid_tracks)}")
    content.append("")
    
    for i, song in enumerate(valid_tracks, 1):
        audio_path = (song.get('formats', {}).get('mp3') or 
                     song.get('formats', {}).get('wav', {})).get('path')
        title = f"{song.get('artist', 'Unknown')} - {song.get('title', 'Unknown')}"
        
        content.append(f"File{i}={audio_path}")
        content.append(f"Title{i}={title}")
        content.append(f"Length{i}=-1")
        content.append("")
    
    content.append("Version=2")
    
    return '\n'.join(content)

def load_library():
    """Carga la biblioteca de música."""
    with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_all_playlists():
    """Genera todas las playlists."""
    print("🎵 BLACKMAMBA PLAYLIST GENERATOR")
    print("=" * 60)
    
    # Crear directorio de playlists
    PLAYLISTS_DIR.mkdir(exist_ok=True)
    
    # Cargar biblioteca
    library = load_library()
    print(f"📚 Cargadas {len(library)} canciones\n")
    
    # Clasificar por origen
    by_source = {
        'all': library,
        'soundcloud': [],
        'suno': [],
        'local': []
    }
    
    for song in library:
        source = detect_source(song)
        by_source[source].append(song)
    
    # Estadísticas
    print("📊 Clasificación:")
    print(f"   🔊 SoundCloud: {len(by_source['soundcloud'])} canciones")
    print(f"   🎵 Suno: {len(by_source['suno'])} canciones")
    print(f"   💿 Local: {len(by_source['local'])} canciones")
    print(f"   📀 Total: {len(library)} canciones\n")
    
    # Generar playlists
    print("📝 Generando playlists...\n")
    
    playlists_created = []
    
    for source_name, songs in by_source.items():
        if not songs:
            continue
        
        # M3U (Simple)
        m3u_file = PLAYLISTS_DIR / f"BlackMamba_{source_name.upper()}.m3u"
        m3u_content = generate_m3u_playlist(songs, source_name, extended=False)
        m3u_file.write_text(m3u_content, encoding='utf-8')
        playlists_created.append(m3u_file)
        
        # M3U8 (Extended)
        m3u8_file = PLAYLISTS_DIR / f"BlackMamba_{source_name.upper()}.m3u8"
        m3u8_content = generate_m3u_playlist(songs, source_name, extended=True)
        m3u8_file.write_text(m3u8_content, encoding='utf-8')
        playlists_created.append(m3u8_file)
        
        # PLS
        pls_file = PLAYLISTS_DIR / f"BlackMamba_{source_name.upper()}.pls"
        pls_content = generate_pls_playlist(songs, source_name)
        pls_file.write_text(pls_content, encoding='utf-8')
        playlists_created.append(pls_file)
        
        print(f"✅ {source_name.upper()}:")
        print(f"   • {m3u_file.name} ({len(songs)} canciones)")
        print(f"   • {m3u8_file.name} (con metadata)")
        print(f"   • {pls_file.name} (formato PLS)")
    
    # Playlist por formato (MP3/WAV)
    print("\n📀 Playlists por formato:")
    
    mp3_songs = [s for s in library if s.get('formats', {}).get('mp3')]
    wav_songs = [s for s in library if s.get('formats', {}).get('wav')]
    
    for format_type, songs in [('MP3', mp3_songs), ('WAV', wav_songs)]:
        if songs:
            m3u8_file = PLAYLISTS_DIR / f"BlackMamba_{format_type}_ONLY.m3u8"
            m3u8_content = generate_m3u_playlist(songs, f"{format_type}_only", extended=True)
            m3u8_file.write_text(m3u8_content, encoding='utf-8')
            playlists_created.append(m3u8_file)
            print(f"✅ {m3u8_file.name} ({len(songs)} canciones)")
    
    # Resumen
    print("\n" + "=" * 60)
    print(f"✅ {len(playlists_created)} playlists generadas")
    print(f"📁 Ubicación: {PLAYLISTS_DIR}")
    print("\n💡 Usa estas playlists en:")
    print("   • VLC Media Player")
    print("   • iTunes/Apple Music")
    print("   • Winamp")
    print("   • foobar2000")
    print("   • Cualquier reproductor que soporte M3U/PLS")
    
    return playlists_created

def create_master_playlist():
    """Crea una playlist maestra con todo."""
    print("\n🎼 Creando playlist maestra...")
    
    library = load_library()
    
    # Agrupar por artista
    by_artist = {}
    for song in library:
        artist = song.get('artist', 'Unknown')
        if artist not in by_artist:
            by_artist[artist] = []
        by_artist[artist].append(song)
    
    # Ordenar canciones por artista
    sorted_songs = []
    for artist in sorted(by_artist.keys()):
        sorted_songs.extend(sorted(by_artist[artist], key=lambda s: s.get('title', '')))
    
    master_file = PLAYLISTS_DIR / "BlackMamba_MASTER_COLLECTION.m3u8"
    master_content = generate_m3u_playlist(sorted_songs, "Master Collection", extended=True)
    master_file.write_text(master_content, encoding='utf-8')
    
    print(f"✅ {master_file.name}")
    print(f"   • {len(sorted_songs)} canciones ordenadas por artista")

if __name__ == "__main__":
    generate_all_playlists()
    
    print("\n¿Crear playlist maestra ordenada por artista? (s/n): ", end='')
    response = input()
    if response.lower() == 's':
        create_master_playlist()
    
    print("\n🎵 ¡Listo! Abre cualquier playlist con tu reproductor favorito")
