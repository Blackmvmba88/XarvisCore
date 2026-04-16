
from flask import Flask, jsonify, request
from flask_cors import CORS
import psutil
import platform
import datetime
import socket
import subprocess
import os

app = Flask(__name__)
CORS(app) # Permitir que XarvisCore (puerto 5050) consulte datos

def get_network_scan():
    try:
        # Intento rápido con arp si nmap no está disponible de inmediato
        res = subprocess.check_output(["arp", "-a"]).decode()
        return res
    except:
        return "Escaneo no disponible"

@app.route("/")
def index():
    return jsonify({
        "module": "XARVIS FULL POWER",
        "status": "OPERATIONAL",
        "endpoints": ["/estado", "/red", "/sistema"]
    })

@app.route("/estado")
def estado():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "uptime": str(datetime.timedelta(seconds=int(datetime.datetime.now().timestamp() - psutil.boot_time()))),
        "disks": [{"mount": d.mountpoint, "percent": psutil.disk_usage(d.mountpoint).percent} for d in psutil.disk_partitions() if 'cdrom' not in d.opts]
    })

@app.route("/red")
def red():
    return jsonify({
        "local_ip": socket.gethostbyname(socket.gethostname()),
        "devices": get_network_scan()
    })

@app.route("/ram")
def ram_status():
    """Endpoint para monitoreo detallado de RAM"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Obtener top 10 procesos por memoria
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            info = proc.info
            if info['memory_percent'] and info['memory_percent'] > 0.5:
                processes.append({
                    'name': info['name'],
                    'memory_percent': round(info['memory_percent'], 2)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    
    return jsonify({
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "percent": mem.percent,
        "swap_percent": swap.percent,
        "top_processes": processes[:10],
        "status": "CRITICAL" if mem.percent > 85 else "WARNING" if mem.percent > 75 else "GOOD"
    })

@app.route("/sistema")
def sistema():
    return jsonify({
        "os": platform.system(),
        "version": platform.version(),
        "arch": platform.machine(),
        "processor": platform.processor()
    })

if __name__ == "__main__":
    # Robustez: Solo corre si no hay otro proceso en el puerto
    app.run(host="0.0.0.0", port=8080, debug=False)
