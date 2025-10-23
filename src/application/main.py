from src.application.workflow.chatbot import ChatBot
from src.domain.internal.user_request import UserRequest


if __name__ == "__main__":
    import asyncio

    async def main():
        chatbot = ChatBot()
        user_quer = UserRequest(query="Привет, как настроить fail2ban на VPS?")
        result = await chatbot.run(request=user_quer)
        print("Final result:\n", result)

    asyncio.run(main())
