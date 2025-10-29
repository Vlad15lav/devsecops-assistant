from typing import List
from langchain.schema import BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from src.application.agents.base_agent import AgentState
from src.domain.entities.internal.user_request import UserRequest
from src.domain.entities.internal.chatbot_response import ChatbotResponse


class ChatBot:
    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph

    def _get_response_from_state(self, state: AgentState) -> ChatbotResponse:
        """Вывод ответа из состояния."""
        # Проверка модерации
        moderation_output = state.get("moderation_output")
        if moderation_output and not moderation_output.is_relevant:
            answer = (
                "Извините, ваш запрос не соответствует требованиям. "
                f"Причина: {moderation_output.reason}"
            )
            return ChatbotResponse(answer=answer, retriever_docs=[])

        # Вывод ответа
        writer_agent_output = state.get("writer_agent_output")
        if writer_agent_output is None:
            answer = "Запрос не был обработан. Пожалуйста, попробуйте еще раз."
            return ChatbotResponse(answer=answer, retriever_docs=[])

        chatbot_response = ChatbotResponse(
            answer=writer_agent_output.answer,
            retriever_docs=writer_agent_output.retriever_docs
        )

        return chatbot_response

    def _user_request_to_messages(
        self,
        request: UserRequest
    ) -> List[BaseMessage]:
        """Конвертация запроса в список сообщений."""
        return [HumanMessage(content=request.query)]

    async def run(self, request: UserRequest) -> ChatbotResponse:
        """Выполнение запроса пользователя."""
        try:
            # Создание состояния агента с запросом пользователя
            state = AgentState(
                messages=self._user_request_to_messages(request)
            )
            result_state_dict = await self.graph.ainvoke(
                state
            )
            # Получение ответа
            chatbot_response = self._get_response_from_state(result_state_dict)

            return chatbot_response
        except Exception as e:
            print("[Chatbot] Chatbot execution failed: %s", str(e))
            raise
