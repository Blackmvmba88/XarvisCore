#!/usr/bin/env python3
"""
🛡️ RASPBERRY GUARDIAN PROTOCOL
Arquitecto: Iyari Cancino Gomez
Filosofía: "La mejor defensa es distribuir la responsabilidad"

URGENCIA: Alta - Seguridad crítica del sistema
HARDWARE: Raspberry Pi 3/4/5
OBJETIVO: Nodo de seguridad separado del sistema principal

Este protocolo define la arquitectura de seguridad distribuida usando
Raspberry Pi como guardian físico independiente del Mac principal.
"""

import os
import json
import datetime
import subprocess
from pathlib import Path

class RaspberryGuardian:
    """
    Guardian de seguridad en Raspberry Pi.
    Separación física = mayor seguridad.
    """
    
    def __init__(self):
        self.philosophy = "Separar para proteger. Distribuir para sobrevivir."
        self.status = "Configuración urgente"
        self.hardware = "Raspberry Pi"
        self.capabilities = [
            "firewall",
            "vpn_server",
            "backup_automatico",
            "monitoring_24_7",
            "honeypot",
            "log_centralizado",
            "alerta_intrusion"
        ]
    
    def get_security_config(self):
        """Configuración de seguridad recomendada para Raspberry."""
        return {
            "nivel_1_firewall": {
                "herramienta": "UFW (Uncomplicated Firewall)",
                "reglas_basicas": [
                    "Bloquear todo por defecto",
                    "Permitir solo puertos esenciales (22, 80, 443, 5050, 8080)",
                    "Rate limiting en SSH (max 3 intentos/minuto)",
                    "Logging de todas las conexiones bloqueadas"
                ],
                "comandos_instalacion": [
                    "sudo apt update && sudo apt install ufw -y",
                    "sudo ufw default deny incoming",
                    "sudo ufw default allow outgoing",
                    "sudo ufw allow 22/tcp",  # SSH
                    "sudo ufw allow 5050/tcp",  # Xarvis Core
                    "sudo ufw allow 8080/tcp",  # Xarvis Power
                    "sudo ufw limit 22/tcp",  # Rate limit SSH
                    "sudo ufw enable"
                ]
            },
            
            "nivel_2_vpn": {
                "herramienta": "WireGuard (más rápido que OpenVPN)",
                "beneficio": "Todo el tráfico del Mac pasa por VPN de Raspberry",
                "ventaja": "IP pública = Raspberry, Mac principal oculto",
                "instalacion": [
                    "sudo apt install wireguard -y",
                    "wg genkey | tee privatekey | wg pubkey > publickey",
                    "# Configurar /etc/wireguard/wg0.conf"
                ]
            },
            
            "nivel_3_backup": {
                "estrategia": "Backups automáticos incrementales",
                "destino": "USB externo conectado a Raspberry",
                "frecuencia": "Cada 6 horas",
                "herramienta": "rsync + cron",
                "directorios_criticos": [
                    "/Users/blackmamba/Desktop/XarvisCore",
                    "/Users/blackmamba/Desktop/XarvisCore/1_CORE",
                    "/Users/blackmamba/Desktop/XarvisCore/12_SOVEREIGN_FINANCE",
                    "/Users/blackmamba/Desktop/XarvisCore/5_INFRA/logs"
                ],
                "script_ejemplo": """
#!/bin/bash
# Backup automático desde Mac a Raspberry
SOURCE_MAC="blackmamba@192.168.1.X:/Users/blackmamba/Desktop/XarvisCore"
DEST_RASP="/mnt/backups/xarvis/$(date +%Y%m%d_%H%M%S)"
rsync -avz --delete $SOURCE_MAC $DEST_RASP
find /mnt/backups/xarvis -mtime +7 -delete  # Borrar >7 días
"""
            },
            
            "nivel_4_monitoring": {
                "herramienta": "Netdata (dashboard tiempo real)",
                "metricas": [
                    "CPU, RAM, disco Raspberry",
                    "Tráfico red entrante/saliente",
                    "Intentos conexión bloqueados",
                    "Estado servicios críticos"
                ],
                "instalacion": "bash <(curl -Ss https://my-netdata.io/kickstart.sh)",
                "acceso": "http://raspberry-ip:19999"
            },
            
            "nivel_5_honeypot": {
                "concepto": "Servicio falso para atraer atacantes",
                "herramienta": "SSH Honeypot (Cowrie)",
                "puerto": "2222 (SSH falso)",
                "registro": "Log completo de comandos ejecutados por atacante",
                "alerta": "Notificación cuando alguien intenta entrar"
            },
            
            "nivel_6_logs": {
                "centralizacion": "Todos los logs en Raspberry",
                "desde": ["Mac principal", "Raspberry misma", "Xarvis Core", "Xarvis Power"],
                "herramienta": "rsyslog server",
                "almacenamiento": "30 días comprimidos",
                "ubicacion": "/var/log/centralized/"
            },
            
            "nivel_7_alertas": {
                "eventos_criticos": [
                    "Más de 5 intentos SSH fallidos",
                    "Uso CPU >90% por 5 minutos",
                    "Disco >85% lleno",
                    "Servicio Xarvis caído",
                    "Conexión desde IP desconocida"
                ],
                "notificacion": "Telegram Bot + Email",
                "script_alerta": "Python con requests"
            }
        }
    
    def get_setup_plan_urgente(self):
        """Plan de configuración urgente (24 horas)."""
        return {
            "fase_1_hardware": {
                "tiempo": "30 minutos",
                "tareas": [
                    "1. Conectar Raspberry a red (Ethernet preferido)",
                    "2. Conectar USB externo para backups (64GB mínimo)",
                    "3. Anotar IP de Raspberry: ip a | grep inet",
                    "4. Configurar IP estática en router"
                ]
            },
            
            "fase_2_sistema_base": {
                "tiempo": "1 hora",
                "tareas": [
                    "1. Actualizar sistema: sudo apt update && sudo apt upgrade -y",
                    "2. Instalar esenciales: sudo apt install -y vim git curl htop",
                    "3. Cambiar password: passwd",
                    "4. Configurar SSH keys desde Mac",
                    "5. Deshabilitar password SSH: sudo vim /etc/ssh/sshd_config"
                ]
            },
            
            "fase_3_firewall": {
                "tiempo": "30 minutos",
                "tareas": [
                    "1. Instalar UFW (ver comandos en config)",
                    "2. Configurar reglas básicas",
                    "3. Probar desde Mac: ssh raspberry-ip",
                    "4. Verificar: sudo ufw status verbose"
                ]
            },
            
            "fase_4_backups": {
                "tiempo": "1 hora",
                "tareas": [
                    "1. Montar USB: sudo mount /dev/sda1 /mnt/backups",
                    "2. Auto-mount: sudo vim /etc/fstab",
                    "3. Crear script backup (ver ejemplo)",
                    "4. Programar cron: crontab -e → 0 */6 * * * /home/pi/backup.sh",
                    "5. Probar manualmente: bash /home/pi/backup.sh"
                ]
            },
            
            "fase_5_monitoring": {
                "tiempo": "30 minutos",
                "tareas": [
                    "1. Instalar Netdata (comando en config)",
                    "2. Abrir puerto: sudo ufw allow 19999/tcp",
                    "3. Acceder desde Mac: http://raspberry-ip:19999",
                    "4. Configurar alertas básicas"
                ]
            },
            
            "fase_6_logs": {
                "tiempo": "45 minutos",
                "tareas": [
                    "1. Configurar rsyslog server en Raspberry",
                    "2. En Mac: enviar logs a Raspberry",
                    "3. Verificar recepción: tail -f /var/log/centralized/mac.log"
                ]
            },
            
            "fase_7_opcional_avanzado": {
                "tiempo": "2-4 horas",
                "tareas": [
                    "VPN WireGuard (si se necesita acceso remoto seguro)",
                    "Honeypot SSH (para monitorear atacantes)",
                    "Pi-hole (bloqueador DNS ads + tracker)",
                    "Fail2ban (banear IPs con intentos fallidos)"
                ]
            }
        }
    
    def get_architecture_diagram(self):
        """Arquitectura visual de seguridad distribuida."""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║                  🛡️ ARQUITECTURA RASPBERRY GUARDIAN               ║
