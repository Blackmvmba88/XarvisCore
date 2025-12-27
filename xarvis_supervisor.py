
import os
import subprocess
import time
import signal
import sys
from datetime import datetime

# === INFRAESTRUCTURA DE DOMINIOS XARVIS ===
# Arquitectura Soberana: 19 Dominios Integrados (0-18)
BASE_DIR = "/Users/blackmamba/Desktop/XarvisCore"
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")
LOG_DIR = os.path.join(BASE_DIR, "5_INFRA/logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Mapa de Procesos por Dominio - Núcleo Principal
PROCESSES = {
    "CORE_SOVEREIGN": {
        "path": os.path.join(BASE_DIR, "1_CORE/xarvis_core.py"),
        "log": os.path.join(LOG_DIR, "core.log"),
        "proc": None,
        "priority": 1  # Máxima prioridad
    },
    "POWER_EXECUTION": {
        "path": os.path.join(BASE_DIR, "3_POWER/xarvis_full_power.py"),
        "log": os.path.join(LOG_DIR, "full_power.log"),
        "proc": None,
        "priority": 2
    }
}

# Procesos Extendidos - Activación Opcional
EXTENDED_PROCESSES = {
    "STATION_COMMAND": {
        "path": os.path.join(BASE_DIR, "18_BLACKMAMBA_STATION/core/simple_server.py"),
        "log": os.path.join(LOG_DIR, "station.log"),
        "proc": None,
        "priority": 3,
        "enabled": False  # Activar manualmente cuando sea necesario
    }
}

def log_master(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [MASTER_INFRA] {msg}")
    with open(os.path.join(LOG_DIR, "master.log"), "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def start_process(name, config):
    log_master(f"Cargando Dominio {name}...")
    try:
        f_log = open(config["log"], "a")
        proc = subprocess.Popen(
            [VENV_PYTHON, config["path"]],
            stdout=f_log,
            stderr=f_log,
            preexec_fn=os.setsid,
            cwd=os.path.dirname(config["path"]) # Correr en su propio directorio
        )
        config["proc"] = proc
        log_master(f"{name} en línea. PID: {proc.pid}")
    except Exception as e:
        log_master(f"FALLO CRÍTICO en {name}: {e}")

def kill_process(name, config):
    if config["proc"]:
        log_master(f"Desactivando {name} (PID: {config['proc'].pid})...")
        try:
            os.killpg(os.getpgid(config["proc"].pid), signal.SIGTERM)
        except:
            pass
        config["proc"] = None

def signal_handler(sig, frame):
    log_master("Apagado de Infraestructura solicitado. Resguardando dominios...")
    for name, config in PROCESSES.items():
        kill_process(name, config)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

log_master("==== ORQUESTADOR DE INFRAESTRUCTURA DEL MUNDO INICIADO ====")

# Despliegue Inicial
for name, config in PROCESSES.items():
    start_process(name, config)

# Vigilancia Resiliente
try:
    while True:
        time.sleep(15)
        for name, config in PROCESSES.items():
            if config["proc"].poll() is not None:
                log_master(f"⚠️ Alerta: Dominio {name} fuera de servicio. Restaurando...")
                start_process(name, config)
except KeyboardInterrupt:
    signal_handler(None, None)
