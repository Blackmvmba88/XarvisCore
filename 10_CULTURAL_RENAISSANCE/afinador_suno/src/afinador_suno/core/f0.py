from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import librosa
import numpy as np
import torch
import torchcrepe
import os


@dataclass
class AnalysisResult:
    sr: int
    hop_s: float
    a4_hz: float
    f0_hz: List[float]

    def to_json(self) -> Dict:
        return {
            "sr": self.sr,
            "hop_s": self.hop_s,
            "a4_hz": self.a4_hz,
            "f0_hz": self.f0_hz,
        }


def extract_f0_offline(
    wav_mono_44k: Path,
    hop_s: float = 0.010,
    a4_hz: float = 440.0,
    model: str = "full",
    resample_sr: int = 16000,
    fmin: float = 50.0,
    fmax: float = 1000.0,
) -> AnalysisResult:
    """Extrae F0 frame a frame con torchcrepe.

    Parámetros clave:
    - model: "full" (preciso) o "tiny" (rápido)
    - hop_s: 0.01 (preciso) o 0.02 (rápido)
    - resample_sr: típicamente 16000.
    """
    assert wav_mono_44k.exists(), f"No existe WAV: {wav_mono_44k}"

    y, sr = librosa.load(str(wav_mono_44k), sr=resample_sr, mono=True)
    hop_length = int(sr * hop_s)

    # Por estabilidad en macOS, preferimos CPU por defecto; habilitar MPS sólo si AFINADOR_USE_MPS=1
    use_mps = os.environ.get("AFINADOR_USE_MPS") == "1"
    device = "mps" if (use_mps and torch.backends.mps.is_available()) else ("cuda" if torch.cuda.is_available() else "cpu")

    x = torch.tensor(y, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.inference_mode():
        f0, pd = torchcrepe.predict(
            x,
            sr,
            hop_length,
            fmin=fmin,
            fmax=fmax,
            model=model,
            batch_size=1024 if model == "full" else 256,
            device=device,
            return_periodicity=True,
        )
        # post-proceso básico
        pd = torchcrepe.filter.median(pd, 3)
        f0 = torchcrepe.filter.mean(f0, 3)
        f0[pd < 0.5] = 0.0
    f0_np = f0.squeeze(0).detach().cpu().numpy().astype(float).tolist()

    return AnalysisResult(sr=sr, hop_s=hop_s, a4_hz=a4_hz, f0_hz=f0_np)


def save_analysis_json(result: AnalysisResult, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_json()), encoding="utf-8")
