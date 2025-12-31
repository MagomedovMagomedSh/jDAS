from pathlib import Path

import numpy as np
import obspy


def load_mseed_files(folder_path: Path) -> np.ndarray:
    """Загружает каналы 647-771 из mseed файлов"""
    data = []
    for channel in range(647, 772):
        pattern = f"{channel:05d}.HSF.TW..*.mseed"
        files = list(folder_path.glob(pattern))
        if files:
            st = obspy.read(str(files[0]))
            # Преобразуем в numpy array
            channel_data = st[0].data.astype(np.float32)
            data.append(channel_data)

    # Объединяем каналы
    return np.stack(data)  # [channels, time_samples]
