"""Player package for the Quantum Audio Player.

This package contains the PyQt6 user interface and the simulated quantum
digital‑to‑analog converter (DAC) and digital signal processing (DSP) engine.
"""

from .ui import QuantumAudioPlayer  # noqa: F401
from .quantum_engine import QuantumDAC  # noqa: F401