╚═══════════════════════════════════════════════════════════════════╝

┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   INTERNET      │◄────────┤  RASPBERRY PI    │◄────────┤   MAC MINI  │
│   🌐            │         │  🛡️ Guardian     │         │   💻 Core   │
└─────────────────┘         └──────────────────┘         └─────────────┘
        │                            │                            │
        │                    ┌───────┴────────┐                  │
        │                    │                │                  │
        ▼                    ▼                ▼                  ▼
   ┌─────────┐       ┌──────────┐    ┌──────────┐       ┌──────────┐
   │ Firewall│       │ Backups  │    │ Monitor  │       │  Logs    │
   │ (UFW)   │       │ (rsync)  │    │(Netdata) │       │ (rsyslog)│
   └─────────┘       └──────────┘    └──────────┘       └──────────┘
        │                    │                │                  │
        │                    └────────┬───────┘                  │
        │                             ▼                          │
        │                      ┌─────────────┐                  │
        │                      │  USB 64GB   │                  │
        │                      │  💾 Backup  │                  │
        │                      └─────────────┘                  │
        │                                                        │
        └────────────────────────┬───────────────────────────────┘
                                 ▼
                        ┌────────────────┐
                        │ Telegram Bot   │
                        │ 🔔 Alertas     │
                        └────────────────┘

