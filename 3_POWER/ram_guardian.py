"""
RAM Guardian - Sistema de Gestión Automática de Memoria
Dominio: 3_POWER
Arquitecto: Iyari Cancino Gomez
"""

import psutil
import os
import signal
import time
import logging
import subprocess
from datetime import datetime
from collections import defaultdict

# === CONFIGURACIÓN ===
RAM_THRESHOLD_WARNING = 65  # % - Advertencia (más agresivo)
RAM_THRESHOLD_CRITICAL = 75  # % - Acción inmediata (más agresivo)
RAM_THRESHOLD_OPTIMAL = 50  # % - Objetivo óptimo
RAM_THRESHOLD_PURGE = 70  # % - Activar purge de memoria
CHECK_INTERVAL = 5  # segundos entre chequeos (más frecuente)
AGGRESSIVE_MODE = True  # Modo agresivo de limpieza

# Procesos protegidos (nunca cerrar)
PROTECTED_PROCESSES = {
    'xarvis_core.py',
    'xarvis_full_power.py',
    'xarvis_supervisor.py',
    'ram_guardian.py',
    'kernel_task',
    'launchd',
    'WindowServer',
    'loginwindow',
    'systemd',
    'System',
    'python3'  # Proteger procesos Python core
}

# Procesos de baja prioridad (candidatos a cierre)
LOW_PRIORITY_PATTERNS = [
    'Google Chrome Helper',
    'ChatGPT Atlas (Renderer)',
    'Code Helper (Renderer)',
    'Code Helper (Plugin)',
    'Spotify Helper',
    'slack',
    'discord',
    'Steam',
    'Epic',
    'firefox',
    'safari',
    'mail',
    'calendar',
    'Messages',
    'Photos',
    'Music'
]

