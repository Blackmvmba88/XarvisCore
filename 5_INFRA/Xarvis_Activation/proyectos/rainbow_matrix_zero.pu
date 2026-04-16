import random
import shutil
import time
import os
from colorama import init, Fore, Back, Style

init()

cols, rows = shutil.get_terminal_size()
characters = list("セカタナソウミラシオケチツヨヌマリロメネワン0123456789")

# Cada columna tiene su propia "lluvia"
matrix = [0 for _ in range(cols)]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def rain():
    while True:
        output = [''] * rows
        for i in range(cols):
            char = random.choice(characters)
            drop_pos = matrix[i]

            for j in range(rows):
                if j == drop_pos:
                    output[j] += Style.BRIGHT + Fore.GREEN + char
                elif j < drop_pos:
                    output[j] += Fore.GREEN + Style.DIM + random.choice(characters)
                else:
                    output[j] += ' '
            
            # Controlamos la velocidad de caída individual por columna
            if random.random() > 0.975:
                matrix[i] = 0
            else:
                matrix[i] = (matrix[i] + 1) % rows

        clear()
        for line in output:
            print(line)
        time.sleep(0.05)

try:
    rain()
except KeyboardInterrupt:
    clear()
    print("👋 Cerrado Matrix. Hasta luego, hacker.")


