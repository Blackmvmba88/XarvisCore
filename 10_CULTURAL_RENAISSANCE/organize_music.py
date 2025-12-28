#!/usr/bin/env python3
"""
Organizador de Música BlackMamba
Mueve todas las canciones a una carpeta única
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import json
import shutil
import os
from pathlib import Path
from datetime import datetime

# === CONFIGURACIÓN ===
MUSIC_LIBRARY = Path(__file__).parent / "music_library.json"
UNIFIED_FOLDER = Path(__file__).parent / "BlackMamba_Music_Collection"
DRY_RUN = False  # Cambiar a False para ejecutar

def load_library():
    """Carga la biblioteca de música."""
    with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
        return json.load(f)

def organize_music():
    """Organiza todas las canciones en una carpeta única."""
    print("🎵 BLACKMAMBA MUSIC ORGANIZER")
    print("=" * 60)
    
    # Crear carpeta unificada
    UNIFIED_FOLDER.mkdir(exist_ok=True)
    print(f"📁 Carpeta destino: {UNIFIED_FOLDER}")
    
    # Cargar biblioteca
    library = load_library()
    print(f"📚 Canciones en biblioteca: {len(library)}")
    
    stats = {
        'copied': 0,
        'skipped': 0,
        'errors': 0,
        'missing': 0
    }
    
    for song in library:
        song_name = song['song_name']
        formats = song.get('formats', {})
        
        # Procesar cada formato (mp3, wav)
        for format_type, format_data in formats.items():
            if not isinstance(format_data, dict):
                continue
                
            source_path = Path(format_data.get('path', ''))
            
            if not source_path.exists():
                print(f"⚠️  No encontrado: {song_name}.{format_type}")
                stats['missing'] += 1
                continue
            
            # Nombre de archivo limpio
            clean_name = f"{song['title']} - {song['artist']}".replace('/', '-')
            dest_filename = f"{clean_name}.{format_type}"
            dest_path = UNIFIED_FOLDER / dest_filename
            
            # Verificar si ya existe
            if dest_path.exists():
                print(f"⏭️  Ya existe: {dest_filename}")
                stats['skipped'] += 1
                continue
            
            # Copiar archivo
            try:
                if DRY_RUN:
                    print(f"🔍 [DRY RUN] Copiaría: {source_path.name} → {dest_filename}")
                    stats['copied'] += 1
                else:
                    shutil.copy2(source_path, dest_path)
                    print(f"✅ Copiado: {dest_filename}")
                    stats['copied'] += 1
            except Exception as e:
                print(f"❌ Error copiando {song_name}: {e}")
                stats['errors'] += 1
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"✅ Copiadas: {stats['copied']}")
    print(f"⏭️  Omitidas (ya existen): {stats['skipped']}")
    print(f"⚠️  No encontradas: {stats['missing']}")
    print(f"❌ Errores: {stats['errors']}")
    print(f"\n📁 Carpeta destino: {UNIFIED_FOLDER}")
    
    if DRY_RUN:
        print("\n⚠️  MODO DRY RUN - No se copiaron archivos")
        print("   Cambia DRY_RUN = False en el script para ejecutar")

def update_library_paths():
    """Actualiza las rutas en music_library.json."""
    print("\n🔄 Actualizando rutas en music_library.json...")
    
    library = load_library()
    updated = 0
    
    for song in library:
        formats = song.get('formats', {})
        
        for format_type, format_data in formats.items():
            if not isinstance(format_data, dict):
                continue
            
            # Nueva ruta
            clean_name = f"{song['title']} - {song['artist']}".replace('/', '-')
            new_filename = f"{clean_name}.{format_type}"
            new_path = UNIFIED_FOLDER / new_filename
            
            if new_path.exists():
                format_data['path'] = str(new_path)
                updated += 1
    
    # Guardar biblioteca actualizada
    if not DRY_RUN:
        with open(MUSIC_LIBRARY, 'w', encoding='utf-8') as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
        print(f"✅ Actualizadas {updated} rutas en music_library.json")
    else:
        print(f"🔍 [DRY RUN] Se actualizarían {updated} rutas")

if __name__ == "__main__":
    import sys
    
    print("🎵 BlackMamba Music Organizer")
    print("=" * 60)
    print("Este script organizará todas tus canciones en una carpeta única.")
    print(f"Carpeta destino: {UNIFIED_FOLDER}")
    print("=" * 60)
    
    if DRY_RUN:
        print("\n⚠️  MODO DRY RUN ACTIVADO")
        print("   Solo mostrará lo que haría, sin copiar archivos")
        print("   Cambia DRY_RUN = False en el script para ejecutar\n")
    else:
        response = input("\n¿Continuar? (s/n): ")
        if response.lower() != 's':
            print("❌ Cancelado")
            sys.exit(0)
    
    organize_music()
    
    if not DRY_RUN:
        print("\n¿Actualizar rutas en music_library.json? (s/n): ", end='')
        response = input()
        if response.lower() == 's':
            update_library_paths()
    
    print("\n✅ Proceso completado")
