#!/usr/bin/env python3
"""
🛡️ BlackMamba Music Backup Manager
Gestión inteligente de backups de la colección musical
"""

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

# Configuración
MUSIC_LIBRARY = "music_library.json"
BACKUP_DIR = "music_backups"
HASH_CACHE = os.path.join(BACKUP_DIR, "file_hashes.json")

def calculate_file_hash(filepath):
    """Calcula hash SHA256 para detectar duplicados y verificar integridad"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"   ⚠️ Error calculando hash de {filepath}: {e}")
        return None

def load_hash_cache():
    """Carga caché de hashes de archivos"""
    if os.path.exists(HASH_CACHE):
        with open(HASH_CACHE, 'r') as f:
            return json.load(f)
    return {}

def save_hash_cache(cache):
    """Guarda caché de hashes"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(HASH_CACHE, 'w') as f:
        json.dump(cache, f, indent=2)

def create_backup():
    """Crea backup completo de la biblioteca musical"""
    print("🛡️ BLACKMAMBA BACKUP MANAGER")
    print("=" * 60)
    
    # Cargar biblioteca
    with open(MUSIC_LIBRARY, 'r') as f:
        library = json.load(f)
    
    # Crear nombre de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    print(f"📦 Creando backup: {backup_name}")
    os.makedirs(backup_path, exist_ok=True)
    
    # Estadísticas
    total_files = 0
    total_size = 0
    errors = []
    hash_cache = load_hash_cache()
    
    print(f"📂 Respaldando {len(library)} canciones...")
    
    for song in library:
        mp3_path = song.get('file_path_mp3')
        wav_path = song.get('file_path_wav')
        
        # Respaldar MP3
        if mp3_path and os.path.exists(mp3_path):
            try:
                file_hash = calculate_file_hash(mp3_path)
                filename = os.path.basename(mp3_path)
                dest = os.path.join(backup_path, filename)
                shutil.copy2(mp3_path, dest)
                
                # Guardar hash
                hash_cache[filename] = {
                    "hash": file_hash,
                    "size": os.path.getsize(mp3_path),
                    "backup_date": timestamp
                }
                
                total_files += 1
                total_size += os.path.getsize(mp3_path)
            except Exception as e:
                errors.append(f"MP3: {mp3_path} - {e}")
        
        # Respaldar WAV
        if wav_path and os.path.exists(wav_path):
            try:
                file_hash = calculate_file_hash(wav_path)
                filename = os.path.basename(wav_path)
                dest = os.path.join(backup_path, filename)
                shutil.copy2(wav_path, dest)
                
                hash_cache[filename] = {
                    "hash": file_hash,
                    "size": os.path.getsize(wav_path),
                    "backup_date": timestamp
                }
                
                total_files += 1
                total_size += os.path.getsize(wav_path)
            except Exception as e:
                errors.append(f"WAV: {wav_path} - {e}")
    
    # Respaldar biblioteca JSON
    shutil.copy2(MUSIC_LIBRARY, os.path.join(backup_path, MUSIC_LIBRARY))
    
    # Guardar caché de hashes
    save_hash_cache(hash_cache)
    
    # Crear archivo de metadatos del backup
    backup_info = {
        "timestamp": timestamp,
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "errors": errors
    }
    
    with open(os.path.join(backup_path, "backup_info.json"), 'w') as f:
        json.dump(backup_info, f, indent=2)
    
    print(f"\n✅ Backup completado!")
    print(f"   📁 {total_files} archivos respaldados")
    print(f"   💾 {backup_info['total_size_mb']} MB totales")
    print(f"   📂 Ubicación: {backup_path}")
    
    if errors:
        print(f"\n⚠️ {len(errors)} errores encontrados:")
        for err in errors[:5]:  # Mostrar solo primeros 5
            print(f"   - {err}")

def verify_integrity():
    """Verifica integridad de archivos musicales contra hashes"""
    print("🔍 VERIFICACIÓN DE INTEGRIDAD")
    print("=" * 60)
    
    hash_cache = load_hash_cache()
    
    if not hash_cache:
        print("⚠️ No hay caché de hashes. Ejecuta un backup primero.")
        return
    
    with open(MUSIC_LIBRARY, 'r') as f:
        library = json.load(f)
    
    corrupted = []
    missing = []
    verified = 0
    
    print(f"🔎 Verificando integridad de archivos...")
    
    for song in library:
        for path_key in ['file_path_mp3', 'file_path_wav']:
            filepath = song.get(path_key)
            if not filepath:
                continue
            
            filename = os.path.basename(filepath)
            
            # Verificar existencia
            if not os.path.exists(filepath):
                missing.append(filename)
                continue
            
            # Verificar hash
            if filename in hash_cache:
                current_hash = calculate_file_hash(filepath)
                cached_hash = hash_cache[filename]["hash"]
                
                if current_hash == cached_hash:
                    verified += 1
                else:
                    corrupted.append(filename)
    
    print(f"\n📊 Resultados:")
    print(f"   ✅ {verified} archivos verificados")
    print(f"   🚫 {len(missing)} archivos faltantes")
    print(f"   ⚠️ {len(corrupted)} archivos posiblemente corruptos")
    
    if missing:
        print(f"\n🚫 Archivos faltantes:")
        for f in missing[:10]:
            print(f"   - {f}")
    
    if corrupted:
        print(f"\n⚠️ Archivos corruptos:")
        for f in corrupted:
            print(f"   - {f}")

def list_backups():
    """Lista todos los backups disponibles"""
    print("📚 BACKUPS DISPONIBLES")
    print("=" * 60)
    
    if not os.path.exists(BACKUP_DIR):
        print("⚠️ No hay backups creados aún.")
        return
    
    backups = sorted([d for d in os.listdir(BACKUP_DIR) 
                     if os.path.isdir(os.path.join(BACKUP_DIR, d))], 
                     reverse=True)
    
    if not backups:
        print("⚠️ No hay backups creados aún.")
        return
    
    print(f"📦 {len(backups)} backup(s) encontrado(s):\n")
    
    for backup in backups:
        backup_path = os.path.join(BACKUP_DIR, backup)
        info_file = os.path.join(backup_path, "backup_info.json")
        
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                info = json.load(f)
            
            print(f"📂 {backup}")
            print(f"   ⏰ {info['timestamp']}")
            print(f"   📁 {info['total_files']} archivos")
            print(f"   💾 {info['total_size_mb']} MB")
            print()

def main():
    """Menú principal"""
    print("🛡️ BLACKMAMBA MUSIC BACKUP MANAGER")
    print("=" * 60)
    print("1) Crear nuevo backup")
    print("2) Verificar integridad de archivos")
    print("3) Listar backups existentes")
    print("4) Salir")
    print("=" * 60)
    
    choice = input("Selecciona una opción (1-4): ").strip()
    
    if choice == "1":
        create_backup()
    elif choice == "2":
        verify_integrity()
    elif choice == "3":
        list_backups()
    elif choice == "4":
        print("👋 ¡Hasta pronto!")
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
