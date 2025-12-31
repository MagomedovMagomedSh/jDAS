.PHONY: setup train serve process dvc-setup help

setup:
	@echo "🚀 Настройка проекта..."
	uv sync
	pre-commit install
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "⚠️  Заполните .env файл (YANDEX_DISK_TOKEN)"; \
	fi
	@echo "✅ Готово! Заполните .env и запустите: make dvc-setup"

dvc-setup:
	@echo "🔄 Настройка DVC..."
	@read -p "Использовать Яндекс.Диск? (y/N): " choice; \
	if [ "$$choice" = "y" ] || [ "$$choice" = "Y" ]; then \
		read -p "Введите YANDEX_DISK_TOKEN: " token; \
		echo "YANDEX_DISK_TOKEN=$$token" >> .env; \
		dvc remote add -d yandex disk://dvc-cache/; \
		dvc remote modify yandex type yandex; \
		echo "✅ DVC настроен с Яндекс.Диском"; \
	else \
		dvc remote add -d local ./.dvc/remote; \
		echo "✅ DVC настроен локально (.dvc/remote/)"; \
	fi

train:
	uv run jdas train

serve:
	uv run jdas serve --reload

process:
	@echo "Пример:"
	@echo "uv run jdas process --folder-url 'URL' --method bandpass"

dvc-pull:
	dvc pull

dvc-push:
	dvc add data/raw/
	dvc push

help:
	@echo "Доступные команды:"
	@echo "  make setup     - Первоначальная настройка"
	@echo "  make dvc-setup - Настроить DVC (интерактивно)"
	@echo "  make train     - Обучить модель"
	@echo "  make serve     - Запустить веб-сервис"
	@echo "  make dvc-pull  - Скачать данные через DVC"
	@echo "  make dvc-push  - Сохранить данные через DVC"
