import math
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# === INFRAESTRUCTURA DE DOMINIOS XARVIS ===
# Arquitectura Soberana: 19 Dominios Integrados (0-18)
BASE_DIR = Path(os.environ.get("XARVIS_BASE_DIR", Path(__file__).resolve().parent)).expanduser().resolve()
_DEFAULT_VENV_PYTHON = BASE_DIR / "venv" / "bin" / "python3"
VENV_PYTHON = Path(os.environ.get("XARVIS_PYTHON", _DEFAULT_VENV_PYTHON)).expanduser()
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)
LOG_DIR = Path(os.environ.get("XARVIS_LOG_DIR", BASE_DIR / "5_INFRA" / "logs")).expanduser()

LOG_DIR.mkdir(parents=True, exist_ok=True)
ACTIVE_PROCESSES = {}


def positive_float_env(name, default):
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un número positivo") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} debe ser un número positivo")
    return value


MONITOR_INTERVAL = positive_float_env("XARVIS_MONITOR_INTERVAL", 15.0)
RESTART_BACKOFF_INITIAL = positive_float_env("XARVIS_RESTART_BACKOFF_INITIAL", 5.0)
RESTART_BACKOFF_MAX = positive_float_env("XARVIS_RESTART_BACKOFF_MAX", 300.0)
RESTART_STABLE_AFTER = positive_float_env("XARVIS_RESTART_STABLE_AFTER", 60.0)
SHUTDOWN_TIMEOUT = positive_float_env("XARVIS_SHUTDOWN_TIMEOUT", 10.0)


def process_config(relative_path, log_name, priority, enabled=True):
    return {
        "path": BASE_DIR / relative_path,
        "log": LOG_DIR / log_name,
        "proc": None,
        "priority": priority,
        "enabled": enabled,
        "restart_attempts": 0,
        "restart_at": 0.0,
        "started_at": 0.0,
    }


def env_flag(name):
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def clone_processes(processes, force_enabled=False):
    return {
        name: {
            **config,
            "enabled": True if force_enabled else config.get("enabled", True),
            "proc": None,
            "restart_attempts": 0,
            "restart_at": 0.0,
            "started_at": 0.0,
        }
        for name, config in processes.items()
    }


def runtime_processes(include_extended=False):
    processes = clone_processes(PROCESSES)
    if include_extended:
        processes.update(clone_processes(EXTENDED_PROCESSES, force_enabled=True))
    return processes


def enabled_process_items(processes):
    return sorted(
        ((name, config) for name, config in processes.items() if config.get("enabled", True)),
        key=lambda item: (item[1].get("priority", 100), item[0]),
    )


# Mapa de Procesos por Dominio - Núcleo Principal
PROCESSES = {
    "CORE_SOVEREIGN": process_config("1_CORE/xarvis_core.py", "core.log", 1),  # Máxima prioridad
    "POWER_EXECUTION": process_config("3_POWER/xarvis_full_power.py", "full_power.log", 2),
    "RAM_GUARDIAN": process_config("3_POWER/ram_guardian.py", "ram_guardian.log", 2),
}

# Procesos Extendidos - Activación Opcional
EXTENDED_PROCESSES = {
    "STATION_COMMAND": process_config("18_BLACKMAMBA_STATION/core/simple_server.py", "station.log", 3, enabled=False),
}


