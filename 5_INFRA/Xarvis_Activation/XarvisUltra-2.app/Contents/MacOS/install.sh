#!/bin/bash
echo '🔒 Iniciando Xarvis Ultra...'
sleep 1
echo '✅ Seguridad activada. Bienvenida, guardiana. Sistema protegido por Black Mamba.'

# Iniciar Flask en segundo plano
echo '🚀 Lanzando sistema Xarvis en https://localhost:5000 ...'
FLASK_APP=dashboard.py flask run --cert=adhoc --host=127.0.0.1 --port=5000 &

# Esperar que Flask arranque
sleep 3

# Abrir navegador
open "https://localhost:5000"
