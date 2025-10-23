from pydantic import Field
from src.application.models.base_agent_models import (
    BaseAgentOutput,
    BaseAgentInput
)


class WriterAgentInput(BaseAgentInput):
    pass


class WriterAgentOutput(BaseAgentOutput):
    answer: str = Field(
        description="Итоговый ответ пользователю"
    )
    retriever_docs: list[str] = Field(
        description="Список документов, использованных для генерации ответа"
    )
