from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..util.music import hz_to_midi, midi_to_hz


def delta_cents(user_hz: float, target_hz: float, a4_hz: float = 440.0) -> float:
    if user_hz <= 0 or target_hz <= 0:
        return float("nan")
    import math
    return 1200.0 * math.log2(user_hz / target_hz)
