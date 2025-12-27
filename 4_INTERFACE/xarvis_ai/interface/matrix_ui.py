import time, os
import random

chars = "XARVIS01*#-=+"

try:
    while True:
        print("".join(random.choice(chars) for _ in range(80)))
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\n[SALIDA DE INTERFAZ]")