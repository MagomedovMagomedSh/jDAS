import tempfile
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch

from jdas.api.yandex import YandexDiskClient
from jdas.core.filter import bandpass_filter
from jdas.core.loader import load_mseed_files
from jdas.core.model import JDASUnet


def process_das_data(
    folder_url: str,
    time_range: Tuple[int, int] = (0, 3600),
    method: str = "jdаs",
    output_dir: Path = Path("./output"),
) -> Dict:
    """Обрабатывает DAS данные и возвращает результат"""

    output_dir.mkdir(exist_ok=True, parents=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 1. Скачиваем с Яндекс.Диска
        yandex = YandexDiskClient()
        raw_files = yandex.download_folder(folder_url, tmp_path / "raw")

        if not raw_files:
            raise ValueError(f"No .mseed files found in {folder_url}")

        # 2. Загружаем данные
        data = load_mseed_files(tmp_path / "raw")

        # 3. Обрезаем по времени (1000 Hz sampling rate)
        start_idx = int(time_range[0] * 1000)
        end_idx = int(time_range[1] * 1000)
        data = data[:, start_idx:end_idx]

        # 4. Применяем метод очистки
        if method == "bandpass":
            cleaned = bandpass_filter(data)
        else:  # jDAS
            model = JDASUnet()

            # Загружаем веса модели
            model_path = Path("./models/jdаs_final.pth")
            if model_path.exists():
                model.load_state_dict(torch.load(model_path))
            else:
                raise FileNotFoundError(f"Model not found at {model_path}")

            model.eval()

            # Обрабатываем батчами
            batch_size = 10
            cleaned = []

            with torch.no_grad():
                for i in range(0, data.shape[0], batch_size):
                    batch = data[i : i + batch_size]
                    # [batch, channels, time] -> [batch, 1, channels, time]
                    batch_tensor = torch.FloatTensor(batch).unsqueeze(1)
                    cleaned_batch = model(batch_tensor).squeeze(1).numpy()
                    cleaned.append(cleaned_batch)

            cleaned = np.concatenate(cleaned, axis=0)

        # 5. Сохраняем результат
        timestamp = Path(folder_url).name.replace("Event_", "").split("_")[0]
        output_filename = f"cleaned_{timestamp}_{method}.npy"
        output_path = output_dir / output_filename
        np.save(output_path, cleaned)

        # 6. Загружаем на Яндекс.Диск
        result_folder = f"{folder_url}_cleaned_{method}"
        yandex_url = None
        try:
            yandex.upload_file(output_path, f"{result_folder}/{output_filename}")
            yandex_url = f"https://disk.yandex.ru/client/disk/{result_folder}"
        except Exception as e:
            print(f"⚠️ Failed to upload to Yandex Disk: {e}")

        return {
            "local_path": str(output_path),
            "yandex_url": yandex_url,
            "method": method,
            "original_shape": data.shape,
            "cleaned_shape": cleaned.shape,
        }
