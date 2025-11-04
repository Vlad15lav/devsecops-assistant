import os
import asyncpg
import yaml
import pymupdf4llm

from pathlib import Path

from src.data.scripts.pdf_downloader import PdfDownloader
from src.data.scripts.chunker import TextChunker
from src.data.scripts.embedder import TextEmbedder
from src.data.scripts.pgvector_uploader import PgVectorUploader

from src.settings.app_settigns import AppSettings


class DatabaseInitializer:
    """
    Инициализация базы данных RAG:
    - create_database(admin_dsn, db_name)
    - create_tables(dsn)
    - execute(dsn, files_name_list, pdf_urls, download_path, ...)
    - run_all(files_name_list, pdf_urls) — выполняет всё по настройкам
    """

    def __init__(self):
        self.settings = AppSettings()
        self.dsn = self.settings.build_dsn()

    async def create_database(self):
        """
        Создать целевую базу данных, если не существует.
        Подключение выполняется к административной БД 'postgres'.
        """
        conn = await asyncpg.connect(
            dsn=self.settings.build_dsn(db_name="postgres")
        )
        target_db = self.settings.postgres_db_name

        try:
            row = await conn.fetchrow(
                "SELECT 1 FROM pg_database WHERE datname=$1",
                target_db
            )
            if row:
                print(f"База данных {target_db} уже существует")
                return
            await conn.execute(f'CREATE DATABASE "{target_db}"')
            print(f"База данных {target_db} создана")
        finally:
            await conn.close()

    async def create_tables(self):
        """
        Создаёт необходимые расширения и таблицы, если их нет.
        """
        conn = await asyncpg.connect(dsn=self.dsn)
        try:
            # Создаём расширение vector (если не создано)
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Создаём таблицу documents (если не создана)
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename TEXT,
                    chunk_index INT,
                    content TEXT,
                    embedding vector({self.settings.pgvector_dim})
                )
                """
            )
        finally:
            await conn.close()

    async def execute(self):
        src_path = Path(self.settings.data_sources)

        if not src_path.exists():
            raise FileNotFoundError(
                f"Файл источников данных не найден: {src_path}"
            )
        with open(src_path, "r", encoding="utf-8") as f:
            sources = yaml.safe_load(f)

        file_names = [item["name"] for item in sources["sources"]]
        file_urls = [item["url"] for item in sources["sources"]]
        pdf_downloader = PdfDownloader(
            file_names,
            file_urls
        )
        pdf_downloader.execute(
            os.path.join(self.settings.upload_path, "pdf")
        )

        chunker = TextChunker(
            chunk_size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
            unit=self.settings.chunk_unit,
        )
        embedder = TextEmbedder(
            model_name=self.settings.hf_embedder_model,
            device=self.settings.hf_device,
        )
        pgvector_uploader = PgVectorUploader(
            dsn=self.dsn
        )

        for source in sources["sources"]:
            filename = source["name"]

            if await pgvector_uploader.exists(filename):
                print(f"Файл '{filename}' уже загружен, пропуск.")
                continue

            pdf_path = os.path.join(self.settings.upload_path, "pdf", filename)

            document = pymupdf4llm.to_markdown(pdf_path)

            chunks = chunker.execute(
                text=document
            )
            for idx, chunk in enumerate(chunks):
                chunks[idx] = f"{filename}: {chunk}"

            embeddings = embedder.execute(chunks)
            await pgvector_uploader.execute(
                filename=filename,
                chunks=chunks,
                embeddings=embeddings
            )
            print(f"Загружен файл '{filename}' с {len(chunks)} чанками.")


if __name__ == "__main__":
    import asyncio

    async def main():
        db_initializer = DatabaseInitializer()
        await db_initializer.create_database()
        await db_initializer.create_tables()
        await db_initializer.execute()

    asyncio.run(main())
