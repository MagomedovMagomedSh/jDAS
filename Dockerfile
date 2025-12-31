FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install uv

# Копируем зависимости
COPY pyproject.toml ./
RUN uv pip install --system .

# Копируем код
COPY . .

# Создаём необходимые директории
RUN mkdir -p /app/data /app/models /app/output

# Загружаем переменные окружения при запуске
CMD ["sh", "-c", "uvicorn das.api.app:app --host 0.0.0.0 --port 8000"]
