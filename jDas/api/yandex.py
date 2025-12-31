from pathlib import Path
from typing import List

import requests

from jdas.utils.config import get_yandex_token


class YandexDiskClient:
    """Клиент для работы с Яндекс.Диском"""

    def __init__(self, token: str = None):
        self.token = token or get_yandex_token()
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def list_files(self, folder_path: str) -> List[dict]:
        """Список файлов в папке"""
        url = f"{self.base_url}?path={folder_path}"
        response = requests.get(url, headers=self.headers)
        return response.json().get("_embedded", {}).get("items", [])

    def download_folder(self, folder_url: str, local_path: Path) -> List[Path]:
        """Скачивает все mseed файлы из папки"""
        local_path.mkdir(exist_ok=True)

        # Извлекаем путь из URL
        folder_path = folder_url.split("client/disk")[-1]

        downloaded_files = []
        for item in self.list_files(folder_path):
            if item["name"].endswith(".mseed"):
                # Скачиваем файл
                download_url = f"{self.base_url}/download?path={item['path']}"
                response = requests.get(download_url, headers=self.headers)
                download_link = response.json().get("href")

                file_data = requests.get(download_link)
                file_path = local_path / item["name"]
                file_path.write_bytes(file_data.content)
                downloaded_files.append(file_path)

        return downloaded_files

    def upload_file(self, local_path: Path, remote_path: str):
        """Загружает файл на Яндекс.Диск"""
        upload_url = f"{self.base_url}/upload?path={remote_path}&overwrite=true"
        response = requests.get(upload_url, headers=self.headers)
        upload_link = response.json().get("href")

        with open(local_path, "rb") as f:
            requests.put(upload_link, files={"file": f})
