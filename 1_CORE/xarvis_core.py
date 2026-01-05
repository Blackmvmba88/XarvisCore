
from flask import Flask, request, render_template_string, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets
import sys

load_dotenv()

# Importar Quantum Core Protocol
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '19_QUANTUM_CORE'))
try:
    from quantum_core_protocol import quantum_core
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    print("⚠️ Quantum Core no disponible - Dashboard en modo básico")

# --- Configuración Robusta ---
BASE_DIR = "/Users/blackmamba/Desktop/XarvisCore"
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(24))
USERNAME = os.getenv("USERNAME", "BlackSekhmet")
PASSWORD = os.getenv("PASSWORD", "Admin123")
CERT_PATH = os.getenv("CERT_PATH", f"{BASE_DIR}/2_GUARDIANS/xarvis_certificados/cert.pem")
KEY_PATH = os.getenv("KEY_PATH", f"{BASE_DIR}/2_GUARDIANS/xarvis_certificados/key.pem")

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# --- Plantilla Premium (Estética Matrix/Cyberpunk con Glassmorphism) ---
THEME_CSS = """
:root {
    --primary: #00ff41;
    --bg: #0a0a0a;
    --glass: rgba(20, 20, 20, 0.8);
    --border: rgba(0, 255, 65, 0.3);
}

body {
    background: var(--bg);
    color: var(--primary);
    font-family: 'Inter', 'Courier New', monospace;
    margin: 0;
    overflow-x: hidden;
    background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #0a0a0a 100%);
}

.glass-card {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
}

.matrix-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
}

.header {
    text-align: center;
    padding: 50px 0;
    text-transform: uppercase;
    letter-spacing: 5px;
    text-shadow: 0 0 10px var(--primary);
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #fff;
}

input {
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid var(--primary);
    color: var(--primary);
    padding: 12px;
    border-radius: 5px;
    width: 100%;
    margin-bottom: 15px;
}

button {
    background: var(--primary);
    color: #000;
    border: none;
    padding: 12px 25px;
    border-radius: 5px;
    font-weight: bold;
    cursor: pointer;
    transition: 0.3s;
    width: 100%;
}

button:hover {
    box-shadow: 0 0 20px var(--primary);
    transform: translateY(-2px);
}

.status-dot {
    height: 10px;
    width: 10px;
    background-color: var(--primary);
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
    box-shadow: 0 0 10px var(--primary);
}
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>XARVIS | SOVEREIGN ACCESS</title>
    <style>{{ css }}</style>
</head>
<body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
    <div class="glass-card" style="width: 350px;">
        <h2 style="text-align: center;">🛡️ ACCESO CORE</h2>
        <form method="POST">
            <input name="username" placeholder="IDENTIDAD" required>
            <input name="password" type="password" placeholder="CÓDIGO" required>
            <button type="submit">INICIAR FUSIÓN</button>
        </form>
        {% if error %}<p style="color: red; text-align: center;">{{ error }}</p>{% endif %}
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>XARVIS | MASTER COMMAND</title>
    <style>{{ css }}</style>
    <script>
        // Históricos para gráficas
        const cpuHistory = [];
        const ramHistory = [];
        const maxHistory = 30;
        
        async function updateStats() {
            try {
                const response = await fetch('http://localhost:8080/estado');
                const data = await response.json();
                document.getElementById('cpu').innerText = data.cpu + '%';
                document.getElementById('ram').innerText = data.ram + '%';
                document.getElementById('uptime').innerText = data.uptime;
                
                // Actualizar históricos
                cpuHistory.push(parseFloat(data.cpu));
                ramHistory.push(parseFloat(data.ram));
                
                if (cpuHistory.length > maxHistory) {
                    cpuHistory.shift();
                    ramHistory.shift();
                }
                
                drawCharts();
            } catch (e) {
                console.error("Master Power offline");
            }
        }
        
        function drawCharts() {
            drawChart('cpuChart', cpuHistory, '#00ff41');
            drawChart('ramChart', ramHistory, '#ffaa00');
        }
        
        function drawChart(canvasId, data, color) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            
            // Limpiar
            ctx.clearRect(0, 0, width, height);
            
            if (data.length < 2) return;
            
            // Dibujar grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 4; i++) {
                const y = (height / 4) * i;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
            
            // Dibujar línea
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            const stepX = width / (maxHistory - 1);
            const startIndex = Math.max(0, data.length - maxHistory);
            
            data.slice(startIndex).forEach((value, index) => {
                const x = stepX * index;
                const y = height - (value / 100 * height);
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Dibujar puntos
            ctx.fillStyle = color;
            data.slice(startIndex).forEach((value, index) => {
                const x = stepX * index;
                const y = height - (value / 100 * height);
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, Math.PI * 2);
                ctx.fill();
            });
        }
        
        async function updateQuantumCore() {
            try {
                const statusResponse = await fetch('/api/quantum/status');
                const status = await statusResponse.json();
                
                if (status.error) {
                    document.getElementById('quantum-status').innerText = 'STANDBY';
                    document.getElementById('quantum-ollama').innerText = '❌ No disponible';
                    return;
                }
                
                // Estado de Ollama
                const ollamaStatus = status.pilar_4_ollama.metricas.conectado;
                document.getElementById('quantum-status').innerText = ollamaStatus ? 'OPERATIVO' : 'STANDBY';
                document.getElementById('quantum-ollama').innerText = ollamaStatus ? '✅ ACTIVO' : '⚠️ Offline';
                
                // Modelos disponibles
                const models = status.pilar_4_ollama.metricas.modelos_disponibles;
                document.getElementById('quantum-models').innerText = models.length > 0 ? models.join(', ') : 'Ninguno';
                
                // Predicción
                const predResponse = await fetch('/api/quantum/predict');
                const prediction = await predResponse.json();
                
                if (prediction.scenarios && prediction.scenarios.length > 0) {
                    const scenario = prediction.scenarios[0];
                    document.getElementById('quantum-prediction').innerText = 
                        `${scenario.name} (${Math.round(scenario.probability * 100)}%)`;
                    document.getElementById('quantum-prediction').style.color = 
                        scenario.impact === 'high' ? '#ff4444' : '#ffaa00';
                } else {
                    document.getElementById('quantum-prediction').innerText = 'Sistema estable';
                    document.getElementById('quantum-prediction').style.color = 'var(--primary)';
                }
                
            } catch (e) {
                console.error("Quantum Core offline:", e);
                document.getElementById('quantum-status').innerText = 'OFFLINE';
            }
        }
        
        async function sendToOllama() {
            const input = document.getElementById('ollama-input');
            const output = document.getElementById('ollama-output');
            const prompt = input.value.trim();
            
            if (!prompt) {
                output.innerHTML = '<span style="color: #ff4444;">⚠️ Escribe algo primero</span>';
                return;
            }
            
            output.innerHTML = '<span style="color: #ffaa00;">🧠 Pensando...</span>';
            input.disabled = true;
            
            try {
                const response = await fetch('/api/quantum/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt, model: 'mistral'})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    output.innerHTML = `<strong style="color: var(--primary);">💬 Mistral:</strong><br>${data.response}`;
                } else {
                    output.innerHTML = `<span style="color: #ff4444;">❌ Error: ${data.error || data.mensaje}</span>`;
                }
            } catch (e) {
                output.innerHTML = '<span style="color: #ff4444;">❌ Error de conexión</span>';
            } finally {
                input.disabled = false;
                input.value = '';
            }
        }
        
        setInterval(updateStats, 2000);
        setInterval(updateQuantumCore, 5000);
        
        // Ejecutar al cargar
        updateStats();
        updateQuantumCore();
    </script>
</head>
<body>
    <div class="header">
        <h1>XΛЯVIƧ CӨЯΣ</h1>
        <p><span class="status-dot"></span> SISTEMA TOTALMENTE OPERATIVO</p>
    </div>

    <div class="matrix-grid">
        <div class="glass-card">
            <h3>📊 RECURSOS VITALES</h3>
            <p>CPU: <span id="cpu" class="stat-value">--</span></p>
            <p>RAM: <span id="ram" class="stat-value">--</span></p>
            <p>TIEMPO ACTIVO: <span id="uptime" style="color: #888;">Cargando...</span></p>
            <div style="margin-top: 1rem;">
                <small style="color: #888;">CPU (30s)</small>
                <canvas id="cpuChart" width="280" height="60" style="width: 100%; height: 60px; margin-top: 0.5rem;"></canvas>
                <small style="color: #888; margin-top: 0.5rem; display: block;">RAM (30s)</small>
                <canvas id="ramChart" width="280" height="60" style="width: 100%; height: 60px; margin-top: 0.5rem;"></canvas>
            </div>
        </div>
        
        <div class="glass-card">
            <h3>⚡ FULL POWER MODULE</h3>
            <p>Estado: <span style="color: var(--primary);">CONECTADO</span></p>
            <p>Puerto: <code>8080</code></p>
            <button onclick="window.open('http://localhost:8080/red', '_blank')">ESCANEAR RED LOCAL</button>
        </div>

        <div class="glass-card">
            <h3>🛡️ SEGURIDAD ULTRA</h3>
            <p>SSL: <span style="color: var(--primary);">ACTIVO</span></p>
            <p>Certificados: <code>Validado</code></p>
            <button style="background: #333; color: #fff;">REVISAR LOGS</button>
        </div>

        <div class="glass-card">
            <h3>🎓 BIBLIOTECA ALEJANDRÍA</h3>
            <p>Recursos: <span style="color: var(--primary);">Indexando...</span></p>
            <p>Estado: <code>Soberanía Conocimiento</code></p>
            <button onclick="alert('Accediendo al conocimiento democratizado...')">VER ARCHIVOS</button>
        </div>

        <div class="glass-card">
            <h3>🍎 PROTOCOLO HAMBRE CERO</h3>
            <p>Distribución: <span style="color: var(--primary);">Mapa Vital Activo</span></p>
            <p>Alerta: <code style="color: var(--primary);">CERO CARENCIAS</code></p>
            <button onclick="alert('Calculando rutas de abasto...')">ESTADO SUMINISTROS</button>
        </div>
        
        <div class="glass-card" style="grid-column: span 2; background: linear-gradient(135deg, rgba(0, 255, 65, 0.05), rgba(0, 0, 0, 0.8)); border: 2px solid var(--primary);">
            <h3>🧠 QUANTUM INTELLIGENCE CORE</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <p><strong>Estado:</strong> <span id="quantum-status" style="color: var(--primary);">CARGANDO...</span></p>
                    <p><strong>Ollama:</strong> <span id="quantum-ollama">Verificando...</span></p>
                    <p><strong>Modelos:</strong> <span id="quantum-models" style="font-size: 0.85em; color: #888;">--</span></p>
                    <p><strong>Predicción:</strong></p>
                    <p id="quantum-prediction" style="color: var(--primary); font-size: 0.9em; margin-top: 0.5rem;">Analizando...</p>
                </div>
                <div>
                    <p><strong>💬 Chat con Mistral:</strong></p>
                    <div style="background: rgba(0,0,0,0.5); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem; border: 1px solid rgba(0,255,65,0.2);">
                        <div id="ollama-output" style="min-height: 60px; font-size: 0.85em; color: #888; margin-bottom: 0.5rem; max-height: 120px; overflow-y: auto;">
                            Escribe tu consulta abajo...
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            <input id="ollama-input" type="text" placeholder="Pregunta algo al cerebro..." style="flex: 1; background: rgba(0,0,0,0.5); border: 1px solid var(--border); padding: 0.5rem; border-radius: 4px; color: var(--primary); font-size: 0.9em;" onkeypress="if(event.key==='Enter') sendToOllama()">
                            <button onclick="sendToOllama()" style="padding: 0.5rem 1rem; background: var(--primary); color: #000; font-weight: bold;">ENVIAR</button>
                        </div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 1rem; display: flex; gap: 1rem;">
                <button onclick="window.open('/api/quantum/intelligence', '_blank')" style="flex: 1; background: #333;">📊 REPORTE COMPLETO</button>
                <button onclick="window.open('/api/quantum/status', '_blank')" style="flex: 1; background: #333;">🔍 ESTADO JSON</button>
            </div>
        </div>
    </div>

    <div class="glass-card" style="margin: 20px; text-align: center;">
        <h3>🌍 MANIFIESTO GAIA OPERATIVO</h3>
        <p>"El recurso existe, la inteligencia lo distribuye." - Iyari Cancino Gomez</p>
    </div>

    <div style="text-align: center; margin-top: 50px; opacity: 0.5;">
        <p>Sovereign Intelligence | User: {{ user }}</p>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        passwd = request.form.get('password')
        if user == USERNAME and passwd == PASSWORD:
            session['user'] = user
            return render_template_string(DASHBOARD_PAGE, css=THEME_CSS, user=user)
        return render_template_string(LOGIN_PAGE, css=THEME_CSS, error="IDENTIDAD INVÁLIDA")
    return render_template_string(LOGIN_PAGE, css=THEME_CSS)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "version": "2.0.0-SOVEREIGN"})

@app.route('/api/quantum/status')
def quantum_status():
    """Endpoint para obtener el estado del Quantum Core"""
    if not QUANTUM_AVAILABLE:
        return jsonify({"error": "Quantum Core no disponible"}), 503
    
    try:
        status = quantum_core.get_core_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quantum/predict')
def quantum_predict():
    """Endpoint para generar predicción de escenario"""
    if not QUANTUM_AVAILABLE:
        return jsonify({"error": "Quantum Core no disponible"}), 503
    
    try:
        horizon = request.args.get('horizon', 'short')
        prediction = quantum_core.predict_scenario({}, horizon=horizon)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quantum/intelligence')
def quantum_intelligence():
    """Endpoint para reporte de inteligencia del sistema"""
    if not QUANTUM_AVAILABLE:
        return jsonify({"error": "Quantum Core no disponible"}), 503
    
    try:
        report = quantum_core.get_system_intelligence_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quantum/chat', methods=['POST'])
def quantum_chat():
    """Endpoint para chat con Ollama"""
    if not QUANTUM_AVAILABLE:
        return jsonify({"error": "Quantum Core no disponible"}), 503
    
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model = data.get('model', 'mistral')
        
        if not prompt:
            return jsonify({"error": "Prompt vacío"}), 400
        
        response = quantum_core.query_ollama(prompt, model=model)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Validar certificados antes de iniciar
    if not os.path.exists(CERT_PATH) or not os.path.exists(KEY_PATH):
        print(f"❌ Error: Certificados no encontrados en {CERT_PATH}")
        # Fallback a HTTP si no hay certificados (aunque en este caso los tenemos)
        app.run(host='0.0.0.0', port=5050)
    else:
        app.run(host='0.0.0.0', port=5050, ssl_context=(CERT_PATH, KEY_PATH))
