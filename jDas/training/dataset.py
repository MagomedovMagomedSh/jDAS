from pathlib import Path
from typing import Tuple

import numpy as np
import obspy
import torch
from omegaconf import DictConfig
from torch.utils.data import DataLoader, Dataset


class DASDataset(Dataset):
    """Датасет для DAS данных с добавлением шума"""

    def __init__(self, data_path: Path, channels: Tuple[int, int] = (647, 771)):
        self.data_path = Path(data_path)
        self.channels = channels
        self.data = self._load_data()

    def _load_data(self) -> np.ndarray:
        """Загружает все каналы и конкатенирует по времени"""
        all_data = []
        for channel in range(self.channels[0], self.channels[1] + 1):
            pattern = f"{channel:05d}.HSF.TW..*.mseed"
            files = list(self.data_path.glob(pattern))
            if files:
                st = obspy.read(str(files[0]))
                channel_data = st[0].data.astype(np.float32)
                all_data.append(channel_data)

        # [channels, time_samples]
        return np.stack(all_data) if all_data else np.array([])

    def __len__(self) -> int:
        return self.data.shape[1] - 1000  # минус размер окна

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Возвращает noisy и clean пары"""
        window_size = 1000

        # Вырезаем окно
        clean_window = self.data[:, idx : idx + window_size]

        # Добавляем шум для обучения
        noise_level = 0.1
        noise = noise_level * np.random.randn(*clean_window.shape)
        noisy_window = clean_window + noise

        # Нормализуем
        clean_window = self._normalize(clean_window)
        noisy_window = self._normalize(noisy_window)

        # Конвертируем в тензоры [1, channels, time]
        clean_tensor = torch.FloatTensor(clean_window).unsqueeze(0)
        noisy_tensor = torch.FloatTensor(noisy_window).unsqueeze(0)

        return noisy_tensor, clean_tensor

    def _normalize(self, data: np.ndarray) -> np.ndarray:
        """Нормализация данных"""
        return (data - np.mean(data)) / (np.std(data) + 1e-8)


def create_dataloaders(cfg: DictConfig) -> Tuple[DataLoader, DataLoader]:
    """Создаёт DataLoader'ы для обучения и валидации"""
    dataset = DASDataset(
        data_path=Path(cfg.data.path),
        channels=(cfg.data.channels[0], cfg.data.channels[1]),
    )

    # Разделяем на train/val
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )

    train_loader = DataLoader(
        train_dataset, batch_size=cfg.model.batch_size, shuffle=True, num_workers=2
    )

    val_loader = DataLoader(
        val_dataset, batch_size=cfg.model.batch_size, shuffle=False, num_workers=2
    )

    return train_loader, val_loader
