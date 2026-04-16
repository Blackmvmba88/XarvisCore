#!/bin/bash
# Matrix Dynamic Wallpaper by Tu Hermano 🔥

# ========== CONFIGURACIÓN ==========
GLOWHEAD=true    # ¿Cabeza Brillante? (true/false)
RAINBOW=true     # ¿Colores Rainbow? (true/false)
GLITCH=true      # ¿Efecto Glitch Random? (true/false)
SPEED=0.05       # Velocidad de caída (segundos entre frames)

# Caracteres Katakana
katakana=(ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ チ ツ テ ト ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ン)

# ========== INICIALIZACIÓN ==========
clear
tput civis
trap "tput cnorm; clear; exit" SIGINT

lines=$(tput lines)
columns=$(tput cols)

# Estado de cada columna
declare -a y_positions

for ((i=0; i<columns; i++)); do
  y_positions[i]=$((RANDOM % lines))
done

# ========== FUNCIONES ==========

# Colores
color_random() {
  printf "\033[38;5;$((RANDOM%256))m"
}

# Efecto de glitch: cambia letras aleatorias
do_glitch() {
  if $GLITCH && (( RANDOM % 20 == 0 )); then
    tput cup $((RANDOM % lines)) $((RANDOM % columns))
    printf "\033[1;35m%s" "${katakana[RANDOM%${#katakana[@]}]}"
  fi
}

# ========== MAIN LOOP ==========
while true; do
  for ((i=0; i<columns; i++)); do
    if (( RANDOM % 10 > 2 )); then
      y=${y_positions[i]}

      # Glowhead
      if $GLOWHEAD; then
        tput cup $y $i
        printf "\033[1;97m%s" "${katakana[RANDOM%${#katakana[@]}]}"
      fi

      # Trail
      for trail in {1..5}; do
        old_y=$(( (y - trail + lines) % lines ))
        tput cup $old_y $i
        if $RAINBOW; then
          color_random
        else
          printf "\033[32m" # Verde clásico Matrix
        fi
        printf "%s" "${katakana[RANDOM%${#katakana[@]}]}"
      done

      # Clear detrás
      clean_y=$(( (y - 6 + lines) % lines ))
      tput cup $clean_y $i
      printf " "

      # Actualizar posición
      y_positions[i]=$(( (y + 1) % lines ))
    fi
  done

  do_glitch
  sleep $SPEED
done

