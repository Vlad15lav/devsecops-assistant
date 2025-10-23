from fastapi import APIRouter, Depends, HTTPException

from src.application.workflows.graph import get_compiled_graph
from src.domain.entities.internal.chatbot_response import ChatbotResponse
from src.domain.entities.internal.user_request import UserRequest
from src.application.workflows.chatbot import ChatBot


router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=ChatbotResponse)
async def query_endpoint(
    user_request: UserRequest,
    graph=Depends(get_compiled_graph)
):
    try:
        chatbot = ChatBot(graph=graph)
        response = await chatbot.run(user_request)
        return response

    except ValueError as exc:
        # Handle validation errors (e.g., chat not found)
        error_msg = str(exc)
        if "not found" in error_msg:
            print(f"Chat not found: {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    except Exception as exc:
        # Log full stacktrace for easier debugging
        print(f"Query endpoint failed: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc))
