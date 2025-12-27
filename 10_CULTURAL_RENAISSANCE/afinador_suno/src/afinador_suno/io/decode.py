from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import ffmpeg

CACHE_DIR = Path(__file__).resolve().parents[2] / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_ANALYSIS = CACHE_DIR / "mono16k"
CACHE_ANALYSIS.mkdir(parents=True, exist_ok=True)


def ensure_analysis_mono16k(src: Path) -> Path:
    """Decode src into MONO 16 kHz WAV for analysis and cache it.
    Returns path to mono16k wav.
    """
    assert src.exists(), f"No existe el archivo: {src}"
    safe_id = src.stem  # simple id; se puede mejorar con hash si hay colisiones
    mono = CACHE_ANALYSIS / f"{safe_id}_mono_16k.wav"
    if not mono.exists():
        (
            ffmpeg
            .input(str(src))
            .output(str(mono), ac=1, ar=16000, format="wav")
            .overwrite_output()
            .run(quiet=True)
        )
    return mono
