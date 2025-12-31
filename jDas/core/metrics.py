import numpy as np


def calculate_snr(clean: np.ndarray, noisy: np.ndarray) -> float:
    """Signal-to-Noise Ratio в dB"""
    signal_power = np.mean(clean**2)
    noise_power = np.mean((clean - noisy) ** 2)
    return 10 * np.log10(signal_power / noise_power)


def calculate_psnr(clean: np.ndarray, noisy: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio"""
    mse = np.mean((clean - noisy) ** 2)
    max_pixel = np.max(clean)
    return 20 * np.log10(max_pixel / np.sqrt(mse))


def calculate_mse(clean: np.ndarray, noisy: np.ndarray) -> float:
    """Mean Squared Error"""
    return np.mean((clean - noisy) ** 2)
