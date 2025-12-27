#!/usr/bin/env python3
"""
🐍 MAMBA GUARDIAN - Sistema de Monitoreo y Protección
Mata procesos automáticamente cuando consumen demasiados recursos
"""

import subprocess
import time
import os
import signal
import json
from datetime import datetime
from pathlib import Path
import re

# Configuración - MODO AGRESIVO 🔥
CONFIG = {
    "cpu_threshold": 70.0,  # % CPU para matar proceso (antes: 90%)
    "memory_threshold": 60.0,  # % RAM para matar proceso (antes: 80%)
    "check_interval": 3,  # Segundos entre checks (antes: 5)
    "grace_period": 5,  # Segundos antes de matar (antes: 10)
    "protected_processes": [  # NUNCA matar estos
        "kernel_task",
        "launchd",
        "WindowServer",
        "loginwindow",
        "Finder",
        "Dock",
        "SystemUIServer",
        "coreaudiod",
        "mds",
        "mds_stores",
        "spotlight",
        "Terminal",
        "iTerm2",
        "Code",
        "code",
        "Cursor",
        "cursor",
    ],
    "log_file": Path(__file__).parent / "guardian.log",
    "kills_file": Path(__file__).parent / "kills.json",
}


class MambaGuardian:
    def __init__(self):
        self.warnings = {}  # Procesos en periodo de gracia
        self.kills = []  # Historial de kills
        self.load_kills()

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = {"INFO": "ℹ️", "WARN": "⚠️", "KILL": "💀", "OK": "✅"}.get(level, "📝")
        log_line = f"[{timestamp}] {emoji} {level}: {message}"
        print(log_line)
        with open(CONFIG["log_file"], "a") as f:
            f.write(log_line + "\n")

    def load_kills(self):
        if CONFIG["kills_file"].exists():
            try:
                with open(CONFIG["kills_file"]) as f:
                    self.kills = json.load(f)
            except:
                self.kills = []

    def save_kill(self, process_info):
        self.kills.append({"timestamp": datetime.now().isoformat(), **process_info})
        # Mantener solo últimos 100
        self.kills = self.kills[-100:]
        with open(CONFIG["kills_file"], "w") as f:
            json.dump(self.kills, f, indent=2)

    def get_top_processes(self):
        """Obtener procesos ordenados por CPU y memoria"""
        try:
            # Usar ps para obtener procesos con CPU y memoria
            cmd = "ps aux | sort -k3 -nr | head -20"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            processes = []
            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 11:
                    try:
                        processes.append(
                            {
                                "user": parts[0],
                                "pid": int(parts[1]),
                                "cpu": float(parts[2]),
                                "mem": float(parts[3]),
                                "name": parts[10] if len(parts) > 10 else "unknown",
                            }
                        )
                    except (ValueError, IndexError):
                        continue
            return processes
        except Exception as e:
            self.log(f"Error obteniendo procesos: {e}", "WARN")
            return []

    def get_system_stats(self):
        """Obtener estadísticas del sistema"""
        try:
            # CPU usage
            cpu_cmd = "top -l 1 -n 0 | grep 'CPU usage'"
            cpu_result = subprocess.run(
                cpu_cmd, shell=True, capture_output=True, text=True
            )
            cpu_match = re.search(
                r"(\d+\.\d+)% user.*?(\d+\.\d+)% sys", cpu_result.stdout
            )
            cpu_total = 0
            if cpu_match:
                cpu_total = float(cpu_match.group(1)) + float(cpu_match.group(2))

            # Memory usage
            mem_cmd = "vm_stat | head -5"
            mem_result = subprocess.run(
                mem_cmd, shell=True, capture_output=True, text=True
            )

            # Disk usage
            disk_cmd = "df -h / | tail -1"
            disk_result = subprocess.run(
                disk_cmd, shell=True, capture_output=True, text=True
            )
            disk_parts = disk_result.stdout.split()
            disk_used = disk_parts[4] if len(disk_parts) > 4 else "?"

            return {"cpu_total": cpu_total, "disk_used": disk_used}
        except Exception as e:
            return {"cpu_total": 0, "disk_used": "?"}

    def is_protected(self, process_name):
        """Verificar si el proceso está protegido"""
        name_lower = process_name.lower()
        for protected in CONFIG["protected_processes"]:
            if protected.lower() in name_lower:
                return True
        return False

    def kill_process(self, pid, name, reason):
        """Matar un proceso"""
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            # Si sigue vivo, SIGKILL
            try:
                os.kill(pid, 0)  # Check if still alive
                os.kill(pid, signal.SIGKILL)
                self.log(f"SIGKILL enviado a {name} (PID {pid})", "KILL")
            except OSError:
                pass  # Ya murió

            self.log(f"Proceso terminado: {name} (PID {pid}) - Razón: {reason}", "KILL")
            self.save_kill({"pid": pid, "name": name, "reason": reason})
            return True
        except PermissionError:
            self.log(f"Sin permiso para matar {name} (PID {pid})", "WARN")
            return False
        except Exception as e:
            self.log(f"Error matando {name}: {e}", "WARN")
            return False

    def check_and_kill(self):
        """Revisar procesos y matar los problemáticos"""
        processes = self.get_top_processes()
        stats = self.get_system_stats()

        killed = 0
        current_time = time.time()

        for proc in processes:
            pid = proc["pid"]
            name = proc["name"]
            cpu = proc["cpu"]
            mem = proc["mem"]

            # Skip protected
            if self.is_protected(name):
                continue

            # Determinar si es problemático
            is_cpu_hog = cpu > CONFIG["cpu_threshold"]
            is_mem_hog = mem > CONFIG["memory_threshold"]

            if is_cpu_hog or is_mem_hog:
                reason = f"CPU: {cpu}%" if is_cpu_hog else f"MEM: {mem}%"

                # Primera vez? Dar warning
                if pid not in self.warnings:
                    self.warnings[pid] = current_time
                    self.log(
                        f"⚠️ WARNING: {name} (PID {pid}) - {reason} - Grace period iniciado",
                        "WARN",
                    )
                    continue

                # Ya pasó el grace period?
                if current_time - self.warnings[pid] >= CONFIG["grace_period"]:
                    if self.kill_process(pid, name, reason):
                        killed += 1
                        del self.warnings[pid]
            else:
                # Ya no es problemático, quitar de warnings
                if pid in self.warnings:
                    del self.warnings[pid]

        # Limpiar warnings de procesos que ya no existen
        active_pids = {p["pid"] for p in processes}
        self.warnings = {k: v for k, v in self.warnings.items() if k in active_pids}

        return killed, stats

    def run(self):
        """Loop principal del guardian"""
        self.log("🐍 MAMBA GUARDIAN iniciado", "OK")
        self.log(f"CPU threshold: {CONFIG['cpu_threshold']}%", "INFO")
        self.log(f"MEM threshold: {CONFIG['memory_threshold']}%", "INFO")
        self.log(f"Grace period: {CONFIG['grace_period']}s", "INFO")

        try:
            while True:
                killed, stats = self.check_and_kill()

                # Status cada minuto
                if int(time.time()) % 60 < CONFIG["check_interval"]:
                    self.log(
                        f"Sistema: CPU {stats['cpu_total']:.1f}% | Disco: {stats['disk_used']} | Kills hoy: {len([k for k in self.kills if k['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))])}",
                        "INFO",
                    )

                time.sleep(CONFIG["check_interval"])

        except KeyboardInterrupt:
            self.log("🛑 Guardian detenido por usuario", "INFO")


