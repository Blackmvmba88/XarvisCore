#!/bin/bash

# Matrix Rainbow Fullscreen + Katakana 🌈🇯🇵

clear

# Configuración de la pantalla
lines=$(tput lines)
columns=$(tput cols)

# Caracteres Katakana (unicode random seleccionado)
katakana=(ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ チ ツ テ ト ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ン)

# Función para color random
color() {
  printf "\033[38;5;$((RANDOM%256))m"
}

# Limpia la pantalla antes de empezar
tput civis # Oculta cursor para que se vea más bonito
trap "tput cnorm; exit" SIGINT # Si presiona Ctrl+C vuelve el cursor

while true; do
  for ((i=0; i<columns; i++)); do
    color
    printf "%s" "${katakana[RANDOM%${#katakana[@]}]}"
  done
  printf "\n"
  sleep 0.03
done

