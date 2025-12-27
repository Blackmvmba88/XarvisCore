import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print("🎤 Escuchando...")
    audio = r.listen(source)
try:
    comando = r.recognize_google(audio, language="es-MX")
    print(f"🧠 Comando reconocido: {comando}")
except sr.UnknownValueError:
    print("🤖 No entendí nada.")
except sr.RequestError:
    print("❌ Error de conexión con Google Speech.")
