from __future__ import annotations

import queue
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
import subprocess
import shutil


class Player:
    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._t0: Optional[float] = None
        self._on_position: Optional[Callable[[float], None]] = None

    def play(self, audio_path: Path, on_position: Optional[Callable[[float], None]] = None) -> None:
        assert audio_path.exists(), f"No existe archivo: {audio_path}"
        if self._thread and self._thread.is_alive():
            self.stop()
        self._stop.clear()
        self._on_position = on_position
        self._thread = threading.Thread(target=self._run, args=(audio_path,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._t0 = None

    def _run(self, audio_path: Path) -> None:
        self._t0 = time.monotonic()
        q = queue.Queue(maxsize=8)
        ended = threading.Event()
        read_block = 1024
        samplerate = 44100
        channels = 2

        def producer_wav(f: sf.SoundFile):
            try:
                while not self._stop.is_set():
                    data = f.read(read_block, dtype='float32', always_2d=True)
                    if data.size == 0:
                        break
                    try:
                        q.put(data, timeout=0.5)
                    except queue.Full:
                        pass
            finally:
                try:
                    q.put(None, timeout=0.5)
                except queue.Full:
                    pass
                ended.set()

        def producer_ffmpeg():
            # Decode to float32 stereo 44.1k via ffmpeg piping
            cmd = [
                shutil.which('ffmpeg') or 'ffmpeg',
                '-v', 'error', '-nostdin',
                '-i', str(audio_path),
                '-f', 'f32le', '-acodec', 'pcm_f32le', '-ac', '2', '-ar', '44100',
                'pipe:1'
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            frame_bytes = 4 * channels  # float32 per sample * channels
            chunk_frames = read_block
            chunk_bytes = chunk_frames * frame_bytes
            try:
                while not self._stop.is_set():
                    buf = proc.stdout.read(chunk_bytes)
                    if not buf or len(buf) == 0:
                        break
                    arr = np.frombuffer(buf, dtype=np.float32)
                    if arr.size == 0:
                        break
                    arr = arr.reshape((-1, channels))
                    try:
                        q.put(arr, timeout=0.5)
                    except queue.Full:
                        pass
            finally:
                try:
                    q.put(None, timeout=0.5)
                except queue.Full:
                    pass
                ended.set()
                try:
                    proc.kill()
                except Exception:
                    pass

        # Decide backend
        if audio_path.suffix.lower() == '.wav':
            with sf.SoundFile(str(audio_path), mode='r') as f:
                samplerate = f.samplerate
                channels = f.channels
                prod_th = threading.Thread(target=producer_wav, args=(f,), daemon=True)
                prod_th.start()
                self._stream_loop(q, ended, channels, samplerate, read_block)
        else:
            prod_th = threading.Thread(target=producer_ffmpeg, daemon=True)
            prod_th.start()
            self._stream_loop(q, ended, channels, samplerate, read_block)
        self._t0 = None

    def _stream_loop(self, q: "queue.Queue[np.ndarray]", ended: threading.Event, channels: int, samplerate: int, read_block: int) -> None:
        buf = np.zeros((0, channels), dtype='float32')

        def callback(outdata, frames, time_info, status):
            nonlocal buf
            needed = frames
            while buf.shape[0] < needed and not ended.is_set():
                try:
                    nxt = q.get_nowait()
                except queue.Empty:
                    break
                if nxt is None:
                    ended.set()
                    break
                buf = nxt if buf.shape[0] == 0 else np.concatenate((buf, nxt), axis=0)
            if buf.shape[0] >= needed:
                out = buf[:needed, :]
                buf = buf[needed:, :]
            else:
                out = np.zeros((needed, channels), dtype='float32')
                if buf.shape[0] > 0:
                    out[:buf.shape[0], :] = buf
                    buf = np.zeros((0, channels), dtype='float32')
            outdata[:] = out

        with sd.OutputStream(channels=channels, samplerate=samplerate, dtype='float32', callback=callback, blocksize=read_block):
            while not self._stop.is_set() and (not ended.is_set() or buf.shape[0] > 0):
                if self._on_position and self._t0 is not None:
                    t = time.monotonic() - self._t0
                    self._on_position(t)
                time.sleep(0.02)
