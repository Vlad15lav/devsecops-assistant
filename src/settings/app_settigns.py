from typing import Optional
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class AppSettings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # База данных
    postgres_host: str = Field(
        default="localhost",
        description="Хост для подключения к базе данных",
        env="POSTGRES_HOST"
    )
    postgres_port: int = Field(
        default=5432,
        description="Порт для подключения к базе данных",
        env="POSTGRES_PORT"
    )
    postgres_db_name: str = Field(
        default="devsecops_rag",
        description="Имя базы данных",
        env="POSTGRES_DB"
    )
    postgres_user: str = Field(
        default="postgres",
        description="Имя пользователя для подключения к базе данных",
        env="POSTGRES_USER"
    )
    postgres_password: str = Field(
        default="password",
        description="Пароль для подключения к базе данных",
        env="POSTGRES_PASSWORD"
    )

    # Источники данных
    data_sources: str = Field(
        default="./sources.yaml",
        description="Файл с источниками данных",
        env="DATA_SOURCES"
    )
    upload_path: str = Field(
        default="./data_storage",
        description="Каталог с исходными данными",
        env="UPLOAD_PATH"
    )

    # Векторизация текста
    hf_embedder_model: Optional[str] = Field(
        default="sergeyzh/LaBSE-ru-turbo",
        description="Модель для векторизации текста",
        env="HF_EMBEDDER_MODEL"
    )
    hf_device: str = Field(
        default="cpu",
        description="Устройство для векторизации текста",
        env="HF_DEVICE"
    )
    chunk_unit: str = Field(
        default="sentences",
        description="Единица разбиения текста (chars, tokens, sentences)",
        env="CHUNK_UNIT"
    )
    chunk_size: int = Field(
        default=400,
        description="Размер чанка текста для векторизации",
        env="CHUNK_SIZE"
    )
    chunk_overlap: int = Field(
        default=0,
        description="Перекрытие между сегментами текста для векторизации",
        env="CHUNK_OVERLAP"
    )
    pgvector_dim: int = Field(
        default=768,
        description="Размерность вектора для хранения в базе данных",
        env="PGVECTOR_DIM"
    )

    # LLM настройки
    llm_base_url: Optional[str] = Field(
        default=None,
        description="Базовый URL для подключения к LLM",
        env="LLM_BASE_URL"
    )
    llm_model_name: Optional[str] = Field(
        default=None,
        description="Имя модели LLM",
        env="LLM_MODEL_NAME"
    )
    llm_api_key: Optional[str] = Field(
        default=None,
        description="API ключ для подключения к LLM",
        env="LLM_API_KEY"
    )
    llm_temperature: float = Field(
        default=0.0,
        description="Температура LLM",
        env="LLM_TEMPERATURE"
    )
    prompts_path: str = Field(
        default="./src/application/prompts",
        description="Каталог с промптами LLM",
        env="PROMPTS_PATH"
    )

    # Параметры RAG агента
    top_k_docs: int = Field(
        default=3,
        description="Количество документов для использования в RAG агенте",
        env="TOP_K_DOCS"
    )

    def build_dsn(self, db_name: Optional[str] = None) -> str:
        db = db_name or self.postgres_db_name
        user = self.postgres_user
        pwd = self.postgres_password
        host = self.postgres_host
        port = self.postgres_port
        return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


settings = AppSettings()
