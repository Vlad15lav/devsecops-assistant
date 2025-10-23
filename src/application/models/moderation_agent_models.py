from pydantic import Field
from src.application.models.base_agent_models import (
    BaseAgentOutput,
    BaseAgentInput
)


class ModerationAgentInput(BaseAgentInput):
    pass


class ModerationAgentOutput(BaseAgentOutput):
    is_relevant: bool = Field(
        description=(
            "True, если запрос относится к вопросам безопасности "
            "DevOps"
        )
    )
    reason: str = Field(description="Причина для принятия решения")
