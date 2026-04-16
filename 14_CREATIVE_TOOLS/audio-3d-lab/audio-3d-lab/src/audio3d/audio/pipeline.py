import numpy as np
import queue
import threading

from audio3d.dsp.stft import STFTProcessor
from audio3d.dsp.features import log_magnitude, smooth_column

class DSPPipeline:
    def __init__(self, stft_cfg, features_cfg, mesh_cfg):
        self.audio_in_queue = queue.Queue(maxsize=64)
        self.col_queue = queue.Queue(maxsize=128)
        self.scene = None
        self.stft = STFTProcessor(
            n_fft=int(stft_cfg.get("window_size", 1024)),
            hop=int(stft_cfg.get("hop_size", 256))
        )
        self.log_scale = bool(features_cfg.get("log_scale", True))
        self.smoothing = float(features_cfg.get("smoothing", 0.8))
        self.freq_bins = int(mesh_cfg.get("freq_bins", 128))
        self.time_cols = int(mesh_cfg.get("time_cols", 256))
        self.amplitude_scale = float(mesh_cfg.get("amplitude_scale", 1.0))
        self._worker = None
        self._running = False

    def attach_scene(self, scene):
        self.scene = scene

    def reset_state(self, samplerate: int):
        self.stft.reset(samplerate)
        self._ensure_worker()

    def _ensure_worker(self):
        if self._worker and self._worker.is_alive():
            return
        self._running = True
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    def stop(self):
        self._running = False

    def _loop(self):
        prev_col = None
        while self._running:
            try:
                block = self.audio_in_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            cols = self.stft.process_block(block)  # shape: (freq_bins_full, n_frames)
            if cols.size == 0:
                continue
            # Reducir a freq_bins deseados (por ejemplo, recorte o promedio)
            full_bins = cols.shape[0]
            if self.freq_bins < full_bins:
                factor = full_bins // self.freq_bins
                cols = cols[:factor*self.freq_bins, :]
                cols = cols.reshape(self.freq_bins, factor, cols.shape[1]).mean(axis=1)
            elif self.freq_bins > full_bins:
                # padding simple
                pad = self.freq_bins - full_bins
                cols = np.pad(cols, ((0, pad), (0, 0)), mode="edge")

            for i in range(cols.shape[1]):
                col = cols[:, i]
                if self.log_scale:
                    col = log_magnitude(col)
                col = smooth_column(col, prev_col, alpha=self.smoothing)
                prev_col = col
                col = np.clip(col * self.amplitude_scale, 0.0, 1.0)
                try:
                    self.col_queue.put_nowait(col.astype(np.float32))
                except queue.Full:
                    pass

    def flush_to_scene(self, max_columns=4):
        if self.scene is None:
            return
        for _ in range(max_columns):
            try:
                col = self.col_queue.get_nowait()
            except queue.Empty:
                break
            self.scene.append_heightmap_column(col)
