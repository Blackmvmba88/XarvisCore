#!/usr/bin/env python3
"""
🦅 Deep RAM Cleaner - Limpiador Profundo de Memoria
Dominio: 3_POWER
Arquitecto: Iyari Cancino Gomez

Sistema agresivo de limpieza que deja la Mac "como nueva".
Libera memoria comprimida, cierra procesos innecesarios y optimiza el sistema.
"""

import psutil
import subprocess
import time
import os
from datetime import datetime
from collections import defaultdict

class DeepRAMCleaner:
    def __init__(self):
        self.log_file = "/Users/blackmamba/Desktop/XarvisCore/5_INFRA/logs/deep_ram_cleaner.log"
        
        # Procesos críticos que NUNCA se tocan
        self.critical_processes = {
            'kernel_task', 'launchd', 'WindowServer', 'loginwindow',
            'systemd', 'System', 'Finder', 'Dock', 'SystemUIServer',
            'xarvis_core.py', 'xarvis_full_power.py', 'xarvis_supervisor.py',
            'ram_guardian.py', 'deep_ram_cleaner.py'
        }
        
        # Apps que se pueden cerrar completamente
        self.closeable_apps = [
            'Spotify', 'Slack', 'Discord', 'Steam', 'Epic Games',
            'Mail', 'Calendar', 'Messages', 'Photos', 'Music',
            'Safari', 'Firefox', 'News', 'Stocks', 'Weather'
        ]
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def get_memory_stats(self):
        """Obtiene estadísticas detalladas de memoria"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Obtener info de compresión vía vm_stat
        try:
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            vm_lines = result.stdout.split('\n')
            
            compressed = 0
            compressor = 0
            
            for line in vm_lines:
                if 'stored in compressor' in line.lower():
                    compressed = int(line.split(':')[1].strip().replace('.', ''))
                elif 'occupied by compressor' in line.lower():
                    compressor = int(line.split(':')[1].strip().replace('.', ''))
            
            # Convertir páginas a MB (página = 4096 bytes)
            compressed_mb = (compressed * 4096) / (1024**2)
            compressor_mb = (compressor * 4096) / (1024**2)
            
        except:
            compressed_mb = 0
            compressor_mb = 0
        
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent,
            'compressed_mb': round(compressed_mb, 2),
            'compressor_mb': round(compressor_mb, 2),
            'swap_percent': swap.percent
        }
    
    def kill_all_renderers_helpers(self):
        """Cierra todos los procesos Renderer y Helper"""
        killed = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                name = proc.info['name']
                
                # Identificar renderers y helpers
                if any(x in name for x in ['Renderer', 'Helper', 'Plugin']):
                    # Verificar que no sea proceso crítico
                    if not any(crit in name for crit in self.critical_processes):
                        try:
                            p = psutil.Process(proc.info['pid'])
                            p.terminate()
                            killed.append(name)
                            time.sleep(0.1)
                        except:
                            pass
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return killed
    
    def close_apps(self):
        """Cierra aplicaciones completas que pueden cerrarse"""
        closed = []
        
        for app in self.closeable_apps:
            try:
                # Usar AppleScript para cerrar apps gracefully
                script = f'tell application "{app}" to quit'
                subprocess.run(['osascript', '-e', script], 
                             capture_output=True, 
                             timeout=2)
                closed.append(app)
                self.log(f"  ✅ {app} cerrado")
            except:
                pass
        
        return closed
    
    def purge_system_cache(self):
        """Ejecuta purge para liberar caché del sistema"""
        self.log("🧹 Ejecutando purge del sistema...")
        
        try:
            # Verificar si tenemos permisos sudo
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  capture_output=True, 
                                  timeout=1)
            
            if result.returncode == 0:
                # Tenemos sudo sin password
                subprocess.run(['sudo', 'purge'], timeout=60)
                self.log("  ✅ Purge completado")
                return True
            else:
                self.log("  ⚠️ Purge requiere sudo (ejecuta manualmente si es necesario)", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"  ⚠️ Error en purge: {e}", "WARNING")
            return False
    
    def clear_dns_cache(self):
        """Limpia caché DNS"""
        try:
            subprocess.run(['sudo', 'dscacheutil', '-flushcache'], timeout=5)
            subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], timeout=5)
            self.log("  ✅ Caché DNS limpiado")
            return True
        except:
            return False
    
    def optimize_swap(self):
        """Intenta optimizar el uso de swap"""
        swap = psutil.swap_memory()
        
        if swap.percent > 10:
            self.log(f"  ⚠️ Swap alto: {swap.percent}%")
            # El purge ayuda a limpiar swap también
            return True
        else:
            self.log(f"  ✅ Swap normal: {swap.percent}%")
            return False
    
    def deep_clean(self):
        """Limpieza profunda completa"""
        self.log("\n" + "="*60)
        self.log("🦅 DEEP RAM CLEANER - INICIANDO LIMPIEZA PROFUNDA")
        self.log("="*60)
        
        # Estado inicial
        stats_before = self.get_memory_stats()
        self.log(f"📊 ANTES: {stats_before['percent']}% usado ({stats_before['used_gb']}GB / {stats_before['total_gb']}GB)")
        self.log(f"   Comprimido: {stats_before['compressed_mb']}MB")
        self.log(f"   Compresor: {stats_before['compressor_mb']}MB")
        self.log(f"   Swap: {stats_before['swap_percent']}%")
        
        # Paso 1: Cerrar renderers/helpers
        self.log("\n🔧 PASO 1: Cerrando procesos Renderer/Helper...")
        killed = self.kill_all_renderers_helpers()
        self.log(f"  ✂️ {len(killed)} procesos cerrados")
        time.sleep(2)
        
        # Paso 2: Cerrar apps innecesarias
        self.log("\n🔧 PASO 2: Cerrando aplicaciones...")
        closed = self.close_apps()
        self.log(f"  ✅ {len(closed)} aplicaciones cerradas")
        time.sleep(2)
        
        # Paso 3: Limpiar caché DNS
        self.log("\n🔧 PASO 3: Limpiando caché DNS...")
        self.clear_dns_cache()
        
        # Paso 4: Purge del sistema
        self.log("\n🔧 PASO 4: Ejecutando purge...")
        self.purge_system_cache()
        time.sleep(3)
        
        # Paso 5: Optimizar swap
        self.log("\n🔧 PASO 5: Verificando swap...")
        self.optimize_swap()
        
        # Estado final
        time.sleep(2)
        stats_after = self.get_memory_stats()
        
        self.log("\n" + "="*60)
        self.log("📊 RESULTADOS")
        self.log("="*60)
        self.log(f"ANTES:   {stats_before['percent']}% ({stats_before['used_gb']}GB)")
        self.log(f"DESPUÉS: {stats_after['percent']}% ({stats_after['used_gb']}GB)")
        self.log(f"LIBERADO: {stats_before['used_gb'] - stats_after['used_gb']:.2f}GB")
        self.log(f"")
        self.log(f"Compresión: {stats_before['compressed_mb']}MB → {stats_after['compressed_mb']}MB")
        self.log(f"Swap: {stats_before['swap_percent']}% → {stats_after['swap_percent']}%")
        self.log("="*60)
        self.log("✅ LIMPIEZA PROFUNDA COMPLETADA")
        self.log("="*60)
        
        return {
            'before': stats_before,
            'after': stats_after,
            'freed_gb': stats_before['used_gb'] - stats_after['used_gb']
        }

def main():
    """Punto de entrada principal"""
    import sys
    
    cleaner = DeepRAMCleaner()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # Modo automático (sin confirmación)
        cleaner.deep_clean()
    else:
        # Modo interactivo
        print("\n🦅 Deep RAM Cleaner - Limpieza Profunda de Memoria")
        print("="*60)
        print("⚠️  ADVERTENCIA: Esta limpieza cerrará:")
        print("   • Todos los procesos Renderer/Helper")
        print("   • Aplicaciones como Spotify, Slack, Discord, etc.")
        print("   • Ejecutará purge del sistema")
        print("")
        
        stats = cleaner.get_memory_stats()
        print(f"📊 Estado actual: {stats['percent']}% usado")
        print(f"   Memoria: {stats['used_gb']}GB / {stats['total_gb']}GB")
        print(f"   Comprimido: {stats['compressed_mb']}MB")
        print("")
        
        response = input("¿Continuar con la limpieza profunda? [s/N]: ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            cleaner.deep_clean()
        else:
            print("Limpieza cancelada")

if __name__ == "__main__":
    main()
