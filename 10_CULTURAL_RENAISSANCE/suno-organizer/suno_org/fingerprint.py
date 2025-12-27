from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Fingerprint:
    algo: str
    fp: Optional[str]
    duration: Optional[float]


def has_fpcalc() -> bool:
    return shutil.which("fpcalc") is not None


def fingerprint_chromaprint(path: Path) -> Fingerprint:
    """Usa fpcalc -json si está disponible. Devuelve huella y duración.
    Si falla, devuelve Fingerprint(algo="chromaprint", fp=None, duration=None).
    """
    if not has_fpcalc():
        return Fingerprint("chromaprint", None, None)
    try:
        # fpcalc -json FILE
        res = subprocess.run([
            "fpcalc", "-json", str(path)
        ], capture_output=True, text=True, check=True)
        data = json.loads(res.stdout.strip()) if res.stdout.strip() else {}
        fp = data.get("fingerprint")
        dur = data.get("duration")
        try:
            dur = float(dur) if dur is not None else None
        except Exception:
            pass
        return Fingerprint("chromaprint", fp, dur)
    except Exception:
        return Fingerprint("chromaprint", None, None)
