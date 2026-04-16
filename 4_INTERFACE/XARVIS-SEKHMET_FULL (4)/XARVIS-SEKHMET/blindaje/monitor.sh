#!/bin/bash
LOGFILE=logs/actividad.log
touch $LOGFILE
echo "[XARVIS] Iniciando monitoreo..."
while true; do
    date >> $LOGFILE
    ps aux >> $LOGFILE
    sleep 60
done
