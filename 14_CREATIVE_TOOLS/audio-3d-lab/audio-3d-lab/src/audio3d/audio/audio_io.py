from pathlib import Path
import numpy as np
import sounddevice as sd
import librosa
import queue
import threading
import time

class AudioEngine:
    def __init__(self, target_samplerate=48000, blocksize=1024):
        self.target_sr = int(target_samplerate)
        self.blocksize = int(blocksize)
        self.data = None
        self.samplerate = None
        self.stream = None
        self.pos = 0
        self.playing = False
        self.volume = 0.8
        self._start_time_ref = None
        self._last_play_pos = 0
        self._lock = threading.Lock()
        self.dsp_queue = None  # será una queue.Queue() proporcionada por DSPPipeline

    def attach_dsp_queue(self, q):
        self.dsp_queue = q

    def has_audio(self):
        return self.data is not None

    def load_file(self, path: Path):
        try:
            y, sr = librosa.load(str(path), sr=self.target_sr, mono=True)
            y = np.asarray(y, dtype=np.float32)
            with self._lock:
                self.data = y
                self.samplerate = sr
                self.pos = 0
                self.playing = False
                self._last_play_pos = 0
            self._ensure_stream()
            return True
        except Exception as e:
            print(f"[audio] Error cargando {path}: {e}")
            return False

    def load_sine(self, freq: float = 440.0, seconds: float = 60.0, amplitude: float = 0.5):
        try:
            n = int(max(0.1, float(seconds)) * self.target_sr)
            t = np.arange(n, dtype=np.float32) / float(self.target_sr)
            y = (float(amplitude) * np.sin(2.0 * np.pi * float(freq) * t)).astype(np.float32)
            with self._lock:
                self.data = y
                self.samplerate = self.target_sr
                self.pos = 0
                self.playing = False
                self._last_play_pos = 0
            self._ensure_stream()
            return True
        except Exception as e:
            print(f"[audio] Error generando sinusoide: {e}")
            return False

    def is_finished(self) -> bool:
        with self._lock:
            if self.data is None or self.samplerate is None:
                return False
            return (not self.playing) and (self.pos >= len(self.data))

    def _ensure_stream(self):
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        if self.samplerate is None:
            return
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="float32",
            blocksize=self.blocksize,
            callback=self._callback,
        )
        self.stream.start()
        self.playing = False

    def _callback(self, outdata, frames, time_info, status):
        if status:
            # Underrun/overrun info
            pass
        with self._lock:
            if not self.playing or self.data is None:
                outdata[:] = 0
                return
            end = self.pos + frames
            segment = self.data[self.pos:end]
            if len(segment) < frames:
                padded = np.zeros((frames,), dtype=np.float32)
                padded[:len(segment)] = segment
                segment = padded
                # al finalizar, detener reproducción
                self.playing = False
            self.pos = min(end, len(self.data))
        # Salida con volumen
        outdata[:, 0] = segment * float(self.volume)
        # Encolar para DSP (no bloquear en callback)
        if self.dsp_queue is not None:
            try:
                self.dsp_queue.put_nowait(segment.copy())
            except queue.Full:
                pass

    def play(self):
        if self.stream is None or self.data is None:
            return
        with self._lock:
            self.playing = True
            self._start_time_ref = time.time()
            self._last_play_pos = self.pos

    def pause(self):
        with self._lock:
            self.playing = False

    def stop(self):
        with self._lock:
            self.playing = False
            self.pos = 0

    def seek_time(self, t_sec: float):
        if self.data is None or self.samplerate is None:
            return
        with self._lock:
            idx = int(np.clip(t_sec, 0, self.duration_sec()) * self.samplerate)
            self.pos = min(idx, len(self.data))
            self._last_play_pos = self.pos
            self._start_time_ref = time.time()

    def set_volume(self, v: float):
        self.volume = max(0.0, min(1.0, float(v)))

    def duration_sec(self):
        if self.data is None or self.samplerate is None:
            return 0.0
        return len(self.data) / float(self.samplerate)

    def current_time(self):
        with self._lock:
            if not self.playing:
                return self.pos / float(self.samplerate or 1)
            # estimación basada en frames reproducidos desde _start_time_ref
            elapsed = time.time() - (self._start_time_ref or time.time())
            est_pos = self._last_play_pos + int(elapsed * (self.samplerate or 1))
            est_pos = max(0, min(est_pos, len(self.data or [])))
            return est_pos / float(self.samplerate or 1)

    def duration_str(self):
        return self.time_str(self.duration_sec())

    @staticmethod
    def time_str(t):
        t = int(t)
        m, s = divmod(t, 60)
        return f"{m:02d}:{s:02d}"
