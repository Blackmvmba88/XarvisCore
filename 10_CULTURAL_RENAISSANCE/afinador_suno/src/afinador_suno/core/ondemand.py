from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import librosa
import numpy as np
import torch
import torchcrepe


@dataclass
class F0Chunk:
    start_s: float
    hop_s: float
    f0: np.ndarray  # shape (n_frames,)


class OnDemandF0:
    def __init__(self, path: Path, hop_s: float = 0.02, sr: int = 16000, model: str = "tiny") -> None:
        self.path = Path(path)
        self.hop_s = hop_s
        self.sr = sr
        self.model = model
        self.device = "cpu"
        self.window_s = 5.0  # tamaño de chunk
        self.pad_s = 0.5     # pad para bordes

    @lru_cache(maxsize=64)
    def get_chunk(self, chunk_idx: int) -> F0Chunk:
        start = max(0.0, chunk_idx * self.window_s - self.pad_s)
        duration = self.window_s + 2 * self.pad_s
        y, sr = librosa.load(str(self.path), sr=self.sr, mono=True, offset=start, duration=duration)
        hop_length = int(sr * self.hop_s)
        x = torch.tensor(y, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.inference_mode():
            f0, pd = torchcrepe.predict(x, sr, hop_length, fmin=50.0, fmax=1000.0, model=self.model, batch_size=64, device=self.device, return_periodicity=True)
            pd = torchcrepe.filter.median(pd, 3)
            f0 = torchcrepe.filter.mean(f0, 3)
            f0[pd < 0.5] = 0.0
        f0_np = f0.squeeze(0).detach().cpu().numpy()
        return F0Chunk(start_s=start, hop_s=self.hop_s, f0=f0_np)

    def f0_at(self, t: float) -> float:
        idx = int(t // self.window_s)
        chunk = self.get_chunk(idx)
        local_t = t - chunk.start_s
        frame = int(max(0, local_t / chunk.hop_s))
        if frame < 0 or frame >= len(chunk.f0):
            return 0.0
        return float(chunk.f0[frame])