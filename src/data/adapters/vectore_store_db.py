import asyncpg

from typing import List, Optional
from sentence_transformers import SentenceTransformer
from src.settings.app_settigns import AppSettings


class VectorStoreDB:
    def __init__(self, model_name: Optional[str] = None, device: str = "cpu"):
        """
        Инициализация модели векторизации текста.

        Parameters:
        model_name (Optional[str]): Имя модели из SentenceTransformer.
            Если не указано, то будет использоваться модель по умолчанию.
        device (str): Устройство, на котором будет работать модель.
            Default: "cpu".
        """
        self.hf_model = SentenceTransformer(model_name, device=device)

    async def execute(
        self,
        filename: str,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        dsn = AppSettings().build_dsn()

        # query ожидается как строка -> получить embedding через модель
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        # получить вектор (numpy array) от SentenceTransformer
        emb = self.hf_model.encode(query, convert_to_numpy=True)
        try:
            vec_list = [float(x) for x in emb]
        except Exception:
            raise ValueError("Model produced non-numeric embedding")

        if len(vec_list) == 0:
            return []

        vec_lit = "[" + ",".join(repr(x) for x in vec_list) + "]"

        sql = """
            SELECT content
            FROM documents
            WHERE filename = $2
            ORDER BY embedding <=> $1::vector DESC
            LIMIT $3
        """

        conn = await asyncpg.connect(dsn)
        try:
            rows = await conn.fetch(sql, vec_lit, filename, int(top_k))
        finally:
            await conn.close()

        return [r['content'] for r in rows]


if __name__ == "__main__":
    # Пример использования
    import asyncio

    async def main():
        db = VectorStoreDB(
            AppSettings().hf_embedder_model,
            AppSettings().hf_device
        )
        results = await db.execute(
            filename="Безопасность vps сервера.pdf",
            query="Какой у SSH стандартный порт?",
            top_k=1
        )
        for content in results:
            print(content)

    asyncio.run(main())
