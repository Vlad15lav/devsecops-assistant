FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y curl && apt-get clean

# Устанавливаем uv
RUN pip install uv

# Рабочая директория — корень проекта
WORKDIR /app

# Копируем файлы зависимостей из корня (относительно docker-compose контекста)
COPY ./pyproject.toml ./uv.lock ./

# Устанавливаем зависимости в системную среду
RUN uv sync --frozen

# Копируем исходный код
COPY ./src ./src

# Указываем рабочую директорию
ENV PYTHONPATH=/app

# Указываем порт из env
EXPOSE ${FASTAPI_PORT}

# Запускаем FastAPI
CMD ["uv", "run", "./src/api/main.py"]
