FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Указываем переменные окружения
ENV PYTHONPATH=/app
ENV PATH="/root/.local/bin/:$PATH"

# Рабочая директория — корень проекта
WORKDIR /app

# Устанавливаем виртуальное окружение и зависимости с фиксированными версиями
COPY pyproject.toml ./
COPY uv.lock ./

# Создаём и синхронизируем виртуальное окружение
RUN uv venv .venv && \
    uv sync --frozen

# Копируем исходный код
COPY ./src ./src

# Указываем порт из переменной окружения
EXPOSE ${FASTAPI_PORT}

# Запускаем FastAPI
CMD ["uv", "run", "./src/api/main.py"]
