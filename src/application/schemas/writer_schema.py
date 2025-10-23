from pydantic import BaseModel, Field


class WriterOutput(BaseModel):
    """Структурированный вывод агента
    для генерации итогового ответа пользователя.
    """

    answer: str = Field(description="Ответ на вопрос пользователя")
    retriever_docs: list[str] = Field(
        description="Список документов, использованных для ответа"
    )