def log_master(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [MASTER_INFRA] {msg}")
    with (LOG_DIR / "master.log").open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def start_process(name, config):
    if not config.get("enabled", True):
        log_master(f"{name} omitido: dominio desactivado.")
        return False

    script_path = Path(config["path"])
    if not script_path.exists():
        config["enabled"] = False
        log_master(f"{name} omitido: script no encontrado en {script_path}")
        return False

    log_master(f"Cargando Dominio {name}...")
    try:
        with Path(config["log"]).open("a", encoding="utf-8") as f_log:
            proc = subprocess.Popen(
                [str(VENV_PYTHON), str(script_path)],
                stdout=f_log,
                stderr=f_log,
                preexec_fn=os.setsid,
                cwd=str(script_path.parent),  # Correr en su propio directorio
            )
        config["proc"] = proc
        config["restart_at"] = 0.0
        config["started_at"] = time.monotonic()
        log_master(f"{name} en línea. PID: {proc.pid}")
        return True
    except (OSError, ValueError) as e:
        log_master(f"FALLO CRÍTICO en {name}: {e}")
        return False


def kill_process(name, config):
    proc = config.get("proc")
    if proc is None:
        return

    log_master(f"Desactivando {name} (PID: {proc.pid})...")
    try:
        process_group = os.getpgid(proc.pid)
        os.killpg(process_group, signal.SIGTERM)
        proc.wait(timeout=SHUTDOWN_TIMEOUT)
    except ProcessLookupError:
        log_master(f"{name} ya estaba detenido.")
    except PermissionError as exc:
        log_master(f"No se pudo detener {name}: {exc}")
    except subprocess.TimeoutExpired:
        log_master(f"{name} no respondió a SIGTERM; forzando cierre.")
        try:
            os.killpg(process_group, signal.SIGKILL)
            proc.wait(timeout=SHUTDOWN_TIMEOUT)
        except ProcessLookupError:
            pass
        except PermissionError as exc:
            log_master(f"No se pudo forzar el cierre de {name}: {exc}")
        except subprocess.TimeoutExpired:
            log_master(f"{name} sigue activo después de SIGKILL.")
    finally:
        config["proc"] = None


def signal_handler(sig, frame):
    log_master("Apagado de Infraestructura solicitado. Resguardando dominios...")
    for name, config in reversed(enabled_process_items(ACTIVE_PROCESSES)):
        kill_process(name, config)
    sys.exit(0)


def schedule_restart(name, config, now):
    attempts = config.get("restart_attempts", 0) + 1
    delay = min(RESTART_BACKOFF_INITIAL, RESTART_BACKOFF_MAX)
    for _ in range(attempts - 1):
        delay = min(delay * 2, RESTART_BACKOFF_MAX)
        if delay >= RESTART_BACKOFF_MAX:
            break
    config["restart_attempts"] = attempts
    config["restart_at"] = now + delay
    log_master(f"{name} se reintentará en {delay:g}s (intento {attempts}).")


def monitor_once(processes, now=None):
    now = time.monotonic() if now is None else now
    for name, config in enabled_process_items(processes):
        proc = config.get("proc")
        if proc is not None and proc.poll() is None:
            started_at = config.get("started_at", now)
            if config.get("restart_attempts", 0) and now - started_at >= RESTART_STABLE_AFTER:
                config["restart_attempts"] = 0
            continue

        if proc is not None:
            config["proc"] = None
            schedule_restart(name, config, now)
            continue

        restart_at = config.get("restart_at", 0.0)
        if restart_at == 0.0:
            schedule_restart(name, config, now)
            continue
        if now < restart_at:
            continue

        log_master(f"Alerta: Dominio {name} fuera de servicio. Restaurando...")
        if not start_process(name, config) and config.get("enabled", True):
            schedule_restart(name, config, now)


def monitor_processes(processes):
    while True:
        time.sleep(MONITOR_INTERVAL)
        monitor_once(processes)


def main():
    global ACTIVE_PROCESSES
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    ACTIVE_PROCESSES = runtime_processes(include_extended=env_flag("XARVIS_ENABLE_EXTENDED"))

    log_master("==== ORQUESTADOR DE INFRAESTRUCTURA DEL MUNDO INICIADO ====")

    # Despliegue Inicial
    for name, config in enabled_process_items(ACTIVE_PROCESSES):
        start_process(name, config)

    # Vigilancia Resiliente
    try:
        monitor_processes(ACTIVE_PROCESSES)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
