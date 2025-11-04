import asyncpg
import logging

from typing import List


class PgVectorUploader:
    """Загружает список векторов в базу данных Retriever."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None

    async def __aenter__(self):
        if self.conn is None:
            self.conn = await asyncpg.connect(dsn=self.dsn)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def execute(
        self,
        filename: str,
        chunks: List[str],
        embeddings: List[List[float]]
    ):
        """
        Загружает файл с векторами в базу данных.
        Длины списков chunks и embeddings должны совпадать.
        """

        self.conn = self.conn or await asyncpg.connect(dsn=self.dsn)
        if not self.conn:
            raise ConnectionError("No DB connection!")
        try:
            val = await self.conn.fetchval("SELECT 1")
        except Exception as e:
            await self.conn.close()
            self.conn = None
            raise ConnectionError(f"DB health check failed before insert: {e}")
        if val != 1:
            await self.conn.close()
            self.conn = None
            raise ConnectionError(
                "DB health check returned unexpected value before insert"
            )

        records = []
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            emb_literal = "[" + ",".join(repr(float(x)) for x in emb) + "]"
            records.append((filename, idx, chunk, emb_literal))

        try:
            async with self.conn.transaction():
                for filename, idx, chunk, emb_literal in records:
                    await self.conn.execute(
                        """
                        INSERT INTO documents (
                            filename,
                            chunk_index,
                            content,
                            embedding
                        )
                        VALUES ($1, $2, $3, $4::vector)
                        """,
                        filename,
                        idx,
                        chunk,
                        emb_literal,
                    )
        except Exception as e:
            logging.exception(f"Error inserting records: {e}")
            if self.conn:
                await self.conn.close()
            self.conn = None

    async def exists(self, filename: str) -> bool:
        """
        Проверяет, есть ли уже записи с данным filename
        в таблице documents.
        """
        conn_created = False
        conn = self.conn
        try:
            if conn is None:
                conn = await asyncpg.connect(dsn=self.dsn)
                conn_created = True

            row = await conn.fetchrow(
                "SELECT 1 FROM documents WHERE filename = $1 LIMIT 1",
                filename
            )
            return row is not None
        finally:
            if conn_created and conn:
                await conn.close()
