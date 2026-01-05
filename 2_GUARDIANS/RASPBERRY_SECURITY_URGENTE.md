# 🛡️ Plan de Seguridad Urgente con Raspberry Pi
**Arquitecto**: Iyari Cancino Gomez  
**Hardware**: Raspberry Pi  
**Urgencia**: ALTA - Seguridad crítica  
**Filosofía**: "Separar para proteger. Distribuir para sobrevivir."

---

## ⚠️ Por Qué Es Urgente

### Riesgos Actuales
- **Mac Mini único**: Todo en un solo sistema = punto único de fallo
- **Sin backups automáticos**: Código/música/finanzas sin respaldo
- **Sin firewall dedicado**: Vulnerable a ataques externos
- **Sin monitoring 24/7**: No sabes si algo falla hasta que ya falló
- **Logs dispersos**: Difícil diagnóstico post-incidente

### Raspberry = Solución
- **Separación física**: Raspberry comprometida ≠ Mac comprometido
- **Siempre encendida**: 5-10W consumo (vs 85W Mac Mini)
- **Barata**: $2,250 MXN setup completo
- **Dedicada**: Solo seguridad, sin distracciones

---

## 🎯 Setup Inmediato (4 Horas)

### Fase 1: Hardware (30 minutos)
```bash
✅ Tareas:
1. Conectar Raspberry a red (Ethernet > WiFi)
2. Conectar USB 64GB+ para backups
3. Anotar IP: ip a | grep inet
4. Configurar IP estática en router
   - Login router (192.168.1.1 usual)
   - DHCP → Reservar IP para MAC Raspberry
   - Ejemplo: 192.168.1.100 fija
```

**Compras Necesarias** (si no tienes):
- Raspberry Pi 4 (4GB RAM) → $1,500 MXN
- MicroSD 32GB → $150 MXN
- USB 64GB+ → $200 MXN
- Fuente oficial → $300 MXN
- Cable Ethernet → $100 MXN
- **TOTAL**: $2,250 MXN

---

### Fase 2: Sistema Base (1 hora)
```bash
# SSH a Raspberry desde Mac
ssh pi@192.168.1.100  # Password por defecto: raspberry

# Actualizar todo
sudo apt update && sudo apt upgrade -y

# Instalar herramientas esenciales
sudo apt install -y vim git curl wget htop ufw rsync fail2ban

# Cambiar password
passwd
# IMPORTANTE: Usar password fuerte diferente

# Configurar SSH keys (desde Mac)
# En Mac:
ssh-keygen -t ed25519 -C "blackmamba@xarvis"
ssh-copy-id pi@192.168.1.100

# En Raspberry: Deshabilitar password SSH
sudo vim /etc/ssh/sshd_config
# Cambiar: PasswordAuthentication no
sudo systemctl restart sshd
```

---

### Fase 3: Firewall UFW (30 minutos)
```bash
# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir servicios esenciales
sudo ufw allow 22/tcp                # SSH
sudo ufw limit 22/tcp                # Rate limit SSH (anti brute-force)
sudo ufw allow from 192.168.1.0/24  # Solo red local
sudo ufw allow 5050/tcp              # Xarvis Core
sudo ufw allow 8080/tcp              # Xarvis Power
sudo ufw allow 19999/tcp             # Netdata (monitoring)

# Activar
sudo ufw --force enable

# Verificar
sudo ufw status verbose
```

**Resultado**: Todo bloqueado excepto servicios críticos.

---

### Fase 4: Backups Automáticos (1 hora)
```bash
# Montar USB externo
sudo fdisk -l  # Identificar USB (ejemplo: /dev/sda1)
sudo mkdir -p /mnt/backups
sudo mount /dev/sda1 /mnt/backups

# Auto-mount al arrancar
sudo vim /etc/fstab
# Agregar línea:
/dev/sda1 /mnt/backups ext4 defaults 0 2

# Crear directorio Xarvis
sudo mkdir -p /mnt/backups/xarvis
sudo chown -R pi:pi /mnt/backups

# Crear script de backup
vim /home/pi/backup_xarvis.sh
```

