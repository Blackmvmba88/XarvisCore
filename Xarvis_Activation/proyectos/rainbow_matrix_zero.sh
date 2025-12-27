#!/bin/bash

# 🌈 Rain-bowMatrix Zero — Terminal Preview Mode 🧬
# Sekhmet Core Activated

clear
cols=$(tput cols)
lines=$(tput lines)
chars="セカタナソウミラシオケチツヨヌマリロメネワン0123456789"

glow_on=true
speed=0.03

function draw_matrix {
    while true; do
        for ((i=0; i<$lines; i++)); do
            line=""
            for ((j=0; j<$cols; j++)); do
                rand_char=${chars:RANDOM%${#chars}:1}
                if [ "$glow_on" = true ]; then
                    line+="\033[38;2;$((RANDOM%50+150));255;${RANDOM%100+100}m$rand_char"
                else
                    line+="\033[32m$rand_char"
                fi
            done
            echo -e "$line"
        done
        sleep $speed
        clear
    done
}

draw_matrix