def show_status():
    """Mostrar estado actual del sistema"""
    guardian = MambaGuardian()
    processes = guardian.get_top_processes()
    stats = guardian.get_system_stats()

    print("\n🐍 MAMBA GUARDIAN - Estado del Sistema")
    print("=" * 50)
    print(f"CPU Total: {stats['cpu_total']:.1f}%")
    print(f"Disco usado: {stats['disk_used']}")
    print("\n📊 Top 10 procesos por CPU:")
    print("-" * 50)
    print(f"{'PID':>8} {'CPU':>6} {'MEM':>6}  {'Proceso':<30}")
    print("-" * 50)

    for proc in processes[:10]:
        protected = "🛡️" if guardian.is_protected(proc["name"]) else ""
        warning = (
            "⚠️"
            if proc["cpu"] > CONFIG["cpu_threshold"]
            or proc["mem"] > CONFIG["memory_threshold"]
            else ""
        )
        print(
            f"{proc['pid']:>8} {proc['cpu']:>5.1f}% {proc['mem']:>5.1f}%  {proc['name'][:28]:<28} {protected}{warning}"
        )

    print("\n💀 Últimos 5 kills:")
    print("-" * 50)
    for kill in guardian.kills[-5:]:
        print(f"  {kill['timestamp']}: {kill['name']} - {kill['reason']}")

    if not guardian.kills:
        print("  (ninguno)")


def main():
    import sys

    print("""
🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍
   MAMBA GUARDIAN - Protector del Sistema
🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍
    """)

    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            show_status()
        elif sys.argv[1] == "daemon":
            guardian = MambaGuardian()
            guardian.run()
        elif sys.argv[1] == "config":
            print("\n⚙️ Configuración actual:")
            for key, value in CONFIG.items():
                if not isinstance(value, (list, Path)):
                    print(f"  {key}: {value}")
            print(f"\n🛡️ Procesos protegidos: {len(CONFIG['protected_processes'])}")
        else:
            print("Uso: python mamba_guardian.py [status|daemon|config]")
    else:
        print("Opciones:")
        print("  status  - Ver estado del sistema")
        print("  daemon  - Iniciar monitoreo continuo")
        print("  config  - Ver configuración")
        print("\nEjemplo: python mamba_guardian.py daemon")


if __name__ == "__main__":
    main()
