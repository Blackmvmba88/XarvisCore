#!/usr/bin/env python3
"""
Music Library Scanner & Validator
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez

Escanea toda la música dispersa, detecta pares MP3/WAV, 
valida integridad y genera índice unificado.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class MusicLibraryScanner:
    def __init__(self):
        # Ubicaciones a escanear
        self.locations = [
            "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA",
            str(Path.home() / "Downloads"),
            str(Path.home() / "Music/Suno")
        ]
        
        # Formatos soportados
        self.audio_formats = ['.mp3', '.wav', '.flac', '.m4a']
        
        # Índice completo
        self.library = []
        self.pairs = defaultdict(dict)  # Por título: {mp3: path, wav: path}
        self.orphans = []  # Archivos sin par
        
    def get_file_hash(self, filepath, chunk_size=8192):
        """Genera hash MD5 del archivo para identificación única."""
        try:
            md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    md5.update(chunk)
            return md5.hexdigest()[:12]  # Primeros 12 caracteres
        except:
            return None
    
    def extract_song_name(self, filename):
        """
        Extrae el nombre base de la canción sin extensión ni sufijos Suno.
        Ejemplos:
        - "Trap_Vibes.mp3" -> "trap_vibes"
        - "Trap_Vibes (1).wav" -> "trap_vibes"
        - "cosmic_journey_extended.mp3" -> "cosmic_journey_extended"
        """
        # Remover extensión
        name = Path(filename).stem
        
        # Remover números de versión Suno: " (1)", " (2)", etc.
        import re
        name = re.sub(r'\s*\(\d+\)$', '', name)
        
        # Normalizar: lowercase y espacios
        name = name.lower().strip()
        name = name.replace(' ', '_')
        
        return name
    
    def get_file_info(self, filepath):
        """Extrae información completa del archivo."""
        path = Path(filepath)
        
        # Obtener stats
        stats = path.stat()
        size_mb = stats.st_size / (1024 * 1024)
        
        # Extraer nombre base
        song_name = self.extract_song_name(path.name)
        
        info = {
            "file_path": str(path.absolute()),
            "filename": path.name,
            "song_name": song_name,
            "format": path.suffix[1:].lower(),  # mp3, wav, etc.
            "size_mb": round(size_mb, 2),
            "modified_date": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "location": self._get_location_type(str(path)),
            "hash": self.get_file_hash(filepath)
        }
        
        return info
    
    def _get_location_type(self, filepath):
        """Determina de dónde viene el archivo."""
        if "ADATA SC740" in filepath:
            return "USB"
        elif "Downloads" in filepath:
            return "Downloads"
        elif "Music/Suno" in filepath:
            return "Suno"
        else:
            return "Other"
    
    def scan_directory(self, directory):
        """Escanea recursivamente un directorio."""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"⚠️  Ubicación no encontrada: {directory}")
            return []
        
        print(f"📂 Escaneando: {directory}")
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            # Ignorar carpetas ocultas y temporales
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for filename in filenames:
                # Solo archivos de audio
                if any(filename.lower().endswith(ext) for ext in self.audio_formats):
                    filepath = os.path.join(root, filename)
                    try:
                        info = self.get_file_info(filepath)
                        files.append(info)
                    except Exception as e:
                        print(f"❌ Error procesando {filename}: {e}")
        
        print(f"   ✅ Encontrados: {len(files)} archivos")
        return files
    
    def scan_all_locations(self):
        """Escanea todas las ubicaciones configuradas."""
        print("🔍 Iniciando escaneo completo de biblioteca musical...")
        print("━" * 60)
        
        all_files = []
        for location in self.locations:
            files = self.scan_directory(location)
            all_files.extend(files)
        
        print("━" * 60)
        print(f"📊 Total de archivos encontrados: {len(all_files)}")
        
        self.library = all_files
        return all_files
    
    def detect_pairs(self):
        """
        Detecta pares MP3/WAV de la misma canción.
        Agrupa por song_name y marca huérfanos.
        """
        print("\n🔗 Detectando pares MP3/WAV...")
        
        # Agrupar por nombre de canción
        songs = defaultdict(list)
        for file in self.library:
            songs[file['song_name']].append(file)
        
        # Analizar cada grupo
        for song_name, files in songs.items():
            formats = {f['format']: f for f in files}
            
            # Caso ideal: tiene MP3 y WAV
            if 'mp3' in formats and 'wav' in formats:
                self.pairs[song_name] = {
                    'mp3': formats['mp3'],
                    'wav': formats['wav'],
                    'status': 'complete',
                    'quality': 'premium'  # Ambos formatos
                }
            
            # Solo MP3
            elif 'mp3' in formats and 'wav' not in formats:
                self.pairs[song_name] = {
                    'mp3': formats['mp3'],
                    'wav': None,
                    'status': 'mp3_only',
                    'quality': 'standard'
                }
                self.orphans.append({
                    'song': song_name,
                    'has': 'mp3',
                    'missing': 'wav',
                    'path': formats['mp3']['file_path']
                })
            
            # Solo WAV
            elif 'wav' in formats and 'mp3' not in formats:
                self.pairs[song_name] = {
                    'mp3': None,
                    'wav': formats['wav'],
                    'status': 'wav_only',
                    'quality': 'hq'  # Alta calidad pero sin comprimido
                }
                self.orphans.append({
                    'song': song_name,
                    'has': 'wav',
                    'missing': 'mp3',
                    'path': formats['wav']['file_path']
                })
            
            # Otros formatos (FLAC, M4A, etc.)
            else:
                for fmt, file in formats.items():
                    self.pairs[song_name] = {
                        fmt: file,
                        'status': f'{fmt}_only',
                        'quality': 'other'
                    }
        
        print(f"   ✅ Canciones con pares completos: {sum(1 for p in self.pairs.values() if p['status'] == 'complete')}")
        print(f"   ⚠️  Canciones con solo MP3: {sum(1 for p in self.pairs.values() if p['status'] == 'mp3_only')}")
        print(f"   ⚠️  Canciones con solo WAV: {sum(1 for p in self.pairs.values() if p['status'] == 'wav_only')}")
        
        return self.pairs
    
    def generate_unified_index(self, output_path):
        """
        Genera índice unificado con toda la información.
        Formato optimizado para VPA.
        """
        print(f"\n💾 Generando índice unificado...")
        
        unified = []
        
        for song_name, pair in self.pairs.items():
            # Extraer metadatos del primer archivo disponible
            primary = pair.get('mp3') or pair.get('wav')
            if not primary:
                continue
            
            # Construir entrada del índice
            entry = {
                "song_name": song_name,
                "title": song_name.replace('_', ' ').title(),
                "artist": "BlackMamba",  # Por defecto
                "status": pair['status'],
                "quality": pair['quality'],
                "formats": {},
                "locations": set(),
                "size_total_mb": 0,
                "modified_date": primary['modified_date']
            }
            
            # Agregar información de cada formato
            for fmt in ['mp3', 'wav', 'flac', 'm4a']:
                if fmt in pair and pair[fmt]:
                    file_info = pair[fmt]
                    entry['formats'][fmt] = {
                        "path": file_info['file_path'],
                        "size_mb": file_info['size_mb'],
                        "hash": file_info['hash']
                    }
                    entry['locations'].add(file_info['location'])
                    entry['size_total_mb'] += file_info['size_mb']
            
            # Convertir set a list para JSON
            entry['locations'] = list(entry['locations'])
            entry['size_total_mb'] = round(entry['size_total_mb'], 2)
            
            unified.append(entry)
        
        # Ordenar por nombre
        unified.sort(key=lambda x: x['song_name'])
        
        # Guardar
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Índice guardado: {output}")
        print(f"   📊 Total de canciones: {len(unified)}")
        
        return unified
    
    def generate_orphans_report(self, output_path):
        """Genera reporte de archivos huérfanos (sin par)."""
        print(f"\n📋 Generando reporte de archivos huérfanos...")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_orphans": len(self.orphans),
            "orphans": self.orphans
        }
        
        output = Path(output_path)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Reporte guardado: {output}")
        print(f"   ⚠️  Total de huérfanos: {len(self.orphans)}")
        
        return report
    
    def generate_stats(self):
        """Genera estadísticas generales de la biblioteca."""
        stats = {
            "total_files": len(self.library),
            "total_songs": len(self.pairs),
            "complete_pairs": sum(1 for p in self.pairs.values() if p['status'] == 'complete'),
            "orphans": len(self.orphans),
            "by_format": defaultdict(int),
            "by_location": defaultdict(int),
            "total_size_gb": 0
        }
        
        for file in self.library:
            stats['by_format'][file['format']] += 1
            stats['by_location'][file['location']] += 1
            stats['total_size_gb'] += file['size_mb'] / 1024
        
        stats['by_format'] = dict(stats['by_format'])
        stats['by_location'] = dict(stats['by_location'])
        stats['total_size_gb'] = round(stats['total_size_gb'], 2)
        
        return stats
    
    def print_summary(self):
        """Imprime resumen visual de la biblioteca."""
        stats = self.generate_stats()
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE BIBLIOTECA MUSICAL BLACKMAMBA")
        print("=" * 60)
        print(f"\n🎵 Archivos totales: {stats['total_files']}")
        print(f"🎼 Canciones únicas: {stats['total_songs']}")
        print(f"✅ Pares completos (MP3+WAV): {stats['complete_pairs']}")
        print(f"⚠️  Archivos huérfanos: {stats['orphans']}")
        print(f"💾 Tamaño total: {stats['total_size_gb']} GB")
        
        print(f"\n📁 Por formato:")
        for fmt, count in stats['by_format'].items():
            print(f"   {fmt.upper()}: {count}")
        
        print(f"\n📍 Por ubicación:")
        for loc, count in stats['by_location'].items():
            print(f"   {loc}: {count}")
        
        print("\n" + "=" * 60)


def main():
    """Ejecuta escaneo completo."""
    print("🎵 Music Library Scanner v1.0")
    print("Iyari Cancino Gomez - BlackMamba RECORDS")
    print()
    
    # Crear escáner
    scanner = MusicLibraryScanner()
    
    # Escanear todo
    scanner.scan_all_locations()
    
    # Detectar pares
    scanner.detect_pairs()
    
    # Generar índice unificado
    base_dir = Path(__file__).parent
    index_path = base_dir / "music_library.json"
    scanner.generate_unified_index(index_path)
    
    # Generar reporte de huérfanos
    orphans_path = base_dir / "music_orphans_report.json"
    scanner.generate_orphans_report(orphans_path)
    
    # Mostrar resumen
    scanner.print_summary()
    
    print("\n✨ Escaneo completado exitosamente")
    print(f"📄 Índice principal: {index_path}")
    print(f"📋 Reporte huérfanos: {orphans_path}")


if __name__ == "__main__":
    main()
