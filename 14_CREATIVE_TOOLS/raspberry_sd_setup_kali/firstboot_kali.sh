#!/bin/bash
# firstboot_kali.sh – run once on first boot of Raspberry Pi with Kali Linux
# Sets up the XarvisCore environment and registers the main service.

set -e

LOGFILE=/var/log/xarvis_firstboot_kali.log
exec > >(tee -a "$LOGFILE") 2>&1

echo "=== XarvisCore (Kali) first‑boot setup started $(date) ==="

# 1️⃣ Update system and install base dependencies (Kali uses apt)
sudo apt-get update && sudo apt-get full-upgrade -y
# Install Python, virtualenv, git and the full Kali meta‑package (optional but gives many tools)
sudo apt-get install -y python3 python3-venv python3-pip git kali-linux-default

# 2️⃣ Create application directory
APP_DIR=$HOME/xarvis
mkdir -p "$APP_DIR"

# 3️⃣ Copy program files from the boot partition (assumes they are placed in /boot/xarvis/)
BOOT_XARVIS_DIR=/boot/xarvis
if [ -d "$BOOT_XARVIS_DIR" ]; then
  echo "Copying XarvisCore files from $BOOT_XARVIS_DIR to $APP_DIR"
  cp -r "$BOOT_XARVIS_DIR"/* "$APP_DIR/"
else
  echo "ERROR: $BOOT_XARVIS_DIR not found – ensure the SD card contains the program files in /boot/xarvis"
  exit 1
fi

# 4️⃣ Set up a Python virtual environment and install project requirements
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
if [ -f requirements.txt ]; then
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "WARNING: requirements.txt not found – skipping Python package installation"
fi
deactivate

# 5️⃣ Install systemd service that runs the main XarvisCore program
SERVICE_FILE=/etc/systemd/system/xarvis.service
sudo bash -c "cat > $SERVICE_FILE <<'EOF'
[Unit]
Description=XarvisCore main service (Kali)
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$HOME/xarvis
ExecStart=$HOME/xarvis/venv/bin/python $HOME/xarvis/14_CREATIVE_TOOLS/3milpixeles/core.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable xarvis.service

# 6️⃣ Disable this first‑boot service so it does not run again
sudo systemctl disable firstboot_kali.service || true

echo "=== XarvisCore (Kali) first‑boot setup completed $(date) ==="
