#!/usr/bin/env python3
"""
📱 BLACKMAMBA META VIDEOS ORGANIZER
Unifica todos los videos de Meta (Instagram/Facebook) en una carpeta única del USB
Fuentes: Downloads + USB dispersos → USB centralizado
Dominio: 14_CREATIVE_TOOLS
Arquitecto: Iyari Cancino Gomez
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

# === CONFIGURACIÓN ===
USB_BASE = Path("/Volumes/ADATA SC740")
META_UNIFIED = USB_BASE / "03_META_VIDEOS_UNIFIED"
DOWNLOADS = Path.home() / "Downloads"

# Carpetas a escanear en el USB
USB_SEARCH_PATHS = [
    USB_BASE / "00_ORGANIZED_MASTER/01_PROYECTOS/POWER_TOOLS/meta",
    USB_BASE / "02_MEDIA/VIDEO/RENDERS",
    USB_BASE,  # Raíz del USB
]

DRY_RUN = True  # Cambiar a False para ejecutar

# Patrones de archivos de Meta
META_PATTERNS = [
    'AQ',  # Código típico de Instagram/Facebook
    'meta',
    'facebook',
    'instagram',
    'Screen_Recording',  # Screen recordings de apps de Meta
]

def is_meta_video(filepath):
    """Detecta si un video es de Meta por nombre o ubicación."""
    filename = filepath.name.lower()
    parent = str(filepath.parent).lower()
    
    # Excluir anime y series conocidas
    exclude_patterns = [
        'fullmetal', 'alchemist', 'brotherhood', 
        'anime', 'serie', 'season', 'episode'
    ]
    
    for exclude in exclude_patterns:
        if exclude in filename.lower():
            return False
    
    # Detectar por código AQ seguido de muchos caracteres (Instagram/Facebook)
    if filename.startswith('aq') and len(filename) > 30:
        return True
    
    # Detectar por carpeta meta específica
    if '/meta/' in parent and 'metadata' not in parent:
        return True
    
    # Detectar screen recordings de apps Meta
    if 'screen_recording' in filename and 'facebook' in filename:
        return True
    
    return False

def calculate_hash(filepath, size=1024*1024):
    """Calcula hash MD5 de los primeros MB del archivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(size)
            hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def get_file_size_mb(filepath):
    """Obtiene el tamaño del archivo en MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

def find_all_meta_videos():
    """Encuentra todos los videos de Meta en todas las fuentes."""
    print("🔍 BUSCANDO VIDEOS DE META...")
    print("=" * 70)
    
    all_videos = []
    video_extensions = ['mp4', 'mov', 'm4v', 'avi', 'mkv']
    
    # Buscar en raíz del USB
    print(f"\n📁 Buscando en raíz USB: {USB_BASE}")
    try:
        for ext in video_extensions:
            for video in USB_BASE.glob(f"*.{ext}"):
                if is_meta_video(video):
                    all_videos.append(video)
                    print(f"   ✅ {video.name}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Buscar en carpetas específicas del USB
    for search_path in USB_SEARCH_PATHS:
        if not search_path.exists():
            continue
        
        print(f"\n📁 Buscando en: {search_path}")
        try:
            for ext in video_extensions:
                for video in search_path.rglob(f"*.{ext}"):
                    if is_meta_video(video):
                        all_videos.append(video)
                        print(f"   ✅ {video.name}")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    # Buscar en Downloads
    print(f"\n📁 Buscando en Downloads: {DOWNLOADS}")
    try:
        for ext in video_extensions:
            for video in DOWNLOADS.rglob(f"*.{ext}"):
                if is_meta_video(video):
                    all_videos.append(video)
                    print(f"   ✅ {video.name}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    return all_videos

def organize_meta_videos():
    """Organiza todos los videos de Meta en carpeta unificada."""
    print("\n📱 BLACKMAMBA META VIDEOS ORGANIZER")
    print("=" * 70)
    print(f"🎯 Destino: {META_UNIFIED}")
    print(f"🔍 Modo: {'DRY RUN (simulación)' if DRY_RUN else 'EJECUCIÓN REAL'}")
    print("=" * 70)
    
    # Verificar que USB esté montado
    if not USB_BASE.exists():
        print(f"❌ USB no encontrado en {USB_BASE}")
        print("   Conecta el USB ADATA SC740 y vuelve a intentar")
        return
    
    # Buscar todos los videos
    all_videos = find_all_meta_videos()
    
    if not all_videos:
        print("\n❌ No se encontraron videos de Meta")
        return
    
    print(f"\n📊 Total de videos encontrados: {len(all_videos)}")
    print()
    
    # Crear carpeta destino
    if not DRY_RUN:
        META_UNIFIED.mkdir(parents=True, exist_ok=True)
    
    # Estadísticas
    stats = {
        'copied': 0,
        'moved': 0,
        'skipped': 0,
        'duplicates': 0,
        'errors': 0
    }
    
    # Hash tracking para detectar duplicados
    seen_hashes = {}
    organized_files = []
    
    # Procesar cada video
    for video_file in all_videos:
        try:
            filename = video_file.name
            size_mb = get_file_size_mb(video_file)
            
            # Calcular hash para detectar duplicados
            file_hash = calculate_hash(video_file)
            
            if file_hash and file_hash in seen_hashes:
                print(f"🔄 Duplicado: {filename}")
                print(f"   Original: {seen_hashes[file_hash]}")
                stats['duplicates'] += 1
                continue
            
            # Determinar operación (mover vs copiar)
            is_in_usb = str(video_file).startswith(str(USB_BASE))
            operation = "MOVER" if is_in_usb else "COPIAR"
            
            # Ruta destino
            dest_path = META_UNIFIED / filename
            
            # Verificar si existe
            if dest_path.exists() and not DRY_RUN:
                # Agregar timestamp si existe
                stem = dest_path.stem
                ext = dest_path.suffix
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = META_UNIFIED / f"{stem}_{timestamp}{ext}"
            
            # Información del archivo
            info = {
                'original': filename,
                'size_mb': round(size_mb, 2),
                'source': str(video_file),
                'destination': str(dest_path),
                'operation': operation,
                'hash': file_hash
            }
            
            organized_files.append(info)
            
            # Mostrar información
            print(f"📱 [{operation}] {filename}")
            print(f"   Tamaño: {size_mb:.1f} MB")
            print(f"   Origen: {video_file.parent}")
            
            if DRY_RUN:
                print(f"   🔍 [SIMULACIÓN] Se {operation.lower()}ía aquí")
            else:
                # Ejecutar operación
                if is_in_usb:
                    shutil.move(str(video_file), str(dest_path))
                    print(f"   ✅ Movido exitosamente")
                    stats['moved'] += 1
                else:
                    shutil.copy2(str(video_file), str(dest_path))
                    print(f"   ✅ Copiado exitosamente")
                    stats['copied'] += 1
                
                # Registrar hash
                if file_hash:
                    seen_hashes[file_hash] = filename
            
            print()
            
        except Exception as e:
            print(f"❌ Error procesando {video_file.name}: {e}")
            stats['errors'] += 1
            print()
    
    # Guardar catálogo JSON
    catalog_path = META_UNIFIED / "meta_videos_catalog.json"
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
    print(f"📱 Videos de Meta encontrados: {len(all_videos)}")
    print(f"📋 Copiados (desde Downloads): {stats['copied']}")
    print(f"🔄 Movidos (dentro del USB): {stats['moved']}")
    print(f"⏭️  Duplicados detectados: {stats['duplicates']}")
    print(f"❌ Errores: {stats['errors']}")
    print()
    print(f"📁 Carpeta destino: {META_UNIFIED}")
    
    if not DRY_RUN:
        print(f"📋 Catálogo generado: {catalog_path}")
    
    if DRY_RUN:
        print()
        print("⚠️  MODO DRY RUN - No se movieron/copiaron archivos")
        print("   Cambia DRY_RUN = False en el script para ejecutar")
    else:
        print()
        print("✅ Organización completada exitosamente")
        print()
        print("💡 NOTA:")
        print("   - Videos del USB fueron MOVIDOS (ya no están en carpetas originales)")
        print("   - Videos de Downloads fueron COPIADOS (aún están en Downloads)")
        print("   - Duplicados detectados y omitidos automáticamente")

def show_statistics():
    """Muestra estadísticas de la colección unificada."""
    catalog_path = META_UNIFIED / "meta_videos_catalog.json"
    
    if not catalog_path.exists():
        print("❌ No hay catálogo. Ejecuta la organización primero.")
        return
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    print("📊 ESTADÍSTICAS DE VIDEOS META")
    print("=" * 70)
    print(f"📅 Última actualización: {catalog['generated']}")
    print(f"📱 Total de archivos: {catalog['total_files']}")
    print()
    
    stats = catalog['statistics']
    print(f"📋 Copiados: {stats['copied']}")
    print(f"🔄 Movidos: {stats['moved']}")
    print(f"⏭️  Duplicados: {stats['duplicates']}")
    print(f"❌ Errores: {stats['errors']}")
    
    # Calcular tamaño total
    total_size = sum(f['size_mb'] for f in catalog['files'])
    print()
    print(f"💾 Tamaño total: {total_size:.1f} MB ({total_size/1024:.2f} GB)")
    print()
    print(f"📁 Ubicación: {META_UNIFIED}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stats':
        show_statistics()
    else:
        organize_meta_videos()
