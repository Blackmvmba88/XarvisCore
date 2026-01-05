#!/bin/bash
# firstboot.sh – run once on first boot of Raspberry Pi
# This script sets up the XarvisCore environment and starts the main program.

set -e

LOGFILE=/var/log/xarvis_firstboot.log
exec > >(tee -a "$LOGFILE") 2>&1

echo "=== XarvisCore first‑boot setup started $(date) ==="

# 1. Update system and install dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-venv python3-pip git

# 2. Create application directory
APP_DIR=$HOME/xarvis
mkdir -p "$APP_DIR"

# 3. Copy program files from the boot partition (assumes they are placed in /boot/xarvis/)
BOOT_XARVIS_DIR=/boot/xarvis
if [ -d "$BOOT_XARVIS_DIR" ]; then
  echo "Copying XarvisCore files from $BOOT_XARVIS_DIR to $APP_DIR"
  cp -r "$BOOT_XARVIS_DIR"/* "$APP_DIR/"
else
  echo "ERROR: $BOOT_XARVIS_DIR not found – ensure the SD card contains the program files in /boot/xarvis"
  exit 1
fi

# 4. Set up a virtual environment and install Python requirements
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

# 5. Install systemd service to run the main program on boot
SERVICE_FILE=/etc/systemd/system/xarvis.service
sudo bash -c "cat > $SERVICE_FILE <<'EOF'
[Unit]
Description=XarvisCore main service
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

# 6. Disable this first‑boot service so it does not run again
sudo systemctl disable firstboot.service || true

echo "=== XarvisCore first‑boot setup completed $(date) ==="