# Configurar logging
LOG_FILE = "/Users/blackmamba/Desktop/XarvisCore/5_INFRA/logs/ram_guardian.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [RAM_GUARDIAN] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class RAMGuardian:
    """
    Guardian de RAM - Mantiene el sistema optimizado
    """
    
    def __init__(self):
        self.killed_processes = defaultdict(int)
        self.total_memory_freed = 0
        self.interventions = 0
        logging.info("🛡️ RAM Guardian iniciado")
        logging.info(f"Umbrales: Warning={RAM_THRESHOLD_WARNING}%, Critical={RAM_THRESHOLD_CRITICAL}%")
    
    def get_memory_stats(self):
        """Obtiene estadísticas de memoria"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent,
            'swap_percent': swap.percent,
            'status': self._get_status(mem.percent)
        }
    
    def _get_status(self, percent):
        """Determina el estado basado en el uso"""
        if percent < RAM_THRESHOLD_OPTIMAL:
            return "OPTIMAL"
        elif percent < RAM_THRESHOLD_WARNING:
            return "GOOD"
        elif percent < RAM_THRESHOLD_CRITICAL:
            return "WARNING"
        else:
            return "CRITICAL"
    
    def is_protected(self, proc_name):
        """Verifica si un proceso está protegido"""
        proc_name_lower = proc_name.lower()
        
        # Verificar procesos protegidos exactos
        for protected in PROTECTED_PROCESSES:
            if protected.lower() in proc_name_lower:
                return True
        
        return False
    
    def is_low_priority(self, proc_name):
        """Verifica si un proceso es de baja prioridad"""
        proc_name_lower = proc_name.lower()
        
        for pattern in LOW_PRIORITY_PATTERNS:
            if pattern.lower() in proc_name_lower:
                return True
        
        return False
    
    def get_memory_hogs(self, limit=20):
        """Obtiene procesos que consumen más memoria"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
            try:
                info = proc.info
                if info['memory_percent'] and info['memory_percent'] > 0.1:  # Más de 0.1%
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'memory_percent': round(info['memory_percent'], 2),
                        'memory_mb': round(info['memory_info'].rss / (1024**2), 2),
                        'protected': self.is_protected(info['name']),
                        'low_priority': self.is_low_priority(info['name'])
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordenar por uso de memoria descendente
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        return processes[:limit]
    
    def kill_process(self, pid, name):
        """Intenta cerrar un proceso de forma segura"""
        try:
            proc = psutil.Process(pid)
            
            # Intentar cierre graceful primero
            proc.terminate()
            
            # Esperar 3 segundos
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                # Si no responde, forzar
                proc.kill()
            
            self.killed_processes[name] += 1
            logging.info(f"✂️ Proceso cerrado: {name} (PID: {pid})")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.warning(f"No se pudo cerrar {name} (PID: {pid}): {e}")
            return False
    
    def purge_memory_cache(self):
        """Ejecuta purge para limpiar caché de memoria del sistema"""
        try:
            logging.info("🧹 Ejecutando purge del sistema...")
            result = subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
            if result.returncode == 0:
                logging.info("✅ Purge completado - Caché limpiado")
                return True
            else:
                logging.warning("⚠️ Purge requiere permisos sudo")
                return False
        except Exception as e:
            logging.error(f"❌ Error en purge: {e}")
            return False
    
    def kill_duplicate_renderers(self):
        """Cierra procesos duplicados de renderers (ChatGPT, VSCode, etc)"""
        renderers = defaultdict(list)
        
        # Agrupar renderers por tipo
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                name = proc.info['name']
                if 'Renderer' in name or 'Helper' in name:
                    base_name = name.split('(')[0].strip()
                    renderers[base_name].append({
                        'pid': proc.info['pid'],
                        'name': name,
                        'mem': proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        killed = 0
        # Si hay más de 3 del mismo tipo, cerrar los que menos memoria usan
        for base_name, procs in renderers.items():
            if len(procs) > 3:
                # Ordenar por uso de memoria (menor a mayor)
                procs.sort(key=lambda x: x['mem'])
                # Cerrar los menos usados (dejar solo 3)
                for proc in procs[:-3]:
                    if self.kill_process(proc['pid'], proc['name']):
                        killed += 1
                        self.total_memory_freed += proc['mem'] * psutil.virtual_memory().total / 100 / (1024**2)
        
        if killed > 0:
            logging.info(f"✂️ Cerrados {killed} procesos helper duplicados")
        
        return killed
    
    def free_memory(self, target_percent=RAM_THRESHOLD_OPTIMAL):
        """Libera memoria hasta alcanzar el objetivo"""
        mem_before = psutil.virtual_memory().percent
        logging.warning(f"⚠️ LIBERANDO MEMORIA: {mem_before}% → objetivo {target_percent}%")
        
        # Paso 1: Cerrar helpers/renderers duplicados primero
        self.kill_duplicate_renderers()
        time.sleep(1)
        
        # Paso 2: Cerrar procesos de baja prioridad si es necesario
        current_mem = psutil.virtual_memory().percent
        if current_mem > target_percent:
            processes = self.get_memory_hogs(limit=50)
            freed_count = 0
            
            for proc in processes:
                # Verificar si ya alcanzamos el objetivo
                current_mem = psutil.virtual_memory().percent
                if current_mem <= target_percent:
                    logging.info(f"✅ Objetivo alcanzado: {current_mem}%")
                    break
                
                # Solo cerrar procesos no protegidos de baja prioridad
                if not proc['protected'] and proc['low_priority']:
                    if self.kill_process(proc['pid'], proc['name']):
                        freed_count += 1
                        self.total_memory_freed += proc['memory_mb']
                        time.sleep(0.5)  # Pequeña pausa entre cierres
        
        # Paso 3: Purge si aún está alto
        current_mem = psutil.virtual_memory().percent
        if current_mem > RAM_THRESHOLD_PURGE:
            self.purge_memory_cache()
            time.sleep(2)
        
        mem_after = psutil.virtual_memory().percent
        mem_freed = mem_before - mem_after
        
        self.interventions += 1
        
        logging.info(f"🧹 Limpieza completada")
        logging.info(f"📊 Memoria: {mem_before}% → {mem_after}% (liberado: {mem_freed:.1f}%)")
        
        return {
            'memory_before': mem_before,
            'memory_after': mem_after,
            'memory_freed': mem_freed
        }
    
    def monitor_loop(self):
        """Loop principal de monitoreo"""
        logging.info("🔄 Iniciando monitoreo continuo de RAM")
        
        try:
            while True:
                stats = self.get_memory_stats()
                status = stats['status']
                percent = stats['percent']
                
                # Log periódico cada minuto (6 ciclos de 10 segundos)
                if int(time.time()) % 60 < CHECK_INTERVAL:
                    logging.info(
                        f"📊 RAM: {percent}% | "
                        f"Usado: {stats['used_gb']}GB / {stats['total_gb']}GB | "
                        f"Estado: {status}"
                    )
                
                # Acción según el estado
                if status == "CRITICAL":
                    logging.warning(f"🚨 CRÍTICO: {percent}% - Iniciando liberación agresiva")
                    self.free_memory(target_percent=RAM_THRESHOLD_OPTIMAL)
                    
                elif status == "WARNING":
                    logging.warning(f"⚠️ ADVERTENCIA: {percent}% - Liberación preventiva")
                    self.free_memory(target_percent=RAM_THRESHOLD_WARNING - 10)
                
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logging.info("⏹️ Deteniendo RAM Guardian")
            self.print_stats()
    
    def print_stats(self):
        """Imprime estadísticas del guardian"""
        logging.info("=" * 50)
        logging.info("📈 ESTADÍSTICAS DE RAM GUARDIAN")
        logging.info("=" * 50)
        logging.info(f"Intervenciones totales: {self.interventions}")
        logging.info(f"Memoria total liberada: {self.total_memory_freed:.2f} MB")
        logging.info("Procesos cerrados:")
        for proc_name, count in sorted(self.killed_processes.items(), key=lambda x: x[1], reverse=True):
            logging.info(f"  - {proc_name}: {count} veces")
        logging.info("=" * 50)

def run_guardian():
    """Función principal para ejecutar el guardian"""
    guardian = RAMGuardian()
    guardian.monitor_loop()

if __name__ == "__main__":
    run_guardian()
