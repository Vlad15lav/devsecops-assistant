from src.application.workflows.chatbot import ChatBot
from src.domain.entities.internal.user_request import UserRequest
from src.application.workflows.graph import get_compiled_graph


if __name__ == "__main__":
    import asyncio

    async def main():
        chatbot = ChatBot(graph=get_compiled_graph())
        user_quer = UserRequest(query="Привет, как настроить fail2ban на VPS?")
        result = await chatbot.run(request=user_quer)
        print("Final result:\n", result)

    asyncio.run(main())
