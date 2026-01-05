#!/usr/bin/env python3
"""
🦅 BlackMamba Downloads Organizer
Organizador inteligente de Downloads → USB con clasificación automática por tipo
Arquitecto: Iyari Cancino Gomez
Fecha: 30 de Diciembre, 2025
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import hashlib

# === CONFIGURACIÓN ===
DOWNLOADS_DIR = Path.home() / "Downloads"
USB_BASE = Path("/Volumes/ADATA SC740")
CATALOG_FILE = USB_BASE / "downloads_transfer_catalog.json"

# Estructura de destinos en USB
DESTINATIONS = {
    "images": USB_BASE / "05_IMAGENES",
    "audio": USB_BASE / "06_AUDIO",
    "documents": USB_BASE / "07_DOCUMENTOS",
    "archives": USB_BASE / "08_ARCHIVOS",
    "code": USB_BASE / "09_CODIGO",
    "misc": USB_BASE / "10_VARIOS"
}



# Extensiones por categoría
EXTENSIONS = {
    "images": {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.svg'},
    "audio": {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'},
    "documents": {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages', '.html', '.htm'},
    "archives": {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.dmg', '.iso'},
    "code": {'.py', '.js', '.java', '.cpp', '.c', '.h', '.json', '.xml', '.yaml', '.yml', '.sh'}
}

# Archivos a excluir (sistema, temporales, etc.)
EXCLUDE_PATTERNS = [
    '.DS_Store',
    '.localized',
    'Thumbs.db',
    '.Spotlight-V100',
    '.Trashes',
    '.TemporaryItems',
    'desktop.ini'
]

# === FUNCIONES PRINCIPALES ===

def calculate_hash(file_path, chunk_size=1024*1024):
    """Calcula MD5 hash del primer MB para detección de duplicados"""
    try:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            md5.update(chunk)
        return md5.hexdigest()
    except:
        return None

def should_exclude(file_path):
    """Verifica si el archivo debe ser excluido"""
    file_name = os.path.basename(file_path)
    
    # Excluir archivos del sistema
    if file_name in EXCLUDE_PATTERNS:
        return True
    
    # Excluir archivos ocultos
    if file_name.startswith('.'):
        return True
    
    # Excluir archivos temporales
    if file_name.endswith('.tmp') or file_name.endswith('.temp'):
        return True
    
    return False

def categorize_file(file_path):
    """Determina la categoría del archivo según su extensión"""
    extension = Path(file_path).suffix.lower()
    
    for category, exts in EXTENSIONS.items():
        if extension in exts:
            return category
    
    return "misc"  # Categoría por defecto

def safe_filename(filename):
    """Limpia el nombre del archivo de caracteres problemáticos"""
    # Reemplazar caracteres problemáticos
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    return safe_name

def organize_downloads(dry_run=True):
    """
    Organiza todos los archivos de Downloads al USB
    
    Args:
        dry_run: Si True, solo simula (no mueve archivos)
    """
    
    print("🦅 BlackMamba Downloads Organizer")
    print("=" * 60)
    print(f"📁 Origen: {DOWNLOADS_DIR}")
    print(f"💾 Destino: {USB_BASE}")
    print(f"🔍 Modo: {'SIMULACIÓN (Dry Run)' if dry_run else '🔥 EJECUCIÓN REAL'}")
    print("=" * 60)
    print()
    
    # Verificar que existe USB
    if not USB_BASE.exists():
        print(f"❌ Error: USB no encontrado en {USB_BASE}")
        return
    
    # Crear directorios de destino
    for dest_path in DESTINATIONS.values():
        if not dry_run:
            dest_path.mkdir(parents=True, exist_ok=True)
    
    # Escanear Downloads
    print("🔍 Escaneando Downloads...")
    all_files = []
    for root, dirs, files in os.walk(DOWNLOADS_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude(file_path):
                all_files.append(file_path)
    
    print(f"📊 Archivos encontrados: {len(all_files)}")
    print()
    
    # Estadísticas
    stats = {
        "total_found": len(all_files),
        "moved": 0,
        "skipped": 0,
        "errors": 0,
        "duplicates": 0,
        "by_category": {cat: 0 for cat in DESTINATIONS.keys()}
    }
    
    # Catálogo de archivos procesados
    catalog = {
        "transfer_date": datetime.now().isoformat(),
        "source": str(DOWNLOADS_DIR),
        "destination": str(USB_BASE),
        "dry_run": dry_run,
        "files": []
    }
    
    # Hash de archivos ya procesados (para detectar duplicados)
    processed_hashes = set()
    
    # Procesar cada archivo
    for i, file_path in enumerate(all_files, 1):
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            category = categorize_file(file_path)
            dest_dir = DESTINATIONS[category]
            
            # Limpiar nombre de archivo
            safe_name = safe_filename(file_name)
            dest_path = dest_dir / safe_name
            
            # Calcular hash para detectar duplicados
            file_hash = calculate_hash(file_path)
            
            # Verificar duplicados
            if file_hash and file_hash in processed_hashes:
                print(f"⚠️  [{i}/{len(all_files)}] DUPLICADO: {file_name}")
                stats["duplicates"] += 1
                stats["skipped"] += 1
                continue
            
            # Verificar si ya existe en destino
            if dest_path.exists():
                # Si existe, agregar timestamp al nombre
                stem = dest_path.stem
                suffix = dest_path.suffix
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"
            
            # Mover archivo
            if not dry_run:
                shutil.move(file_path, dest_path)
                print(f"✅ [{i}/{len(all_files)}] {category.upper()}: {file_name} → {dest_dir.name}/")
            else:
                print(f"🔍 [{i}/{len(all_files)}] {category.upper()}: {file_name} → {dest_dir.name}/")
            
            # Actualizar estadísticas
            stats["moved"] += 1
            stats["by_category"][category] += 1
            
            if file_hash:
                processed_hashes.add(file_hash)
            
            # Agregar al catálogo
            catalog["files"].append({
                "original_path": file_path,
                "destination_path": str(dest_path),
                "category": category,
                "size": file_size,
                "hash": file_hash,
                "moved": not dry_run
            })
            
        except Exception as e:
            print(f"❌ [{i}/{len(all_files)}] ERROR con {file_name}: {e}")
            stats["errors"] += 1
    
    # Guardar catálogo
    if not dry_run:
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        print(f"\n📋 Catálogo guardado: {CATALOG_FILE}")
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE OPERACIÓN")
    print("=" * 60)
    print(f"Total archivos encontrados: {stats['total_found']}")
    print(f"✅ Movidos: {stats['moved']}")
    print(f"⚠️  Omitidos: {stats['skipped']}")
    print(f"🔄 Duplicados detectados: {stats['duplicates']}")
    print(f"❌ Errores: {stats['errors']}")
    print()
    print("📂 Distribución por categoría:")
    for category, count in stats['by_category'].items():
        if count > 0:
            print(f"  • {category.upper()}: {count} archivos → {DESTINATIONS[category].name}/")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️  ESTO FUE UNA SIMULACIÓN")
        print("Para ejecutar realmente, usa: organize_downloads(dry_run=False)")
    else:
        print("\n✅ OPERACIÓN COMPLETADA")
        print(f"💾 Todos los archivos están ahora en: {USB_BASE}")

def main():
    """Función principal"""
    import sys
    
    # Verificar argumentos
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        dry_run = False
    
    organize_downloads(dry_run=dry_run)

if __name__ == "__main__":
    main()
