#!/usr/bin/env python3
"""
🎼 BLACKMAMBA MUSIC SERVER
Servidor web para reproducir tu biblioteca musical Suno
¿No crees que tu música merece un servidor profesional?
"""

import os
import json
import mimetypes
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from pathlib import Path
import threading
import webbrowser

class BlackMambaMusicHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Volumes/ADATA SC740", **kwargs)
    
    def do_GET(self):
        """Manejar peticiones GET"""
        if self.path == '/api/library':
            self.serve_music_library()
        elif self.path == '/':
            self.serve_player_interface()
        elif self.path.startswith('/api/stream/'):
            self.serve_audio_stream()
        else:
            super().do_GET()
    
    def serve_player_interface(self):
        """Servir la interfaz del reproductor"""
        try:
            player_path = "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/blackmamba_music_player.html"
            with open(player_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, "Reproductor no encontrado")
    
    def serve_music_library(self):
        """Generar y servir el catálogo de música"""
        try:
            library = self.scan_music_library()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            json_data = json.dumps(library, ensure_ascii=False, indent=2)
            self.wfile.write(json_data.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error generando biblioteca: {str(e)}")
    
    def serve_audio_stream(self):
        """Servir archivos de audio para streaming"""
        try:
            # Extraer ruta del archivo del URL
            file_path = urllib.parse.unquote(self.path.replace('/api/stream/', ''))
            full_path = f"/Volumes/ADATA SC740/{file_path}"
            
            if not os.path.exists(full_path):
                self.send_error(404, "Archivo de audio no encontrado")
                return
            
            # Detectar tipo MIME
            mime_type, _ = mimetypes.guess_type(full_path)
            if not mime_type or not mime_type.startswith('audio/'):
                mime_type = 'audio/mpeg'  # Default para MP3
            
            # Enviar headers para streaming
            file_size = os.path.getsize(full_path)
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            
            # Enviar archivo en chunks para streaming eficiente
            with open(full_path, 'rb') as audio_file:
                while True:
                    chunk = audio_file.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                        
        except Exception as e:
            self.send_error(500, f"Error streaming audio: {str(e)}")
    
    def scan_music_library(self):
        """Escanear la biblioteca musical y generar metadatos"""
        library = {
            "total_tracks": 0,
            "total_size_mb": 0,
            "formats": {"mp3": 0, "wav": 0, "m4a": 0, "midi": 0},
            "categories": {},
            "tracks": []
        }
        
        usb_path = Path("/Volumes/ADATA SC740")
        audio_extensions = {'.mp3', '.wav', '.m4a', '.mid', '.midi'}
        
        print("🔍 Escaneando biblioteca musical...")
        
        for audio_file in usb_path.rglob('*'):
            if audio_file.suffix.lower() in audio_extensions and audio_file.is_file():
                try:
                    # Obtener metadatos básicos
                    file_size = audio_file.stat().st_size
                    format_ext = audio_file.suffix[1:].lower()
                    
                    # Filtrar archivos muy pequeños (probablemente corruptos o metadatos)
                    if file_size < 50000:  # Menos de 50KB
                        continue
                    
                    # Filtrar archivos de sistema de macOS
                    if audio_file.name.startswith('._'):
                        continue
                    
                    # Categorizar por contenido del nombre
                    track_category = self.categorize_track(audio_file.name)
                    
                    # Estimar duración por tamaño (aproximado)
                    estimated_duration = self.estimate_duration(file_size, format_ext)
                    
                    # Filtrar archivos con duración 0
                    if estimated_duration == "0:00":
                        continue
                    
                    track_info = {
                        "title": self.clean_track_title(audio_file.stem),
                        "artist": self.extract_artist(audio_file.name),
                        "duration": estimated_duration,
                        "format": format_ext,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "category": track_category,
                        "path": str(audio_file.relative_to(usb_path)),
                        "stream_url": f"/api/stream/{audio_file.relative_to(usb_path)}"
                    }
                    
                    library["tracks"].append(track_info)
                    library["total_tracks"] += 1
                    library["total_size_mb"] += track_info["size_mb"]
                    library["formats"][format_ext] = library["formats"].get(format_ext, 0) + 1
                    library["categories"][track_category] = library["categories"].get(track_category, 0) + 1
                    
                    # Limitar por rendimiento (primeros 500 para mejor experiencia)
                    if library["total_tracks"] >= 500:
                        break
                        
                except Exception as e:
                    print(f"❌ Error procesando {audio_file}: {e}")
                    continue
        
        library["total_size_mb"] = round(library["total_size_mb"], 2)
        print(f"✅ Escaneado completado: {library['total_tracks']} tracks")
        
        return library
    
    def categorize_track(self, filename):
        """Categorizar track por nombre"""
        name_lower = filename.lower()
        
        if any(word in name_lower for word in ['remix', 'edit', 'extended']):
            return 'remix'
        elif any(word in name_lower for word in ['cover', 'ft', 'feat']):
            return 'collaboration'
        elif any(word in name_lower for word in ['demo', 'rough', 'draft']):
            return 'demo'
        elif any(word in name_lower for word in ['náhuatl', 'maya', 'chīchīltikpa', 'día de muertos']):
            return 'cultural'
        elif any(word in name_lower for word in ['neon', 'galactic', 'electronic', 'experimental']):
            return 'experimental'
        else:
            return 'original'
    
    def extract_artist(self, filename):
        """Extraer artista del nombre del archivo"""
        if 'blackmamba' in filename.lower():
            return 'BlackMamba'
        elif 'ft.' in filename.lower() or 'feat.' in filename.lower():
            return 'BlackMamba (Colaboración)'
        else:
            return 'BlackMamba'
    
    def clean_track_title(self, stem):
        """Limpiar título de la canción"""
        # Remover emojis y caracteres especiales del inicio
        import re
        cleaned = re.sub(r'^[🎵🎶🎤🔄✨💫🌑🌙🎧🎸🌷🌺🎭]+\s*', '', stem)
        cleaned = re.sub(r'^\s*["\'"]*\s*', '', cleaned)
        cleaned = re.sub(r'\s*["\'"]*\s*$', '', cleaned)
        return cleaned if cleaned else stem
    
    def estimate_duration(self, file_size, format_ext):
        """Estimar duración basada en tamaño de archivo"""
        # Filtrar archivos muy pequeños (probablemente corruptos)
        if file_size < 50000:  # Menos de 50KB
            return "0:00"
            
        # Aproximaciones basadas en bitrates típicos
        bitrates = {
            'mp3': 160000,   # 160 kbps (más realista para Suno)
            'wav': 1411200,  # 44.1kHz 16-bit stereo
            'm4a': 128000,   # 128 kbps AAC
            'mid': 8000,     # MIDI pequeño
            'midi': 8000
        }
        
        bitrate = bitrates.get(format_ext, 160000)
        
        # Calcular duración en segundos
        if format_ext in ['mid', 'midi']:
            # MIDI: estimar por tamaño relativo
            duration_seconds = max(30, file_size / 1000)  # Mínimo 30 seg
        else:
            duration_seconds = (file_size * 8) / bitrate
        
        # Validar duración razonable (30 seg a 10 min para Suno)
        if duration_seconds < 30:
            duration_seconds = 30 + (file_size % 120)  # Entre 30-150 seg
        elif duration_seconds > 600:  # Más de 10 min
            duration_seconds = 180 + (file_size % 240)  # Entre 3-7 min
        
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        
        return f"{minutes}:{seconds:02d}"

def start_music_server(port=8888):
    """Iniciar el servidor de música"""
    print("🎼 INICIANDO BLACKMAMBA MUSIC SERVER")
    print("=" * 50)
    print(f"🎵 Puerto: {port}")
    print(f"📂 Directorio: /Volumes/ADATA SC740")
    print(f"🌐 URL: http://localhost:{port}")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", port), BlackMambaMusicHandler) as httpd:
            print(f"✅ Servidor iniciado en puerto {port}")
            print("🎧 Accede a http://localhost:8888 para reproducir tu música")
            print("⚠️  Presiona Ctrl+C para detener el servidor")
            
            # Abrir navegador automáticamente
            threading.Timer(2.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 ¡Servidor detenido!")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    # Verificar que el USB está montado
    if not os.path.exists("/Volumes/ADATA SC740"):
        print("❌ USB ADATA SC740 no está montado")
        print("🔌 Conecta tu USB y vuelve a intentar")
        exit(1)
    
    start_music_server()
