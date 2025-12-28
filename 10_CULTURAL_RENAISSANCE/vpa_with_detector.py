"""
VPA + BlackMamba Audio Detector Integration
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez

Integra el detector propio con el sistema VPA.
"""

from vocal_performance_analyzer import VocalPerformanceAnalyzer
from audio_detector import AudioFingerprinter, AudioRecorder
from flask import Flask, jsonify, request
from flask_cors import CORS

class VPAWithDetector(VocalPerformanceAnalyzer):
    """
    Extensión del VPA con detector propio de audio.
    """
    
    def __init__(self):
        super().__init__()
        
        # Inicializar detector BlackMamba
        self.detector = AudioFingerprinter()
        self.recorder = AudioRecorder()
        
        print("✅ VPA + BlackMamba Audio Detector inicializado")
    
    def detect_song_dual(self, duration=10):
        """
        Detecta canción usando ambos métodos:
        1. Shazam (para canciones en Spotify)
        2. BlackMamba Detector (para SoundCloud y locales)
        """
        print("🔍 Iniciando detección dual...")
        
        # Intentar Shazam primero (más rápido)
        shazam_result = self.detect_song_shazam()
        
        if shazam_result.get('detected'):
            song_name = shazam_result.get('song')
            # Buscar en biblioteca local
            local = self.get_song_from_library(song_name)
            if local:
                print(f"✅ Shazam detectó: {song_name}")
                return {
                    "method": "shazam",
                    "detected": True,
                    "song": local,
                    **shazam_result
                }
        
        # Si Shazam falló, usar detector propio
        print("🎵 Shazam no detectó, usando BlackMamba Detector...")
        
        recording = self.recorder.record_system_audio_macos(duration)
        if not recording:
            return {
                "method": "blackmamba",
                "detected": False,
                "error": "No se pudo grabar audio"
            }
        
        result = self.detector.detect_from_recording(recording)
        
        if result:
            print(f"✅ BlackMamba detectó: {result['title']} ({result['confidence']*100:.1f}%)")
            return {
                "method": "blackmamba",
                "detected": True,
                "song": {
                    "title": result['title'],
                    "artist": result['artist'],
                    "file_path": result['file_path']
                },
                "confidence": result['confidence']
            }
        else:
            print("❌ No se pudo detectar la canción")
            return {
                "method": "none",
                "detected": False,
                "message": "No detectada ni por Shazam ni por BlackMamba"
            }
    
    def detect_song_blackmamba(self, duration=10):
        """
        Detecta usando solo el detector propio (para canciones de SoundCloud).
        """
        print(f"🎙️  Grabando {duration} segundos de audio...")
        
        recording = self.recorder.record_system_audio_macos(duration)
        if not recording:
            return {
                "detected": False,
                "error": "Error grabando audio del sistema"
            }
        
        print("🔎 Analizando fingerprint...")
        result = self.detector.detect_from_recording(recording)
        
        if result:
            return {
                "detected": True,
                "song": {
                    "title": result['title'],
                    "artist": result['artist'],
                    "file_path": result['file_path']
                },
                "confidence": result['confidence'],
                "method": "blackmamba_detector"
            }
        else:
            return {
                "detected": False,
                "message": "Canción no encontrada en biblioteca indexada",
                "method": "blackmamba_detector"
            }
    
    def index_library_for_detection(self):
        """
        Indexa toda la biblioteca con fingerprints para detección.
        """
        return self.detector.index_library(self.music_library)


# API Flask con detector integrado
app = Flask(__name__)
CORS(app)
vpa_detector = VPAWithDetector()

@app.route('/api/detect/dual', methods=['POST'])
def api_detect_dual():
    """Detecta usando Shazam primero, luego BlackMamba Detector."""
    duration = request.json.get('duration', 10) if request.json else 10
    result = vpa_detector.detect_song_dual(duration)
    return jsonify(result)

@app.route('/api/detect/blackmamba', methods=['POST'])
def api_detect_blackmamba():
    """Detecta solo con BlackMamba Detector."""
    duration = request.json.get('duration', 10) if request.json else 10
    result = vpa_detector.detect_song_blackmamba(duration)
    return jsonify(result)

@app.route('/api/index', methods=['POST'])
def api_index_library():
    """Indexa biblioteca con fingerprints."""
    indexed = vpa_detector.index_library_for_detection()
    return jsonify({
        "indexed": indexed,
        "status": "success",
        "message": f"{indexed} canciones indexadas con fingerprints"
    })

@app.route('/api/detector/status', methods=['GET'])
def api_detector_status():
    """Estado del detector."""
    return jsonify({
        "status": "operational",
        "indexed_songs": len(vpa_detector.detector.fingerprints),
        "library_songs": len(vpa_detector.library_data),
        "method": "chromaprint_fingerprinting"
    })

if __name__ == "__main__":
    print("🦅 VPA + BlackMamba Audio Detector")
    print("=" * 60)
    print(f"Biblioteca: {len(vpa_detector.library_data)} canciones")
    print(f"Indexadas: {len(vpa_detector.detector.fingerprints)} fingerprints")
    print()
    print("Endpoints disponibles:")
    print("  POST /api/detect/dual         - Shazam + BlackMamba")
    print("  POST /api/detect/blackmamba   - Solo BlackMamba")
    print("  POST /api/index               - Indexar biblioteca")
    print("  GET  /api/detector/status     - Estado del detector")
    print()
    print("Iniciando servidor en http://localhost:9001...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=9001, debug=False)