**Script de Backup** (`backup_xarvis.sh`):
```bash
#!/bin/bash
# Backup automático Xarvis Core desde Mac a Raspberry

MAC_IP="192.168.1.X"  # CAMBIAR por IP real del Mac
MAC_USER="blackmamba"
SOURCE="$MAC_USER@$MAC_IP:/Users/blackmamba/Desktop/XarvisCore"
DEST="/mnt/backups/xarvis/$(date +%Y%m%d_%H%M%S)"
LOG="/var/log/backup_xarvis.log"

echo "[$(date)] 🔄 Iniciando backup..." >> $LOG

rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    $SOURCE $DEST >> $LOG 2>&1

if [ $? -eq 0 ]; then
    SIZE=$(du -sh $DEST | cut -f1)
    echo "[$(date)] ✅ Backup exitoso - Tamaño: $SIZE" >> $LOG
    
    # Enviar notificación Telegram (opcional)
    # curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    #      -d "chat_id=<CHAT_ID>" \
    #      -d "text=✅ Backup Xarvis completado: $SIZE"
else
    echo "[$(date)] ❌ Backup FALLÓ - Código: $?" >> $LOG
    
    # Alerta crítica Telegram
    # curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    #      -d "chat_id=<CHAT_ID>" \
    #      -d "text=🚨 ALERTA: Backup Xarvis FALLÓ"
fi

# Limpiar backups antiguos (mantener últimos 7 días)
find /mnt/backups/xarvis -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null

echo "[$(date)] 🧹 Limpieza completada" >> $LOG
```

```bash
# Dar permisos
chmod +x /home/pi/backup_xarvis.sh

# Programar cada 6 horas
crontab -e
# Agregar:
0 */6 * * * /home/pi/backup_xarvis.sh

# Probar manualmente
bash /home/pi/backup_xarvis.sh
tail -f /var/log/backup_xarvis.log
```

**Resultado**: Backups automáticos cada 6 horas sin intervención.

---

### Fase 5: Monitoring Netdata (30 minutos)
```bash
# Instalación automática
bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait

# Abrir puerto en firewall
sudo ufw allow 19999/tcp

# Acceder desde Mac
# Abrir: http://192.168.1.100:19999
```

**Qué Monitorea**:
- CPU, RAM, disco Raspberry
- Tráfico red (entrante/saliente)
- Temperatura CPU
- Procesos activos
- Alertas automáticas

**Dashboard Visual**: Gráficas en tiempo real actualizadas cada segundo.

---

### Fase 6: Logs Centralizados (45 minutos)
```bash
# En Raspberry: Configurar rsyslog server
sudo vim /etc/rsyslog.conf
# Descomentar líneas:
module(load="imudp")
input(type="imudp" port="514")
module(load="imtcp")
input(type="imtcp" port="514")

sudo systemctl restart rsyslog

# Abrir puerto (solo red local)
sudo ufw allow from 192.168.1.0/24 to any port 514

# Crear directorio logs centralizados
sudo mkdir -p /var/log/centralized
sudo chown -R syslog:adm /var/log/centralized
```

**En Mac** (enviar logs a Raspberry):
```bash
# Editar rsyslog Mac (si está instalado) o usar script Python
# Script Python simple:
cat > /Users/blackmamba/Desktop/XarvisCore/5_INFRA/send_logs_to_raspberry.py << 'EOF'
#!/usr/bin/env python3
import socket
import datetime

RASPBERRY_IP = "192.168.1.100"
RASPBERRY_PORT = 514

def send_log(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timestamp = datetime.datetime.now().isoformat()
    log_line = f"[{timestamp}] [MAC_XARVIS] {message}"
    sock.sendto(log_line.encode(), (RASPBERRY_IP, RASPBERRY_PORT))
    sock.close()

# Usar en cualquier script:
# send_log("Xarvis Core iniciado")
# send_log("RAM Guardian activado")
EOF
```

---

### Fase 7 (Opcional): Avanzado (2-4 horas)

#### A. VPN WireGuard
```bash
# Instalar
sudo apt install wireguard -y

# Generar llaves
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey

# Configurar /etc/wireguard/wg0.conf
sudo vim /etc/wireguard/wg0.conf
```

**Beneficio**: Acceso remoto seguro desde cualquier lugar.

