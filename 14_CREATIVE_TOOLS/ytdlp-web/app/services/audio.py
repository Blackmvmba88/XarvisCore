from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path


def shift_pitch(source: Path, destination: Path, semitones: float, ffmpeg_path: str = "ffmpeg") -> None:
    """Shift the pitch of the provided audio file using ffmpeg filters."""

    destination.parent.mkdir(parents=True, exist_ok=True)

    if abs(semitones) < 1e-6:
        shutil.copyfile(source, destination)
        return

    pitch_factor = math.pow(2.0, semitones / 12.0)
    atempo = 1.0 / pitch_factor

    filter_chain = f"asetrate=44100*{pitch_factor:.6f},aresample=44100,atempo={atempo:.6f}"

    cmd = [
        ffmpeg_path,
        "-y",
        "-i",
        str(source),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-filter:a",
        filter_chain,
        str(destination),
    ]

    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(
            "ffmpeg no pudo procesar el audio", process.stderr  # type: ignore[arg-type]
        )
