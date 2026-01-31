
import os
import subprocess
import time
import signal
import sys
from datetime import datetime

# === INFRAESTRUCTURA DE DOMINIOS XARVIS ===
# Arquitectura Soberana: 19 Dominios Integrados (0-18)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")
LOG_DIR = os.path.join(BASE_DIR, "5_INFRA/logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

import json

# === INFRAESTRUCTURA DE DOMINIOS XARVIS ===
# Arquitectura Soberana: 19 Dominios Integrados (0-18)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")
LOG_DIR = os.path.join(BASE_DIR, "5_INFRA/logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Carga de configuración de procesos desde JSON
def load_process_config():
    config_path = os.path.join(BASE_DIR, "supervisor_config.json")
    processes = {}
    extended_processes = {}
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        for name, proc_info in config.get("core_processes", {}).items():
            processes[name] = {
                "path": os.path.join(BASE_DIR, proc_info["path"]),
                "log": os.path.join(BASE_DIR, proc_info["log"]),
                "proc": None,
                "priority": proc_info["priority"]
            }

        for name, proc_info in config.get("extended_processes", {}).items():
            extended_processes[name] = {
                "path": os.path.join(BASE_DIR, proc_info["path"]),
                "log": os.path.join(BASE_DIR, proc_info["log"]),
                "proc": None,
                "priority": proc_info["priority"],
                "enabled": proc_info.get("enabled", False)
            }
        
        log_master("Configuración de dominios cargada desde supervisor_config.json")
        return processes, extended_processes
    except Exception as e:
        log_master(f"FALLO CRÍTICO al cargar supervisor_config.json: {e}")
        # Retornar diccionarios vacíos para evitar que el supervisor se caiga
        return {}, {}

PROCESSES, EXTENDED_PROCESSES = load_process_config()


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
            os.killpg(os.getpgid(config['proc'].pid), signal.SIGTERM)
        except ProcessLookupError:
            # El proceso ya no existe, lo cual está bien.
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
            if config["proc"] and config["proc"].poll() is not None:
                log_master(f"⚠️ Alerta: Dominio {name} fuera de servicio. Restaurando...")
                start_process(name, config)
except KeyboardInterrupt:
    signal_handler(None, None)
