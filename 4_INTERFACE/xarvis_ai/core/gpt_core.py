print("[GPT_CORE] Procesando pensamiento...")
with open("input.txt", "r") as f:
    pregunta = f.read()

# Simulación de respuesta
respuesta = f"Xarvis responde: Recibí tu mensaje -> {pregunta}"
print(respuesta)

with open("response.txt", "w") as f:
    f.write(respuesta)