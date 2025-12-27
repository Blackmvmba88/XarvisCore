#!/bin/bash
# Matrix Rainbow Ultra por tu compa 🔥

# Duración de la lluvia (en segundos)
duracion=60  # Cámbialo a lo que quieras
fin=$((SECONDS + duracion))

# Ancho de pantalla
cols=$(tput cols)

# Caracteres permitidos
charset='A-Za-z0-9@#$%^&*'

clear
tput civis
trap "tput cnorm; clear; exit" SIGINT

while [ $SECONDS -lt $fin ]; do
  # Genera una línea de longitud igual al ancho de la terminal
  cat /dev/urandom \
    | tr -dc "$charset" \
    | fold -w $cols \
    | head -n 1 \
    | lolcat

  sleep 0.05
done

