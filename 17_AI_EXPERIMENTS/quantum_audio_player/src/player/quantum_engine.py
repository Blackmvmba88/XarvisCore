"""Simulated quantum digital‑to‑analog converter (DAC) and DSP engine.

This module provides the :class:`QuantumDAC` class, which applies a band‑pass
filter and dynamic range normalisation to input audio data.  The goal is to
emulate the purity and precision of a hypothetical quantum DAC by removing
out‑of‑band noise and scaling the signal appropriately.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, lfilter


class QuantumDAC:
    """Quantum‑inspired digital‑to‑analog converter.

    Parameters
    ----------
    low_cut : float
        The lower cutoff frequency in Hz for the band‑pass filter.
    high_cut : float
        The upper cutoff frequency in Hz for the band‑pass filter.
    order : int
        The order of the Butterworth filter.  Higher orders result in a
        steeper filter slope.
    """

    def __init__(self, low_cut: float = 20.0, high_cut: float = 20000.0, order: int = 4) -> None:
        self.low_cut = low_cut
        self.high_cut = high_cut
        self.order = order

    def _bandpass_filter(self, data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply a Butterworth band‑pass filter to the data.

        The filter removes frequencies below ``low_cut`` and above ``high_cut``.

        Parameters
        ----------
        data : ndarray
            Input audio samples as a 1‑D or 2‑D NumPy array.
        sample_rate : int
            Sampling rate of the audio in Hz.

        Returns
        -------
        ndarray
            Filtered audio samples with the same shape as the input.
        """
        nyq = 0.5 * sample_rate
        low = self.low_cut / nyq
        high = self.high_cut / nyq
        b, a = butter(self.order, [low, high], btype="band", analog=False)
        if data.ndim == 1:
            return lfilter(b, a, data)
        # Apply filter to each channel separately
        return np.stack([lfilter(b, a, channel) for channel in data.T], axis=1)

    def process(self, data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio data through the quantum‑inspired DAC pipeline.

        This function normalises the input to a consistent dynamic range and
        applies a band‑pass filter.  The result aims to reduce harmonic
        distortion and out‑of‑band noise, simulating a quantum DAC.

        Parameters
        ----------
        data : ndarray
            Input audio samples as floating‑point values in the range ``[-1.0, 1.0]``.
            The shape may be ``(n_samples,)`` for mono or ``(n_samples, n_channels)`` for multi‑channel audio.
        sample_rate : int
            Sampling rate of the audio in Hz.

        Returns
        -------
        ndarray
            Processed audio samples with the same shape as the input.
        """
        # Normalise to unit dynamic range
        max_amp = np.max(np.abs(data))
        if max_amp > 0:
            data = data / max_amp

        # Apply band‑pass filter
        filtered = self._bandpass_filter(data, sample_rate)
        return filtered