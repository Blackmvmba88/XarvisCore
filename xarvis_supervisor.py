
import os
import subprocess
import time
import signal
import sys
import psutil
from datetime import datetime

# Configuración de Rutas
BASE_DIR = "/Users/blackmamba/Desktop/XarvisCore"
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")
LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

PROCESSES = {
    "CORE": {
        "path": os.path.join(BASE_DIR, "xarvis_launcher_mac_termux/xarvis_core.py"),
        "log": os.path.join(LOG_DIR, "core.log"),
        "proc": None
    },
    "FULL_POWER": {
        "path": os.path.join(BASE_DIR, "xarvis_full_power_full_package/xarvis_full_power.py"),
        "log": os.path.join(LOG_DIR, "full_power.log"),
        "proc": None
    }
}

def log_master(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [MASTER] {msg}")
    with open(os.path.join(LOG_DIR, "master.log"), "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def start_process(name, config):
    log_master(f"Levantando {name}...")
    try:
        f_log = open(config["log"], "a")
        proc = subprocess.Popen(
            [VENV_PYTHON, config["path"]],
            stdout=f_log,
            stderr=f_log,
            preexec_fn=os.setsid
        )
        config["proc"] = proc
        log_master(f"{name} iniciado con PID: {proc.pid}")
    except Exception as e:
        log_master(f"ERROR iniciando {name}: {e}")

def kill_process(name, config):
    if config["proc"]:
        log_master(f"Cerrando {name} (PID: {config['proc'].pid})...")
        try:
            os.killpg(os.getpgid(config["proc"].pid ribbon), signal.SIGTERM)
        except:
            pass
        config["proc"] = None

def signal_handler(sig, frame):
    log_master("Señal de apagado recibida. Cerrando Xarvis...")
    for name, config in PROCESSES.items():
        kill_process(name, config)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

log_master("==== XARVIS MASTER SUPERVISOR INICIADO ====")

# Inicialización
for name, config in PROCESSES.items():
    start_process(name, config)

# Bucle de Supervisión Vital
try:
    while True:
        time.sleep(10)
        for name, config in PROCESSES.items():
            if config["proc"].poll() is not None:
                log_master(f"⚠️ Alerta: {name} se ha detenido inesperadamente. Reiniciando...")
                start_process(name, config)
            else:
                # Validación de Salud (Opcional: aquí podríamos hacer un ping al puerto)
                pass
except KeyboardInterrupt:
    signal_handler(None, None)
