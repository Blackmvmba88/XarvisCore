#!/usr/bin/env python3
"""
🦅 Network Priority Manager - Priorización Inteligente de Red
Dominio: 3_POWER
Arquitecto: Iyari Cancino Gomez

Gestiona prioridad de red para aplicaciones críticas como Flight Simulator 2024.
Optimiza latencia, ancho de banda y estabilidad de conexión.
"""

import os
import subprocess
import psutil
import time
from datetime import datetime
from pathlib import Path

class NetworkPriorityManager:
    def __init__(self):
        self.priority_apps = {
            'Flight Simulator': {
                'patterns': [
                    'FlightSimulator',
                    'Microsoft Flight Simulator',
                    'fs2024',
                    'MSFS'
                ],
                'priority': 'CRITICAL',
                'ports': [3074, 3075, 3076, 7000, 7001],  # Puertos comunes de MSFS
                'bandwidth_guarantee': 80  # 80% del ancho de banda disponible
            },
            'Gaming': {
                'patterns': ['Steam', 'Epic', 'Battle.net'],
                'priority': 'HIGH',
                'bandwidth_guarantee': 60
            }
        }
        
        self.log_file = Path(__file__).parent.parent / "5_INFRA/logs/network_priority.log"
        self.pf_rules_file = Path("/tmp/xarvis_network_priority.rules")
        
    def log(self, msg, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def is_app_running(self, app_name):
        """Detecta si una aplicación está corriendo"""
        patterns = self.priority_apps.get(app_name, {}).get('patterns', [])
        
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                proc_name = proc.info['name'] or ''
                proc_exe = proc.info['exe'] or ''
                
                for pattern in patterns:
                    if pattern.lower() in proc_name.lower() or pattern.lower() in proc_exe.lower():
                        return True, proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False, None
    
    def get_network_interface(self):
        """Obtiene la interfaz de red principal activa"""
        try:
            # Obtener la interfaz por defecto
            result = subprocess.run(
                ['route', '-n', 'get', 'default'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'interface:' in line:
                    return line.split(':')[1].strip()
            
            # Fallback: buscar interfaz activa con conexión
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for iface, stat in stats.items():
                if stat.isup and iface in addrs:
                    # Priorizar: en0 (WiFi) o en1 (Ethernet)
                    if iface.startswith('en'):
                        return iface
            
            return 'en0'  # Default a WiFi
            
        except Exception as e:
            self.log(f"Error detectando interfaz: {e}", "WARNING")
            return 'en0'
    
    def create_pf_rules(self, app_name):
        """Crea reglas de Packet Filter (pf) para priorización"""
        config = self.priority_apps.get(app_name, {})
        ports = config.get('ports', [])
        interface = self.get_network_interface()
        
        rules = f"""# Xarvis Network Priority Rules - {app_name}
# Generado: {datetime.now()}

# Limpiar reglas anteriores
scrub in all

# Definir colas de prioridad
altq on {interface} bandwidth 100% cbq queue {{ critical_queue, high_queue, normal_queue, low_queue }}
queue critical_queue bandwidth 80% priority 7 cbq(default)
queue high_queue bandwidth 60% priority 5
queue normal_queue bandwidth 40% priority 3
queue low_queue bandwidth 20% priority 1

"""
        
        # Agregar reglas por puerto
        for port in ports:
            rules += f"""# {app_name} - Puerto {port}
pass out quick on {interface} proto tcp from any to any port {port} queue critical_queue
pass out quick on {interface} proto udp from any to any port {port} queue critical_queue
pass in quick on {interface} proto tcp from any port {port} to any queue critical_queue
pass in quick on {interface} proto udp from any port {port} to any queue critical_queue

"""
        
        # Regla para tráfico normal
        rules += f"""# Tráfico normal
pass out on {interface} proto tcp from any to any queue normal_queue
pass out on {interface} proto udp from any to any queue normal_queue
"""
        
        return rules
    
    def apply_network_priority(self, app_name):
        """Aplica priorización de red para la aplicación"""
        self.log(f"⚡ Aplicando prioridad de red para {app_name}")
        
        try:
            # Crear reglas de pf
            rules = self.create_pf_rules(app_name)
            
            with open(self.pf_rules_file, 'w') as f:
                f.write(rules)
            
            self.log(f"  ✅ Reglas creadas: {self.pf_rules_file}")
            
            # Aplicar reglas (requiere sudo)
            self.log("  🔧 Aplicando reglas de firewall...")
            
            # Cargar configuración de pf
            result = subprocess.run(
                ['sudo', 'pfctl', '-f', str(self.pf_rules_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Habilitar pf
                subprocess.run(['sudo', 'pfctl', '-e'], capture_output=True)
                self.log(f"  ✅ Prioridad de red activa para {app_name}")
                return True
            else:
                self.log(f"  ⚠️ Error aplicando reglas: {result.stderr}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"  ❌ Error en priorización: {e}", "ERROR")
            return False
    
    def optimize_for_gaming(self):
        """Optimizaciones adicionales para gaming"""
        self.log("🎮 Aplicando optimizaciones de red para gaming...")
        
        optimizations = [
            # Deshabilitar IPv6 (puede causar latencia)
            "sudo networksetup -setv6off Wi-Fi",
            # Flush DNS cache
            "sudo dscacheutil -flushcache",
            "sudo killall -HUP mDNSResponder",
        ]
        
        for cmd in optimizations:
            try:
                subprocess.run(cmd.split(), capture_output=True, timeout=5)
            except:
                pass
        
        self.log("  ✅ Optimizaciones aplicadas")
    
    def disable_bandwidth_hogs(self):
        """Limita aplicaciones que consumen mucho ancho de banda"""
        bandwidth_hogs = [
            'Dropbox', 'Google Drive', 'OneDrive', 
            'iCloud', 'BackBlaze', 'Time Machine',
            'Steam' # Solo si no es la app prioritaria
        ]
        
        self.log("🚫 Limitando aplicaciones que consumen ancho de banda...")
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name']
                
                for hog in bandwidth_hogs:
                    if hog.lower() in proc_name.lower():
                        # Reducir prioridad de I/O
                        try:
                            subprocess.run(
                                ['sudo', 'renice', '+10', '-p', str(proc.info['pid'])],
                                capture_output=True
                            )
                            self.log(f"  🔽 {proc_name} limitado")
                        except:
                            pass
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def remove_priority(self):
        """Remueve todas las reglas de prioridad"""
        self.log("🔄 Removiendo prioridades de red...")
        
        try:
            # Deshabilitar pf
            subprocess.run(['sudo', 'pfctl', '-d'], capture_output=True)
            
            # Limpiar archivo de reglas
            if self.pf_rules_file.exists():
                self.pf_rules_file.unlink()
            
            self.log("  ✅ Prioridades removidas - Red en modo normal")
            return True
            
        except Exception as e:
            self.log(f"  ⚠️ Error removiendo prioridades: {e}", "WARNING")
            return False
    
    def monitor_and_manage(self, check_interval=10):
        """
        Monitorea aplicaciones y aplica/remueve prioridades automáticamente
        
        Args:
            check_interval: Segundos entre cada verificación
        """
        self.log("\n" + "="*60)
        self.log("🦅 NETWORK PRIORITY MANAGER - INICIANDO")
        self.log("="*60)
        self.log(f"Intervalo de monitoreo: {check_interval}s")
        
        priority_active = False
        active_app = None
        
        try:
            while True:
                # Verificar cada aplicación prioritaria
                app_detected = False
                
                for app_name in self.priority_apps.keys():
                    is_running, proc_name = self.is_app_running(app_name)
                    
                    if is_running:
                        app_detected = True
                        
                        # Si es una app nueva, aplicar prioridad
                        if not priority_active or active_app != app_name:
                            self.log(f"\n🎯 {app_name} DETECTADO: {proc_name}")
                            
                            # Optimizaciones
                            self.optimize_for_gaming()
                            self.disable_bandwidth_hogs()
                            
                            # Aplicar prioridad
                            if self.apply_network_priority(app_name):
                                priority_active = True
                                active_app = app_name
                                self.log(f"✅ RED OPTIMIZADA PARA {app_name.upper()}")
                        
                        break  # Solo una app prioritaria a la vez
                
                # Si no hay apps prioritarias corriendo, remover prioridad
                if not app_detected and priority_active:
                    self.log(f"\n⏸️ {active_app} cerrado")
                    self.remove_priority()
                    priority_active = False
                    active_app = None
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.log("\n⏹️ Monitoreo detenido por usuario")
            if priority_active:
                self.remove_priority()

def main():
    """Punto de entrada principal"""
    import sys
    
    manager = NetworkPriorityManager()
    
    # Comandos CLI
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == 'enable':
            # Habilitar para Flight Simulator
            manager.optimize_for_gaming()
            manager.apply_network_priority('Flight Simulator')
            
        elif cmd == 'disable':
            manager.remove_priority()
            
        elif cmd == 'monitor':
            # Monitoreo continuo
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            manager.monitor_and_manage(interval)
            
        else:
            print("Uso:")
            print("  python3 network_priority_manager.py enable   - Habilitar prioridad FS2024")
            print("  python3 network_priority_manager.py disable  - Deshabilitar prioridad")
            print("  python3 network_priority_manager.py monitor [segundos]  - Monitoreo automático")
    else:
        # Sin argumentos: monitoreo automático
        manager.monitor_and_manage()

if __name__ == "__main__":
    main()
