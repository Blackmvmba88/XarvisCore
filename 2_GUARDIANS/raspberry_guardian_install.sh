#!/bin/bash
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
