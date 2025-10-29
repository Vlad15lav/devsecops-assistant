from src.application.agents.base_agent import BaseAgent
from src.application.schemas.writer_schema import WriterOutput
from src.application.models.agent_state import AgentState


class WriterAgent(BaseAgent):
    """Агент для генерации итогового ответа пользователю."""

    def __init__(self):
        super().__init__(
            name="writer_agent",
            structured_output=WriterOutput
        )

    def _prepare_input(self, state: AgentState) -> AgentState:
        """Преподготовка входных данных."""
        return state

    async def _handle_output(
        self,
        result: WriterOutput,
        state: AgentState
    ) -> AgentState:
        """Запись результата в историю сообщений."""
        state["writer_agent_output"] = result
        return state