#### B. Fail2ban (Anti Brute-Force)
```bash
# Instalar
sudo apt install fail2ban -y

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo vim /etc/fail2ban/jail.local
# Ajustar:
# bantime = 1h
# maxretry = 3

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Beneficio**: Banea IPs con 3+ intentos SSH fallidos.

#### C. Pi-hole (Bloqueador DNS)
```bash
# Instalación
curl -sSL https://install.pi-hole.net | bash

# Configurar Mac para usar Raspberry como DNS
# System Preferences → Network → Advanced → DNS
# Agregar: 192.168.1.100
```

**Beneficio**: Bloquea ads/trackers a nivel DNS para TODA la red.

---

## 📊 Checklist de Validación

### Después del Setup
```bash
# En Raspberry:
✅ sudo ufw status → Debe mostrar reglas activas
✅ df -h → USB montado en /mnt/backups
✅ crontab -l → Backup cada 6 horas
✅ curl localhost:19999 → Netdata responde
✅ ls /var/log/backup_xarvis.log → Existe
✅ tail -f /var/log/syslog → Sin errores

# Desde Mac:
✅ ssh pi@192.168.1.100 → Conecta con key
✅ http://192.168.1.100:19999 → Dashboard visible
✅ bash backup_xarvis.sh → Ejecuta sin error
✅ ls /mnt/backups/xarvis → Backup existe
```

---

## 🔥 Script de Instalación Automatizada

Creado en: `/Users/blackmamba/Desktop/XarvisCore/2_GUARDIANS/raspberry_guardian_install.sh`

**Ejecutar en Raspberry**:
```bash
# Copiar desde Mac a Raspberry
scp raspberry_guardian_install.sh pi@192.168.1.100:~

# SSH a Raspberry
ssh pi@192.168.1.100

# Ejecutar
bash raspberry_guardian_install.sh
```

**Qué Hace**:
1. Actualiza sistema
2. Instala herramientas (UFW, rsync, fail2ban, htop)
3. Configura firewall automáticamente
4. Instala Netdata
5. Crea script de backup
6. Programa cron de 6 horas
7. Muestra status final

**Tiempo**: 15-20 minutos automatizado.

---

## 💰 Costo vs. Beneficio

### Inversión
- **Hardware**: $2,250 MXN (una sola vez)
- **Tiempo setup**: 4 horas (valor: $0 - lo haces tú)
- **Mantenimiento**: 0 (automático)

### ROI (Return on Investment)
- **Pérdida de datos sin backup**: INVALUABLE (años de trabajo)
- **Ataque exitoso sin firewall**: $50K-500K MXN potencial
- **Downtime sin monitoring**: Horas perdidas sin saber
- **Tranquilidad mental**: PRICELESS

**Veredicto**: $2,250 MXN es RIDÍCULAMENTE barato para la protección que ofrece.

---

## 🎯 Ejecución Inmediata

### Hoy (29 Diciembre)
- [ ] Verificar si tienes Raspberry Pi
- [ ] Si NO: Comprar online (MercadoLibre $1,500-2,000 MXN)
- [ ] Si SÍ: Conectar y obtener IP

### Mañana (30 Diciembre)
- [ ] Ejecutar Fase 1-3 (2 horas)
- [ ] Firewall funcionando
- [ ] Primer backup manual exitoso

### 31 Diciembre
- [ ] Ejecutar Fase 4-6 (2.5 horas)
- [ ] Backups automáticos activos
- [ ] Netdata monitoring

### 1 Enero 2026
- [ ] Validar que todo funciona
- [ ] Primer backup automático confirmado
- [ ] Dashboard Netdata revisado

---

## 📈 Integración con Sistema Económico

La Raspberry también puede:
1. **Servir tu música**: Streaming local de 280 tracks
2. **Alojar demos**: Herramientas web (3milpixeles, YTDLP-Web)
3. **Mini servidor**: Para clientes que quieran ver Xarvis en acción
4. **Desarrollo remoto**: SSH desde cualquier lugar

**Línea de negocio adicional**: "Setup de seguridad para freelancers/emprendedores" → $5K-10K MXN por instalación completa.

---

## 🛡️ Filosofía Final

> "Un sistema sin backups es un sistema que ya perdió todo, solo no lo sabe todavía."

> "La seguridad no es un gasto, es la inversión más rentable que jamás harás."

> "Raspberry Pi: 70 gramos de hardware, toneladas de tranquilidad."

---

🦅 **El Rey protege su reino con inteligencia, no con suerte.**

