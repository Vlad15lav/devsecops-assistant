from typing import List
from langchain.schema import BaseMessage, HumanMessage
from src.application.agents.base_agent import AgentState
from src.application.workflow.graph import get_compiled_graph
from src.domain.internal.user_request import UserRequest
from src.domain.internal.chatbot_response import ChatbotResponse


class ChatBot:
    def __init__(self):
        self.graph = get_compiled_graph()

    def _get_response_from_state(self, state: AgentState) -> ChatbotResponse:
        """Extract the formatted answer from the final agent state."""
        # Проверка модерации
        moderation_output = state.get("moderation_output")
        if moderation_output and not moderation_output.is_relevant:
            return (
                "Извините, ваш запрос не соответствует требованиям. "
                f"Причина: {moderation_output.reason}"
            )

        # Вывод ответа
        writer_agent_output = state.get("writer_agent_output")
        if writer_agent_output is None:
            return "Запрос не был обработан. Пожалуйста, попробуйте еще раз."

        chatbot_response = ChatbotResponse(
            answer=writer_agent_output.answer,
            retriever_docs=writer_agent_output.retriever_docs
        )

        return chatbot_response

    def _user_request_to_messages(
        self,
        request: UserRequest
    ) -> List[BaseMessage]:
        """Combine chat history with current user request."""
        return [HumanMessage(content=request.query)]

    async def run(self, request: UserRequest) -> ChatbotResponse:
        try:
            # Build state with history and current message
            state = AgentState(
                messages=self._user_request_to_messages(request)
            )
            result_state_dict = await self.graph.ainvoke(
                state
            )
            # Get response
            chatbot_response = self._get_response_from_state(result_state_dict)

            return chatbot_response
        except Exception as e:
            print("[Chatbot] Chatbot execution failed: %s", str(e))
            raise
