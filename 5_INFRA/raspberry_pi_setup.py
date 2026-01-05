#!/usr/bin/env python3
"""
🦅 Raspberry Pi Setup - Preparación de Arsenal Portátil
Dominio: 5_INFRA
Arquitecto: Iyari Cancino Gomez

Detecta, formatea y prepara microSD para Raspberry Pi con XarvisCore embebido.
El Rey ahora es portátil.
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

class RaspberryPiSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.log_file = self.base_dir / "5_INFRA/logs/raspberry_setup.log"
        
        # Módulos esenciales para Raspberry Pi
        self.essential_modules = [
            "3_POWER/xarvis_full_power.py",
            "3_POWER/ram_guardian.py",
            "3_POWER/network_priority_manager.py",
            "10_CULTURAL_RENAISSANCE/music_library.json",
            "10_CULTURAL_RENAISSANCE/audio_fingerprints.json",
            "10_CULTURAL_RENAISSANCE/audio_detector.py",
            "10_CULTURAL_RENAISSANCE/suno_autopipeline.py",
        ]
        
    def log(self, msg, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    
    def detect_sd_card(self):
        """Detecta microSD conectada"""
        self.log("🔍 Buscando microSD...")
        
        try:
            # Listar todos los discos
            result = subprocess.run(
                ['diskutil', 'list'],
                capture_output=True,
                text=True
            )
            
            # Buscar discos externos (normalmente /dev/disk2, /dev/disk3, etc.)
            lines = result.stdout.split('\n')
            sd_candidates = []
            
            current_disk = None
            for line in lines:
                if '/dev/disk' in line:
                    current_disk = line.split()[0]
                if current_disk and ('external' in line.lower() or 'sd' in line.lower()):
                    if current_disk not in sd_candidates:
                        sd_candidates.append(current_disk)
            
            if not sd_candidates:
                self.log("❌ No se detectó microSD", "ERROR")
                return None
            
            # Obtener info detallada de cada candidato
            for disk in sd_candidates:
                result = subprocess.run(
                    ['diskutil', 'info', disk],
                    capture_output=True,
                    text=True
                )
                
                info = result.stdout
                if 'Removable Media' in info or 'SD' in info:
                    size = self._extract_size(info)
                    self.log(f"✅ MicroSD detectada: {disk} ({size})")
                    return disk
            
            return None
            
        except Exception as e:
            self.log(f"❌ Error detectando microSD: {e}", "ERROR")
            return None
    
    def _extract_size(self, info_text):
        """Extrae el tamaño del disco de la info"""
        for line in info_text.split('\n'):
            if 'Disk Size' in line or 'Total Size' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    return parts[1].strip().split('(')[0].strip()
        return "Desconocido"
    
    def format_sd_card(self, disk, label="XARVIS_PI"):
        """
        Formatea la microSD con el sistema de archivos apropiado
        
        Args:
            disk: Dispositivo (ej: /dev/disk2)
            label: Etiqueta del volumen
        """
        self.log(f"⚠️  ADVERTENCIA: Esto borrará TODO en {disk}")
        self.log(f"📋 Etiqueta: {label}")
        
        confirm = input("\n¿Continuar con el formateo? (SI/no): ")
        if confirm.lower() not in ['si', 's', 'yes', 'y']:
            self.log("❌ Formateo cancelado por usuario")
            return False
        
        try:
            # Desmontar el disco primero
            self.log(f"📤 Desmontando {disk}...")
            subprocess.run(['diskutil', 'unmountDisk', disk], check=True)
            
            # Formatear como FAT32 (exFAT para >32GB)
            self.log(f"🔧 Formateando como FAT32/exFAT...")
            
            # Determinar formato según tamaño
            info_result = subprocess.run(
                ['diskutil', 'info', disk],
                capture_output=True,
                text=True
            )
            
            # Si es mayor a 32GB, usar exFAT, sino FAT32
            use_exfat = 'GB' in info_result.stdout and \
                       any(int(s) > 32 for s in info_result.stdout.split() if s.isdigit())
            
            format_type = 'ExFAT' if use_exfat else 'MS-DOS FAT32'
            
            result = subprocess.run(
                ['diskutil', 'eraseDisk', format_type, label, disk],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.log(f"✅ MicroSD formateada exitosamente")
            self.log(f"📋 Formato: {format_type}")
            self.log(f"📁 Etiqueta: {label}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error formateando: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Error inesperado: {e}", "ERROR")
            return False
    
    def get_mount_point(self, label="XARVIS_PI"):
        """Obtiene el punto de montaje de la SD"""
        mount_path = Path(f"/Volumes/{label}")
        if mount_path.exists():
            return mount_path
        return None
    
    def create_raspberry_structure(self, mount_point):
        """Crea estructura de carpetas para Raspberry Pi"""
        self.log(f"📁 Creando estructura en {mount_point}...")
        
        folders = [
            "xarvis_core",
            "xarvis_core/modules",
            "xarvis_core/config",
            "xarvis_core/logs",
            "xarvis_core/data",
            "music_library",
            "scripts",
            "docs"
        ]
        
        for folder in folders:
            path = mount_point / folder
            path.mkdir(parents=True, exist_ok=True)
            self.log(f"  ✅ {folder}/")
        
        return True
    
    def copy_essential_modules(self, mount_point):
        """Copia módulos esenciales de XarvisCore"""
        self.log(f"📦 Copiando módulos esenciales...")
        
        dest_modules = mount_point / "xarvis_core/modules"
        
        for module in self.essential_modules:
            src = self.base_dir / module
            if src.exists():
                dest = dest_modules / src.name
                
                try:
                    if src.is_file():
                        import shutil
                        shutil.copy2(src, dest)
                        self.log(f"  ✅ {module}")
                    else:
                        self.log(f"  ⏭️  {module} (directorio omitido)", "WARNING")
                except Exception as e:
                    self.log(f"  ❌ Error copiando {module}: {e}", "ERROR")
        
        return True
    
    def create_raspberry_installer(self, mount_point):
        """Crea script de instalación para Raspberry Pi"""
        self.log(f"📝 Creando instalador para Raspberry Pi...")
        
        installer_script = """#!/bin/bash
