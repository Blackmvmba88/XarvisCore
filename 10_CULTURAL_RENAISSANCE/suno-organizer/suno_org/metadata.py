from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from mutagen import File as MutagenFile


@dataclass
class AudioMeta:
    duration_sec: Optional[float]
    sample_rate: Optional[int]
    channels: Optional[int]
    bitrate: Optional[int]
    codec: Optional[str]
    tags: Dict[str, Any]


def extract_audio_meta(path: Path) -> AudioMeta:
    try:
        m = MutagenFile(path)
        if not m:
            return AudioMeta(None, None, None, None, None, {})
        duration = float(getattr(m.info, "length", None)) if getattr(m, "info", None) else None
        sample_rate = int(getattr(m.info, "sample_rate", 0)) or None if getattr(m, "info", None) else None
        channels = int(getattr(m.info, "channels", 0)) or None if getattr(m, "info", None) else None
        bitrate = int(getattr(m.info, "bitrate", 0)) or None if getattr(m, "info", None) else None
        codec = type(m.info).__name__ if getattr(m, "info", None) else None
        tags = {}
        if m.tags:
            for k, v in m.tags.items():
                try:
                    tags[str(k)] = str(v)
                except Exception:
                    tags[str(k)] = repr(v)
        return AudioMeta(duration, sample_rate, channels, bitrate, codec, tags)
    except Exception:
        return AudioMeta(None, None, None, None, None, {})


def is_suno_like(file_path: Path, meta: AudioMeta) -> tuple[bool, str]:
    # Heurística: buscar "suno" en tags o nombre de archivo
    name = file_path.name.lower()
    needles = ["suno", "suno ai", "suno.ai"]
    # en tags: artist, album, title, encoder, comment, description
    candidates = []
    if meta and meta.tags:
        for k in ("artist", "album", "title", "encoder", "encodedby", "comment", "description"):
            for tk, tv in meta.tags.items():
                if k in tk.lower() and isinstance(tv, str):
                    candidates.append(tv.lower())
    hay = name + " " + " ".join(candidates)
    for n in needles:
        if n in hay:
            return True, f"match:{n}"
    # como respaldo, patrones de nombre comunes: Verso, Cover, Arantza, etc. (no determinista)
    generic_tokens = ["verso", "cover"]
    for n in generic_tokens:
        if n in name:
            return True, f"heuristic:{n}"
    return False, ""
