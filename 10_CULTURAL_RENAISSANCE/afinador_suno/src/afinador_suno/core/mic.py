from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import torch
import torchcrepe


@dataclass
class PitchFrame:
    t_s: float
    f0_hz: float
    voiced: bool
    rms: float
    pd: float  # periodicity confidence (0..1)


class MicPitchDetector:
    def __init__(self, sr: int = 16000, hop_ms: int = 10) -> None:
        self.sr = sr
        self.hop = int(sr * (hop_ms / 1000.0))
        self._buf = deque(maxlen=sr * 2)  # ~2s
        self._frames: deque[PitchFrame] = deque(maxlen=512)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._on_frame: Optional[Callable[[PitchFrame], None]] = None
        # Voice gating helpers
        self.noise_rms: float = 0.0
        self._last_rms: float = 0.0

    def start(self, on_frame: Optional[Callable[[PitchFrame], None]] = None) -> None:
        self.stop()
        self._stop.clear()
        self._on_frame = on_frame
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    # Calibration: set baseline noise RMS based on recent buffer
    def calibrate_noise(self) -> float:
        val = self._last_rms
        self.noise_rms = val
        return val

    def get_noise_rms(self) -> float:
        return self.noise_rms

    def _run(self) -> None:
        # Por estabilidad, forzamos CPU en RT
        device = "cpu"
        model = "tiny"  # RT-friendly
        hop = self.hop

        def audio_cb(indata, frames, time_info, status):
            mono = np.mean(indata, axis=1).astype(np.float32)
            self._buf.extend(mono.tolist())

        with sd.InputStream(channels=1, samplerate=self.sr, dtype='float32', callback=audio_cb):
            x_win = int(self.sr * 0.1)  # 100 ms ventana
            last_buf_len = 0
            last_pred = 0.0
            torch.set_num_threads(1)
            while not self._stop.is_set():
                now = time.time()
                if len(self._buf) >= x_win and (len(self._buf) - last_buf_len) >= hop and (now - last_pred) >= 0.075:
                    last_buf_len = len(self._buf)
                    last_pred = now
                    x = np.array(list(self._buf)[-x_win:], dtype=np.float32)
                    rms = float(np.sqrt(np.mean(x ** 2)))
                    self._last_rms = rms
                    xt = torch.tensor(x, dtype=torch.float32, device=device).unsqueeze(0)
                    with torch.inference_mode():
                        f0, pd = torchcrepe.predict(
                            xt,
                            self.sr,
                            hop,
                            fmin=50.0,
                            fmax=1000.0,
                            model=model,
                            batch_size=48,
                            device=device,
                            return_periodicity=True,
                        )
                        pd = torchcrepe.filter.median(pd, 3)
                        f0 = torchcrepe.filter.mean(f0, 3)
                        pd_mean = float(pd.mean().item())
                        voiced = bool(pd_mean >= 0.7)
                        f0_val = float(f0.mean().item()) if voiced else 0.0
                    t_s = time.time()
                    frame = PitchFrame(t_s=t_s, f0_hz=f0_val, voiced=voiced, rms=rms, pd=pd_mean)
                    self._frames.append(frame)
                    if self._on_frame:
                        self._on_frame(frame)
                time.sleep(hop / self.sr)
