"""
BlackMamba Audio Detector
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez

Sistema de detección de audio propio usando fingerprinting acústico.
Reconoce tus canciones de SoundCloud que Shazam no detecta.
"""

import os
import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess
import tempfile

class AudioFingerprinter:
    """
    Genera huellas digitales acústicas de canciones usando chromaprint.
    """
    
    def __init__(self):
        self.fingerprints_db = Path(__file__).parent / "audio_fingerprints.json"
        self.fingerprints = self._load_fingerprints()
    
    def _load_fingerprints(self):
        """Carga base de datos de fingerprints."""
        if self.fingerprints_db.exists():
            with open(self.fingerprints_db, encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_fingerprints(self):
        """Guarda base de datos de fingerprints."""
        with open(self.fingerprints_db, 'w', encoding='utf-8') as f:
            json.dump(self.fingerprints, f, indent=2, ensure_ascii=False)
    
    def check_fpcalc_installed(self):
        """Verifica si chromaprint/fpcalc está instalado."""
        try:
            result = subprocess.run(['fpcalc', '-version'], 
                                  capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def install_chromaprint(self):
        """Instala chromaprint via Homebrew."""
        print("📦 Instalando chromaprint (fingerprinting engine)...")
        try:
            subprocess.run(['brew', 'install', 'chromaprint'], check=True)
            print("✅ Chromaprint instalado")
            return True
        except:
            print("❌ Error instalando chromaprint")
            return False
    
    def generate_fingerprint(self, audio_path):
        """
        Genera fingerprint de un archivo de audio usando chromaprint.
        Retorna: (duration, fingerprint_string)
        """
        try:
            # Ejecutar fpcalc
            result = subprocess.run(
                ['fpcalc', '-raw', '-json', str(audio_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None, None
            
            # Parsear resultado JSON
            data = json.loads(result.stdout)
            duration = data.get('duration', 0)
            fingerprint = data.get('fingerprint', [])
            
            # Convertir fingerprint a string compacto
            fp_str = ','.join(map(str, fingerprint))
            
            return duration, fp_str
            
        except Exception as e:
            print(f"Error generando fingerprint para {audio_path}: {e}")
            return None, None
    
    def generate_quick_signature(self, audio_path):
        """
        Genera firma rápida alternativa si chromaprint no está disponible.
        Usa características básicas del archivo.
        """
        try:
            path = Path(audio_path)
            stats = path.stat()
            
            # Leer primeros 8KB del archivo (header + inicio de audio)
            with open(audio_path, 'rb') as f:
                header = f.read(8192)
                
            # Hash del contenido inicial
            content_hash = hashlib.md5(header).hexdigest()
            
            signature = {
                'size': stats.st_size,
                'content_hash': content_hash,
                'filename': path.name,
                'type': 'quick_signature'
            }
            
            return signature
            
        except Exception as e:
            print(f"Error generando firma rápida: {e}")
            return None
    
    def index_song(self, audio_path, song_info):
        """
        Indexa una canción con su fingerprint.
        """
        print(f"🔍 Indexando: {song_info['title']}")
        
        # Generar fingerprint con chromaprint
        duration, fingerprint = self.generate_fingerprint(audio_path)
        
        if fingerprint:
            # Usar fingerprint completo
            song_data = {
                'title': song_info['title'],
                'artist': song_info.get('artist', 'BlackMamba'),
                'file_path': str(audio_path),
                'duration': duration,
                'fingerprint': fingerprint,
                'type': 'chromaprint',
                'indexed_at': datetime.now().isoformat()
            }
        else:
            # Fallback a firma rápida
            signature = self.generate_quick_signature(audio_path)
            if not signature:
                return False
            
            song_data = {
                'title': song_info['title'],
                'artist': song_info.get('artist', 'BlackMamba'),
                'file_path': str(audio_path),
                'signature': signature,
                'type': 'quick_signature',
                'indexed_at': datetime.now().isoformat()
            }
        
        # Usar song_name como key
        key = song_info.get('song_name', song_info['title'].lower().replace(' ', '_'))
        self.fingerprints[key] = song_data
        
        return True
    
    def index_library(self, music_library_path):
        """
        Indexa toda la biblioteca musical con fingerprints.
        """
        print("🎵 Iniciando indexación de biblioteca con fingerprints...")
        print("━" * 60)
        
        # Verificar chromaprint
        if not self.check_fpcalc_installed():
            print("⚠️  Chromaprint no encontrado")
            install = input("¿Instalar chromaprint? (S/n): ").strip().lower()
            if install != 'n':
                if not self.install_chromaprint():
                    print("⚠️  Continuando con firmas rápidas (menos precisas)")
        
        # Cargar biblioteca
        with open(music_library_path, encoding='utf-8') as f:
            library = json.load(f)
        
        print(f"📚 Biblioteca: {len(library)} canciones")
        print()
        
        # Indexar cada canción
        indexed = 0
        skipped = 0
        
        for song in library:
            # Usar MP3 si existe, sino WAV
            audio_path = None
            if 'mp3' in song['formats']:
                audio_path = song['formats']['mp3']['path']
            elif 'wav' in song['formats']:
                audio_path = song['formats']['wav']['path']
            
            if not audio_path or not Path(audio_path).exists():
                skipped += 1
                continue
            
            song_info = {
                'song_name': song['song_name'],
                'title': song['title'],
                'artist': song['artist']
            }
            
            if self.index_song(audio_path, song_info):
                indexed += 1
                if indexed % 10 == 0:
                    print(f"   Progreso: {indexed}/{len(library)}")
        
        # Guardar base de datos
        self._save_fingerprints()
        
        print()
        print("━" * 60)
        print(f"✅ Indexación completa")
        print(f"   Indexadas: {indexed}")
        print(f"   Omitidas: {skipped}")
        print(f"   Base de datos: {self.fingerprints_db}")
        
        return indexed
    
    def compare_fingerprints(self, fp1, fp2, threshold=0.85):
        """
        Compara dos fingerprints y retorna similitud (0-1).
        Implementación simple: cuenta coincidencias de segmentos.
        """
        try:
            # Convertir strings a listas
            arr1 = [int(x) for x in fp1.split(',')]
            arr2 = [int(x) for x in fp2.split(',')]
            
            # Comparar segmentos (sliding window)
            max_similarity = 0
            window_size = min(len(arr1), len(arr2), 100)
            
            for offset in range(-20, 21):  # Probar diferentes offsets
                matches = 0
                comparisons = 0
                
                for i in range(window_size):
                    idx1 = i
                    idx2 = i + offset
                    
                    if 0 <= idx2 < len(arr2):
                        comparisons += 1
                        if arr1[idx1] == arr2[idx2]:
                            matches += 1
                
                if comparisons > 0:
                    similarity = matches / comparisons
                    max_similarity = max(max_similarity, similarity)
            
            return max_similarity
            
        except Exception as e:
            print(f"Error comparando fingerprints: {e}")
            return 0.0
    
    def detect_from_recording(self, recording_path):
        """
        Detecta qué canción es a partir de una grabación.
        """
        print("🔍 Analizando grabación...")
        
        # Generar fingerprint de la grabación
        duration, rec_fingerprint = self.generate_fingerprint(recording_path)
        
        if not rec_fingerprint:
            print("⚠️  No se pudo generar fingerprint de la grabación")
            return None
        
        # Comparar con todas las canciones indexadas
        best_match = None
        best_score = 0
        
        print(f"🔎 Comparando contra {len(self.fingerprints)} canciones...")
        
        for key, song_data in self.fingerprints.items():
            if song_data.get('type') != 'chromaprint':
                continue
            
            song_fp = song_data['fingerprint']
            similarity = self.compare_fingerprints(rec_fingerprint, song_fp)
            
            if similarity > best_score:
                best_score = similarity
                best_match = song_data
        
        if best_match and best_score > 0.6:  # 60% de similitud mínima
            print(f"✅ Detectado: {best_match['title']}")
            print(f"   Confianza: {best_score*100:.1f}%")
            return {
                'title': best_match['title'],
                'artist': best_match['artist'],
                'file_path': best_match['file_path'],
                'confidence': best_score,
                'detected_at': datetime.now().isoformat()
            }
        else:
            print(f"❌ No se encontró coincidencia (mejor: {best_score*100:.1f}%)")
            return None


class AudioRecorder:
    """
    Graba audio del sistema para detección.
    """
    
    def __init__(self):
        self.recordings_dir = Path(__file__).parent / "audio_recordings"
        self.recordings_dir.mkdir(exist_ok=True)
    
    def record_system_audio_macos(self, duration=10):
        """
        Graba audio del sistema en macOS usando ffmpeg + BlackHole/ScreenCapture.
        """
        output_file = self.recordings_dir / f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        print(f"🎙️  Grabando {duration} segundos de audio del sistema...")
        print("   (Reproduce tu canción ahora)")
        
        try:
            # Usar rec (sox) para grabar desde el micrófono default
            # Nota: Para capturar audio del sistema necesitas BlackHole o similar
            subprocess.run([
                'rec',
                '-c', '1',          # Mono
                '-r', '44100',      # 44.1kHz
                str(output_file),
                'trim', '0', str(duration)
            ], check=True, capture_output=True)
            
            print(f"✅ Grabación guardada: {output_file}")
            return str(output_file)
            
        except FileNotFoundError:
            print("⚠️  'rec' (sox) no encontrado. Instalando...")
            subprocess.run(['brew', 'install', 'sox'], check=True)
            return self.record_system_audio_macos(duration)
            
        except Exception as e:
            print(f"❌ Error grabando: {e}")
            return None


def main():
    """Script principal de detección."""
    import argparse
    
    parser = argparse.ArgumentParser(description='BlackMamba Audio Detector')
    parser.add_argument('--index', action='store_true', 
                       help='Indexar biblioteca con fingerprints')
    parser.add_argument('--detect', type=int, metavar='SECONDS',
                       help='Grabar N segundos y detectar canción')
    parser.add_argument('--library', type=str, 
                       default='music_library.json',
                       help='Ruta al archivo de biblioteca')
    
    args = parser.parse_args()
    
    fingerprinter = AudioFingerprinter()
    
    if args.index:
        # Indexar biblioteca
        library_path = Path(__file__).parent / args.library
        if not library_path.exists():
            print(f"❌ No se encontró {args.library}")
            print("   Ejecuta scan_music_library.py primero")
            return
        
        fingerprinter.index_library(library_path)
    
    elif args.detect:
        # Grabar y detectar
        recorder = AudioRecorder()
        recording = recorder.record_system_audio_macos(args.detect)
        
        if recording:
            result = fingerprinter.detect_from_recording(recording)
            if result:
                print("\n🎵 Canción detectada:")
                print(f"   Título: {result['title']}")
                print(f"   Artista: {result['artist']}")
                print(f"   Confianza: {result['confidence']*100:.1f}%")
            else:
                print("\n❌ No se pudo identificar la canción")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
