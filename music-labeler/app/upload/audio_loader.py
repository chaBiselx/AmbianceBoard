from math import gcd

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


def load_audio(path: str, target_sr: int, mono: bool = True) -> tuple[np.ndarray, int]:
    """Charge un fichier audio, le convertit en mono et resample si necessaire."""
    audio, source_sr = sf.read(path, always_2d=True, dtype="float32")

    if mono:
        processed = audio.mean(axis=1)
    else:
        processed = audio.T

    if source_sr != target_sr:
        ratio_gcd = gcd(source_sr, target_sr)
        up = target_sr // ratio_gcd
        down = source_sr // ratio_gcd
        processed = resample_poly(processed, up, down)

    return np.asarray(processed, dtype=np.float32), target_sr