# 🦅 Xarvis Core - Raspberry Pi Installer
# Arquitecto: Iyari Cancino Gomez

echo "🦅 XarvisCore - Instalación para Raspberry Pi"
echo "=============================================="
echo ""

# Verificar que estamos en Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "❌ Este script debe ejecutarse en una Raspberry Pi"
    exit 1
fi

echo "✅ Raspberry Pi detectada"
echo ""

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
echo "📦 Instalando dependencias..."
sudo apt install -y python3 python3-pip python3-venv git htop

# Python packages
echo "🐍 Instalando paquetes Python..."
pip3 install flask flask-cors psutil

# Audio dependencies (para detector)
sudo apt install -y chromaprint-tools sox

# Crear directorio de instalación
INSTALL_DIR="$HOME/xarvis_core"
mkdir -p "$INSTALL_DIR"

# Copiar módulos desde SD
echo "📂 Copiando módulos..."
cp -r /mnt/usb/xarvis_core/modules/* "$INSTALL_DIR/"
cp -r /mnt/usb/music_library "$HOME/"

# Crear entorno virtual
echo "🔧 Creando entorno virtual..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Instalar requirements
pip install flask flask-cors psutil

echo ""
echo "✅ Instalación completada"
echo ""
echo "Para iniciar Xarvis:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python3 xarvis_full_power.py"
echo ""
"""
        
        installer_path = mount_point / "scripts/install_on_raspberry.sh"
        with open(installer_path, 'w', encoding='utf-8') as f:
            f.write(installer_script)
        
        # Hacer ejecutable
        os.chmod(installer_path, 0o755)
        
        self.log(f"  ✅ Instalador creado")
        return True
    
    def create_readme(self, mount_point):
        """Crea README con instrucciones"""
        self.log(f"📝 Creando documentación...")
        
        readme_content = f"""# 🦅 XarvisCore - Arsenal Portátil para Raspberry Pi

**Arquitecto**: Iyari Cancino Gomez
**Fecha**: {datetime.now().strftime('%d de %B, %Y')}

## 📋 Contenido de esta microSD

- **xarvis_core/**: Módulos esenciales del sistema
- **music_library/**: Biblioteca musical completa
- **scripts/**: Scripts de instalación y configuración
- **docs/**: Documentación

## 🚀 Instalación en Raspberry Pi

### Requisitos:
- Raspberry Pi 3B+ o superior
- Raspberry Pi OS (Bullseye o Bookworm)
- Conexión a Internet

### Pasos:

1. **Inserta esta microSD en tu Raspberry Pi**

2. **Monta la SD** (si no se monta automáticamente):
   ```bash
   sudo mount /dev/sda1 /mnt/usb
   ```

3. **Ejecuta el instalador**:
   ```bash
   cd /mnt/usb/scripts
   bash install_on_raspberry.sh
   ```

4. **Inicia Xarvis**:
   ```bash
   cd ~/xarvis_core
   source venv/bin/activate
   python3 xarvis_full_power.py
   ```

## 🎯 Módulos Disponibles

### 1. Full Power Monitor
- Monitoreo de sistema (CPU, RAM, disco)
- API REST en puerto 8080
- Dashboard en tiempo real

### 2. RAM Guardian
- Protección de memoria
- Liberación automática
- Umbrales inteligentes

### 3. Network Priority Manager
- Optimización de red
- Priorización de tráfico
- QoS automático

### 4. Audio Detector
- Detección de canciones por fingerprint
- Biblioteca musical de 550+ tracks
- Funciona offline

### 5. Suno AutoPipeline
- Procesamiento automático de música
- Extracción de letras
- Organización inteligente

## 🔧 Configuración

### WiFi
Configura tu red WiFi:
```bash
sudo raspi-config
# System Options → Wireless LAN
```

### Auto-inicio
Para que Xarvis arranque con el sistema:
```bash
crontab -e
# Agregar:
@reboot cd $HOME/xarvis_core && source venv/bin/activate && python3 xarvis_full_power.py &
```

## 📊 Acceso Remoto

Una vez iniciado, accede desde tu Mac:
```
http://[IP_DE_TU_RASPBERRY]:8080
```

Para encontrar la IP de tu Raspberry:
```bash
hostname -I
```

## 🎵 Biblioteca Musical

La biblioteca completa está en `~/music_library/`:
- 550+ canciones indexadas
- Fingerprints acústicos
- Metadata completa

## 🦅 El Reino es Portátil

Este sistema convierte tu Raspberry Pi en un nodo soberano de XarvisCore.
Monitoreo, música, análisis y poder de procesamiento en tu mano.

**"El Rey no necesita trono. Solo necesita código."**

---
*Sistema XarvisCore - El Arsenal Nunca Descansa*
"""
        
        readme_path = mount_point / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.log(f"  ✅ README.md creado")
        return True
    
    def create_config_file(self, mount_point):
        """Crea archivo de configuración"""
        config = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "platform": "raspberry_pi",
            "modules": {
                "full_power": {
                    "enabled": True,
                    "port": 8080
                },
                "ram_guardian": {
                    "enabled": True,
                    "check_interval": 10
                },
                "audio_detector": {
                    "enabled": True,
                    "library_path": "~/music_library"
                }
            }
        }
        
        config_path = mount_point / "xarvis_core/config/raspberry_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        self.log(f"  ✅ Configuración creada")
        return True
    
    def run_full_setup(self):
        """Ejecuta el setup completo"""
        self.log("\n" + "="*60)
        self.log("🦅 RASPBERRY PI SETUP - ARSENAL PORTÁTIL")
        self.log("="*60)
        
        # 1. Detectar microSD
        disk = self.detect_sd_card()
        if not disk:
            self.log("❌ No se pudo detectar microSD", "ERROR")
            return False
        
        # 2. Formatear
        if not self.format_sd_card(disk):
            return False
        
        # 3. Esperar que se monte
        self.log("⏳ Esperando que se monte la SD...")
        import time
        time.sleep(3)
        
        mount_point = self.get_mount_point()
        if not mount_point:
            self.log("❌ No se pudo montar la SD", "ERROR")
            return False
        
        # 4. Crear estructura
        self.create_raspberry_structure(mount_point)
        
        # 5. Copiar módulos
        self.copy_essential_modules(mount_point)
        
        # 6. Crear instalador
        self.create_raspberry_installer(mount_point)
        
        # 7. Crear README
        self.create_readme(mount_point)
        
        # 8. Crear config
        self.create_config_file(mount_point)
        
        # Resumen final
        self.log("\n" + "="*60)
        self.log("🎉 SETUP COMPLETADO")
        self.log("="*60)
        self.log(f"📁 MicroSD lista en: {mount_point}")
        self.log(f"📋 Revisa: {mount_point}/README.md")
        self.log("")
        self.log("🚀 Próximos pasos:")
        self.log("  1. Expulsa la microSD de forma segura")
        self.log("  2. Insértala en tu Raspberry Pi")
        self.log("  3. Ejecuta: bash /mnt/usb/scripts/install_on_raspberry.sh")
        self.log("  4. El Reino es tuyo, Rey")
        
        return True

def main():
    """Punto de entrada"""
    setup = RaspberryPiSetup()
    
    try:
        setup.run_full_setup()
    except KeyboardInterrupt:
        setup.log("\n⏹️  Setup interrumpido por usuario")
        sys.exit(1)
    except Exception as e:
        setup.log(f"\n❌ Error fatal: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
