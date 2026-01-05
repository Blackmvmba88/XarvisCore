#!/usr/bin/env python3
"""
🦅 SUNO AUTOPIPELINE - Sistema Inteligente de Procesamiento Automático
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez

Flujo Completo:
1. Detecta canciones nuevas de Suno (MP3 + WAV)
2. Las incorpora a music_library.json
3. Extrae letras automáticamente
4. Sincroniza al USB
5. Genera fingerprints para el detector

Este script es el corazón del flujo de producción musical del Reino.
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
import hashlib
import re

# === CONFIGURACIÓN ===
BASE_DIR = Path(__file__).parent
SUNO_DOWNLOAD_PATHS = [
    Path.home() / "Downloads",
    Path.home() / "Music/Suno",
    Path.home() / "Desktop"
]

# Destinos
MUSIC_VAULT = Path.home() / "Desktop/BlackMamba_Music_Vault"
USB_PATHS = [
    Path("/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA"),
    Path("/Volumes/ADATA SC740/BlackMamba_Music_Arsenal"),
    Path("/Volumes/ADATA/BlackMamba_Music_Arsenal")
]

# Archivos de índice
MUSIC_LIBRARY = BASE_DIR / "music_library.json"
FINGERPRINTS_DB = BASE_DIR / "audio_fingerprints.json"
LYRICS_CACHE = BASE_DIR / "lyrics_cache.json"
PIPELINE_LOG = BASE_DIR / "suno_pipeline.log"

# Patrones Suno
SUNO_PATTERNS = [
    r'.*\(.*\)\.mp3$',  # Cualquier cosa con (algo).mp3
    r'.*\(.*\)\.wav$',
    r'.*-.*\.mp3$',     # Formato con guión
    r'.*_v\d+\.mp3$'    # Versiones v1, v2, etc
]

class SunoAutoPipeline:
    def __init__(self):
        self.new_songs = []
        self.processed_songs = []
        self.usb_path = self._detect_usb()
        
        # Crear directorios si no existen
        MUSIC_VAULT.mkdir(parents=True, exist_ok=True)
        (MUSIC_VAULT / "MP3").mkdir(exist_ok=True)
        (MUSIC_VAULT / "WAV").mkdir(exist_ok=True)
        (MUSIC_VAULT / "Lyrics").mkdir(exist_ok=True)
        
    def log(self, msg, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        
        with open(PIPELINE_LOG, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    
    def _detect_usb(self):
        """Detecta el USB conectado"""
        for path in USB_PATHS:
            if path.exists():
                self.log(f"USB detectado: {path}")
                return path
        self.log("USB no detectado - se omitirá sincronización", "WARNING")
        return None
    
    def _get_file_hash(self, filepath):
        """Hash MD5 del archivo"""
        try:
            md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    md5.update(chunk)
            return md5.hexdigest()[:12]
        except:
            return None
    
    def _normalize_song_name(self, filename):
        """
        Normaliza el nombre de la canción para encontrar pares MP3/WAV
        "Mi Cancion (Intro).mp3" -> "mi_cancion"
        """
        name = Path(filename).stem
        # Remover contenido entre paréntesis
        name = re.sub(r'\([^)]*\)', '', name)
        # Remover sufijos comunes de Suno
        name = re.sub(r'[-_]v\d+', '', name)
        name = re.sub(r'[-_]\d{8}', '', name)
        # Limpiar y normalizar
        name = name.strip().lower()
        name = re.sub(r'[^a-z0-9]+', '_', name)
        name = name.strip('_')
        return name
    
    def scan_for_new_songs(self):
        """Escanea carpetas de descarga buscando canciones nuevas de Suno"""
        self.log("🔍 Escaneando carpetas de descarga...")
        
        found_files = {}  # normalized_name: {mp3: path, wav: path}
        
        for folder in SUNO_DOWNLOAD_PATHS:
            if not folder.exists():
                continue
            
            self.log(f"Escaneando: {folder}")
            
            for file in folder.rglob("*"):
                if not file.is_file():
                    continue
                
                ext = file.suffix.lower()
                if ext not in ['.mp3', '.wav']:
                    continue
                
                # Verificar si es de Suno (patrones o reciente)
                is_suno = any(re.match(pattern, file.name, re.IGNORECASE) 
                             for pattern in SUNO_PATTERNS)
                
                # O es archivo muy reciente (últimas 24 horas)
                if not is_suno:
                    age_hours = (time.time() - file.stat().st_mtime) / 3600
                    is_suno = age_hours < 24
                
                if not is_suno:
                    continue
                
                # Normalizar nombre para agrupar pares
                normalized = self._normalize_song_name(file.name)
                
                if normalized not in found_files:
                    found_files[normalized] = {}
                
                if ext == '.mp3':
                    found_files[normalized]['mp3'] = file
                elif ext == '.wav':
                    found_files[normalized]['wav'] = file
        
        # Filtrar canciones que ya existen en la biblioteca
        existing_library = self._load_library()
        existing_hashes = {song.get('hash') for song in existing_library if song.get('hash')}
        
        new_count = 0
        for normalized, files in found_files.items():
            # Verificar si ya existe por hash
            mp3_path = files.get('mp3')
            if mp3_path:
                file_hash = self._get_file_hash(mp3_path)
                if file_hash not in existing_hashes:
                    self.new_songs.append({
                        'normalized_name': normalized,
                        'mp3': mp3_path,
                        'wav': files.get('wav'),
                        'hash': file_hash
                    })
                    new_count += 1
        
        self.log(f"✅ Encontradas {new_count} canciones nuevas")
        return new_count
    
    def _load_library(self):
        """Carga la biblioteca musical existente"""
        if MUSIC_LIBRARY.exists():
            with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_library(self, library):
        """Guarda la biblioteca musical"""
        with open(MUSIC_LIBRARY, 'w', encoding='utf-8') as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
    
    def copy_to_vault(self, song):
        """Copia MP3 y WAV al vault local"""
        self.log(f"📦 Copiando '{song['normalized_name']}'...")
        
        copied = {}
        
        if song['mp3']:
            dest = MUSIC_VAULT / "MP3" / song['mp3'].name
            shutil.copy2(song['mp3'], dest)
            copied['mp3'] = str(dest)
            self.log(f"  ✅ MP3 -> {dest.name}")
        
        if song['wav']:
            dest = MUSIC_VAULT / "WAV" / song['wav'].name
            shutil.copy2(song['wav'], dest)
            copied['wav'] = str(dest)
            self.log(f"  ✅ WAV -> {dest.name}")
        
        return copied
    
    def extract_lyrics(self, song):
        """
        Extrae letras de la canción.
        En Suno, las letras suelen estar en archivos .txt acompañantes
        o en los metadatos del audio.
        """
        self.log(f"📝 Extrayendo letras de '{song['normalized_name']}'...")
        
        lyrics = None
        
        # Método 1: Buscar archivo .txt con el mismo nombre
        if song['mp3']:
            txt_file = song['mp3'].with_suffix('.txt')
            if txt_file.exists():
                with open(txt_file, 'r', encoding='utf-8') as f:
                    lyrics = f.read().strip()
                self.log(f"  ✅ Letras encontradas en .txt")
        
        # Método 2: Buscar en el mismo directorio archivos .txt recientes
        if not lyrics and song['mp3']:
            parent_dir = song['mp3'].parent
            for txt_file in parent_dir.glob("*.txt"):
                # Si el txt es reciente (última hora)
                age_hours = (time.time() - txt_file.stat().st_mtime) / 3600
                if age_hours < 1:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        # Verificar que parezca letra (tiene más de 50 caracteres)
                        if len(content) > 50:
                            lyrics = content
                            self.log(f"  ✅ Letras encontradas en {txt_file.name}")
                            break
        
        # Método 3: Intentar extraer de metadatos con ffmpeg
        if not lyrics and song['mp3']:
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                     '-show_format', str(song['mp3'])],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    metadata = json.loads(result.stdout)
                    tags = metadata.get('format', {}).get('tags', {})
                    lyrics = tags.get('lyrics') or tags.get('LYRICS') or tags.get('unsyncedlyrics')
                    if lyrics:
                        self.log(f"  ✅ Letras extraídas de metadatos")
            except:
                pass
        
        # Guardar letras si se encontraron
        if lyrics:
            lyrics_file = MUSIC_VAULT / "Lyrics" / f"{song['normalized_name']}.txt"
            with open(lyrics_file, 'w', encoding='utf-8') as f:
                f.write(lyrics)
            return str(lyrics_file)
        else:
            self.log(f"  ⚠️ Letras no encontradas", "WARNING")
            return None
    
    def add_to_library(self, song, vault_paths, lyrics_path):
        """Agrega la canción a music_library.json"""
        library = self._load_library()
        
        # Crear entrada
        entry = {
            'title': song['normalized_name'].replace('_', ' ').title(),
            'artist': 'BlackMamba',
            'source': 'suno',
            'hash': song['hash'],
            'date_added': datetime.now().isoformat(),
            'paths': vault_paths
        }
        
        if lyrics_path:
            entry['lyrics'] = lyrics_path
        
        # Agregar tags de Suno
        entry['tags'] = ['suno', 'blackmamba_records', '2026']
        
        library.append(entry)
        self._save_library(library)
        
        self.log(f"  ✅ Agregada a biblioteca: {entry['title']}")
        return entry
    
    def generate_fingerprint(self, song_entry):
        """Genera fingerprint para el detector de audio"""
        mp3_path = song_entry['paths'].get('mp3')
        if not mp3_path or not Path(mp3_path).exists():
            return False
        
        try:
            # Verificar si fpcalc está disponible
            if not shutil.which('fpcalc'):
                self.log(f"  ⏭️ fpcalc no instalado - omitiendo fingerprint", "WARNING")
                return False
            
            # Usar fpcalc para generar fingerprint
            result = subprocess.run(
                ['fpcalc', '-json', mp3_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                fp_data = json.loads(result.stdout)
                
                # Cargar base de fingerprints - debe ser lista
                fingerprints = []
                if FINGERPRINTS_DB.exists():
                    try:
                        with open(FINGERPRINTS_DB, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Asegurar que sea lista
                            fingerprints = data if isinstance(data, list) else []
                    except:
                        fingerprints = []
                
                # Agregar nuevo fingerprint
                fingerprints.append({
                    'title': song_entry['title'],
                    'artist': song_entry['artist'],
                    'file_path': mp3_path,
                    'duration': fp_data['duration'],
                    'fingerprint': ','.join(map(str, fp_data['fingerprint'])),
                    'indexed_at': datetime.now().isoformat()
                })
                
                # Guardar
                with open(FINGERPRINTS_DB, 'w', encoding='utf-8') as f:
                    json.dump(fingerprints, f, indent=2, ensure_ascii=False)
                
                self.log(f"  ✅ Fingerprint generado")
                return True
        except Exception as e:
            self.log(f"  ⚠️ Error generando fingerprint: {e}", "WARNING")
        
        return False
    
    def _sanitize_filename(self, filename):
        """Sanitiza nombres de archivo removiendo caracteres problemáticos"""
        # Remover emojis y caracteres especiales
        sanitized = filename
        # Remover emojis comunes
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        sanitized = emoji_pattern.sub('', sanitized)
        
        # Remover otros caracteres problemáticos pero mantener guiones, espacios, paréntesis
        sanitized = re.sub(r'[<>:"|?*\x00-\x1f]', '', sanitized)
        
        # Limpiar espacios múltiples y guiones bajos
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        
        return sanitized
    
    def sync_to_usb(self, song_entry):
        """Sincroniza la canción al USB"""
        if not self.usb_path:
            self.log("  ⏭️ USB no disponible - omitiendo sync", "WARNING")
            return False
        
        try:
            # Crear estructura en USB si no existe
            (self.usb_path / "MP3").mkdir(parents=True, exist_ok=True)
            (self.usb_path / "WAV").mkdir(parents=True, exist_ok=True)
            (self.usb_path / "Lyrics").mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos con nombres sanitizados
            for format_type, path in song_entry['paths'].items():
                src = Path(path)
                if src.exists():
                    # Sanitizar nombre de archivo
                    clean_name = self._sanitize_filename(src.name)
                    dest = self.usb_path / format_type.upper() / clean_name
                    
                    try:
                        shutil.copy2(src, dest)
                        self.log(f"  ✅ USB sync: {format_type.upper()}")
                    except Exception as e:
                        self.log(f"  ⚠️ USB sync falló para {src.name}: {e}", "WARNING")
            
            # Copiar letras si existen
            if song_entry.get('lyrics'):
                lyrics_src = Path(song_entry['lyrics'])
                if lyrics_src.exists():
                    clean_name = self._sanitize_filename(lyrics_src.name)
                    lyrics_dest = self.usb_path / "Lyrics" / clean_name
                    try:
                        shutil.copy2(lyrics_src, lyrics_dest)
                        self.log(f"  ✅ USB sync: Lyrics")
                    except Exception as e:
                        self.log(f"  ⚠️ USB sync falló para letras: {e}", "WARNING")
            
            return True
        except Exception as e:
            self.log(f"  ❌ Error en USB sync: {e}", "ERROR")
            return False
    
    def process_song(self, song):
        """Procesa una canción completa: copia, letras, índice, fingerprint, USB"""
        self.log(f"\n🎵 PROCESANDO: {song['normalized_name']}")
        self.log("=" * 60)
        
        try:
            # 1. Copiar a vault
            vault_paths = self.copy_to_vault(song)
            
            # 2. Extraer letras
            lyrics_path = self.extract_lyrics(song)
            
            # 3. Agregar a biblioteca
            entry = self.add_to_library(song, vault_paths, lyrics_path)
            
            # 4. Generar fingerprint
            self.generate_fingerprint(entry)
            
            # 5. Sincronizar al USB
            self.sync_to_usb(entry)
            
            self.processed_songs.append(entry)
            self.log(f"✅ COMPLETADO: {entry['title']}")
            
        except Exception as e:
            self.log(f"❌ ERROR procesando {song['normalized_name']}: {e}", "ERROR")
    
    def run(self):
        """Ejecuta el pipeline completo"""
        self.log("\n" + "=" * 60)
        self.log("🦅 SUNO AUTOPIPELINE - INICIANDO")
        self.log("=" * 60)
        
        # 1. Escanear nuevas canciones
        count = self.scan_for_new_songs()
        
        if count == 0:
            self.log("\n✅ No hay canciones nuevas que procesar")
            return
        
        # 2. Procesar cada canción
        for i, song in enumerate(self.new_songs, 1):
            self.log(f"\n[{i}/{count}]")
            self.process_song(song)
            time.sleep(0.5)  # Pequeña pausa entre canciones
        
        # 3. Resumen final
        self.log("\n" + "=" * 60)
        self.log("🎉 PIPELINE COMPLETADO")
        self.log("=" * 60)
        self.log(f"📊 Canciones procesadas: {len(self.processed_songs)}")
        self.log(f"📁 Biblioteca actualizada: {MUSIC_LIBRARY}")
        if self.usb_path:
            self.log(f"💾 USB sincronizado: {self.usb_path}")
        self.log(f"📋 Log completo: {PIPELINE_LOG}")
        
        # Mostrar canciones procesadas
        if self.processed_songs:
            self.log("\n🎵 CANCIONES AGREGADAS:")
            for entry in self.processed_songs:
                self.log(f"  • {entry['title']}")

def main():
    """Punto de entrada principal"""
    pipeline = SunoAutoPipeline()
    pipeline.run()

if __name__ == "__main__":
    main()
