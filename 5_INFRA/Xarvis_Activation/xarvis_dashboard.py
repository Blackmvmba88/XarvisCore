import sys
import os
import webbrowser
import threading
import numpy as np
import pyaudio
import wave
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QMessageBox,
    QInputDialog, QFileDialog, QTextEdit, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import QTimer
import pyttsx3
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import pytesseract
from PIL import ImageGrab
import pyqtgraph as pg
from PyQt5.QtGui import QClipboard

class AudioVisualizer(pg.GraphicsLayoutWidget):
    def __init__(self, audio_file, parent=None):
        super().__init__(parent)
        self.setBackground('k')
        self.plot = self.addPlot(title="Visualización de Audio")
        self.plot.setYRange(0, 1)
        self.curve = self.plot.plot(pen=pg.mkPen(color='00ffcc', width=1))
        self.wf = wave.open(audio_file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True,
            stream_callback=self.callback
        )
        self.data = None
        self.timer = QTimer(); self.timer.timeout.connect(self.update_plot)

    def start(self):
        self.stream.start_stream()
        self.timer.start(50)

    def callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        self.data = np.frombuffer(data, dtype=np.int16) / 32768.0
        return (data, pyaudio.paContinue)

    def update_plot(self):
        if self.data is not None:
            freqs = np.fft.rfft(self.data)
            mags = np.abs(freqs)
            self.curve.setData(mags)

    def stop(self):
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class XarvisDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xarvis Control Center")
        self.setStyleSheet("background-color: #0f0f0f; color: #00ffcc;")
        self.resize(1100, 800)

        # Voz
        self.engine = pyttsx3.init(); self.engine.setProperty('rate', 150)
        # GPT-2
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")

        # Clipboard
        self.clipboard = QApplication.clipboard()

        # Layouts
        main_layout = QVBoxLayout(self)
        grid = QGridLayout(); grid.setSpacing(20)

        # Text input area
        self.text_input = QTextEdit(); self.text_input.setPlaceholderText("Escribe aquí...")
        main_layout.addWidget(self.text_input)

        # Copy/Paste buttons
        cp_layout = QHBoxLayout()
        btn_copy = QPushButton("Copiar"); btn_copy.clicked.connect(self.copy_text)
        btn_paste = QPushButton("Pegar"); btn_paste.clicked.connect(self.paste_text)
        cp_layout.addWidget(btn_copy); cp_layout.addWidget(btn_paste)
        main_layout.addLayout(cp_layout)

        # Feature buttons
        buttons = [
            ("🎤 Música & Visual", self.activate_music_visual),
            ("🧠 IA GPT-2", self.ask_ai),
            ("📚 Biblioteca", self.open_library),
            ("📸 OCR", self.start_vision),
            ("📊 Votación", self.launch_voting),
            ("🛠️ Plugins", self.show_plugins),
            ("🌍 Misiones", self.view_missions)
        ]
        for idx, (text, cmd) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setStyleSheet("background-color: #00ffcc; color: #000; font-size: 14px; padding: 10px; border-radius: 8px;")
            btn.clicked.connect(cmd)
            grid.addWidget(btn, idx//3, idx%3)
        main_layout.addLayout(grid)

        self.setLayout(main_layout)

    def speak(self, text):
        try: self.engine.say(text); self.engine.runAndWait()
        except: pass

    def copy_text(self):
        text = self.text_input.toPlainText()
        self.clipboard.setText(text)
        self.speak("Texto copiado al portapapeles")
        QMessageBox.information(self, "Copiar", "Texto copiado exitosamente.")

    def paste_text(self):
        text = self.clipboard.text()
        self.text_input.setPlainText(text)
        self.speak("Texto pegado desde el portapapeles")
        QMessageBox.information(self, "Pegar", "Texto pegado exitosamente.")

    def activate_music_visual(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo WAV", os.path.expanduser('~'), "Audio Files (*.wav)")
        if not file_path: return
        self.speak("Reproduciendo música y mostrando visualización")
        self.vis = AudioVisualizer(file_path); self.vis.show()
        threading.Thread(target=self.vis.start).start()

    def ask_ai(self):
        question, ok = QInputDialog.getText(self, "IA GPT-2", "¿Qué deseas preguntar?")
        if not ok or not question: return
        self.speak("Procesando pregunta en GPT-2 local")
        inputs = self.tokenizer.encode(question, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=200)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        self.text_input.setPlainText(answer)
        self.copy_text()

    def open_library(self):
        QMessageBox.information(self, "Biblioteca", "Abriendo recursos...")
        lib_path = os.path.expanduser('~/XarvisLibrary'); os.makedirs(lib_path, exist_ok=True)
        webbrowser.open(f'file://{lib_path}')

    def start_vision(self):
        self.speak("Capturando pantalla para OCR")
        try: screenshot = ImageGrab.grab(); text = pytesseract.image_to_string(screenshot)
        except Exception as e: text = f"Error al capturar pantalla: {e}"
        self.text_input.setPlainText(text)
        self.copy_text()

    def launch_voting(self):
        QMessageBox.information(self, "Votación", "Abriendo votación blockchain...")
        webbrowser.open('http://localhost:5000/vote')

    def show_plugins(self):
        QMessageBox.information(self, "Plugins", "Mostrando plugins activos...")

    def view_missions(self):
        QMessageBox.information(self, "Misiones", "Cargando misiones globales...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = XarvisDashboard(); dashboard.show()
    sys.exit(app.exec_())