FLUJO DE SEGURIDAD:
1. Todo tráfico internet pasa por Raspberry primero (Firewall)
2. Raspberry decide qué permitir/bloquear
3. Mac hace backups automáticos cada 6 horas a Raspberry
4. Netdata monitorea salud de ambos sistemas 24/7
5. Logs centralizados en Raspberry (30 días)
6. Alertas críticas → Telegram inmediato

VENTAJAS:
✅ Separación física: Mac comprometido ≠ Raspberry comprometida
✅ Consumo bajo: Raspberry siempre encendida (5-10W)
✅ Backups automáticos: Sin intervención manual
✅ Visibilidad total: Dashboard Netdata tiempo real
✅ Respuesta rápida: Alertas inmediatas vía Telegram
"""
    
    def get_raspberry_shopping_list(self):
        """Lista de compras para setup completo."""
        return {
            "hardware_esencial": [
                "Raspberry Pi 4 (4GB RAM mínimo) - $1,500 MXN",
                "MicroSD 32GB (sistema) - $150 MXN",
                "USB 64GB+ (backups) - $200 MXN",
                "Fuente oficial Raspberry - $300 MXN",
                "Cable Ethernet - $100 MXN"
            ],
            "hardware_opcional": [
                "Case con ventilador - $200 MXN",
                "USB Hub powered - $300 MXN",
                "Segundo USB para redundancia - $200 MXN"
            ],
            "total_basico": "$2,250 MXN",
            "total_completo": "$2,950 MXN"
        }
    
    def generate_installation_script(self):
        """Script de instalación automatizada."""
        script = """#!/bin/bash
# 🛡️ Raspberry Guardian - Instalación Automatizada
# Arquitecto: Iyari Cancino Gomez
# Ejecutar: bash raspberry_guardian_install.sh

echo "🛡️ RASPBERRY GUARDIAN - INSTALACIÓN AUTOMÁTICA"
echo "================================================"

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar herramientas esenciales
echo "🔧 Instalando herramientas esenciales..."
sudo apt install -y vim git curl wget htop ufw rsync fail2ban

# 3. Configurar Firewall (UFW)
echo "🔥 Configurando firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw limit 22/tcp
sudo ufw allow 5050/tcp  # Xarvis Core
sudo ufw allow 8080/tcp  # Xarvis Power
sudo ufw allow 19999/tcp # Netdata
sudo ufw --force enable

# 4. Instalar Netdata (Monitoring)
echo "📊 Instalando Netdata..."
bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait

# 5. Configurar Fail2ban (Anti-brute force)
echo "🛡️ Configurando Fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 6. Crear directorio backups
echo "💾 Preparando directorio backups..."
sudo mkdir -p /mnt/backups/xarvis
sudo chown -R $USER:$USER /mnt/backups

