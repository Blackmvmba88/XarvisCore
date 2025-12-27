import numpy as np
from typing import Optional

def log_magnitude(col: np.ndarray, eps=1e-7):
    return np.log1p(np.maximum(col, 0.0) + eps)

def smooth_column(col: np.ndarray, prev: Optional[np.ndarray], alpha=0.8):
    if prev is None:
        return col
    alpha = float(alpha)
    return alpha * prev + (1.0 - alpha) * col
