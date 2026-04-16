from __future__ import annotations

import math
from typing import Tuple

NOTE_NAMES_SHARP = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
]


def hz_to_midi(f_hz: float) -> float:
    if f_hz <= 0 or math.isnan(f_hz) or math.isinf(f_hz):
        return float("nan")
    return 69.0 + 12.0 * math.log2(f_hz / 440.0)


def midi_to_hz(m: float, a4_hz: float = 440.0) -> float:
    return a4_hz * (2.0 ** ((m - 69.0) / 12.0))


def midi_to_note_name(m: float) -> Tuple[str, int]:
    n = int(round(m))
    name = NOTE_NAMES_SHARP[n % 12]
    octave = n // 12 - 1
    return name, octave


def hz_to_name_and_cents(f_hz: float, a4_hz: float = 440.0) -> Tuple[str, int, float]:
    """Return (note_name, octave, cents_delta) for a frequency.

    cents_delta is positive if f_hz is above the nearest tempered note.
    """
    m = hz_to_midi(f_hz)
    if math.isnan(m):
        return ("-", 0, float("nan"))
    n_round = round(m)
    f_ref = midi_to_hz(n_round, a4_hz=a4_hz)
    cents = 1200.0 * math.log2(f_hz / f_ref)
    name, octave = midi_to_note_name(n_round)
    return name, octave, cents
