from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QVBoxLayout, QToolBar,
    QSlider, QLabel, QComboBox, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt6.QtGui import QAction
from pathlib import Path
from typing import List

from audio3d.viz.scene import create_scene, available_backends
from audio3d.audio.audio_io import AudioEngine
from audio3d.audio.pipeline import DSPPipeline

AUDIO_FILTERS = "Audio (*.wav *.mp3 *.flac *.m4a *.ogg *.opus);;Todos (*)"
SUPPORTED_EXTS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"}

class AppWindow(QMainWindow):
    def __init__(self, config, initial_file=None, initial_dir=None, sine=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio 3D - Cubo sobre Piso (STFT)")
        self.resize(1200, 800)
        self.config = config
        self.source_dir = Path(config.get("source_dir")).expanduser()
        self.auto_advance = bool(config.get("auto_advance", True))

        # Backend de visualización
        self.backend_name = config.get("backend", "pyqtgraph_gl")
        self.scene = create_scene(self.backend_name)
        self.view_widget = self.scene.widget()

        # Audio + DSP
        self.audio = AudioEngine(target_samplerate=config.get("sample_rate", 48000))
        self.pipeline = DSPPipeline(
            stft_cfg=config.get("stft", {"window_size": 1024, "hop_size": 256}),
            features_cfg=config.get("features", {"log_scale": True, "smoothing": 0.8}),
            mesh_cfg=config.get("mesh", {"freq_bins": 128, "time_cols": 256, "amplitude_scale": 1.0})
        )
        self.audio.attach_dsp_queue(self.pipeline.audio_in_queue)
        self.pipeline.attach_scene(self.scene)

        # Playlist
        self.playlist: List[Path] = []
        self.play_index: int = -1

        # UI
        central = QWidget()
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(0,0,0,0)

        # Barra de herramientas
        toolbar = QToolBar("Controles")
        self.addToolBar(toolbar)

        act_open = QAction("Abrir", self)
        act_open_dir = QAction("Abrir carpeta", self)
        act_gen_sine = QAction("Generar Onda (sine)", self)
        act_play = QAction("Play", self)
        act_pause = QAction("Pausa", self)
        act_stop = QAction("Stop", self)
        act_prev = QAction("Anterior", self)
        act_next = QAction("Siguiente", self)

        toolbar.addAction(act_open)
        toolbar.addAction(act_open_dir)
        toolbar.addAction(act_gen_sine)
        toolbar.addSeparator()
        toolbar.addAction(act_play)
        toolbar.addAction(act_pause)
        toolbar.addAction(act_stop)
        toolbar.addSeparator()
        toolbar.addAction(act_prev)
        toolbar.addAction(act_next)

        # Controles inferiores
        bottom = QWidget()
        h = QHBoxLayout(bottom)
        h.setContentsMargins(8, 4, 8, 4)

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 1000)
        self.seek.setValue(0)

        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(80)
        self.vol.setFixedWidth(150)

        self.lbl_time = QLabel("00:00 / 00:00  SR: -")
        self.cbo_backend = QComboBox()
        self.cbo_backend.addItems(available_backends())
        self.cbo_backend.setCurrentText(self.backend_name)

        h.addWidget(QLabel("Posición"))
        h.addWidget(self.seek, 1)
        h.addWidget(QLabel("Volumen"))
        h.addWidget(self.vol)
        h.addWidget(QLabel("Backend"))
        h.addWidget(self.cbo_backend)
        h.addWidget(self.lbl_time)

        vbox.addWidget(self.view_widget, 1)
        vbox.addWidget(bottom, 0)
        self.setCentralWidget(central)

        # Conexiones
        act_open.triggered.connect(self.on_open)
        act_open_dir.triggered.connect(self.on_open_dir)
        act_gen_sine.triggered.connect(self.on_generate_sine)
        act_play.triggered.connect(self.on_play)
        act_pause.triggered.connect(self.on_pause)
        act_stop.triggered.connect(self.on_stop)
        act_prev.triggered.connect(self.on_prev)
        act_next.triggered.connect(self.on_next)
        self.seek.sliderMoved.connect(self.on_seek_moved)
        self.vol.valueChanged.connect(self.on_volume_changed)
        self.cbo_backend.currentTextChanged.connect(self.on_backend_changed)

        # Temporizador de UI + visual
        self.fps = int(self.config.get("fps_cap", 60))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(int(1000 / max(1, self.fps)))

        # Inicialización según CLI
        if initial_dir:
            self.load_playlist_from_dir(Path(initial_dir))
        elif sine:
            self.load_sine(freq=float(sine.get("freq", 440.0)), seconds=float(sine.get("seconds", 60.0)))
        elif initial_file:
            p = Path(initial_file).expanduser()
            if p.exists():
                self.set_playlist([p], 0)
                self.load_current()
            else:
                QMessageBox.warning(self, "Archivo no encontrado", str(p))

        # Mostrar dummy si aún no hay audio
        if not self.audio.has_audio():
            self.scene.show_dummy_heightmap()

    def on_open(self):
        start_dir = str(self.source_dir)
        file, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo de audio", start_dir, AUDIO_FILTERS
        )
        if file:
            p = Path(file)
            self.set_playlist([p], 0)
            self.load_current()

    def on_open_dir(self):
        start_dir = str(self.source_dir)
        d = QFileDialog.getExistingDirectory(self, "Abrir carpeta con canciones", start_dir)
        if d:
            self.load_playlist_from_dir(Path(d))

    def build_playlist_from_dir(self, folder: Path) -> List[Path]:
        paths = []
        try:
            for p in folder.rglob('*'):
                if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
                    paths.append(p)
        except Exception:
            pass
        paths.sort(key=lambda x: x.name.lower())
        return paths

    def set_playlist(self, paths: List[Path], start_index: int = 0):
        self.playlist = paths
        self.play_index = max(0, min(start_index, len(paths) - 1)) if paths else -1

    def load_current(self):
        if 0 <= self.play_index < len(self.playlist):
            self.load_file(self.playlist[self.play_index])

    def on_next(self):
        if not self.playlist:
            return
        if self.play_index < len(self.playlist) - 1:
            self.play_index += 1
            self.load_current()
            self.on_play()

    def on_prev(self):
        if not self.playlist:
            return
        if self.play_index > 0:
            self.play_index -= 1
            self.load_current()
            self.on_play()

    def load_playlist_from_dir(self, folder: Path):
        paths = self.build_playlist_from_dir(folder)
        if not paths:
            QMessageBox.information(self, "Vacío", "No se encontraron archivos de audio en la carpeta.")
            return
        self.set_playlist(paths, 0)
        self.load_current()

    def load_sine(self, freq: float = 440.0, seconds: float = 60.0):
        ok = self.audio.load_sine(freq=freq, seconds=seconds, amplitude=float(self.config.get("generator", {}).get("sine_amplitude", 0.5)))
        if not ok:
            QMessageBox.critical(self, "Error", "No se pudo generar la sinusoide.")
            return
        self.pipeline.reset_state(self.audio.samplerate)
        self.setWindowTitle(f"Audio 3D - Sine {freq:.1f} Hz")
        self.lbl_time.setText(f"00:00 / {self.audio.duration_str()}  SR: {self.audio.samplerate}")
        self.seek.setValue(0)

    def load_file(self, path: Path):
        ok = self.audio.load_file(path)
        if not ok:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {path}")
            return
        self.pipeline.reset_state(self.audio.samplerate)
        self.setWindowTitle(f"Audio 3D - {path.name}")
        self.lbl_time.setText(f"00:00 / {self.audio.duration_str()}  SR: {self.audio.samplerate}")
        self.seek.setValue(0)

    def on_play(self):
        self.audio.play()

    def on_pause(self):
        self.audio.pause()

    def on_stop(self):
        self.audio.stop()
        self.seek.setValue(0)

    def on_seek_moved(self, value):
        # value 0..1000
        if self.audio.duration_sec() > 0:
            t = (value / 1000.0) * self.audio.duration_sec()
            self.audio.seek_time(t)

    def on_volume_changed(self, value):
        self.audio.set_volume(value / 100.0)

    def on_backend_changed(self, name):
        if name == self.backend_name:
            return
        # recrear escena
        self.backend_name = name
        new_scene = create_scene(name)
        new_view = new_scene.widget()
        self.pipeline.attach_scene(new_scene)

        # reemplazar widget central
        layout = self.centralWidget().layout()
        layout.replaceWidget(self.view_widget, new_view)
        self.view_widget.setParent(None)
        self.scene = new_scene
        self.view_widget = new_view

    def on_generate_sine(self):
        # Pedir frecuencia
        freq, ok = QInputDialog.getDouble(self, "Onda sinusoidal", "Frecuencia (Hz)",
                                          float(self.config.get("generator", {}).get("sine_freq", 440.0)), 10.0, 20000.0, 1)
        if not ok:
            return
        secs, ok = QInputDialog.getDouble(self, "Onda sinusoidal", "Duración (segundos)",
                                          float(self.config.get("generator", {}).get("sine_seconds", 60.0)), 1.0, 6000.0, 0)
        if not ok:
            return
        self.set_playlist([], -1)
        self.load_sine(freq=freq, seconds=secs)
        self.on_play()

    def on_tick(self):
        # actualizar labels y visualizar columnas pendientes
        self.pipeline.flush_to_scene(max_columns=4)
        cur = self.audio.current_time()
        dur = self.audio.duration_sec()
        if dur > 0:
            self.seek.blockSignals(True)
            self.seek.setValue(int((cur / dur) * 1000))
            self.seek.blockSignals(False)
        self.lbl_time.setText(f"{self.audio.time_str(cur)} / {self.audio.duration_str()}  SR: {self.audio.samplerate}")
        self.scene.move_cube(cur)

        # Avance automático en playlist
        if self.auto_advance and self.playlist and self.audio.is_finished() and self.play_index < len(self.playlist) - 1:
            self.on_next()
