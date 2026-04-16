#!/usr/bin/env python3
"""
🎬 BlackMamba Cinema
Netflix personal para pobres con inteligencia
Tu biblioteca de películas organizada y accesible como Netflix
Arquitecto: Iyari Cancino Gomez
Fecha: 1 de Enero, 2026
"""

import os
import json
import mimetypes
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, send_file, jsonify, request
from flask_cors import CORS
import hashlib

# === CONFIGURACIÓN ===
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent
MOVIES_DIR = Path.home() / "Movies"
CATALOG_FILE = BASE_DIR / "cinema_catalog.json"
POSTERS_DIR = BASE_DIR / "cinema_posters"

# Crear directorio de pósters
POSTERS_DIR.mkdir(exist_ok=True)

# Extensiones de video soportadas
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

# Base de datos de géneros por palabras clave
GENRE_KEYWORDS = {
    'action': ['action', 'fight', 'combat', 'war', 'batalla'],
    'comedy': ['comedy', 'funny', 'comedia', 'risa'],
    'drama': ['drama'],
    'horror': ['horror', 'terror', 'scary', 'miedo'],
    'sci-fi': ['sci-fi', 'space', 'alien', 'future', 'futuro'],
    'romance': ['love', 'romance', 'amor'],
    'thriller': ['thriller', 'suspense'],
    'animation': ['animation', 'animated', 'animación'],
    'documentary': ['documentary', 'documental']
}

class CinemaLibrary:
    """Biblioteca de películas estilo Netflix"""
    
    def __init__(self):
        self.catalog = self.load_catalog()
    
    def load_catalog(self):
        """Carga el catálogo existente"""
        if CATALOG_FILE.exists():
            with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'movies': [], 'last_scan': None}
    
    def save_catalog(self):
        """Guarda el catálogo"""
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)
    
    def get_file_hash(self, filepath):
        """Genera ID único para la película"""
        return hashlib.md5(str(filepath).encode()).hexdigest()[:16]
    
    def detect_genre(self, filename):
        """Detecta género por nombre de archivo"""
        filename_lower = filename.lower()
        detected = []
        
        for genre, keywords in GENRE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    detected.append(genre)
                    break
        
        return detected if detected else ['general']
    
    def extract_metadata(self, filepath):
        """Extrae metadata de una película"""
        stat = filepath.stat()
        size_mb = stat.st_size / (1024 * 1024)
        
        # Limpiar nombre
        title = filepath.stem
        title = title.replace('_', ' ').replace('.', ' ')
        
        # Detectar año en el nombre (formato: YYYY)
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        year = int(year_match.group()) if year_match else None
        
        # Detectar género
        genres = self.detect_genre(title)
        
        return {
            'id': self.get_file_hash(filepath),
            'title': title.strip(),
            'filename': filepath.name,
            'path': str(filepath),
            'size_mb': round(size_mb, 2),
            'duration_min': None,  # Se puede extraer con ffprobe si está instalado
            'year': year,
            'genres': genres,
            'added_date': datetime.now().isoformat(),
            'last_watched': None,
            'watch_count': 0,
            'rating': None
        }
    
    def scan_library(self):
        """Escanea el directorio de películas"""
        print(f"🎬 Escaneando: {MOVIES_DIR}")
        
        if not MOVIES_DIR.exists():
            print(f"❌ Directorio no encontrado: {MOVIES_DIR}")
            return
        
        # IDs existentes
        existing_ids = {m['id'] for m in self.catalog['movies']}
        
        # Buscar películas
        found = 0
        new = 0
        
        for filepath in MOVIES_DIR.rglob('*'):
            if filepath.is_file() and filepath.suffix.lower() in VIDEO_EXTENSIONS:
                found += 1
                file_id = self.get_file_hash(filepath)
                
                # Si es nueva, agregar
                if file_id not in existing_ids:
                    metadata = self.extract_metadata(filepath)
                    self.catalog['movies'].append(metadata)
                    new += 1
                    print(f"  ✅ Nueva: {metadata['title']}")
                else:
                    print(f"  ♻️  Ya existe: {filepath.name}")
        
        self.catalog['last_scan'] = datetime.now().isoformat()
        self.save_catalog()
        
        print(f"\n📊 Resumen:")
        print(f"  Total encontradas: {found}")
        print(f"  Nuevas agregadas: {new}")
        print(f"  Total en catálogo: {len(self.catalog['movies'])}")
    
    def get_all_movies(self):
        """Obtiene todas las películas"""
        return sorted(self.catalog['movies'], key=lambda x: x.get('title', ''))
    
    def get_movies_by_genre(self, genre):
        """Filtra películas por género"""
        return [m for m in self.catalog['movies'] if genre in m.get('genres', [])]
    
    def get_recent_movies(self, limit=10):
        """Obtiene películas recientes"""
        movies = sorted(
            self.catalog['movies'],
            key=lambda x: x.get('added_date', ''),
            reverse=True
        )
        return movies[:limit]
    
    def search_movies(self, query):
        """Busca películas por título"""
        query_lower = query.lower()
        return [
            m for m in self.catalog['movies']
            if query_lower in m.get('title', '').lower()
        ]
    
    def mark_watched(self, movie_id):
        """Marca película como vista"""
        for movie in self.catalog['movies']:
            if movie['id'] == movie_id:
                movie['last_watched'] = datetime.now().isoformat()
                movie['watch_count'] = movie.get('watch_count', 0) + 1
                self.save_catalog()
                return True
        return False
    
    def rate_movie(self, movie_id, rating):
        """Califica una película (1-5)"""
        for movie in self.catalog['movies']:
            if movie['id'] == movie_id:
                movie['rating'] = max(1, min(5, int(rating)))
                self.save_catalog()
                return True
        return False

