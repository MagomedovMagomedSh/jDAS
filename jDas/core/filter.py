import numpy as np
from scipy.signal import butter, filtfilt


def bandpass_filter(
    data: np.ndarray,
    low_freq: float = 10.0,
    high_freq: float = 100.0,
    sample_rate: float = 1000.0,
) -> np.ndarray:
    """Bandpass фильтр 10-100 Hz"""
    nyquist = 0.5 * sample_rate
    low = low_freq / nyquist
    high = high_freq / nyquist
    b, a = butter(4, [low, high], btype="band")

    # Применяем к каждому каналу
    filtered = np.zeros_like(data)
    for i in range(data.shape[0]):
        filtered[i] = filtfilt(b, a, data[i])

    return filtered
