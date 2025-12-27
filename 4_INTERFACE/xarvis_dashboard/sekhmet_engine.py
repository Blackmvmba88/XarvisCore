# sekhmet_engine.py - módulo de análisis
import os

def scan():
    load = os.popen("top -n 1 | head -n 5").read()
    return f"Sekhmet dice:\n{load}"

if __name__ == "__main__":
    print(scan())
