import numpy as np
from scipy.signal import get_window

class STFTProcessor:
    def __init__(self, n_fft=1024, hop=256, window="hann"):
        self.n_fft = int(n_fft)
        self.hop = int(hop)
        self.window_name = window
        self.win = get_window(window, self.n_fft, fftbins=True).astype(np.float32)
        self.buffer = np.zeros((0,), dtype=np.float32)
        self.sr = 48000

    def reset(self, samplerate: int):
        self.sr = int(samplerate)
        self.buffer = np.zeros((0,), dtype=np.float32)

    def process_block(self, block: np.ndarray):
        # Acumular y computar STFT por hopping
        if block.ndim != 1:
            block = block.reshape(-1)
        self.buffer = np.concatenate([self.buffer, block.astype(np.float32)], axis=0)
        frames = []
        i = 0
        while i + self.n_fft <= len(self.buffer):
            frame = self.buffer[i:i+self.n_fft]
            windowed = frame * self.win
            spec = np.fft.rfft(windowed, n=self.n_fft)
            mag = np.abs(spec)
            frames.append(mag)
            i += self.hop
        # Desplazar buffer (mantener solapamiento)
        if i > 0:
            self.buffer = self.buffer[i:]
        if not frames:
            return np.zeros((0, 0), dtype=np.float32)
        mats = np.stack(frames, axis=1)  # (freq_bins, n_frames)
        return mats.astype(np.float32)
