# 🛡️ Raspberry Pi Conectada - Primeros Pasos INMEDIATOS
**Fecha**: 29 Diciembre 2025  
**Status**: CONECTADA ✅  
**Siguiente**: Configuración inicial (30 minutos)

---

## 📍 PASO 1: Obtener IP de la Raspberry (5 minutos)

### Opción A: Desde tu Mac (RECOMENDADO)
```bash
# Escanear red local para encontrar Raspberry
nmap -sn 192.168.1.0/24 | grep -B 2 "Raspberry"

# O usando arp
arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01"
# Estos son los MAC address prefixes de Raspberry Pi
```

### Opción B: Desde el router
```bash
1. Abrir navegador: http://192.168.1.1 (o http://192.168.0.1)
2. Login (usuario/password del router)
3. Buscar "DHCP" o "Dispositivos conectados"
4. Buscar "raspberrypi" o "Raspberry Pi"
5. Anotar la IP (ejemplo: 192.168.1.150)
```

### Opción C: Conectar monitor/teclado a Raspberry
```bash
# Una vez conectado, ejecutar en la Raspberry:
hostname -I
# Mostrará la IP actual
```

**⚠️ ANOTA LA IP AQUÍ**: `192.168.1.___`

---

## 🔐 PASO 2: Primera Conexión SSH (5 minutos)

### Desde tu Mac:
```bash
# Conectar (password por defecto: raspberry)
ssh pi@192.168.1.XXX

# Si es primera vez, te preguntará:
# "Are you sure you want to continue connecting?"
# Escribe: yes
```

**Si NO funciona SSH**:
```bash
# La Raspberry puede tener SSH deshabilitado
# Opción 1: Conectar monitor + teclado y ejecutar:
sudo raspi-config
# Interfacing Options → SSH → Enable

# Opción 2: Si tienes acceso a la SD card:
# Crear archivo vacío llamado "ssh" en boot partition
touch /Volumes/boot/ssh
```

---

## ⚡ PASO 3: Configuración Inicial Básica (10 minutos)

### Una vez conectado por SSH:

#### 3.1 Cambiar Password (CRÍTICO)
```bash
passwd
# Ingresar password actual: raspberry
# Ingresar nuevo password FUERTE (anótalo en lugar seguro)
# Confirmar nuevo password
```

**⚠️ NUEVO PASSWORD**: `___________________` (anótalo físicamente)

#### 3.2 Actualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
# Tomará 5-10 minutos dependiendo de cuánto esté desactualizada
```

#### 3.3 Configurar Hostname
```bash
sudo raspi-config
# 1. System Options → S4 Hostname
# Cambiar a: xarvis-guardian
# Finish → Reboot: Yes
```

#### 3.4 Obtener Info del Sistema
```bash
# Después del reboot, conectar de nuevo:
ssh pi@192.168.1.XXX

# Ver info:
cat /etc/os-release
free -h
df -h
vcgencmd measure_temp
```

---

## 🌐 PASO 4: Configurar IP Estática (10 minutos)

### Método Recomendado: En el Router
```bash
1. Login al router (192.168.1.1)
2. Buscar "DHCP Reservations" o "Static IP"
3. Encontrar Raspberry Pi en lista de dispositivos
4. Asignar IP fija: 192.168.1.100
5. Guardar y aplicar cambios
```

### Método Alternativo: En la Raspberry
```bash
# Editar dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Agregar al final:
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Guardar: Ctrl+O, Enter
# Salir: Ctrl+X

# Reiniciar networking
sudo systemctl restart dhcpcd

# Verificar nueva IP
hostname -I
```

**IP ESTÁTICA CONFIGURADA**: `192.168.1.___`

---

## 📦 PASO 5: Instalar Herramientas Esenciales (5 minutos)

```bash
# Instalar paquetes básicos
sudo apt install -y \
    vim \
    git \
    curl \
    wget \
    htop \
    screen \
    rsync

# Verificar instalación
vim --version
git --version
htop --version
```

---

## 🔑 PASO 6: Configurar SSH Keys (10 minutos)

### En tu Mac:
```bash
# Generar key si no tienes una
cd ~/.ssh
ssh-keygen -t ed25519 -C "blackmamba@xarvis-guardian"
# Enter para ubicación por defecto
# Enter para sin passphrase (o usa una si prefieres)

# Copiar key pública a Raspberry
ssh-copy-id pi@192.168.1.100

# Probar conexión sin password
ssh pi@192.168.1.100
# Debe conectar SIN pedir password
```

### Deshabilitar Password SSH (SEGURIDAD)
```bash
# En Raspberry:
sudo nano /etc/ssh/sshd_config

# Cambiar estas líneas:
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no

# Guardar y reiniciar SSH
sudo systemctl restart sshd

# IMPORTANTE: NO cierres esta sesión hasta verificar
# que puedes conectar desde otra terminal sin password
```

---

## ✅ CHECKLIST DE VALIDACIÓN

Después de completar estos pasos, verificar:

```bash
# En Raspberry:
✅ hostname → debe mostrar: xarvis-guardian
✅ whoami → debe mostrar: pi
✅ ip a → debe mostrar IP estática (192.168.1.100)
✅ sudo apt update → debe funcionar sin errores
✅ htop → debe abrir dashboard de procesos (q para salir)
✅ vcgencmd measure_temp → debe mostrar temperatura <60°C

# Desde Mac:
✅ ssh pi@192.168.1.100 → conecta sin password
✅ ping 192.168.1.100 → responde
```

---

## 🎯 SIGUIENTE FASE: Instalación Automatizada

Una vez completados estos pasos básicos, proceder con:

```bash
# Copiar script de instalación desde Mac a Raspberry
cd /Users/blackmamba/Desktop/XarvisCore/2_GUARDIANS
scp raspberry_guardian_install.sh pi@192.168.1.100:~

# Conectar a Raspberry
ssh pi@192.168.1.100

# Ejecutar instalación automatizada
bash raspberry_guardian_install.sh

# Tiempo estimado: 15-20 minutos
# Instalará: Firewall, Netdata, Fail2ban, Scripts de backup
```

---

## 📊 Estado Actual

**Completado**:
- [x] Raspberry conectada a red
- [ ] IP obtenida y anotada
- [ ] Primera conexión SSH exitosa
- [ ] Password cambiado
- [ ] Sistema actualizado
- [ ] Hostname configurado
- [ ] IP estática asignada
- [ ] Herramientas esenciales instaladas
- [ ] SSH keys configuradas

**Siguiente**: Ejecutar `raspberry_guardian_install.sh`

---

## 🆘 Troubleshooting

### No puedo encontrar la IP
```bash
# Verificar que Raspberry esté encendida
# LED verde debe parpadear (acceso SD card)
# LED rojo debe estar fijo (power)

# Conectar monitor HDMI y ver IP en pantalla
# O conectar teclado y ejecutar: hostname -I
```

### SSH no funciona
```bash
# Verificar que SSH esté habilitado
# Conectar monitor + teclado
sudo raspi-config
# Interfacing Options → SSH → Enable
```

### Password no cambió
```bash
# Usar comando passwd de nuevo
passwd
# Seguir instrucciones en pantalla
```

### IP estática no funciona
```bash
# Verificar configuración
cat /etc/dhcpcd.conf

# Reiniciar servicio
sudo systemctl restart dhcpcd

# Verificar
hostname -I
```

---

🛡️ **Cuando completes esta fase, tendrás la base sólida para el Guardian.**

