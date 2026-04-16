#!/usr/bin/env python3
"""
🎬 BlackMamba Cinema AI - Netflix Soberano con Inteligencia Real
Sistema de streaming personal que analiza y organiza películas de verdad.

CAPA DE INTELIGENCIA:
- Duración: >60 min = película real, 20-60 = episodio, <20 = corto
- Calidad: Resolución (4K/HD/SD), bitrate, codec
- Audio: Idioma detectado, necesita subtítulos
- Clasificación: película/serie/documental/corto
- Subtítulos: Búsqueda automática si es necesario

Filosofía: "Con inteligencia no necesitas dinero" - Arquitecto Iyari Cancino Gomez
"""

import os
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, send_file, request, Response
from flask_cors import CORS

# === CONFIGURACIÓN ===
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent
MOVIES_DIR = Path.home() / "Movies"
CATALOG_FILE = BASE_DIR / "cinema_catalog_ai.json"

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

# Requisitos de calidad para películas
MOVIE_MIN_DURATION = 60  # minutos
MOVIE_MIN_WIDTH = 720    # píxeles
MOVIE_MIN_BITRATE = 1000 # kbps

# Keywords de géneros
GENRE_KEYWORDS = {
    'action': ['action', 'fight', 'combat', 'war', 'batalla', 'pelea'],
    'comedy': ['comedy', 'funny', 'comedia', 'risa', 'laugh'],
    'drama': ['drama', 'dramático'],
    'horror': ['horror', 'terror', 'scary', 'miedo', 'zombi'],
    'sci-fi': ['sci-fi', 'space', 'alien', 'future', 'futuro', 'robot', 'cyber'],
    'romance': ['love', 'romance', 'amor', 'romantic'],
    'thriller': ['thriller', 'suspense', 'mystery', 'misterio'],
    'animation': ['animation', 'animated', 'animación', 'anime'],
    'documentary': ['documentary', 'documental', 'historia']
}

