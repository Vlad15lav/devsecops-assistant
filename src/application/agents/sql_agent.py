from src.application.agents.base_agent import BaseAgent
from langchain_core.messages import AIMessage
from src.application.models.agent_state import AgentState
from src.application.tools.sql_tool import SQLTool
from src.application.models.sql_agent_models import SQLAgentOutput


class SQLAgent(BaseAgent):
    """Агент для работы с SQL запросами."""

    def __init__(self):
        super().__init__(
            name="sql_agent",
            tools=[SQLTool()]
        )

    async def _aprepare_input(self, state: AgentState) -> AgentState:
        """Преподготовка входных данных."""
        return state

    async def _handle_output(
        self,
        result: AIMessage,
        state: AgentState
    ) -> AgentState:
        """Запись результата в историю сообщений."""
        returned_rows = self._extract_data_from_tool(state, "sql_tool")

        if returned_rows and not isinstance(returned_rows[0], dict):
            returned_rows = [
                dict(r) if hasattr(r, 'items') else {"content": str(r)}
                for r in returned_rows
            ]

        state["sql_agent_output"] = SQLAgentOutput(
            result=result.content,
            returned_rows=returned_rows
        )
        return state