# Instancia global
library = CinemaLibrary()

# === RUTAS WEB ===

@app.route('/')
def index():
    """Página principal del cinema"""
    return send_file('blackmamba_cinema.html')

@app.route('/api/movies')
def api_movies():
    """API: Obtener todas las películas"""
    genre = request.args.get('genre')
    search = request.args.get('search')
    
    if search:
        movies = library.search_movies(search)
    elif genre and genre != 'all':
        movies = library.get_movies_by_genre(genre)
    else:
        movies = library.get_all_movies()
    
    return jsonify({
        'movies': movies,
        'total': len(movies),
        'last_scan': library.catalog.get('last_scan')
    })

@app.route('/api/recent')
def api_recent():
    """API: Películas recientes"""
    limit = int(request.args.get('limit', 10))
    return jsonify({'movies': library.get_recent_movies(limit)})

@app.route('/api/genres')
def api_genres():
    """API: Obtener todos los géneros"""
    all_genres = set()
    for movie in library.catalog['movies']:
        all_genres.update(movie.get('genres', []))
    
    return jsonify({'genres': sorted(all_genres)})

@app.route('/api/movie/<movie_id>')
def api_movie_detail(movie_id):
    """API: Detalle de película"""
    for movie in library.catalog['movies']:
        if movie['id'] == movie_id:
            return jsonify(movie)
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/api/movie/<movie_id>/watch', methods=['POST'])
def api_mark_watched(movie_id):
    """API: Marcar como vista"""
    if library.mark_watched(movie_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/api/movie/<movie_id>/rate', methods=['POST'])
def api_rate_movie(movie_id):
    """API: Calificar película"""
    data = request.get_json()
    rating = data.get('rating')
    
    if library.rate_movie(movie_id, rating):
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid rating'}), 400

@app.route('/api/stream/<movie_id>')
def api_stream(movie_id):
    """API: Streaming de video"""
    for movie in library.catalog['movies']:
        if movie['id'] == movie_id:
            filepath = Path(movie['path'])
            if filepath.exists():
                # Marcar como vista
                library.mark_watched(movie_id)
                
                # Streaming con soporte para range requests
                return send_file(
                    filepath,
                    mimetype='video/mp4',
                    as_attachment=False,
                    download_name=movie['filename']
                )
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API: Re-escanear biblioteca"""
    library.scan_library()
    return jsonify({'success': True, 'total': len(library.catalog['movies'])})

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--scan':
        # Modo escaneo
        library.scan_library()
    else:
        # Modo servidor
        print("🎬 BlackMamba Cinema - Netflix para Pobres con Inteligencia")
        print("=" * 60)
        print(f"📁 Directorio: {MOVIES_DIR}")
        print(f"🎥 Películas en catálogo: {len(library.catalog['movies'])}")
        print(f"🌐 Servidor: http://localhost:5001")
        print("=" * 60)
        print("\n🚀 Iniciando servidor...")
        print("   Presiona Ctrl+C para detener\n")
        
        app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    main()
