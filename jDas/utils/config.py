import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Загружаем .env файл
def load_env(env_path: Optional[Path] = None):
    """Загружает переменные окружения из .env файла"""
    if env_path is None:
        env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Загружены переменные из {env_path}")
    else:
        print(f"⚠️  Файл {env_path} не найден, используются системные переменные")

def get_yandex_token() -> str:
    """Получает токен Яндекс.Диска"""
    token = os.getenv("YANDEX_DISK_TOKEN")
    if not token:
        raise ValueError(
            "YANDEX_DISK_TOKEN не найден. "
            "Добавьте его в .env файл или экспортируйте в окружение.\n"
            "Инструкция по получению токена: "
            "https://yandex.ru/dev/id/doc/ru/"
        )
    return token

def get_mlflow_uri() -> str:
    """Получает URI для MLFlow"""
    return os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

def get_model_path() -> Path:
    """Получает путь к модели"""
    return Path(os.getenv("MODEL_PATH", "./models/jdаs_final.pth"))

def get_data_path() -> Path:
    """Получает путь к данным"""
    return Path(os.getenv("DATA_PATH", "./data/raw"))

def get_output_path() -> Path:
    """Получает путь для выходных данных"""
    return Path(os.getenv("OUTPUT_PATH", "./output"))

# Загружаем при импорте модуля
load_env()
