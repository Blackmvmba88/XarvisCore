#!/usr/bin/env python3
"""
🎬 BLACKMAMBA MOVIE ORGANIZER
Organiza películas de Downloads con categorización inteligente
Dominio: 14_CREATIVE_TOOLS
Arquitecto: Iyari Cancino Gomez
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# === CONFIGURACIÓN ===
DOWNLOADS = Path.home() / "Downloads"
MOVIES_BASE = Path.home() / "Movies" / "BlackMamba_Cinema"
DRY_RUN = True  # Cambiar a False para ejecutar

# Estructura de carpetas
CATEGORIES = {
    'Películas': ['mkv', 'mp4', 'avi', 'mov', 'm4v'],
    'Documentales': [],  # Se detectan por nombre
    'Series': [],
    'Cortos': [],  # Videos < 15 minutos
    'Sin_Clasificar': []
}

# Keywords para categorización automática
KEYWORDS = {
    'Documentales': ['documental', 'documentary', 'national', 'geographic', 'discovery'],
    'Series': ['s01', 's02', 's03', 'season', 'episode', 'ep', 'temporada'],
    'Películas': ['1080p', '720p', '4K', 'BluRay', 'WEB-DL', 'IMAX', 'HDRip']
}

def get_file_size_mb(filepath):
    """Obtiene el tamaño del archivo en MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

def get_video_duration(filepath):
    """Intenta obtener la duración del video (requiere ffprobe)."""
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 
             'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
             str(filepath)],
            capture_output=True,
            text=True,
            timeout=5
        )
        duration_sec = float(result.stdout.strip())
        return duration_sec / 60  # Retornar en minutos
    except:
        return None

def categorize_video(filename, filepath):
    """Categoriza el video según nombre y características."""
    filename_lower = filename.lower()
    
    # Detectar series
    for keyword in KEYWORDS['Series']:
        if keyword in filename_lower:
            return 'Series'
    
    # Detectar documentales
    for keyword in KEYWORDS['Documentales']:
        if keyword in filename_lower:
            return 'Documentales'
    
    # Detectar películas por keywords de calidad
    for keyword in KEYWORDS['Películas']:
        if keyword in filename_lower:
            return 'Películas'
    
    # Detectar cortos por duración (si ffprobe disponible)
    duration = get_video_duration(filepath)
    if duration and duration < 15:
        return 'Cortos'
    
    # Detectar por tamaño (películas suelen ser > 500MB)
    size_mb = get_file_size_mb(filepath)
    if size_mb > 500:
        return 'Películas'
    elif size_mb < 100:
        return 'Cortos'
    
    # Por defecto
    return 'Sin_Clasificar'

def clean_filename(filename):
    """Limpia el nombre del archivo."""
    # Remover patrones comunes de releases
    patterns_to_remove = [
        'WEB-DL', 'BluRay', 'HDTV', 'HDRip', 'BRRip',
        'x264', 'x265', 'HEVC', 'AAC', 'AC3',
        '1080p', '720p', '480p', '4K',
        'IMAX', 'PROPER', 'REPACK'
    ]
    
    clean = filename
    for pattern in patterns_to_remove:
        clean = clean.replace(pattern, '')
        clean = clean.replace(pattern.lower(), '')
    
    # Limpiar caracteres
    clean = clean.replace('_', ' ')
    clean = clean.replace('.', ' ')
    clean = ' '.join(clean.split())  # Múltiples espacios
    
    return clean.strip()

