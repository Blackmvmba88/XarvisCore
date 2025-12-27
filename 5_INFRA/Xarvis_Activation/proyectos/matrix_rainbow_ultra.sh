#!/bin/bash
# Matrix Rainbow Ultra v2 🔥 por el Hermano del Fuego

# =========================
# Configuración
DURACION=60       # duración en segundos
SPEED=0.05        # velocidad de caída
GLOW=true         # activar efecto glow (cabeza brillante)
CHARSET="アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789@#$%&*"

# =========================
# Preparativos
fin=$((SECONDS + DURACION))
cols=$(tput cols)
rows=$(tput lines)

# Inicializa posiciones de cada columna
for ((i=0; i<cols; i++)); do
  pos[i]=$((RANDOM % rows))
done

clear
tput civis
trap "tput cnorm; clear; exit" SIGINT

# =========================
# Funciones
rand_char() {
  echo -n "${CHARSET:RANDOM%${#CHARSET}:1}"
}

rand_color() {
  printf "\033[38;5;$((RANDOM % 160 + 50))m"
}

# =========================
# Loop principal
while [ $SECONDS -lt $fin ]; do
  for ((i=0; i<cols; i++)); do
    # Cabeza brillante
    if $GLOW; then
      tput cup ${pos[i]} $i
      printf "\033[1m\033[97m$(rand_char)\033[0m"
    fi

    # Cuerpo de la columna
    tput cup $(((pos[i] - 1 + rows) % rows)) $i
    rand_color
    printf "$(rand_char)\033[0m"

    # Borrar letras viejas
    tput cup $(((pos[i] - 20 + rows) % rows)) $i
    echo " "

    # Avanza la columna
    pos[i]=$(((pos[i] + 1) % rows))
  done

  sleep $SPEED
done
