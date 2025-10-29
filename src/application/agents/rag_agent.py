import os

from src.application.models.agent_state import AgentState
from src.application.agents.sql_agent import SQLAgent
from src.settings.app_settigns import AppSettings


class RAGAgent(SQLAgent):
    """Агент для работы с RAG."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "rag_agent"
        self.prompt_template = self._create_prompt_template()
        self.runnable_chain = self._create_runnable_chain()

    async def _aprepare_input(self, state: AgentState) -> AgentState:
        """Преподготовка входных данных."""
        return state

    def get_system_prompt(self) -> str:
        """Возвращает специальный системный промпт для агента."""
        settings = AppSettings()
        path = os.path.join(settings.prompts_path, "sql_agent_prompt.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
