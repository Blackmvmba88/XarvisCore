#!/bin/bash
echo '[✓] Instalación automática iniciada...'
./core/blindaje.sh
./core/ssl_setup.sh
./core/auth_system.sh
./core/rainbow_matrix.sh
python3 dash/server.py &
echo '[✓] Xarvis activado.' > xarvis_status.log