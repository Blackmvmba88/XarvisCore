"""PyQt6 user interface for the Quantum Audio Player.

The :class:`QuantumAudioPlayer` window allows users to load a WAV file,
process it with the simulated quantum DAC, and play it with adjustable volume.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

import numpy as np
import simpleaudio as sa
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .quantum_engine import QuantumDAC


class QuantumAudioPlayer(QMainWindow):
    """Main window for the Quantum Audio Player application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Quantum Audio Player")
        self.resize(400, 200)

        # UI elements
        self.label = QLabel("No file loaded")
        self.load_btn = QPushButton("Load")
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.volume_slider)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Configure UI
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)

        # Connect signals
        self.load_btn.clicked.connect(self.load_file)
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.stop_audio)

        # Audio state
        self.dac = QuantumDAC()
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: Optional[int] = None
        self.num_channels: Optional[int] = None
        self.play_obj: Optional[sa.PlayObject] = None

        # Thread lock for play/stop operations
        self._play_lock = threading.Lock()

    def load_file(self) -> None:
        """Open a file dialog and load a WAV file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open WAV file", "", "WAV Files (*.wav)")
        if not file_path:
            return
        path = Path(file_path)
        try:
            import wave

            with wave.open(path.as_posix(), "rb") as wf:
                self.num_channels = wf.getnchannels()
                self.sample_rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                # Convert to numpy array of int16
                audio_array = np.frombuffer(frames, dtype=np.int16)
                # Reshape for channels
                if self.num_channels > 1:
                    audio_array = audio_array.reshape(-1, self.num_channels)
                # Convert to float32 in range [-1, 1]
                audio_float = audio_array.astype(np.float32) / 32768.0
                # Process through quantum DAC
                processed = self.dac.process(audio_float, self.sample_rate)
                # Flatten and convert back to int16
                processed_flat = processed
                if self.num_channels > 1:
                    processed_flat = processed_flat.reshape(-1)
                processed_int16 = np.int16(np.clip(processed_flat * 32768, -32768, 32767))
                self.audio_data = processed_int16

            self.label.setText(f"Loaded: {path.name}")
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        except Exception as exc:
            self.label.setText(f"Error loading file: {exc}")

    def _playback_thread(self, audio_bytes: bytes) -> None:
        """Internal method to play audio in a separate thread."""
        with self._play_lock:
            self.play_obj = sa.play_buffer(audio_bytes, self.num_channels or 1, 2, self.sample_rate or 44100)
            self.play_obj.wait_done()
            self.play_obj = None
            # Reset stop button when done
            self.stop_btn.setEnabled(False)

    def play_audio(self) -> None:
        """Play the loaded audio with volume adjustment."""
        if self.audio_data is None or self.num_channels is None or self.sample_rate is None:
            return
        # Apply volume
        volume = self.volume_slider.value() / 100.0
        audio_scaled = (self.audio_data.astype(np.float32) * volume).astype(np.int16)
        audio_bytes = audio_scaled.tobytes()
        self.stop_btn.setEnabled(True)
        # Start playback in a new thread to avoid blocking the UI
        threading.Thread(target=self._playback_thread, args=(audio_bytes,), daemon=True).start()

    def stop_audio(self) -> None:
        """Stop audio playback if it is in progress."""
        with self._play_lock:
            if self.play_obj is not None:
                self.play_obj.stop()
                self.play_obj = None
            self.stop_btn.setEnabled(False)