import pyttsx3

def xarvis_speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

xarvis_speak("Hola, soy Xarvis. Estoy despierto y listo para ayudarte.")