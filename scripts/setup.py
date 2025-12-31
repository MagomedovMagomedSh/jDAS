#!/usr/bin/env python3
"""Автоматическая настройка проекта"""
import subprocess
import os
from pathlib import Path

def setup_project():
    print("🚀 Настройка DAS проекта...")
    
    # 1. Проверяем .env
    env_path = Path(".env")
    if not env_path.exists():
        print("Создаю .env из шаблона...")
        Path(".env.example").rename(".env")
        print("⚠️  Заполните YANDEX_DISK_TOKEN в .env")
    
    # 2. Настраиваем DVC
    print("\nНастраиваю DVC...")
    token = os.getenv("YANDEX_DISK_TOKEN")
    
    if token:
        subprocess.run(["dvc", "remote", "add", "-d", "yandex", "disk://dvc-cache/"])
        subprocess.run(["dvc", "remote", "modify", "yandex", "type", "yandex"])
        print("✅ DVC remote настроен на Яндекс.Диск")
    else:
        # Локальный remote для удобства
        subprocess.run(["dvc", "remote", "add", "-d", "local", "./.dvc/remote"])
        print("✅ DVC remote настроен локально")
    
    # 3. Pre-commit
    print("\nУстанавливаю pre-commit...")
    subprocess.run(["pre-commit", "install"])
    
    print("\n🎉 Проект настроен!")
    print("\nКоманды:")
    print("  jdas --help          - Показать все команды")
    print("  jdas setup-dvc       - Настроить DVC")
    print("  jdas serve           - Запустить сервер")
    print("  dvc pull             - Скачать данные")
    print("  make train           - Обучить модель")

if __name__ == "__main__":
    setup_project()