def organize_movies():
    """Organiza todas las películas de Downloads."""
    print("🎬 BLACKMAMBA MOVIE ORGANIZER")
    print("=" * 70)
    print(f"📁 Origen: {DOWNLOADS}")
    print(f"🎯 Destino: {MOVIES_BASE}")
    print(f"🔍 Modo: {'DRY RUN (simulación)' if DRY_RUN else 'EJECUCIÓN REAL'}")
    print("=" * 70)
    
    # Buscar todos los videos
    video_extensions = ['mp4', 'mkv', 'avi', 'mov', 'm4v', 'webm', 'flv', 'wmv']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(DOWNLOADS.glob(f"*.{ext}"))
        video_files.extend(DOWNLOADS.glob(f"*.{ext.upper()}"))
    
    if not video_files:
        print("❌ No se encontraron videos en Downloads")
        return
    
    print(f"\n📊 Videos encontrados: {len(video_files)}")
    print()
    
    # Estadísticas
    stats = {
        'Películas': 0,
        'Documentales': 0,
        'Series': 0,
        'Cortos': 0,
        'Sin_Clasificar': 0,
        'errors': 0,
        'skipped': 0
    }
    
    # Crear estructura de carpetas
    if not DRY_RUN:
        MOVIES_BASE.mkdir(parents=True, exist_ok=True)
        for category in CATEGORIES.keys():
            (MOVIES_BASE / category).mkdir(exist_ok=True)
    
    # Procesar cada video
    organized_files = []
    
    for video_file in video_files:
        try:
            filename = video_file.name
            size_mb = get_file_size_mb(video_file)
            
            # Categorizar
            category = categorize_video(filename, video_file)
            
            # Limpiar nombre
            clean_name = clean_filename(video_file.stem)
            extension = video_file.suffix
            new_filename = f"{clean_name}{extension}"
            
            # Ruta destino
            dest_folder = MOVIES_BASE / category
            dest_path = dest_folder / new_filename
            
            # Verificar si existe
            if dest_path.exists() and not DRY_RUN:
                print(f"⏭️  Ya existe: {category}/{new_filename}")
                stats['skipped'] += 1
                continue
            
            # Información del archivo
            info = {
                'original': filename,
                'clean_name': new_filename,
                'category': category,
                'size_mb': round(size_mb, 2),
                'source': str(video_file),
                'destination': str(dest_path)
            }
            
            organized_files.append(info)
            
            # Mostrar información
            print(f"📁 {category}/")
            print(f"   Archivo: {filename}")
            print(f"   → Nuevo: {new_filename}")
            print(f"   Tamaño: {size_mb:.1f} MB")
            
            if DRY_RUN:
                print(f"   🔍 [SIMULACIÓN] Se movería aquí")
            else:
                # Mover archivo
                shutil.move(str(video_file), str(dest_path))
                print(f"   ✅ Movido exitosamente")
            
            print()
            stats[category] += 1
            
        except Exception as e:
            print(f"❌ Error procesando {video_file.name}: {e}")
            stats['errors'] += 1
            print()
    
    # Guardar catálogo JSON
    catalog_path = MOVIES_BASE / "movie_catalog.json"
    if not DRY_RUN:
        catalog_data = {
            'generated': datetime.now().isoformat(),
            'total_files': len(organized_files),
            'files': organized_files,
            'statistics': stats
        }
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
    
    # Resumen final
    print("=" * 70)
    print("📊 RESUMEN DE ORGANIZACIÓN")
    print("=" * 70)
    print(f"🎬 Películas: {stats['Películas']}")
    print(f"📚 Documentales: {stats['Documentales']}")
    print(f"📺 Series: {stats['Series']}")
    print(f"🎞️  Cortos: {stats['Cortos']}")
    print(f"❓ Sin clasificar: {stats['Sin_Clasificar']}")
    print(f"⏭️  Omitidos (ya existen): {stats['skipped']}")
    print(f"❌ Errores: {stats['errors']}")
    print()
    print(f"📁 Carpeta destino: {MOVIES_BASE}")
    
    if not DRY_RUN:
        print(f"📋 Catálogo generado: {catalog_path}")
    
    if DRY_RUN:
        print()
        print("⚠️  MODO DRY RUN - No se movieron archivos")
        print("   Cambia DRY_RUN = False en el script para ejecutar")
    else:
        print()
        print("✅ Organización completada exitosamente")

def show_statistics():
    """Muestra estadísticas de la colección."""
    catalog_path = MOVIES_BASE / "movie_catalog.json"
    
    if not catalog_path.exists():
        print("❌ No hay catálogo. Ejecuta la organización primero.")
        return
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    print("📊 ESTADÍSTICAS DE COLECCIÓN")
    print("=" * 70)
    print(f"📅 Última actualización: {catalog['generated']}")
    print(f"🎬 Total de archivos: {catalog['total_files']}")
    print()
    
    stats = catalog['statistics']
    for category, count in stats.items():
        if category != 'errors' and category != 'skipped':
            print(f"{category}: {count}")
    
    print()
    print(f"📁 Ubicación: {MOVIES_BASE}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stats':
        show_statistics()
    else:
        organize_movies()
