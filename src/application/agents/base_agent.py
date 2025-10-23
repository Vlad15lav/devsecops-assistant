import os

from abc import abstractmethod
from typing import Optional, Any
# from langchain.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema.runnable import Runnable
from src.application.models.agent_state import AgentState
from langchain_core.messages import BaseMessage, ToolMessage
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate
)
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    # HumanMessagePromptTemplate,
    # AIMessagePromptTemplate
)

from src.settings.app_settigns import AppSettings


class BaseAgent:
    """Базовый агент для работы с LLM"""

    def __init__(
        self,
        name: str,
        structured_output: Any = None,
        input_variables: Optional[list[str]] = None,
        llm: Optional[ChatGroq] = None,
        tools: Optional[list[Any]] = None
    ):
        self.settings = AppSettings()
        self.name = name
        self.structured_output = structured_output
        self.input_variables: list[str] = input_variables
        self.llm = llm
        self.tools = tools

        self.prompt_template = self._create_prompt_template()
        self.runnable_chain = self._create_runnable_chain()

    def get_system_prompt(self) -> str:
        """Возвращает системный промпт для агента."""
        prompt_template_path = os.path.join(
            self.settings.prompts_path,
            f"{self.name}_prompt.txt"
        )
        try:
            with open(prompt_template_path, encoding="utf-8") as f:
                template_text = f.read()
            return template_text
        except Exception as e:
            raise RuntimeError(
                f"Не удалось прочитать промпт по '{prompt_template_path}': {e}"
            )

    def _create_prompt_template(
        self,
        name: Optional[str] = None
    ) -> ChatPromptTemplate:
        template_text = self.get_system_prompt()

        prompt_template = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate(
                    prompt=PromptTemplate(
                        template=template_text,
                        input_variables=self.input_variables
                    )
                ),
                MessagesPlaceholder(variable_name="messages")
            ]
        )
        return prompt_template

    def _create_runnable_chain(self) -> Runnable:
        if self.llm is None:
            model = ChatGroq(
                # base_url=self.settings.llm_base_url,
                model=self.settings.llm_model_name,
                api_key=self.settings.llm_api_key,
                temperature=self.settings.llm_temperature,
            )
        else:
            model = self.llm

        if self.structured_output and self.tools:
            raise ValueError(
                "Нельзя одновременно использовать tools и Structured Output"
            )
        if self.tools:
            model = model.bind_tools(self.tools)
        if self.structured_output:
            model = model.with_structured_output(self.structured_output)

        prompt = self._create_prompt_template()

        return prompt | model

    async def _aprepare_input(self, state: AgentState) -> AgentState:
        """Асинхронная подготовка входного состояния"""
        return state

    @abstractmethod
    async def _handle_output(
        self,
        result: Any,
        state: AgentState,
    ) -> AgentState:
        """Обрабатывает результат выполнения цепочки"""
        pass

    async def __call__(self, state: AgentState) -> AgentState:
        """Основной метод обработки с использованием Runnable"""
        try:
            # Асинхронная подготовка входных данных
            state = await self._aprepare_input(state)

            # Выполняем модель напрямую на списке сообщений
            result = await self.runnable_chain.ainvoke(state)

            # Сохраняем ответ в историю сообщений
            if isinstance(result, BaseMessage):
                state_messages = state.get("messages", [])
                state_messages.append(result)
                state["messages"] = state_messages

            # Обрабатываем результат
            updated_state = await self._handle_output(result, state)
            return updated_state

        except Exception as e:
            print("[%s] Агент произошла ошибка: %s", self.name, str(e))
            raise

    def _get_last_tool_message(
        self,
        state: AgentState,
        tool_name: Optional[str] = None
    ) -> Optional[ToolMessage]:
        # Validate that tools are provided to this agent
        if not self.tools:
            return None

        # If tool_name is specified, validate it exists
        if tool_name is not None:
            available_tool_names = [tool.name for tool in self.tools]
            if tool_name not in available_tool_names:
                raise ValueError(
                    f"Tool '{tool_name}' is not available "
                    f"to agent '{self.name}'. "
                    f"Available tools: {available_tool_names}"
                )

        messages = state.get("messages", [])
        # Ищем ToolMessage в обратном порядке (от последнего к первому)
        for message in reversed(messages):
            if isinstance(message, ToolMessage):
                # Если указано имя инструмента, проверяем соответствие
                if tool_name is None or message.name == tool_name:
                    return message

        return None

    def _extract_data_from_tool(
        self,
        state: AgentState,
        tool_name: Optional[str] = None
    ) -> Optional[Any]:
        last_tool_message = self._get_last_tool_message(state, tool_name)
        if not last_tool_message:
            return None

        # Check for errors
        if hasattr(last_tool_message, 'status') and \
                last_tool_message.status == "error":
            return None

        # Parse the content as JSON
        try:
            import json
            data = json.loads(last_tool_message.content)
            return data
        except (json.JSONDecodeError, ValueError, TypeError):
            return None
