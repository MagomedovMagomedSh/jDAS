from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Tuple
import tempfile
from pathlib import Path

from jdas.api.yandex import YandexDiskClient
from jdas.core.loader import load_mseed_files
from jdas.core.filter import bandpass_filter
from jdas.core.model import JDASUnet

app = FastAPI(title="DAS Cleaning Service")

class ProcessingRequest(BaseModel):
    folder_url: str
    time_range: Tuple[int, int] = (0, 3600)  # в секундах
    method: str = "jdаs"  # "jdаs" или "bandpass"

@app.post("/api/process")
async def process_das(request: ProcessingRequest, background_tasks: BackgroundTasks):
    """Основной endpoint для обработки DAS данных"""
    
    # Создаём временную папку
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # 1. Скачиваем с Яндекс.Диска
        yandex = YandexDiskClient()
        yandex.download_folder(request.folder_url, tmp_path / "raw")
        
        # 2. Загружаем и обрезаем по времени
        data = load_mseed_files(tmp_path / "raw")
        start_idx = int(request.time_range[0] * 1000)  # 1000 Hz
        end_idx = int(request.time_range[1] * 1000)
        data = data[:, start_idx:end_idx]
        
        # 3. Применяем метод очистки
        if request.method == "bandpass":
            cleaned = bandpass_filter(data)
        else:  # jDAS
            model = JDASUnet.load_from_checkpoint("jdаs_model.pth")
            # Конвертируем в tensor и обрабатываем
            # (упрощённо для примера)
            cleaned = data  # заглушка
        
        # 4. Сохраняем результат
        output_path = tmp_path / "cleaned.npy"
        np.save(output_path, cleaned)
        
        # 5. Загружаем обратно на Яндекс.Диск
        result_folder = f"{request.folder_url}_cleaned"
        yandex.upload_file(output_path, f"{result_folder}/cleaned.npy")
        
        return {
            "status": "completed",
            "result_url": f"https://disk.yandex.ru/client/disk/{result_folder}",
            "method": request.method
        }

@app.get("/")
async def root():
    return {
        "service": "DAS Cleaning API",
        "endpoints": {
            "process": "/api/process",
            "docs": "/docs"
        }
    }
