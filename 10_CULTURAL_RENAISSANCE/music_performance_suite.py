#!/usr/bin/env python3
"""
🎵 BlackMamba Music Performance Suite
Integración completa: Music Manager + VPA + Audio Detector
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import json
import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# Configurar directorio base
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Importar componentes
try:
    from vpa_with_detector import VPAWithDetector
    VPA_AVAILABLE = True
except ImportError:
    VPA_AVAILABLE = False
    print("⚠️ VPA no disponible")

try:
    from audio_detector import AudioFingerprinter
    DETECTOR_AVAILABLE = True
except ImportError:
    DETECTOR_AVAILABLE = False
    print("⚠️ Audio Detector no disponible")

# Flask app
app = Flask(__name__)
CORS(app)

# Configuración
MUSIC_LIBRARY = os.path.join(SCRIPT_DIR, "music_library.json")
FINGERPRINTS_DB = os.path.join(SCRIPT_DIR, "audio_fingerprints.json")
PORT = 9002

# Estado global
vpa_instance = None
detector_instance = None

def load_music_library():
    """Carga la biblioteca musical"""
    if os.path.exists(MUSIC_LIBRARY):
        with open(MUSIC_LIBRARY, 'r') as f:
            return json.load(f)
    return []

def init_components():
    """Inicializa componentes disponibles"""
    global vpa_instance, detector_instance
    
    if VPA_AVAILABLE:
        try:
            vpa_instance = VPAWithDetector()
            print("✅ VPA + Detector inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando VPA: {e}")
    
    if DETECTOR_AVAILABLE and not vpa_instance:
        try:
            detector_instance = AudioFingerprinter()
            print("✅ Audio Detector standalone inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando Detector: {e}")

# ============================================================
# ENDPOINTS DE DETECCIÓN
# ============================================================

@app.route('/api/detect/dual', methods=['POST'])
def detect_dual():
    """Detecta canción usando Shazam + BlackMamba"""
    if not vpa_instance:
        return jsonify({
            "error": "VPA no disponible",
            "available": False
        }), 503
    
    data = request.json or {}
    duration = data.get('duration', 10)
    
    try:
        result = vpa_instance.detect_song_dual(duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/detect/blackmamba', methods=['POST'])
def detect_blackmamba():
    """Detecta canción usando solo BlackMamba Detector"""
    if not vpa_instance and not detector_instance:
        return jsonify({
            "error": "Detector no disponible",
            "available": False
        }), 503
    
    data = request.json or {}
    duration = data.get('duration', 10)
    
    try:
        if vpa_instance:
            result = vpa_instance.detect_song_blackmamba(duration)
        else:
            # Usar detector standalone
            from audio_detector import AudioRecorder
            recorder = AudioRecorder()
            recording = recorder.record_system_audio_macos(duration)
            
            if not recording:
                return jsonify({
                    "detected": False,
                    "error": "No se pudo grabar audio"
                })
            
            result = detector_instance.detect_from_recording(recording)
            
            if result:
                result = {
                    "detected": True,
                    "song": {
                        "title": result['title'],
                        "artist": result['artist'],
                        "file_path": result['file_path']
                    },
                    "confidence": result['confidence']
                }
            else:
                result = {"detected": False}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/detect/shazam', methods=['POST'])
def detect_shazam():
    """Detecta canción usando solo Shazam"""
    if not vpa_instance:
        return jsonify({
            "error": "VPA no disponible",
            "available": False
        }), 503
    
    try:
        result = vpa_instance.detect_song_shazam()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# ENDPOINTS DE ANÁLISIS VOCAL
# ============================================================

@app.route('/api/analyze/vocal', methods=['POST'])
def analyze_vocal():
    """Analiza performance vocal"""
    if not vpa_instance:
        return jsonify({
            "error": "VPA no disponible",
            "available": False
        }), 503
    
    data = request.json or {}
    audio_path = data.get('audio_path')
    
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Archivo de audio no válido"}), 400
    
    try:
        result = vpa_instance.analyze_vocal_pitch(audio_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lyrics', methods=['GET'])
def get_lyrics():
    """Obtiene letras de una canción"""
    if not vpa_instance:
        return jsonify({
            "error": "VPA no disponible",
            "available": False
        }), 503
    
    title = request.args.get('title', '')
    artist = request.args.get('artist', '')
    
    if not title or not artist:
        return jsonify({"error": "Se requiere título y artista"}), 400
    
    try:
        lyrics = vpa_instance.fetch_lyrics(title, artist)
        return jsonify({
            "title": title,
            "artist": artist,
            "lyrics": lyrics
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# ENDPOINTS DE BIBLIOTECA MUSICAL
# ============================================================

@app.route('/api/library', methods=['GET'])
def get_library():
    """Retorna la biblioteca musical completa"""
    try:
        library = load_music_library()
        return jsonify({
            "total": len(library),
            "songs": library
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/library/search', methods=['GET'])
def search_library():
    """Busca en la biblioteca musical"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "Query vacío"}), 400
    
    try:
        library = load_music_library()
        results = []
        
        for song in library:
            if (query in song.get('title', '').lower() or 
                query in song.get('artist', '').lower()):
                results.append(song)
        
        return jsonify({
            "query": query,
            "total": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# STATUS Y DASHBOARD
# ============================================================

@app.route('/api/status', methods=['GET'])
def status():
    """Estado del sistema"""
    library = load_music_library()
    
    # Contar fingerprints indexados
    indexed_count = 0
    if os.path.exists('audio_fingerprints.json'):
        try:
            with open('audio_fingerprints.json', 'r') as f:
                fingerprints = json.load(f)
                indexed_count = len(fingerprints)
        except:
            indexed_count = 0
    
    return jsonify({
        "status": "operational",
        "components": {
            "vpa": VPA_AVAILABLE and vpa_instance is not None,
            "detector": DETECTOR_AVAILABLE or (vpa_instance is not None),
            "music_library": len(library)
        },
        "features": {
            "dual_detection": vpa_instance is not None,
            "shazam": vpa_instance is not None,
            "blackmamba_detector": vpa_instance is not None or detector_instance is not None,
            "vocal_analysis": vpa_instance is not None,
            "lyrics_fetch": vpa_instance is not None
        },
        "library_stats": {
            "total_songs": len(library),
            "indexed": indexed_count
        }
    })

@app.route('/music_webui.html')
def music_webui():
    """Redirigir a la WebUI de música"""
    if os.path.exists('music_webui.html'):
        with open('music_webui.html', 'r') as f:
            return f.read()
    else:
        return jsonify({
            "error": "WebUI no encontrada",
            "message": "music_webui.html no existe en este directorio"
        }), 404

@app.route('/')
def dashboard():
    """Dashboard principal"""
    library = load_music_library()
    
    html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 BlackMamba Music Performance Suite</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #00ff41;
            --bg: #0a0a0a;
            --glass: rgba(20, 20, 20, 0.8);
            --border: rgba(0, 255, 65, 0.3);
        }
        
        body {
            font-family: 'Inter', 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: var(--primary);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        h1 {
            font-size: 2.5em;
            text-shadow: 0 0 20px var(--primary);
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: rgba(0, 255, 65, 0.7);
            font-size: 1.1em;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 10px 30px rgba(0, 255, 65, 0.2);
        }
        
        .card h2 {
            font-size: 1.5em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: auto;
        }
        
        .status.active {
            background: var(--primary);
            box-shadow: 0 0 10px var(--primary);
        }
        
        .status.inactive {
            background: #666;
        }
        
        .action-btn {
            width: 100%;
            padding: 15px;
            margin-top: 15px;
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--primary);
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: rgba(0, 255, 65, 0.2);
            border-color: var(--primary);
            transform: scale(1.02);
        }
        
        .action-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            text-shadow: 0 0 10px var(--primary);
        }
        
        .stat-label {
            font-size: 0.9em;
            color: rgba(0, 255, 65, 0.7);
            margin-top: 5px;
        }
        
        .result {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0, 255, 65, 0.05);
            border: 1px solid var(--border);
            border-radius: 8px;
            display: none;
        }
        
        .result.show {
            display: block;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.show {
            display: block;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading::after {
            content: '...';
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎵 BlackMamba Music Performance Suite</h1>
            <p class="subtitle">VPA + Audio Detector + Music Library Integration</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{{ total_songs }}</div>
                    <div class="stat-label">Canciones</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="components-count">0</div>
                    <div class="stat-label">Componentes Activos</div>
                </div>
            </div>
        </header>
        
        <div class="grid">
            <!-- Detección Dual -->
            <div class="card">
                <h2>
                    🔍 Detección Dual
                    <span class="status" id="status-dual"></span>
                </h2>
                <p>Shazam + BlackMamba Detector</p>
                <button class="action-btn" onclick="detectDual()" id="btn-dual">
                    Detectar Canción (10s)
                </button>
                <div class="loading" id="loading-dual">Detectando</div>
                <div class="result" id="result-dual"></div>
            </div>
            
            <!-- BlackMamba Detector -->
            <div class="card">
                <h2>
                    🎵 BlackMamba Detector
                    <span class="status" id="status-detector"></span>
                </h2>
                <p>Detección offline por fingerprint</p>
                <button class="action-btn" onclick="detectBlackMamba()" id="btn-detector">
                    Detectar (Solo Local)
                </button>
                <div class="loading" id="loading-detector">Analizando</div>
                <div class="result" id="result-detector"></div>
            </div>
            
            <!-- Shazam -->
            <div class="card">
                <h2>
                    🔊 Shazam
                    <span class="status" id="status-shazam"></span>
                </h2>
                <p>Detección vía API Shazam</p>
                <button class="action-btn" onclick="detectShazam()" id="btn-shazam">
                    Detectar (Streaming)
                </button>
                <div class="loading" id="loading-shazam">Consultando Shazam</div>
                <div class="result" id="result-shazam"></div>
            </div>
            
            <!-- Análisis Vocal -->
            <div class="card">
                <h2>
                    🎤 Análisis Vocal
                    <span class="status" id="status-vocal"></span>
                </h2>
                <p>Métricas de afinación y timing</p>
                <input type="file" id="audio-file" accept="audio/*" style="display: none;">
                <button class="action-btn" onclick="selectAudioFile()" id="btn-vocal">
                    Seleccionar Audio
                </button>
                <div class="loading" id="loading-vocal">Analizando vocal</div>
                <div class="result" id="result-vocal"></div>
            </div>
            
            <!-- Letras -->
            <div class="card">
                <h2>
                    📝 Letras
                    <span class="status" id="status-lyrics"></span>
                </h2>
                <p>Obtener letras de canciones</p>
                <input type="text" id="lyrics-title" placeholder="Título" 
                       style="width: 100%; padding: 10px; margin-top: 10px; 
                              background: rgba(0,0,0,0.3); border: 1px solid var(--border); 
                              border-radius: 5px; color: var(--primary);">
                <input type="text" id="lyrics-artist" placeholder="Artista" 
                       style="width: 100%; padding: 10px; margin-top: 10px; 
                              background: rgba(0,0,0,0.3); border: 1px solid var(--border); 
                              border-radius: 5px; color: var(--primary);">
                <button class="action-btn" onclick="fetchLyrics()" id="btn-lyrics">
                    Buscar Letras
                </button>
                <div class="loading" id="loading-lyrics">Buscando</div>
                <div class="result" id="result-lyrics"></div>
            </div>
            
            <!-- Biblioteca -->
            <div class="card">
                <h2>
                    📚 Biblioteca Musical
                    <span class="status active"></span>
                </h2>
                <p>{{ total_songs }} canciones indexadas</p>
                <button class="action-btn" onclick="window.open('music_webui.html', '_blank')">
                    Abrir WebUI
                </button>
                <button class="action-btn" onclick="window.location.href='./music_manager.sh'">
                    Music Manager
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // Inicializar estado
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Actualizar contadores
                document.getElementById('components-count').textContent = 
                    Object.values(data.components).filter(v => v).length;
                
                // Actualizar estados
                updateStatus('dual', data.features.dual_detection);
                updateStatus('detector', data.features.blackmamba_detector);
                updateStatus('shazam', data.features.shazam);
                updateStatus('vocal', data.features.vocal_analysis);
                updateStatus('lyrics', data.features.lyrics_fetch);
                
                // Habilitar/deshabilitar botones
                document.getElementById('btn-dual').disabled = !data.features.dual_detection;
                document.getElementById('btn-detector').disabled = !data.features.blackmamba_detector;
                document.getElementById('btn-shazam').disabled = !data.features.shazam;
                document.getElementById('btn-vocal').disabled = !data.features.vocal_analysis;
                document.getElementById('btn-lyrics').disabled = !data.features.lyrics_fetch;
                
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }
        
        function updateStatus(component, isActive) {
            const el = document.getElementById(`status-${component}`);
            if (el) {
                el.className = `status ${isActive ? 'active' : 'inactive'}`;
            }
        }
        
        function showLoading(component, show = true) {
            document.getElementById(`loading-${component}`).className = show ? 'loading show' : 'loading';
            document.getElementById(`btn-${component}`).disabled = show;
        }
        
        function showResult(component, html) {
            const el = document.getElementById(`result-${component}`);
            el.innerHTML = html;
            el.className = 'result show';
        }
        
        async function detectDual() {
            showLoading('dual');
            try {
                const response = await fetch('/api/detect/dual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: 10 })
                });
                const data = await response.json();
                
                if (data.detected) {
                    showResult('dual', `
                        <strong>✅ Detectado (${data.method})</strong><br>
                        🎵 ${data.song.title}<br>
                        🎤 ${data.song.artist}<br>
                        ${data.confidence ? `📊 Confianza: ${(data.confidence*100).toFixed(1)}%` : ''}
                    `);
                } else {
                    showResult('dual', '<strong>❌ No detectado</strong>');
                }
            } catch (error) {
                showResult('dual', `<strong>Error:</strong> ${error.message}`);
            } finally {
                showLoading('dual', false);
            }
        }
        
        async function detectBlackMamba() {
            showLoading('detector');
            try {
                const response = await fetch('/api/detect/blackmamba', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: 10 })
                });
                const data = await response.json();
                
                if (data.detected) {
                    showResult('detector', `
                        <strong>✅ Detectado</strong><br>
                        🎵 ${data.song.title}<br>
                        🎤 ${data.song.artist}<br>
                        📊 Confianza: ${(data.confidence*100).toFixed(1)}%
                    `);
                } else {
                    showResult('detector', '<strong>❌ No detectado</strong>');
                }
            } catch (error) {
                showResult('detector', `<strong>Error:</strong> ${error.message}`);
            } finally {
                showLoading('detector', false);
            }
        }
        
        async function detectShazam() {
            showLoading('shazam');
            try {
                const response = await fetch('/api/detect/shazam', { method: 'POST' });
                const data = await response.json();
                
                if (data.detected) {
                    showResult('shazam', `
                        <strong>✅ Detectado</strong><br>
                        🎵 ${data.song}<br>
                        🔗 <a href="${data.url}" target="_blank" style="color: var(--primary);">Ver en Shazam</a>
                    `);
                } else {
                    showResult('shazam', '<strong>❌ No detectado</strong>');
                }
            } catch (error) {
                showResult('shazam', `<strong>Error:</strong> ${error.message}`);
            } finally {
                showLoading('shazam', false);
            }
        }
        
        function selectAudioFile() {
            document.getElementById('audio-file').click();
        }
        
        document.getElementById('audio-file').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            showLoading('vocal');
            // TODO: Implementar upload y análisis
            showResult('vocal', '<strong>ℹ️ Función en desarrollo</strong>');
            showLoading('vocal', false);
        });
        
        async function fetchLyrics() {
            const title = document.getElementById('lyrics-title').value;
            const artist = document.getElementById('lyrics-artist').value;
            
            if (!title || !artist) {
                showResult('lyrics', '<strong>⚠️ Se requiere título y artista</strong>');
                return;
            }
            
            showLoading('lyrics');
            try {
                const response = await fetch(`/api/lyrics?title=${encodeURIComponent(title)}&artist=${encodeURIComponent(artist)}`);
                const data = await response.json();
                
                if (data.lyrics) {
                    showResult('lyrics', `
                        <strong>✅ Letras encontradas</strong><br>
                        <pre style="white-space: pre-wrap; max-height: 300px; overflow-y: auto; margin-top: 10px;">
${data.lyrics}
                        </pre>
                    `);
                } else {
                    showResult('lyrics', '<strong>❌ Letras no encontradas</strong>');
                }
            } catch (error) {
                showResult('lyrics', `<strong>Error:</strong> ${error.message}`);
            } finally {
                showLoading('lyrics', false);
            }
        }
        
        // Inicializar al cargar
        checkStatus();
        setInterval(checkStatus, 30000); // Actualizar cada 30s
    </script>
</body>
</html>
    """
    
    return render_template_string(html, total_songs=len(library))

# ============================================================
# MAIN
# ============================================================

def main():
    """Punto de entrada principal"""
    print("🎵 BLACKMAMBA MUSIC PERFORMANCE SUITE")
    print("=" * 60)
    print("Inicializando componentes...")
    
    # Inicializar
    init_components()
    
    # Mostrar estado
    print("\n📊 Estado del Sistema:")
    print(f"   VPA: {'✅' if vpa_instance else '❌'}")
    print(f"   Audio Detector: {'✅' if (vpa_instance or detector_instance) else '❌'}")
    print(f"   Biblioteca: ✅ ({len(load_music_library())} canciones)")
    
    print(f"\n🚀 Servidor iniciado en http://localhost:{PORT}")
    print("   Presiona Ctrl+C para detener\n")
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == "__main__":
    main()
