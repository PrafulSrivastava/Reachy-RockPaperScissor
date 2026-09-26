"""Microphone voice-activity check. Any sustained sound can start a round."""

from typing import Sequence

import numpy as np


def voice_active(samples: Sequence[float] | np.ndarray | None, threshold: float = 0.02) -> bool:
    """True when the chunk's RMS is above the threshold."""
    if samples is None:
        return False
    values = np.asarray(samples, dtype=np.float32)
    if values.size == 0:
        return False
    rms = float(np.sqrt(np.mean(np.square(values))))
    return rms > threshold
