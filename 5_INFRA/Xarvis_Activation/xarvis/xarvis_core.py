from flask import Flask, request, render_template_string, redirect, url_for
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto")
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "1234")
CERT_PATH = os.getenv("CERT_PATH", "certs/cert.pem")
KEY_PATH = os.getenv("KEY_PATH", "certs/key.pem")

app = Flask(__name__)
app.secret_key = SECRET_KEY

template_login = """
<!DOCTYPE html>
<html>
<head>
    <title>Xarvis Access</title>
    <style>
        body { background-color: black; color: lime; font-family: monospace; text-align: center; margin-top: 10%; }
        input { background: black; color: lime; border: 1px solid lime; padding: 10px; margin: 5px; }
        button { background: lime; color: black; padding: 10px; border: none; }
    </style>
</head>
<body>
    <h2>🛡️ Xarvis - Access Control</h2>
    <form method="POST">
        <input name="username" placeholder="Usuario"><br>
        <input name="password" type="password" placeholder="Contraseña"><br>
        <button type="submit">Entrar</button>
    </form>
</body>
</html>
"""

template_dashboard = """
<!DOCTYPE html>
<html>
<head>
    <title>Xarvis Dashboard</title>
    <style>
        body { background-color: black; color: lime; font-family: monospace; text-align: center; margin-top: 5%; }
    </style>
</head>
<body>
    <h1>🔥 Bienvenido al Dashboard de Xarvis 🔐</h1>
    <p>Autenticado correctamente. El universo te saluda, {{ user }}.</p>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        passwd = request.form.get('password')
        if user == USERNAME and passwd == PASSWORD:
            return render_template_string(template_dashboard, user=user)
        else:
            return "⛔ Acceso denegado", 401
    return render_template_string(template_login)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, ssl_context=(CERT_PATH, KEY_PATH))
