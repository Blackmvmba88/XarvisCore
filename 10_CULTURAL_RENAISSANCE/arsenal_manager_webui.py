#!/usr/bin/env python3
"""
🦅 BLACKMAMBA MUSIC ARSENAL MANAGER - WebUI
Arquitecto: Iyari Cancino Gomez
Puerto: 8888

Administración completa del arsenal musical:
- Visualización de biblioteca
- Edición de metadatos (ID3, MP3, WAV, FLAC)
- Inyección masiva de metadata
- Búsqueda y filtros avanzados
- Gestión de duplicados
- Estadísticas en vivo
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json
import os
from datetime import datetime
import hashlib

# Librerías de metadatos
try:
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.wave import WAVE
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, COMM
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("⚠️  Mutagen no instalado. Ejecutar: pip install mutagen")

app = Flask(__name__)
CORS(app)

# Configuración
BASE_DIR = Path(__file__).parent
MUSIC_VAULT = Path.home() / "Desktop" / "BlackMamba_Music_Vault"
LIBRARY_JSON = BASE_DIR / "music_library.json"

class MusicArsenalManager:
    def __init__(self):
        self.vault = MUSIC_VAULT
        self.library = self.load_library()
    
    def load_library(self):
        """Cargar biblioteca desde JSON"""
        if LIBRARY_JSON.exists():
            with open(LIBRARY_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_library(self):
        """Guardar biblioteca a JSON"""
        with open(LIBRARY_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.library, f, indent=2, ensure_ascii=False)
    
    def scan_vault(self):
        """Escanear vault completo"""
        songs = []
        
        for ext_dir in ['WAV_Masters', 'MP3_Distribution', 'FLAC_Archive']:
            folder = self.vault / ext_dir
            if not folder.exists():
                continue
            
            for file_path in folder.rglob('*'):
                if file_path.suffix.lower() in ['.mp3', '.wav', '.flac']:
                    metadata = self.read_metadata(file_path)
                    songs.append({
                        'path': str(file_path),
                        'filename': file_path.name,
                        'format': file_path.suffix[1:].upper(),
                        'size_mb': round(file_path.stat().st_size / (1024*1024), 2),
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        'metadata': metadata
                    })
        
        return songs
    
    def read_metadata(self, file_path):
        """Leer metadatos de un archivo"""
        if not MUTAGEN_AVAILABLE:
            return {'title': '', 'artist': '', 'album': '', 'year': '', 'genre': ''}
        
        try:
            ext = file_path.suffix.lower()
            
            if ext == '.mp3':
                audio = MP3(file_path)
                return {
                    'title': str(audio.get('TIT2', [''])[0]),
                    'artist': str(audio.get('TPE1', [''])[0]),
                    'album': str(audio.get('TALB', [''])[0]),
                    'year': str(audio.get('TDRC', [''])[0]),
                    'genre': str(audio.get('TCON', [''])[0])
                }
            elif ext == '.flac':
                audio = FLAC(file_path)
                return {
                    'title': audio.get('title', [''])[0],
                    'artist': audio.get('artist', [''])[0],
                    'album': audio.get('album', [''])[0],
                    'year': audio.get('date', [''])[0],
                    'genre': audio.get('genre', [''])[0]
                }
            elif ext == '.wav':
                # WAV usa ID3 tags si están disponibles
                try:
                    audio = ID3(file_path)
                    return {
                        'title': str(audio.get('TIT2', [''])[0]),
                        'artist': str(audio.get('TPE1', [''])[0]),
                        'album': str(audio.get('TALB', [''])[0]),
                        'year': str(audio.get('TDRC', [''])[0]),
                        'genre': str(audio.get('TCON', [''])[0])
                    }
                except:
                    return {'title': '', 'artist': '', 'album': '', 'year': '', 'genre': ''}
        except Exception as e:
            print(f"Error leyendo metadata de {file_path.name}: {e}")
            return {'title': '', 'artist': '', 'album': '', 'year': '', 'genre': ''}
    
    def write_metadata(self, file_path, metadata):
        """Escribir metadatos a un archivo"""
        if not MUTAGEN_AVAILABLE:
            return False, "Mutagen no disponible"
        
        try:
            file_path = Path(file_path)
            ext = file_path.suffix.lower()
            
            if ext == '.mp3':
                audio = MP3(file_path)
                audio['TIT2'] = TIT2(encoding=3, text=metadata.get('title', ''))
                audio['TPE1'] = TPE1(encoding=3, text=metadata.get('artist', ''))
                audio['TALB'] = TALB(encoding=3, text=metadata.get('album', ''))
                audio['TDRC'] = TDRC(encoding=3, text=metadata.get('year', ''))
                audio['TCON'] = TCON(encoding=3, text=metadata.get('genre', ''))
                audio.save()
                
            elif ext == '.flac':
                audio = FLAC(file_path)
                audio['title'] = metadata.get('title', '')
                audio['artist'] = metadata.get('artist', '')
                audio['album'] = metadata.get('album', '')
                audio['date'] = metadata.get('year', '')
                audio['genre'] = metadata.get('genre', '')
                audio.save()
                
            elif ext == '.wav':
                try:
                    audio = ID3(file_path)
                except:
                    audio = ID3()
                
                audio['TIT2'] = TIT2(encoding=3, text=metadata.get('title', ''))
                audio['TPE1'] = TPE1(encoding=3, text=metadata.get('artist', ''))
                audio['TALB'] = TALB(encoding=3, text=metadata.get('album', ''))
                audio['TDRC'] = TDRC(encoding=3, text=metadata.get('year', ''))
                audio['TCON'] = TCON(encoding=3, text=metadata.get('genre', ''))
                audio.save(file_path)
            
            return True, "Metadatos guardados"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def batch_update_metadata(self, files, metadata):
        """Actualizar metadatos en múltiples archivos"""
        results = []
        
        for file_path in files:
            success, msg = self.write_metadata(file_path, metadata)
            results.append({
                'file': Path(file_path).name,
                'success': success,
                'message': msg
            })
        
        return results
    
    def get_statistics(self):
        """Obtener estadísticas del arsenal"""
        songs = self.scan_vault()
        
        stats = {
            'total_songs': len(songs),
            'by_format': {},
            'total_size_gb': 0,
            'missing_metadata': 0,
            'complete_metadata': 0
        }
        
        for song in songs:
            # Por formato
            fmt = song['format']
            stats['by_format'][fmt] = stats['by_format'].get(fmt, 0) + 1
            
            # Tamaño total
            stats['total_size_gb'] += song['size_mb']
            
            # Metadatos
            meta = song['metadata']
            if not meta.get('title') or not meta.get('artist'):
                stats['missing_metadata'] += 1
            else:
                stats['complete_metadata'] += 1
        
        stats['total_size_gb'] = round(stats['total_size_gb'] / 1024, 2)
        
        return stats

# Instancia global
manager = MusicArsenalManager()

# ============================================
# RUTAS DE LA API
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Escanear vault completo"""
    songs = manager.scan_vault()
    return jsonify({'success': True, 'songs': songs, 'count': len(songs)})

