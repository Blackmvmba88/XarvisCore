import os, sys
text = " ".join(sys.argv[1:]) or "Hola, soy Xarvis. Voz activada."
os.system(f"say '{text}'")