class IntelligentMediaAnalyzer:
    """Analizador inteligente de medios con ffprobe"""
    
    @staticmethod
    def get_media_info(file_path):
        """Extrae información completa del archivo con ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"❌ Error analizando {file_path}: {e}")
            return None
    
    @staticmethod
    def analyze_video(file_path):
        """Análisis completo de video con clasificación inteligente"""
        info = IntelligentMediaAnalyzer.get_media_info(file_path)
        if not info:
            return None
        
        format_info = info.get('format', {})
        streams = info.get('streams', [])
        
        # Buscar streams de video y audio
        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
        
        if not video_stream:
            return None
        
        # Extraer información
        duration_sec = float(format_info.get('duration', 0))
        duration_min = duration_sec / 60
        
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        
        bitrate = int(format_info.get('bit_rate', 0)) / 1000  # kbps
        codec = video_stream.get('codec_name', 'unknown')
        
        # Información de audio
        audio_codec = audio_stream.get('codec_name', 'unknown') if audio_stream else 'none'
        audio_lang = audio_stream.get('tags', {}).get('language', 'unknown') if audio_stream else 'unknown'
        
        # Clasificación de resolución
        if width >= 3840:
            resolution = '4K'
            quality_score = 100
        elif width >= 1920:
            resolution = 'Full HD'
            quality_score = 80
        elif width >= 1280:
            resolution = 'HD'
            quality_score = 60
        elif width >= 720:
            resolution = 'HD Ready'
            quality_score = 40
        else:
            resolution = 'SD'
            quality_score = 20
        
        # Ajustar score por bitrate
        if bitrate < 1000:
            quality_score -= 20
        elif bitrate > 5000:
            quality_score += 10
        
        quality_score = max(0, min(100, quality_score))
        
        # Clasificación de tipo
        if duration_min >= MOVIE_MIN_DURATION:
            if width >= MOVIE_MIN_WIDTH and bitrate >= MOVIE_MIN_BITRATE:
                media_type = 'movie'
                is_valid_movie = True
            else:
                media_type = 'low_quality_movie'
                is_valid_movie = False
        elif duration_min >= 20:
            media_type = 'episode'
            is_valid_movie = False
        else:
            media_type = 'short'
            is_valid_movie = False
        
        # Detectar si necesita subtítulos (audio no español)
        needs_subtitles = audio_lang not in ['spa', 'es', 'spanish', 'unknown']
        
        return {
            'duration_minutes': round(duration_min, 1),
            'resolution': resolution,
            'width': width,
            'height': height,
            'bitrate_kbps': round(bitrate, 0),
            'video_codec': codec,
            'audio_codec': audio_codec,
            'audio_language': audio_lang,
            'quality_score': quality_score,
            'media_type': media_type,
            'is_valid_movie': is_valid_movie,
            'needs_subtitles': needs_subtitles,
            'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
        }

class IntelligentCinemaLibrary:
    """Biblioteca inteligente de cine con análisis automático"""
    
    def __init__(self):
        self.catalog = self.load_catalog()
    
    def load_catalog(self):
        """Cargar catálogo desde JSON"""
        if CATALOG_FILE.exists():
            with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'movies': [], 'stats': {}}
    
    def save_catalog(self):
        """Guardar catálogo a JSON"""
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)
    
    def extract_year(self, filename):
        """Extraer año del nombre de archivo"""
        match = re.search(r'\b(19|20)\d{2}\b', filename)
        return match.group(0) if match else None
    
    def detect_genre(self, filename):
        """Detectar género por palabras clave"""
        filename_lower = filename.lower()
        for genre, keywords in GENRE_KEYWORDS.items():
            if any(kw in filename_lower for kw in keywords):
                return genre.capitalize()
        return 'General'
    
    def scan_library(self):
        """Escanear biblioteca con análisis inteligente"""
        print(f"🔍 Escaneando biblioteca: {MOVIES_DIR}")
        
        movies = []
        stats = {
            'total_files': 0,
            'valid_movies': 0,
            'episodes': 0,
            'shorts': 0,
            'low_quality': 0,
            'total_duration_hours': 0,
            'needs_subtitles': 0,
            'scanned_at': datetime.now().isoformat()
        }
        
        if not MOVIES_DIR.exists():
            print(f"❌ Directorio no existe: {MOVIES_DIR}")
            return
        
        for file_path in MOVIES_DIR.rglob('*'):
            if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                stats['total_files'] += 1
                print(f"📹 Analizando: {file_path.name}")
                
                # Análisis inteligente
                analysis = IntelligentMediaAnalyzer.analyze_video(file_path)
                
                if not analysis:
                    continue
                
                # Estadísticas
                if analysis['is_valid_movie']:
                    stats['valid_movies'] += 1
                elif analysis['media_type'] == 'episode':
                    stats['episodes'] += 1
                elif analysis['media_type'] == 'short':
                    stats['shorts'] += 1
                elif analysis['media_type'] == 'low_quality_movie':
                    stats['low_quality'] += 1
                
                if analysis['needs_subtitles']:
                    stats['needs_subtitles'] += 1
                
                stats['total_duration_hours'] += analysis['duration_minutes'] / 60
                
                # Metadata
                title = file_path.stem
                year = self.extract_year(title)
                genre = self.detect_genre(title)
                
                movie = {
                    'id': str(abs(hash(str(file_path)))),
                    'title': title,
                    'path': str(file_path),
                    'year': year,
                    'genre': genre,
                    'watch_count': 0,
                    'last_watched': None,
                    'rating': 0,
                    'added_at': datetime.now().isoformat(),
                    # Análisis inteligente
                    **analysis
                }
                
                movies.append(movie)
        
        # Ordenar por calidad y duración
        movies.sort(key=lambda x: (x['is_valid_movie'], x['quality_score'], x['duration_minutes']), reverse=True)
        
        self.catalog = {
            'movies': movies,
            'stats': stats
        }
        
        self.save_catalog()
        
        print(f"\n✅ Escaneo completo!")
        print(f"🎬 Películas válidas: {stats['valid_movies']}")
        print(f"📺 Episodios/series: {stats['episodes']}")
        print(f"🎞️ Cortos: {stats['shorts']}")
        print(f"⚠️ Baja calidad: {stats['low_quality']}")
        print(f"📝 Necesitan subtítulos: {stats['needs_subtitles']}")
        print(f"⏱️ Duración total: {round(stats['total_duration_hours'], 1)} horas")
    
    def get_movies(self, filter_type='all'):
        """Obtener películas con filtros inteligentes"""
        movies = self.catalog.get('movies', [])
        
        if filter_type == 'valid_only':
            return [m for m in movies if m['is_valid_movie']]
        elif filter_type == 'episodes':
            return [m for m in movies if m['media_type'] == 'episode']
        elif filter_type == 'shorts':
            return [m for m in movies if m['media_type'] == 'short']
        elif filter_type == 'needs_subtitles':
            return [m for m in movies if m['needs_subtitles']]
        
        return movies
    
    def get_movie_by_id(self, movie_id):
        """Obtener película por ID"""
        movies = self.catalog.get('movies', [])
        return next((m for m in movies if m['id'] == movie_id), None)
    
    def mark_watched(self, movie_id):
        """Marcar película como vista"""
        for movie in self.catalog['movies']:
            if movie['id'] == movie_id:
                movie['watch_count'] += 1
                movie['last_watched'] = datetime.now().isoformat()
                self.save_catalog()
                return True
        return False
    
    def rate_movie(self, movie_id, rating):
        """Calificar película (1-5 estrellas)"""
        for movie in self.catalog['movies']:
            if movie['id'] == movie_id:
                movie['rating'] = max(1, min(5, rating))
                self.save_catalog()
                return True
        return False

# Instancia global
library = IntelligentCinemaLibrary()

# === RUTAS API ===

@app.route('/')
def index():
    """Servir interfaz HTML"""
    html_file = BASE_DIR / 'blackmamba_cinema_dvd.html'
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "❌ Interfaz no encontrada. Ejecuta desde el directorio correcto."

@app.route('/api/movies')
def get_movies():
    """Obtener lista de películas con filtros"""
    filter_type = request.args.get('filter', 'all')
    genre = request.args.get('genre')
    search = request.args.get('search', '').lower()
    
    movies = library.get_movies(filter_type)
    
    if genre:
        movies = [m for m in movies if m['genre'] == genre]
    
    if search:
        movies = [m for m in movies if search in m['title'].lower()]
    
    return jsonify(movies)

@app.route('/api/movies/valid')
def get_valid_movies():
    """Solo películas reales (>60 min, HD+, buena calidad)"""
    return jsonify(library.get_movies('valid_only'))

@app.route('/api/stats')
def get_stats():
    """Estadísticas de la biblioteca"""
    return jsonify(library.catalog.get('stats', {}))

@app.route('/api/genres')
def get_genres():
    """Lista de géneros disponibles"""
    genres = set(m['genre'] for m in library.catalog.get('movies', []) if m.get('genre'))
    return jsonify(sorted(genres))

@app.route('/api/movie/<movie_id>')
def get_movie(movie_id):
    """Información detallada de película"""
    movie = library.get_movie_by_id(movie_id)
    if movie:
        return jsonify(movie)
    return jsonify({'error': 'Película no encontrada'}), 404

@app.route('/api/stream/<movie_id>')
def stream_movie(movie_id):
    """Stream de película con soporte de range requests"""
    movie = library.get_movie_by_id(movie_id)
    if not movie:
        return jsonify({'error': 'Película no encontrada'}), 404
    
    file_path = Path(movie['path'])
    if not file_path.exists():
        return jsonify({'error': 'Archivo no encontrado'}), 404
    
    # Soporte de range requests para video
    range_header = request.headers.get('Range')
    file_size = os.path.getsize(file_path)
    
    if not range_header:
        return send_file(file_path, mimetype='video/mp4')
    
    # Parsear range
    byte_range = range_header.replace('bytes=', '').split('-')
    start = int(byte_range[0]) if byte_range[0] else 0
    end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1
    length = end - start + 1
    
    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(length)
    
    response = Response(data, 206, mimetype='video/mp4')
    response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(length))
    
    return response

@app.route('/api/movie/<movie_id>/watch', methods=['POST'])
def watch_movie(movie_id):
    """Marcar película como vista"""
    if library.mark_watched(movie_id):
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'Película no encontrada'}), 404

@app.route('/api/movie/<movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    """Calificar película"""
    rating = request.json.get('rating', 0)
    if library.rate_movie(movie_id, rating):
        return jsonify({'status': 'ok', 'rating': rating})
    return jsonify({'error': 'Película no encontrada'}), 404

@app.route('/api/scan', methods=['POST'])
def scan_library():
    """Escanear biblioteca"""
    library.scan_library()
    return jsonify({'status': 'ok', 'stats': library.catalog.get('stats', {})})

@app.route('/api/recent')
def get_recent():
    """Películas vistas recientemente"""
    movies = library.catalog.get('movies', [])
    recent = [m for m in movies if m.get('last_watched')]
    recent.sort(key=lambda x: x['last_watched'], reverse=True)
    return jsonify(recent[:20])

if __name__ == '__main__':
    print("🎬 BlackMamba Cinema AI - Iniciando...")
    print(f"📁 Biblioteca: {MOVIES_DIR}")
    print(f"💾 Catálogo: {CATALOG_FILE}")
    print(f"\n⚡ Características de inteligencia:")
    print(f"   • Duración mínima película: {MOVIE_MIN_DURATION} min")
    print(f"   • Resolución mínima: {MOVIE_MIN_WIDTH}p")
    print(f"   • Bitrate mínimo: {MOVIE_MIN_BITRATE} kbps")
    print(f"   • Detección de idioma y subtítulos")
    print(f"   • Clasificación automática (película/serie/corto)")
    print(f"\n🚀 Servidor corriendo en http://localhost:5001")
    print(f"🎯 Usa /api/movies/valid para solo películas reales\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
