#!/usr/bin/env python3
"""
🦅 BLACKMAMBA TOTAL ARSENAL ORGANIZER
Arquitecto: Iyari Cancino Gomez
Fecha: 30 de Diciembre, 2025

Sistema de organización total del arsenal musical:
- Extrae todo de Downloads
- Organiza por formato (WAV/MP3/FLAC)
- Sincroniza con USB (ADATA SC740)
- Limpia nombres de archivo
- Actualiza music_library.json
"""

import os
import shutil
import json
import re
from pathlib import Path
from datetime import datetime
import hashlib

class TotalArsenalOrganizer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.downloads_dir = Path.home() / "Downloads"
        
        # Estructura de carpetas paralela
        self.music_vault = Path.home() / "Desktop" / "BlackMamba_Music_Vault"
        self.wav_dir = self.music_vault / "WAV_Masters"
        self.mp3_dir = self.music_vault / "MP3_Distribution"
        self.flac_dir = self.music_vault / "FLAC_Archive"
        
        # USB (detectar automáticamente)
        self.usb_paths = [
            Path("/Volumes/ADATA SC740"),
            Path("/Volumes/ADATA"),
            Path("/Volumes/SC740")
        ]
        self.usb_dir = None
        for usb in self.usb_paths:
            if usb.exists():
                self.usb_dir = usb / "BlackMamba_Music_Arsenal"
                break
        
        # Logs
        self.log_file = self.base_dir / "organization_log.json"
        self.stats = {
            "moved": 0,
            "renamed": 0,
            "duplicates": 0,
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def setup_structure(self):
        """Crear estructura de carpetas"""
        print("📁 Creando estructura de carpetas...")
        
        # Carpetas locales
        for dir_path in [self.wav_dir, self.mp3_dir, self.flac_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path.name}")
        
        # Carpetas USB
        if self.usb_dir:
            usb_dirs = [
                self.usb_dir / "WAV_Masters",
                self.usb_dir / "MP3_Distribution", 
                self.usb_dir / "FLAC_Archive",
                self.usb_dir / "Backups"
            ]
            for dir_path in usb_dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ USB: {self.usb_dir}")
        else:
            print("  ⚠️  USB no detectado (conectar ADATA SC740)")
    
    def clean_filename(self, filename):
        """Limpiar nombres de archivo horribles"""
        # Remover __Title_, __Título_, etc.
        name = re.sub(r'__[Tt]itle?_?\s*["\']?', '', filename)
        name = re.sub(r'__[Tt]ítulo_?\s*["\']?', '', name)
        name = re.sub(r'["\']__', '', name)
        name = re.sub(r'__', ' - ', name)
        
        # Remover (Cover) (1) (2) etc
        name = re.sub(r'\s*\(Cover\)\s*', '', name)
        name = re.sub(r'\s*\(\d+\)\s*', '', name)
        
        # Limpiar caracteres especiales excepto básicos
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        
        # Normalizar espacios
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        
        # Si termina en "- BlackMamba.ext", está bien
        # Si no, agregar "- BlackMamba"
        base, ext = os.path.splitext(name)
        if not base.endswith('- BlackMamba'):
            if ' - ' not in base:
                base = f"{base} - BlackMamba"
        
        return f"{base}{ext}"
    
    def get_file_hash(self, filepath):
        """Calcular hash del archivo (primeros 64KB)"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                hasher.update(f.read(65536))
            return hasher.hexdigest()[:12]
        except:
            return None
    
    def is_duplicate(self, source_path, target_path):
        """Verificar si es duplicado por hash"""
        if not target_path.exists():
            return False
        
        source_hash = self.get_file_hash(source_path)
        target_hash = self.get_file_hash(target_path)
        
        return source_hash == target_hash
    
    def organize_file(self, file_path):
        """Organizar un archivo individual"""
        try:
            # Determinar extensión y carpeta destino
            ext = file_path.suffix.lower()
            if ext == '.wav':
                local_dest_dir = self.wav_dir
                usb_dest_dir = self.usb_dir / "WAV_Masters" if self.usb_dir else None
            elif ext == '.mp3':
                local_dest_dir = self.mp3_dir
                usb_dest_dir = self.usb_dir / "MP3_Distribution" if self.usb_dir else None
            elif ext == '.flac':
                local_dest_dir = self.flac_dir
                usb_dest_dir = self.usb_dir / "FLAC_Archive" if self.usb_dir else None
            else:
                return  # Ignorar otros formatos
            
            # Limpiar nombre
            clean_name = self.clean_filename(file_path.name)
            local_target = local_dest_dir / clean_name
            
            # Verificar duplicado
            if self.is_duplicate(file_path, local_target):
                print(f"  ⏭️  Duplicado: {file_path.name}")
                self.stats["duplicates"] += 1
                file_path.unlink()  # Eliminar duplicado
                return
            
            # Mover a carpeta local
            if local_target.exists():
                # Si existe pero no es duplicado, agregar sufijo
                base = local_target.stem
                counter = 1
                while local_target.exists():
                    local_target = local_dest_dir / f"{base}_{counter}{ext}"
                    counter += 1
            
            shutil.move(str(file_path), str(local_target))
            print(f"  ✅ {file_path.name} → {local_target.name}")
            self.stats["moved"] += 1
            
            if file_path.name != clean_name:
                self.stats["renamed"] += 1
            
            # Copiar a USB si está disponible
            if usb_dest_dir:
                usb_target = usb_dest_dir / clean_name
                if not usb_target.exists():
                    shutil.copy2(str(local_target), str(usb_target))
                    print(f"    💾 USB: {usb_target.name}")
        
        except Exception as e:
            error_msg = f"Error con {file_path.name}: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats["errors"].append(error_msg)
    
    def scan_and_organize_downloads(self):
        """Escanear Downloads y organizar todos los archivos de audio"""
        print(f"\n🔍 Escaneando Downloads: {self.downloads_dir}")
        
        audio_extensions = {'.mp3', '.wav', '.flac'}
        files_found = []
        
        for file_path in self.downloads_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                # Ignorar archivos de VS Code
                if 'Visual Studio Code.app' in str(file_path):
                    continue
                files_found.append(file_path)
        
        print(f"📊 Encontrados: {len(files_found)} archivos")
        
        for file_path in files_found:
            self.organize_file(file_path)
    
    def scan_and_organize_collection(self):
        """Organizar la colección actual (BlackMamba_Music_Collection)"""
        collection_dir = self.base_dir / "BlackMamba_Music_Collection"
        
        if not collection_dir.exists():
            return
        
        print(f"\n🎵 Organizando colección: {collection_dir}")
        
        audio_extensions = {'.mp3', '.wav', '.flac'}
        files_found = []
        
        for file_path in collection_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                files_found.append(file_path)
        
        print(f"📊 Encontrados: {len(files_found)} archivos")
        
        for file_path in files_found:
            self.organize_file(file_path)
    
    def generate_report(self):
        """Generar reporte de organización"""
        print("\n" + "="*60)
        print("📊 REPORTE DE ORGANIZACIÓN")
        print("="*60)
        print(f"✅ Archivos movidos: {self.stats['moved']}")
        print(f"🔄 Archivos renombrados: {self.stats['renamed']}")
        print(f"⏭️  Duplicados eliminados: {self.stats['duplicates']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errores ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")
        
        print(f"\n📁 Carpeta local: {self.music_vault}")
        if self.usb_dir:
            print(f"💾 USB: {self.usb_dir}")
        
        # Guardar log
        with open(self.log_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"\n📝 Log guardado: {self.log_file}")
        print("="*60)
    
    def run(self):
        """Ejecutar organización completa"""
        print("🦅 BLACKMAMBA TOTAL ARSENAL ORGANIZER")
        print("="*60)
        
        self.setup_structure()
        self.scan_and_organize_downloads()
        self.scan_and_organize_collection()
        self.generate_report()
        
        print("\n✅ Organización completada. Todo en orden, Rey.")

if __name__ == "__main__":
    organizer = TotalArsenalOrganizer()
    organizer.run()
