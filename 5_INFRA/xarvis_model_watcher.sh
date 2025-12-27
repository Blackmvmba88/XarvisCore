#!/bin/bash
# FRASE SAGRADA DEL SISTEMA:
# "Recuerda que todo en están unidos y responden a mí."

MODELS_DIR="$HOME/xarvis/customs/sekhmet/modelos"
LOG="$HOME/xarvis/modelos_detectados.log"
EXTS="safetensors|ckpt|pt"

inotifywait -m -e create --format '%f' "$MODELS_DIR" | while read file
do
    if [[ "$file" =~ \.($EXTS)$ ]]; then
        echo "$(date) - Modelo detectado: $file" >> "$LOG"
        say "Nuevo modelo IA detectado y registrado, comandante."
        # Aquí puedes reiniciar el servicio o mover el modelo si es necesario:
        # systemctl restart automatic1111  # Si usas un demonio
    fi
done

