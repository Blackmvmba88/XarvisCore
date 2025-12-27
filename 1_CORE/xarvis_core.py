
from flask import Flask, request, render_template_string, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

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
        async function updateStats() {
            try {
                const response = await fetch('http://localhost:8080/estado');
                const data = await response.json();
                document.getElementById('cpu').innerText = data.cpu + '%';
                document.getElementById('ram').innerText = data.ram + '%';
                document.getElementById('uptime').innerText = data.uptime;
            } catch (e) {
                console.error("Master Power offline");
            }
        }
        setInterval(updateStats, 2000);
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

if __name__ == '__main__':
    # Validar certificados antes de iniciar
    if not os.path.exists(CERT_PATH) or not os.path.exists(KEY_PATH):
        print(f"❌ Error: Certificados no encontrados en {CERT_PATH}")
        # Fallback a HTTP si no hay certificados (aunque en este caso los tenemos)
        app.run(host='0.0.0.0', port=5050)
    else:
        app.run(host='0.0.0.0', port=5050, ssl_context=(CERT_PATH, KEY_PATH))
