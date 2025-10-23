from src.application.agents.base_agent import BaseAgent
from src.application.schemas.moderation_schema import ModerationOutput
from src.application.models.agent_state import AgentState


class ModerationAgent(BaseAgent):
    """Агент для проверки безопасости запроса через LLM."""

    def __init__(self):
        super().__init__(
            name="moderation_agent",
            structured_output=ModerationOutput
        )

    def _prepare_input(self, state: AgentState) -> AgentState:
        """Prepare input for the moderation agent."""
        return state

    async def _handle_output(
        self,
        result: ModerationOutput,
        state: AgentState
    ) -> AgentState:
        """Store the moderation result."""
        state["moderation_output"] = result
        return state
