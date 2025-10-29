import json

from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from src.data.adapters.vectore_store_db import VectorStoreDB


class SQLQueryInput(BaseModel):
    """Входные параметры для SQLTool."""

    query: str = Field(
        min_length=1,
        description=(
            "SQL SELECT query to execute on the database. "
            "Only SELECT queries are allowed for security reasons. "
            "Example: 'SELECT * FROM documents "
            "WHERE filename = \"k8s.pdf\" "
            "LIMIT 3'"
        ),
    )
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
        "Only SELECT queries are allowed for security reasons. "
        "Returns results in JSON format."
    )
    args_schema: Type[BaseModel] = SQLQueryInput

    async def _arun(self, query: str, user_query: str, **kwargs) -> str:
        """Выполняет SQL-запрос и возвращает результаты."""
        try:
            query = query.replace('"', "'")
            # Validate that only SELECT queries are allowed
            query_upper = query.strip().upper()
            if not query_upper.startswith('SELECT'):
                error_msg = "Only SELECT " \
                    "queries are allowed for security reasons"
                raise ValueError(error_msg)

            db = VectorStoreDB()
            results = await db.execute(
                query=query,
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
