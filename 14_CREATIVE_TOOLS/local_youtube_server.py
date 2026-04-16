#!/usr/bin/env python3
"""
🦅 BlackMamba LocalTube Server
Servidor para reproducir videos locales sin lag
Arquitecto: Iyari Cancino Gomez
Fecha: 30 de Diciembre, 2025
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, send_file, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración
USB_BASE = Path("/Volumes/ADATA SC740")
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.mov', '.avi', '.webm', '.m4v'}
CACHE_FILE = Path(__file__).parent / "video_library_cache.json"

# Cache de videos
video_library = []
last_scan = None

def get_video_icon(filename):
    """Retorna emoji según tipo de video"""
    name_lower = filename.lower()
    
    if any(x in name_lower for x in ['mandalorian', 'series', 'episode', 'temporada']):
        return '📺'
    elif any(x in name_lower for x in ['movie', 'pelicula', 'film']):
        return '🎬'
    elif any(x in name_lower for x in ['music', 'musica', 'song']):
        return '🎵'
    elif any(x in name_lower for x in ['tutorial', 'curso', 'clase']):
        return '📚'
    else:
        return '🎥'

def format_size(bytes):
    """Formatea tamaño en bytes a legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

def scan_videos(max_videos=500):
    """Escanea el USB buscando videos"""
    global video_library, last_scan
    
    print("🔍 Escaneando USB en busca de videos...")
    videos = []
    
    try:
        # Buscar en directorios principales
        search_dirs = [
            USB_BASE / "04_SERIES",
            USB_BASE / "02_MEDIA",
            USB_BASE / "untitled folder",
            USB_BASE / "00_ORGANIZED_MASTER"
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            print(f"  📁 Escaneando: {search_dir.name}")
            
            for root, dirs, files in os.walk(search_dir):
                # Saltar carpetas ocultas
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if Path(file).suffix.lower() in VIDEO_EXTENSIONS:
                        file_path = Path(root) / file
                        
                        try:
                            stat = file_path.stat()
                            
                            video_info = {
                                'title': file,
                                'path': str(file_path),
                                'relative_path': str(file_path.relative_to(USB_BASE)),
                                'size': format_size(stat.st_size),
                                'size_bytes': stat.st_size,
                                'format': file_path.suffix[1:].upper(),
                                'folder': file_path.parent.name,
                                'icon': get_video_icon(file),
                                'date': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            }
                            
                            videos.append(video_info)
                            
                            # Limitar para velocidad
                            if len(videos) >= max_videos:
                                print(f"  ⚠️  Límite alcanzado: {max_videos} videos")
                                break
                                
                        except Exception as e:
                            print(f"  ❌ Error con {file}: {e}")
                            continue
                
                if len(videos) >= max_videos:
                    break
        
        # Ordenar por fecha (más recientes primero)
        videos.sort(key=lambda x: x['date'], reverse=True)
        
        video_library = videos
        last_scan = datetime.now().isoformat()
        
        # Guardar cache
        cache_data = {
            'last_scan': last_scan,
            'total_videos': len(videos),
            'videos': videos
        }
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Escaneo completo: {len(videos)} videos encontrados")
        return videos
        
    except Exception as e:
        print(f"❌ Error en escaneo: {e}")
        return []

def load_cache():
    """Carga cache si existe"""
    global video_library, last_scan
    
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                video_library = data['videos']
                last_scan = data['last_scan']
                print(f"📋 Cache cargado: {len(video_library)} videos")
                return True
        except:
            pass
    return False

# === RUTAS API ===

@app.route('/')
def index():
    """Sirve la interfaz HTML"""
    html_file = Path(__file__).parent / "local_youtube.html"
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/videos')
def get_videos():
    """Retorna lista de videos"""
    if not video_library:
        if not load_cache():
            scan_videos()
    
    return jsonify({
        'total': len(video_library),
        'last_scan': last_scan,
        'videos': video_library
    })

@app.route('/api/scan')
def scan():
    """Fuerza un nuevo escaneo"""
    videos = scan_videos(max_videos=1000)
    return jsonify({
        'status': 'success',
        'total': len(videos),
        'message': f'Encontrados {len(videos)} videos'
    })

@app.route('/api/video/<path:video_path>')
def serve_video(video_path):
    """Sirve un video específico"""
    try:
        full_path = USB_BASE / video_path
        if full_path.exists():
            return send_file(
                full_path,
                mimetype='video/mp4',
                as_attachment=False
            )
        else:
            return jsonify({'error': 'Video no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def stats():
    """Estadísticas de la biblioteca"""
    if not video_library:
        load_cache()
    
    total_size = sum(v['size_bytes'] for v in video_library)
    
    formats = {}
    for v in video_library:
        fmt = v['format']
        formats[fmt] = formats.get(fmt, 0) + 1
    
    return jsonify({
        'total_videos': len(video_library),
        'total_size': format_size(total_size),
        'total_size_bytes': total_size,
        'formats': formats,
        'last_scan': last_scan
    })

if __name__ == '__main__':
    print("🦅 BlackMamba LocalTube Server")
    print("=" * 50)
    print(f"📁 USB Base: {USB_BASE}")
    print(f"🎬 Extensiones: {', '.join(VIDEO_EXTENSIONS)}")
    print("=" * 50)
    
    # Cargar cache o escanear
    if not load_cache():
        print("⚡ Primera ejecución: escaneando USB...")
        scan_videos(max_videos=500)
    
    print("\n✅ Servidor listo!")
    print("🌐 Abre: http://localhost:8888")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8888, debug=False)
