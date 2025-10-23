# from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel, Field


class ModerationOutput(BaseModel):
    """Структурированный вывод агента модерации"""

    is_relevant: bool = Field(
        description=(
            "true если запрос относится к вопросам DevOps-безопасности "
            "(VPS, Docker, CI/CD, Kubernetes); "
            "false если полностью не связан с работой"
        )
    )
    reason: str = Field(description="Краткая и четкая причина решения")
