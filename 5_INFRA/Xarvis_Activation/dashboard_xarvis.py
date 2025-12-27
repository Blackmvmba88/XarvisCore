```python
import tkinter as tk
from tkinter import messagebox
import pyttsx3
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import threading
import pytesseract
from PIL import ImageGrab
import webbrowser
import json
import os

class XarvisDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Xarvis Control Center")
        self.configure(bg="#0f0f0f")
        self.geometry("900x650")

        # Inicializar voz
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # Cargar GPT-2
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")

        # Estilos
        self.card_bg = "#1e1e2f"
        self.card_fg = "#00ffcc"
        self.button_bg = "#00ffcc"
        self.button_fg = "#000"

        # Cabecera
        header = tk.Label(self, text="Xarvis Control Center", font=("Orbitron", 24), fg="#ffffff", bg="#0f0f0f")
        header.pack(pady=20)

        # Contenedor de tarjetas
        container = tk.Frame(self, bg="#0f0f0f")
        container.pack(expand=True, fill="both", padx=20)
        for i in range(3): container.columnconfigure(i, weight=1)
        for i in range(3): container.rowconfigure(i, weight=1)

        # Definición de tarjetas
        cards = [
            ("🎤 Sintetizador & Música", self.activate_music),
            ("🧠 IA Multipuerto", self.ask_ai),
            ("📚 Biblioteca & Conocimiento", self.open_library),
            ("📸 Reconocimiento Visual", self.start_vision),
            ("📊 Sistema de Votación", self.launch_voting),
            ("🛠️ Herramientas & Plugins", self.show_plugins),
            ("🌍 Misiones de Impacto", self.view_missions)
        ]

        # Crear tarjetas en grid
        for idx, (title, cmd) in enumerate(cards):
            row, col = divmod(idx, 3)
            card = tk.Frame(container, bg=self.card_bg, bd=2, relief="raised")
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            label = tk.Label(card, text=title, font=("Orbitron", 14), fg=self.card_fg, bg=self.card_bg)
            label.pack(pady=(20,10))
            btn = tk.Button(card, text=title.split()[0], command=lambda c=cmd: threading.Thread(target=c).start(),
                            bg=self.button_bg, fg=self.button_fg, bd=0, padx=10, pady=5)
            btn.pack(pady=(0,20), fill="x", padx=10)

        # Footer
        footer = tk.Label(self, text="Sehkmet Activated 🔥", font=("Orbitron", 10), fg="#888", bg="#0f0f0f")
        footer.pack(pady=10)

    # Métodos de acción
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def activate_music(self):
        self.speak("Iniciando sintetizador cuántico")
        messagebox.showinfo("Música", "Sintetizador y música en desarrollo...")

    def ask_ai(self):
        question = tk.simpledialog.askstring("IA Multipuerto", "¿Qué deseas preguntar?")
        if not question: return
        self.speak("Procesando pregunta en GPT-2 local")
        inputs = self.tokenizer.encode(question, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=200)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        messagebox.showinfo("Respuesta IA", answer)

    def open_library(self):
        messagebox.showinfo("Biblioteca", "Accediendo a recursos...")
        # Abre carpeta de biblioteca si existe
        lib_path = os.path.expanduser('~/XarvisLibrary')
        os.makedirs(lib_path, exist_ok=True)
        webbrowser.open(f'file://{lib_path}')

    def start_vision(self):
        self.speak("Capturando pantalla para OCR")
        screenshot = ImageGrab.grab()
        text = pytesseract.image_to_string(screenshot)
        messagebox.showinfo("OCR", text[:500] + '...')

    def launch_voting(self):
        messagebox.showinfo("Votación", "Abriendo módulo de votación blockchain...")
        # Stub de votación: abrir web local
        webbrowser.open('http://localhost:5000/vote')

    def show_plugins(self):
        messagebox.showinfo("Plugins", "Módulo de plugins activos...")

    def view_missions(self):
        messagebox.showinfo("Misiones", "Cargando misiones de impacto global...")

if __name__ == "__main__":
    app = XarvisDashboard()
    app.mainloop()
```