# 7. Crear script de backup
echo "📝 Creando script de backup..."
cat > /home/$USER/backup_xarvis.sh << 'EOF'
#!/bin/bash
# Backup automático Xarvis Core desde Mac
MAC_IP="192.168.1.X"  # CAMBIAR POR IP DEL MAC
MAC_USER="blackmamba"
SOURCE="$MAC_USER@$MAC_IP:/Users/blackmamba/Desktop/XarvisCore"
DEST="/mnt/backups/xarvis/$(date +%Y%m%d_%H%M%S)"
LOG="/var/log/backup_xarvis.log"

echo "[$(date)] Iniciando backup..." >> $LOG
rsync -avz --delete $SOURCE $DEST >> $LOG 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] ✅ Backup exitoso" >> $LOG
else
    echo "[$(date)] ❌ Backup falló" >> $LOG
fi

# Limpiar backups >7 días
find /mnt/backups/xarvis -mtime +7 -delete
EOF

chmod +x /home/$USER/backup_xarvis.sh

# 8. Programar backup cada 6 horas
echo "⏰ Programando backups automáticos..."
(crontab -l 2>/dev/null; echo "0 */6 * * * /home/$USER/backup_xarvis.sh") | crontab -

# 9. Mostrar status
echo ""
echo "✅ INSTALACIÓN COMPLETADA"
echo "========================="
echo ""
echo "🔥 Firewall: sudo ufw status"
echo "📊 Netdata: http://$(hostname -I | awk '{print $1}'):19999"
echo "🛡️ Fail2ban: sudo fail2ban-client status"
echo "💾 Backups: ls -lh /mnt/backups/xarvis"
echo ""
echo "⚠️ PENDIENTE:"
echo "1. Configurar IP del Mac en /home/$USER/backup_xarvis.sh"
echo "2. Configurar SSH keys desde Mac: ssh-copy-id raspberry-ip"
echo "3. Montar USB permanente en /mnt/backups"
echo ""
echo "🎯 Próximo paso: Probar backup manualmente"
echo "   bash /home/$USER/backup_xarvis.sh"
"""
        return script
    
    def dashboard(self):
        """Dashboard del estado de seguridad."""
        print("🛡️ RASPBERRY GUARDIAN PROTOCOL")
        print("=" * 70)
        print(f"Arquitecto: Iyari Cancino Gomez")
        print(f"Filosofía: '{self.philosophy}'")
        print(f"Status: {self.status}")
        print("=" * 70)
        
        print("\n🎯 CAPACIDADES DE SEGURIDAD:")
        for cap in self.capabilities:
            print(f"   ✅ {cap.replace('_', ' ').title()}")
        
        print("\n📋 PLAN DE SETUP URGENTE (4 horas):")
        plan = self.get_setup_plan_urgente()
        for fase, detalles in plan.items():
            print(f"\n   {fase.upper()}:")
            print(f"   Tiempo: {detalles['tiempo']}")
            for tarea in detalles['tareas'][:2]:  # Primeras 2 tareas
                print(f"      • {tarea}")
        
        print("\n💰 INVERSIÓN REQUERIDA:")
        shopping = self.get_raspberry_shopping_list()
        print(f"   Básico: {shopping['total_basico']}")
        print(f"   Completo: {shopping['total_completo']}")
        
        print("\n🔥 URGENCIA: ALTA")
        print("   La seguridad no puede esperar. Raspberry lista = Sistema protegido.")
        print("\n📖 Ver arquitectura completa:")
        print("   from raspberry_guardian_protocol import raspberry_guardian")
        print("   print(raspberry_guardian.get_architecture_diagram())")

# Singleton global
raspberry_guardian = RaspberryGuardian()

if __name__ == "__main__":
    raspberry_guardian.dashboard()
    print("\n" + "=" * 70)
    print(raspberry_guardian.get_architecture_diagram())
    
    # Guardar script de instalación
    script_path = Path(__file__).parent / "raspberry_guardian_install.sh"
    with open(script_path, "w") as f:
        f.write(raspberry_guardian.generate_installation_script())
    
    print(f"\n✅ Script de instalación guardado: {script_path}")
    print(f"📝 Ejecutar en Raspberry: bash {script_path.name}")
