import sounddevice as sd
import numpy as np

def print_vumeter(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    bar = "#" * int(volume_norm)
    print(f"\rVUMETRO: [{bar:<50}]", end="")

with sd.InputStream(callback=print_vumeter):
    print("🎙️ Escuchando micrófono... pulsa Ctrl+C para salir.")
    while True:
        pass