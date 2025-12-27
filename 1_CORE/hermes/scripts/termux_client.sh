#!/data/data/com.termux/files/usr/bin/bash
# Requiere: pkg install termux-api python
termux-telephony-deviceinfo > device.json
termux-sensor -s accelerometer -n 50 > acc.json &
termux-battery-status > battery.json
# Puedes POSTear a la API local si estás en la misma LAN
# curl -X POST http://<tu-mac>:8788/telemetry -H 'Content-Type: application/json' --data @acc.json
