"""
Vocal Performance Analyzer (VPA)
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez

Sistema de Análisis Vocal en Tiempo Real:
- Detección de canción actual (Shazam API)
- Obtención de letras sincronizadas
- Análisis de afinación y timing del canto
- Métricas de performance vocal
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import subprocess

class VocalPerformanceAnalyzer:
    def __init__(self):
        self.philosophy = "Interpretación Consciente sobre Perfección Mecánica"
        self.status = "Iniciando"
        self.base_dir = Path(__file__).parent
        
        # Índice unificado generado por scan_music_library.py
        self.music_library = self.base_dir / "music_library.json"
        self.orphans_report = self.base_dir / "music_orphans_report.json"
        
        # Cache y logs
        self.lyrics_cache = self.base_dir / "lyrics_cache"
        self.performance_logs = self.base_dir / "performance_logs"
        
        # Crear directorios necesarios
        self.lyrics_cache.mkdir(exist_ok=True)
        self.performance_logs.mkdir(exist_ok=True)
        
        # Cargar biblioteca
        self.library_data = self._load_library()
        
        # Estado actual
        self.current_song = None
        self.current_lyrics = None
        self.performance_metrics = {
            "pitch_accuracy": [],
            "timing_accuracy": [],
            "breath_control": [],
            "emotional_intensity": []
        }
    
    def detect_song_shazam(self):
        """
        Detecta la canción actual usando Shazam Desktop.
        Método 1: Lee el archivo de estado de Shazam (si está disponible)
        Método 2: Usa ShazamKit API (macOS)
        Método 3: Captura de audio y análisis con ShazamIO
        """
        # Intento 1: Leer desde Shazam Desktop
        shazam_log = Path.home() / "Library/Application Support/Shazam/recent.json"
        if shazam_log.exists():
            try:
                with open(shazam_log) as f:
                    data = json.load(f)
                    if data and len(data) > 0:
                        latest = data[0]
                        return {
                            "title": latest.get("title", "Unknown"),
                            "artist": latest.get("subtitle", "Unknown"),
                            "shazam_id": latest.get("key", ""),
                            "detected_at": datetime.now().isoformat()
                        }
            except Exception as e:
                print(f"Error leyendo Shazam log: {e}")
        
        # Intento 2: Usar osascript para interactuar con Shazam (macOS)
        try:
            result = subprocess.run(
                ["osascript", "-e", 'tell application "Shazam" to get name of current track'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return {
                    "title": result.stdout.strip(),
                    "artist": "Unknown",
                    "detected_at": datetime.now().isoformat()
                }
        except:
            pass
        
        print("⚠️ No se pudo detectar canción con Shazam Desktop")
        return None
    
    def _load_library(self):
        """Carga el índice unificado de música."""
        if not self.music_library.exists():
            print("⚠️ Biblioteca no encontrada. Ejecuta scan_music_library.py primero")
            return []
        
        try:
            with open(self.music_library, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando biblioteca: {e}")
            return []
    
    def get_song_from_library(self, title, artist="BlackMamba"):
        """
        Busca canción en la biblioteca unificada con fuzzy matching.
        Retorna información completa incluyendo formatos disponibles.
        """
        if not self.library_data:
            return None
        
        # Normalizar búsqueda
        title_norm = title.lower().replace(' ', '_')
        artist_norm = artist.lower()
        
        # Búsqueda exacta por song_name
        for song in self.library_data:
            if song['song_name'] == title_norm:
                return self._format_song_result(song)
        
        # Búsqueda fuzzy por título
        for song in self.library_data:
            song_title = song['title'].lower()
            if title.lower() in song_title or title_norm in song['song_name']:
                return self._format_song_result(song)
        
        # Búsqueda por palabras clave
        search_words = set(title.lower().split())
        for song in self.library_data:
            song_words = set(song['song_name'].split('_'))
            if len(search_words & song_words) >= 2:  # Al menos 2 palabras coinciden
                return self._format_song_result(song)
        
        print(f"⚠️ No se encontró '{title}' en la biblioteca")
        return None
    
    def _format_song_result(self, song):
        """Formatea resultado de búsqueda con metadatos completos."""
        # Determinar archivo preferido (MP3 primero, luego WAV)
        preferred_path = None
        if 'mp3' in song['formats']:
            preferred_path = song['formats']['mp3']['path']
        elif 'wav' in song['formats']:
            preferred_path = song['formats']['wav']['path']
        
        return {
            "song_name": song['song_name'],
            "title": song['title'],
            "artist": song['artist'],
            "status": song['status'],
            "quality": song['quality'],
            "file_path": preferred_path,
            "formats": song['formats'],
            "locations": song['locations'],
            "size_mb": song['size_total_mb'],
            "has_mp3": 'mp3' in song['formats'],
            "has_wav": 'wav' in song['formats'],
            "is_complete": song['status'] == 'complete'
        }
    
    def fetch_lyrics(self, title, artist):
        """
        Obtiene letra de la canción desde múltiples fuentes:
        1. Cache local
        2. Genius API
        3. Musixmatch API
        4. LyricsOVH API (gratuito)
        """
        cache_file = self.lyrics_cache / f"{title}_{artist}.json".replace(" ", "_")
        
        # Intento 1: Cache local
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        # Intento 2: LyricsOVH (API gratuita)
        try:
            url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                lyrics = {
                    "title": title,
                    "artist": artist,
                    "lyrics": data.get("lyrics", ""),
                    "synced": False,  # LyricsOVH no provee sincronización
                    "source": "lyrics.ovh",
                    "fetched_at": datetime.now().isoformat()
                }
                
                # Guardar en cache
                with open(cache_file, "w") as f:
                    json.dump(lyrics, f, indent=2, ensure_ascii=False)
                
                return lyrics
        except Exception as e:
            print(f"Error obteniendo lyrics de LyricsOVH: {e}")
        
        # Si falla, intentar con otras APIs (requieren API keys)
        print("⚠️ No se pudieron obtener las letras automáticamente")
        return None
    
    def analyze_vocal_pitch(self, audio_chunk, reference_pitch):
        """
        Analiza la afinación del canto vs referencia.
        Integración con el Afinador Suno existente.
        
        Retorna:
        - pitch_deviation: desviación en cents (-100 a +100)
        - is_on_pitch: bool (dentro de ±25 cents)
        - confidence: 0-1
        """
        # TODO: Integrar con torchcrepe del afinador_suno
        # Por ahora retornar mock data
        return {
            "pitch_deviation": 0,  # cents
            "is_on_pitch": True,
            "confidence": 0.85,
            "timestamp": time.time()
        }
    
    def analyze_timing_sync(self, vocal_onset, lyric_timestamp):
        """
        Analiza la sincronización del canto con la letra.
        
        Retorna:
        - timing_offset: diferencia en ms
        - sync_quality: "early" | "on_time" | "late"
        - score: 0-100
        """
        offset_ms = (vocal_onset - lyric_timestamp) * 1000
        
        # Tolerancia: ±200ms = perfecto, ±500ms = aceptable
        if abs(offset_ms) <= 200:
            quality = "on_time"
            score = 100
        elif abs(offset_ms) <= 500:
            quality = "early" if offset_ms < 0 else "late"
            score = 70
        else:
            quality = "early" if offset_ms < 0 else "late"
            score = 40
        
        return {
            "timing_offset": offset_ms,
            "sync_quality": quality,
            "score": score
        }
    
    def get_performance_report(self):
        """
        Genera reporte de la performance actual.
        """
        if not self.current_song:
            return {"error": "No hay canción activa"}
        
        # Calcular promedios
        avg_pitch = sum(self.performance_metrics["pitch_accuracy"]) / max(len(self.performance_metrics["pitch_accuracy"]), 1)
        avg_timing = sum(self.performance_metrics["timing_accuracy"]) / max(len(self.performance_metrics["timing_accuracy"]), 1)
        
        return {
            "song": self.current_song,
            "performance": {
                "pitch_score": avg_pitch,
                "timing_score": avg_timing,
                "overall_score": (avg_pitch + avg_timing) / 2,
                "samples": len(self.performance_metrics["pitch_accuracy"])
            },
            "metrics": self.performance_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_performance(self, filename=None):
        """
        Guarda la performance en archivo JSON.
        """
        if not filename:
            filename = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.get_performance_report()
        filepath = self.performance_logs / filename
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Performance guardada en: {filepath}")
        return filepath
    
    def get_system_status(self):
        """
        Estado del sistema VPA para integración con dashboard.
        """
        return {
            "philosophy": self.philosophy,
            "status": self.status,
            "current_song": self.current_song,
            "has_lyrics": self.current_lyrics is not None,
            "performance_samples": len(self.performance_metrics["pitch_accuracy"]),
            "timestamp": datetime.now().isoformat()
        }


# Instancia global para integración
vpa = VocalPerformanceAnalyzer()


# === API Flask para Dashboard ===
if __name__ == "__main__":
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route("/detect", methods=["POST"])
    def detect_song():
        """Detecta canción actual con Shazam"""
        song = vpa.detect_song_shazam()
        if song:
            vpa.current_song = song
            # Buscar en biblioteca unificada
            library_song = vpa.get_song_from_library(song["title"], song["artist"])
            if library_song:
                song.update(library_song)
                vpa.current_song = song
            # Obtener letras
            vpa.current_lyrics = vpa.fetch_lyrics(song["title"], song["artist"])
            return jsonify({"success": True, "song": song, "lyrics": vpa.current_lyrics})
        return jsonify({"success": False, "error": "No se detectó canción"})
    
    @app.route("/lyrics", methods=["GET"])
    def get_lyrics():
        """Retorna letras de la canción actual"""
        if vpa.current_lyrics:
            return jsonify(vpa.current_lyrics)
        return jsonify({"error": "No hay letras cargadas"}), 404
    
    @app.route("/performance", methods=["GET"])
    def get_performance():
        """Retorna métricas de performance actual"""
        return jsonify(vpa.get_performance_report())
    
    @app.route("/status", methods=["GET"])
    def get_status():
        """Estado del sistema VPA"""
        return jsonify(vpa.get_system_status())
    
    print("🎤 Vocal Performance Analyzer iniciado en puerto 9000")
    print("📊 Dashboard: http://localhost:9000/status")
    app.run(host="0.0.0.0", port=9000, debug=True)
