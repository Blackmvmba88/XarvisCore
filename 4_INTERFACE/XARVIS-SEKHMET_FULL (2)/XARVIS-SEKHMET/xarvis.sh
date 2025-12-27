#!/bin/bash
echo "[XARVIS] Iniciando sistema..."
bash blindaje/blindaje.sh
bash core/ai_response.sh "Sistema blindado y listo, ¿qué deseas hacer?"
python3 core/gpt_chat.py "Iniciando sesión principal en XARVIS"
