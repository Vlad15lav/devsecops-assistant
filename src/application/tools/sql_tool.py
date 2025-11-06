import json

from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from src.data.adapters.vectore_store_db import VectorStoreDB


class SQLQueryInput(BaseModel):
    """Входные параметры для SQLTool."""

    user_query: str = Field(
        min_length=1,
        description=(
            "The user's original text query used "
            "to generate the vector for the SQL query."
        )
    )


class SQLTool(BaseTool):
    """Инструмент для выполнения SQL-запросов."""

    name: str = "sql_tool"
    description: str = (
        "Execute SQL SELECT queries on the database. "
        "Use the 'filename' and 'user_query' parameters. "
        "Returns results in JSON format."
    )
    args_schema: Type[BaseModel] = SQLQueryInput

    async def _arun(self, user_query: str, filename: str, **kwargs) -> str:
        """Выполняет SQL-запрос и возвращает результаты."""
        try:
            db = VectorStoreDB()
            results = await db.execute(
                user_query=user_query,
                **kwargs
            )
            return json.dumps(results, ensure_ascii=False, default=str)

        except ValueError as exc:
            return f"SQL query failed: {str(exc)}"
        except Exception as exc:
            return f"SQL tool failed: {exc}"

    def _run(self, query: str, **kwargs) -> str:
        """Синхронная версия инструмента."""
        raise NotImplementedError("Use async version of the tool")
