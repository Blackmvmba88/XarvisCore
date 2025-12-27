
from flask import Flask, request, jsonify
import subprocess
import os
import json
import platform
import socket
import datetime
import psutil

app = Flask(__name__)

def detectar_dispositivos():
    red_local = socket.gethostbyname(socket.gethostname())
    red_base = ".".join(red_local.split(".")[:-1])
    resultados = subprocess.check_output(["nmap", "-sn", f"{red_base}.0/24"]).decode()
    return resultados

def obtener_estado_sistema():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "uptime": str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())),
        "sistema": platform.platform()
    }

def ejecutar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True)
        return resultado.decode()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def crear_launch_agent():
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.xarvis.fullpower.plist")
    python_path = "/usr/local/bin/python3"
    script_path = os.path.abspath(__file__)

    contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
     "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.xarvis.fullpower</string>
        <key>ProgramArguments</key>
        <array>
            <string>{python_path}</string>
            <string>{script_path}</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <true/>
        <key>StandardOutPath</key>
        <string>/tmp/xarvis.out</string>
        <key>StandardErrorPath</key>
        <string>/tmp/xarvis.err</string>
    </dict>
    </plist>
    """

    with open(plist_path, "w") as f:
        f.write(contenido)

    os.system(f"launchctl load {plist_path}")
    return f"LaunchAgent creado y activado en {plist_path}"

@app.route("/")
def index():
    return "<h1>Xarvis Full Power Activo 🧠💥</h1>"

@app.route("/estado")
def estado():
    return jsonify(obtener_estado_sistema())

@app.route("/red")
def red():
    return jsonify({"dispositivos": detectar_dispositivos()})

@app.route("/comando", methods=["POST"])
def comando():
    data = request.json
    resultado = ejecutar_comando(data.get("cmd", ""))
    return jsonify({"resultado": resultado})

@app.route("/activar_jarvis", methods=["GET"])
def activar_jarvis():
    resultado = crear_launch_agent()
    return jsonify({"resultado": resultado})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
