#!/bin/bash

# Lanzar Ollama (IA local)
osascript -e 'tell application "Terminal" to do script "ollama serve"'

# Esperar unos segundos para que cargue el servidor
sleep 5

# Lanzar watcher visual
osascript -e 'tell application "Terminal" to do script "~/xarvis_local/scripts/xarvis_foto_watcher.sh"'

# Confirmación
echo "XΛЯVIƧ AUTORUN COMPLETO: Motor + Vigilancia activados."