@app.route('/api/metadata/<path:file_path>', methods=['GET'])
def api_get_metadata(file_path):
    """Obtener metadatos de un archivo"""
    metadata = manager.read_metadata(Path(file_path))
    return jsonify({'success': True, 'metadata': metadata})

@app.route('/api/metadata/<path:file_path>', methods=['POST'])
def api_update_metadata(file_path):
    """Actualizar metadatos de un archivo"""
    metadata = request.json
    success, msg = manager.write_metadata(file_path, metadata)
    return jsonify({'success': success, 'message': msg})

@app.route('/api/batch_update', methods=['POST'])
def api_batch_update():
    """Actualizar metadatos en lote"""
    data = request.json
    files = data.get('files', [])
    metadata = data.get('metadata', {})
    
    results = manager.batch_update_metadata(files, metadata)
    
    return jsonify({
        'success': True,
        'results': results,
        'total': len(results),
        'succeeded': sum(1 for r in results if r['success'])
    })

@app.route('/api/statistics', methods=['GET'])
def api_statistics():
    """Obtener estadísticas"""
    stats = manager.get_statistics()
    return jsonify({'success': True, 'statistics': stats})

@app.route('/api/audio/<path:file_path>', methods=['GET'])
def api_serve_audio(file_path):
    """Servir archivo de audio para reproducción"""
    from flask import send_file
    try:
        return send_file(file_path, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

# ============================================
# TEMPLATE HTML
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦅 BlackMamba Arsenal Manager</title>
    <style>
        /* TEMA MATRIX (Default) */
        :root {
            --primary: #00ff41;
            --secondary: #ff0080;
            --accent: #00ffff;
            --bg: #0a0a0a;
            --glass: rgba(20, 20, 20, 0.85);
            --border: rgba(0, 255, 65, 0.3);
            --text: #e0e0e0;
            --gradient: linear-gradient(135deg, #00ff41, #00ffff);
        }
        
        /* TEMA CYBERPUNK ROSA */
        [data-theme="cyberpunk"] {
            --primary: #ff0080;
            --secondary: #00ffff;
            --accent: #ff00ff;
            --bg: #0a0014;
            --glass: rgba(20, 0, 30, 0.85);
            --border: rgba(255, 0, 128, 0.4);
            --gradient: linear-gradient(135deg, #ff0080, #ff00ff);
        }
        
        /* TEMA OCÉANO */
        [data-theme="ocean"] {
            --primary: #00d4ff;
            --secondary: #0080ff;
            --accent: #00ffff;
            --bg: #001a2e;
            --glass: rgba(0, 26, 46, 0.85);
            --border: rgba(0, 212, 255, 0.4);
            --gradient: linear-gradient(135deg, #00d4ff, #0080ff);
        }
        
        /* TEMA FUEGO */
        [data-theme="fire"] {
            --primary: #ff4500;
            --secondary: #ffaa00;
            --accent: #ff0000;
            --bg: #1a0500;
            --glass: rgba(26, 5, 0, 0.85);
            --border: rgba(255, 69, 0, 0.4);
            --gradient: linear-gradient(135deg, #ff4500, #ffaa00);
        }
        
        /* TEMA PÚRPURA REAL */
        [data-theme="royal"] {
            --primary: #9d00ff;
            --secondary: #ff00ff;
            --accent: #d400ff;
            --bg: #0f0020;
            --glass: rgba(15, 0, 32, 0.85);
            --border: rgba(157, 0, 255, 0.4);
            --gradient: linear-gradient(135deg, #9d00ff, #ff00ff);
        }
        
        /* TEMA NEÓN RAINBOW */
        [data-theme="rainbow"] {
            --primary: #ff00ff;
            --secondary: #00ffff;
            --accent: #ffff00;
            --bg: #000000;
            --glass: rgba(10, 10, 30, 0.85);
            --border: rgba(255, 255, 255, 0.3);
            --gradient: linear-gradient(135deg, #ff0080, #00ff80, #0080ff, #ff00ff);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Courier New', monospace;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            background-image: 
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 255, 65, 0.03) 2px, rgba(0, 255, 65, 0.03) 4px);
            position: relative;
            overflow-x: hidden;
            transition: all 0.5s ease;
        }
        20px);
            border-bottom: 2px solid var(--border);
            padding: 20px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 5px 30px rgba(0, 0, 0, 0.5);
        }
        
        .header h1 {
            color: var(--primary);
            text-shadow: 0 0 20px var(--primary), 0 0 40px var(--primary);
            font-size: 2.5rem;
            margin-bottom: 10px;
            animation: glow 3s ease-in-out infinite;
        }
        
        .header .subtitle {
            color: var(--text);
            opacity: 0.7;
        }
        
        /* Selector de tema */
        .theme-selector {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            gap: 10px;
            background: var(--glass);
            backdrop-filter: blur(20px);
            padding: 15px;
            border-radius: 15px;
            border: 1px solid var(--border);
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
        }
        
        .theme-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }
        
        .theme-btn:hover {
            transform: scale(1.2);
            box-shadow: 0 0 20px currentColor;
        }
        
        .theme-btn.active {
            border-color: white;
            box-shadow: 0 0 30px currentColor;
        }
        
        .theme-matrix { background: linear-gradient(135deg, #00ff41, #00ffff); }
        .theme-cyberpunk { background: linear-gradient(135deg, #ff0080, #ff00ff); }
        .theme-ocean { background: linear-gradient(135deg, #00d4ff, #0080ff); }
        .theme-fire { background: linear-gradient(135deg, #ff4500, #ffaa00); }
        .theme-royal { background: linear-gradient(135deg, #9d00ff, #ff00ff); }
        .theme-rainbow { background: linear-gradient(135deg, #ff0080, #00ff80, #0080ff, #ff00ff);     top: 0;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: var(--primary);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
            z-index: -1;
        }
        
        .btn:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .btn:hover {
            color: var(--bg);
            box-shadow: 0 0 30px var(--primary), 0 0 60px var(--primary);
            transform: translateY(-3px) scale(1.05
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: var(--text);
            opacity: 0.7;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px;
        }
        
        .toolbar {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .btn {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.2), rgba(0, 255, 65, 0.1));
            border: 1px solid var(--primary);
            color: var(--primary);
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            text-transform: uppercase;
            font-size: 0.9rem;
        }
        
        .btn:hover {
            background: var(--primary);
            color: var(--bg);
            box-shadow: 0 0 20px var(--primary);
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        
        .search-box {
            flex: 1;
            min-width: 300px;
        }
        
        .search-box input {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 12px;
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-card .value {
            font-size: 2.5rem;
            color: var(--primary);
            text-shadow: 0 0 10px var(--primary);
            font-weight: bold;
        }
        
        .stat-card .label {
            color: var(--text);
            opacity: 0.7;
            margin-top: 10px;4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .song-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
            opacity: 0;
            transition: all 0.6s;
        }
        
        .song-card:hover::before {
            left: 100%;
            opacity: 0.3;
        }
        
        .song-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 30px var(--primary), inset 0 0 30px rgba(0, 255, 65, 0.1);
            transform: translateX(10px) scale(1.02);
        }
        
        .song-card.selected {
            border-color: var(--secondary);
            box-shadow: 0 0 30px var(--secondary), 0 0 60px var(--secondary);
            background: linear-gradient(135deg, var(--glass), rgba(255, 0, 128, 0.1)
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 20px;
            align-items: center;
            transition: all 0.3s;
        }
        
        .song-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
            transform: translateX(5px);
        }
        
        .song-card.selected {
            border-color: var(--secondary);
            box-shadow: 0 0 20px rgba(255, 0, 128, 0.3);
        }
        
        .song-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        /* Reproductor de audio */
        .audio-player {
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }
        
        .play-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--gradient);
            border: 2px solid var(--primary);
            color: var(--bg);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            transition: all 0.3s;
            box-shadow: 0 0 20px var(--primary);
        }
        
        .play-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 40px var(--primary);
        }
        
        .play-btn:active {
            transform: scale(0.95);
        }
        
        /* Waveform estilo SoundCloud */
        .waveform-container {
            width: 150px;
            height: 60px;
            position: relative;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            overflow: hidden;
            cursor: pointer;
            border: 1px solid var(--border);
        }
        
        .waveform-container canvas {
            width: 100%;
            height: 100%;
        }
        
        .waveform-progress {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            background: linear-gradient(90deg, var(--primary), transparent);
            opacity: 0.3;
            pointer-events: none;
            transition: width 0.1s linear;
            width: 0%;
        }
        
        .time-display {
            font-size: 0.7rem;
            color: var(--primary);
            text-align: center;
            font-family: 'Courier New', monospace;
        }
        
        .song-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .info-group label {
            display: block;
            color: var(--primary);
            font-size: 0.8rem;
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        
        .info-group input {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px;
            border-radius: 5px;
        }
        
        .info-group input:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .song-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn-small {
            padding: 8px 15px;
            font-size: 0.8rem;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border: 2px solid var(--primary);
            border-radius: 15px;
            padding: 40px;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 0 50px rgba(0, 255, 65, 0.3);
        }
        
        .modal-header {
            color: var(--primary);
            font-size: 1.8rem;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            color: var(--primary);
            margin-bottom: 8px;
            text-transform: uppercase;
            font-size: 0.9rem;
        }
        
        .form-group input {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 12px;
            border-radius: 8px;
            font-size: 1rem;
        }
        
        @keyframes glow {
            0%, 100% { 
                text-shadow: 0 0 20px var(--primary), 0 0 40px var(--primary);
            }
            50% { 
                text-shadow: 0 0 30px var(--primary), 0 0 60px var(--primary), 0 0 90px var(--primary);
            }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
     !-- Canvas para partículas -->
    <canvas id="particlesCanvas"></canvas>
    
    <!-- Línea de escaneo -->
    <div class="scan-line"></div>
    
    <!-- Selector de tema -->
    <div class="theme-selector">
        <div class="theme-btn theme-matrix active" onclick="setTheme('matrix')" title="Matrix"></div>
        <div class="theme-btn theme-cyberpunk" onclick="setTheme('cyberpunk')" title="Cyberpunk"></div>
        <div class="theme-btn theme-ocean" onclick="setTheme('ocean')" title="Océano"></div>
        <div class="theme-btn theme-fire" onclick="setTheme('fire')" title="Fuego"></div>
        <div class="theme-btn theme-royal" onclick="setTheme('royal')" title="Royal"></div>
        <div class="theme-btn theme-rainbow" onclick="setTheme('rainbow')" title="Rainbow"></div>
    </div>
    
    <div class="header">
        <h1>🦅 BLACKMAMBA ARSENAL MANAGER</h1>
        <div class="subtitle">Sistema de Administración Total de Metadatos • Built on the road that Bill Gates paved
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .song-card {
            animation: slideIn 0.5s ease-out;
        }
        
        /* Efecto de escaneo */
        @keyframes scan {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100vh); }
        }
        
        .scan-line {
            position: fixed;
            width: 100%;
            height: 2px;
            background: var(--gradient);
            box-shadow: 0 0 20px var(--primary);
            z-index: 9999;
            animation: scan 3s linear infinite;
            opacity: 0.5;
        }
        
        /* Efecto Matrix rain (opcional) */
        .matrix-rain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            opacity: 0.1;
        }
        
        .modal-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: var(--primary);
            font-size: 1.2rem;
        }
        
        .loading.active {
            display: block;
        }
        
        .format-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
        // ============================================
        // SISTEMA DE TEMAS
        // ============================================
        
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('arsenalTheme', theme);
            
            // Actualizar botones activos
            document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`.theme-${theme}`).classList.add('active');
            
            // Reiniciar partículas con nuevos colores
            initParticles();
        }
        
        // Cargar tema guardado
        window.addEventListener('load', () => {
            const savedTheme = localStorage.getItem('arsenalTheme') || 'matrix';
            if (savedTheme !== 'matrix') {
                setTheme(savedTheme);
            }
        });
        
        // ============================================
        // SISTEMA DE PARTÍCULAS
        // ============================================
        
        const canvas = document.getElementById('particlesCanvas');
        const ctx = canvas.getContext('2d');
        let particles = [];
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
        
        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.size = Math.random() * 2 + 1;
            }
            
            update() {
                this.x += this.vx;
                this.y += this.vy;
                
                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            }
            
            draw() {
                const style = getComputedStyle(document.documentElement);
                const primary = style.getPropertyValue('--primary').trim();
                
                ctx.fillStyle = primary;
                ctx.shadowBlur = 10;
                ctx.shadowColor = primary;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        function initParticles() {
            particles = [];
            for (let i = 0; i < 50; i++) {
                particles.push(new Particle());
            }
        }
        
        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                particle.update();
                particle.draw();
            });
            
            // Conectar partículas cercanas
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < 150) {
                        const style = getComputedStyle(document.documentElement);
                        const primary = style.getPropertyValue('--primary').trim();
                        
                        ctx.strokeStyle = primary;
                        ctx.lineWidth = 0.5;
                        ctx.globalAlpha = 1 - (distance / 150);
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                        ctx.globalAlpha = 1;
                    }
                }
            }
            
            requestAnimationFrame(animateParticles);
        }
        
        // Iniciar sistema de partículas
        initParticles();
        animateParticles();
        
        // ============================================
        // FUNCIONES PRINCIPALES
        // ============================================
        
            font-weight: bold;
        }
        
        .format-mp3 { background: rgba(0, 255, 65, 0.2); color: var(--primary); }
        .format-wav { background: rgba(255, 0, 128, 0.2); color: var(--secondary); }
        .format-flac { background: rgba(0, 128, 255, 0.2); color: #0080ff; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦅 BLACKMAMBA ARSENAL MANAGER</h1>
        <div class="subtitle">Sistema de Administración Total de Metadatos</div>
    </div>
    
    <div class="container">
        <div class="toolbar">
            <button class="btn" onclick="scanLibrary()">🔍 ESCANEAR</button>
            <button class="btn" onclick="openBatchModal()" id="btnBatch" disabled>📝 EDITAR LOTE</button>
            <button class="btn" onclick="selectAll()">☑️ SELECCIONAR TODO</button>
            <button class="btn" onclick="deselectAll()">☐ DESELECCIONAR</button>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔎 Buscar por título, artista, álbum..." onkeyup="filterSongs()">
            </div>
        </div>
        
        <div class="stats-grid" id="statsGrid" style="display:none;">
            <div class="stat-card">
                <div class="value" id="statTotal">0</div>
                <div class="label">Total Canciones</div>
            </div>
            <div class="stat-card">
                <div class="value" id="statMP3">0</div>
                <div class="label">MP3</div>
            </div>
            <div class="stat-card">
                <div class="value" id="statWAV">0</div>
                <div class="label">WAV</div>
            </div>
            <div class="stat-card">
                <div class="value" id="statFLAC">0</div>
                <div class="label">FLAC</div>
            </div>
            <div class="stat-card">
                <div class="value" id="statSize">0 GB</div>
                <div class="label">Tamaño Total</div>
            </div>
            <div class="stat-card">
                <div class="value" id="statComplete">0</div>
                <div class="label">Metadata Completa</div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="pulse">⚡ CARGANDO ARSENAL...</div>
        </div>
        
        <div class="songs-grid" id="songsGrid"></div>
    </div>
    
    <!-- Modal de edición en lote -->
    <div class="modal" id="batchModal">
        <div class="modal-content">
            <div class="modal-header">📝 EDICIÓN EN LOTE</div>
            <div class="form-group">
                <label>Artista</label>
                <input type="text" id="batchArtist" placeholder="BlackMamba">
            </div>
            <div class="form-group">
                <label>Álbum</label>
                <input type="text" id="batchAlbum" placeholder="BlackMamba RECORDS">
            </div>
            <div class="form-group">
                <label>Año</label>
                <input type="text" id="batchYear" placeholder="2025">
            </div>
            <div class="form-group">
                <label>Género</label>
                <input type="text" id="batchGenre" placeholder="Trap/Reggae/Electronic">
            </div>
            <div class="modal-actions">
                <button class="btn" onclick="applyBatch()">💾 APLICAR</button>
                <button class="btn" onclick="closeBatchModal()">❌ CANCELAR</button>
            </div>
        </div>
    </div>
    
    <script>
        let allSongs = [];
        let selectedSongs = [];
        
        async function scanLibrary() {
            document.getElementById('loading').classList.add('active');
            document.getElementById('songsGrid').innerHTML = '';
            
            try {
                const response = await fetch('/api/scan', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    allSongs = data.songs;
                    renderSongs(allSongs);
                    await loadStatistics();
                }
            } catch (error) {
                alert('Error al escanear: ' + error);
            } finally {
                document.getElementById('loading').classList.remove('active');
            }
        }
        
        function renderSongs(songs) {
            const grid = document.getElementById('songsGrid');
            grid.innerHTML = '';
            
            if (songs.length === 0) {
                grid.innerHTML = '<div style="text-align:center; padding:40px; color:var(--primary);">No se encontraron canciones. Ejecuta ESCANEAR.</div>';
                return;
            }
            
            songs.forEach((song, index) => {
                const card = document.createElement('div');
                card.className = 'song-card';
                card.dataset.path = song.path;
                card.dataset.index = index;
                
                card.innerHTML = `
                    <input type="checkbox" class="song-checkbox" onchange="toggleSong('${song.path}')">
                    
                    <!-- Reproductor de audio -->
                    <div class="audio-player">
                        <button class="play-btn" onclick="togglePlay(${index})" id="playBtn${index}">▶</button>
                        <div class="time-display" id="time${index}">0:00</div>
                    </div>
                    
                    <!-- Waveform visual -->
                    <div class="waveform-container" onclick="seekAudio(${index}, event)">
                        <canvas id="waveCanvas${index}" width="150" height="60"></canvas>
                        <div class="waveform-progress" id="progress${index}"></div>
                    </div>
                    
                    <audio id="audio${index}" src="/api/audio/${encodeURIComponent(song.path)}" preload="metadata"></audio>
                    
                    <div class="song-info">
                        <div class="info-group">
                            <label>Archivo</label>
                            <input type="text" value="${song.filename}" readonly>
                        </div>
                        <div class="info-group">
                            <label>Formato</label>
                            <span class="format-badge format-${song.format.toLowerCase()}">${song.format}</span>
                            <span style="margin-left:10px; opacity:0.7;">${song.size_mb} MB</span>
                        </div>
                        <div class="info-group">
                            <label>Título</label>
                            <input type="text" value="${song.metadata.title || ''}" 
                                   onchange="updateField('${song.path}', 'title', this.value)">
                        </div>
                        <div class="info-group">
                            <label>Artista</label>
                            <input type="text" value="${song.metadata.artist || ''}"
                                   onchange="updateField('${song.path}', 'artist', this.value)">
                        </div>
                        <div class="info-group">
                            <label>Álbum</label>
                            <input type="text" value="${song.metadata.album || ''}"
                                   onchange="updateField('${song.path}', 'album', this.value)">
                        </div>
                        <div class="info-group">
                            <label>Año</label>
                            <input type="text" value="${song.metadata.year || ''}"
                                   onchange="updateField('${song.path}', 'year', this.value)">
                        </div>
                    </div>
                    <div class="song-actions">
                        <button class="btn btn-small" onclick="saveSong('${song.path}')">💾</button>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }
        
        async function updateField(path, field, value) {
            const song = allSongs.find(s => s.path === path);
            if (song) {
                song.metadata[field] = value;
            }
        }
        
        async function saveSong(path) {
            const song = allSongs.find(s => s.path === path);
            if (!song) return;
            
            try {
                const response = await fetch(`/api/metadata/${encodeURIComponent(path)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(song.metadata)
                });
                
                const data = await response.json();
                alert(data.success ? '✅ Guardado' : '❌ ' + data.message);
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        function toggleSong(path) {
            const card = document.querySelector(`[data-path="${path}"]`);
            const checkbox = card.querySelector('.song-checkbox');
            
            if (checkbox.checked) {
                selectedSongs.push(path);
                card.classList.add('selected');
            } else {
                selectedSongs = selectedSongs.filter(p => p !== path);
                card.classList.remove('selected');
            }
            
            document.getElementById('btnBatch').disabled = selectedSongs.length === 0;
        }
        
        function selectAll() {
            document.querySelectorAll('.song-checkbox').forEach(cb => {
                cb.checked = true;
                toggleSong(cb.closest('.song-card').dataset.path);
            });
        }
        
        function deselectAll() {
            document.querySelectorAll('.song-checkbox').forEach(cb => {
                cb.checked = false;
            });
            selectedSongs = [];
            document.querySelectorAll('.song-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.getElementById('btnBatch').disabled = true;
        }
        
        function openBatchModal() {
            document.getElementById('batchModal').classList.add('active');
        }
        
        function closeBatchModal() {
            document.getElementById('batchModal').classList.remove('active');
        }
        
        async function applyBatch() {
            const metadata = {
                artist: document.getElementById('batchArtist').value,
                album: document.getElementById('batchAlbum').value,
                year: document.getElementById('batchYear').value,
                genre: document.getElementById('batchGenre').value
            };
            
            // Filtrar campos vacíos
            Object.keys(metadata).forEach(key => {
                if (!metadata[key]) delete metadata[key];
            });
            
            if (Object.keys(metadata).length === 0) {
                alert('⚠️ Ingresa al menos un campo');
                return;
            }
            
            try {
                const response = await fetch('/api/batch_update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        files: selectedSongs,
                        metadata: metadata
                    })
                });
                
                const data = await response.json();
                alert(`✅ ${data.succeeded}/${data.total} archivos actualizados`);
                
                closeBatchModal();
                scanLibrary();
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const data = await response.json();
                
                if (data.success) {
                    const stats = data.statistics;
                    document.getElementById('statTotal').textContent = stats.total_songs;
                    document.getElementById('statMP3').textContent = stats.by_format.MP3 || 0;
                    document.getElementById('statWAV').textContent = stats.by_format.WAV || 0;
                    document.getElementById('statFLAC').textContent = stats.by_format.FLAC || 0;
                    document.getElementById('statSize').textContent = stats.total_size_gb + ' GB';
                    document.getElementById('statComplete').textContent = stats.complete_metadata;
                    
                    document.getElementById('statsGrid').style.display = 'grid';
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        function filterSongs() {
            const query = document.getElementById('searchInput').value.toLowerCase();
           ============================================
        // REPRODUCTOR DE AUDIO Y WAVEFORM
        // ============================================
        
        let currentlyPlaying = null;
        const audioContexts = new Map();
        
        async function generateWaveform(audioElement, canvasId) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            
            // Limpiar canvas
            ctx.clearRect(0, 0, width, height);
            
            // Generar waveform procedural (sin necesidad de analizar el audio completo)
            const bars = 50;
            const barWidth = width / bars;
            
            // Crear patrón pseudo-aleatorio basado en el nombre del archivo
            const seed = canvasId.split('Canvas')[1];
            
            for (let i = 0; i < bars; i++) {
                // Altura pseudo-aleatoria pero consistente
                const randomHeight = (Math.sin(i * 0.5 + parseInt(seed)) * 0.5 + 0.5) * 0.8 + 0.2;
                const barHeight = height * randomHeight;
                const x = i * barWidth;
                const y = (height - barHeight) / 2;
                
                // Gradient
                const style = getComputedStyle(document.documentElement);
                const primary = style.getPropertyValue('--primary').trim();
                
                const gradient = ctx.createLinearGradient(0, 0, 0, height);
                gradient.addColorStop(0, primary);
                gradient.addColorStop(1, 'transparent');
                
                ctx.fillStyle = gradient;
                ctx.fillRect(x, y, barWidth - 1, barHeight);
            }
        }
        
        function togglePlay(index) {
            const audio = document.getElementById(`audio${index}`);
            const btn = document.getElementById(`playBtn${index}`);
            
            // Pausar cualquier otra canción
            if (currentlyPlaying !== null && currentlyPlaying !== index) {
                const prevAudio = document.getElementById(`audio${currentlyPlaying}`);
                const prevBtn = document.getElementById(`playBtn${currentlyPlaying}`);
                prevAudio.pause();
                prevBtn.textContent = '▶';
            }
            
            if (audio.paused) {
                audio.play();
                btn.textContent = '⏸';
                currentlyPlaying = index;
                updateProgress(index);
            } else {
                audio.pause();
                btn.textContent = '▶';
                currentlyPlaying = null;
            }
        }
        
        function updateProgress(index) {
            const audio = document.getElementById(`audio${index}`);
            const progress = document.getElementById(`progress${index}`);
            const timeDisplay = document.getElementById(`time${index}`);
            
            function update() {
                if (!audio.paused) {
                    const percent = (audio.currentTime / audio.duration) * 100;
                    progress.style.width = percent + '%';
                    
                    const currentMin = Math.floor(audio.currentTime / 60);
                    const currentSec = Math.floor(audio.currentTime % 60);
                    timeDisplay.textContent = `${currentMin}:${currentSec.toString().padStart(2, '0')}`;
                    
                    requestAnimationFrame(update);
                }
            }
            
            update();
            
            audio.addEventListener('ended', () => {
                document.getElementById(`playBtn${index}`).textContent = '▶';
                progress.style.width = '0%';
                timeDisplay.textContent = '0:00';
                currentlyPlaying = null;
            });
        }
        
        function seekAudio(index, event) {
            const audio = document.getElementById(`audio${index}`);
            const container = event.currentTarget;
            const rect = container.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const percent = x / rect.width;
            
            audio.currentTime = audio.duration * percent;
        }
        
        // Generar waveforms al cargar canciones
        function initializeAudioPlayers() {
            allSongs.forEach((song, index) => {
                const audio = document.getElementById(`audio${index}`);
                const canvasId = `waveCanvas${index}`;
                
                if (audio) {
                    audio.addEventListener('loadedmetadata', () => {
                        generateWaveform(audio, canvasId);
                    });
                    
                    // Generar inmediatamente
                    generateWaveform(audio, canvasId);
                }
            });
        }
        
        // Auto-escanear al cargar
        window.addEventListener('load', () => {
            scanLibrary().then(() => {
                // Esperar un momento para que se rendericen las canciones
                setTimeout(initializeAudioPlayers, 500);
            }ngs(allSongs);
                return;
            }
            
            const filtered = allSongs.filter(song => {
                return song.filename.toLowerCase().includes(query) ||
                       song.metadata.title.toLowerCase().includes(query) ||
                       song.metadata.artist.toLowerCase().includes(query) ||
                       song.metadata.album.toLowerCase().includes(query);
            });
            
            renderSongs(filtered);
        }
        
        // Auto-escanear al cargar
        window.addEventListener('load', () => {
            scanLibrary();
        });
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    print("🦅 BLACKMAMBA ARSENAL MANAGER")
    print("="*60)
    print(f"📁 Music Vault: {MUSIC_VAULT}")
    print(f"🌐 WebUI: http://localhost:8888")
    print("="*60)
    
    if not MUTAGEN_AVAILABLE:
        print("\n⚠️  IMPORTANTE: Instala mutagen para editar metadatos:")
        print("   pip install mutagen\n")
    
    app.run(host='0.0.0.0', port=8888, debug=True)
