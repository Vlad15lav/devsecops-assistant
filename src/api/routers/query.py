import logging

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
    """
    Endpoint to query the chatbot.

    Args:
        user_request: UserRequest - contains the query to be processed
            by the chatbot.
        graph: CompiledStateGraph - the compiled graph of agents and tools.

    Returns:
        ChatbotResponse - the response from the chatbot.

    Raises:
        HTTPException - if the query endpoint fails.
    """
    try:
        chatbot = ChatBot(graph=graph)
        response = await chatbot.run(user_request)
        return response

    except ValueError as exc:
        # Handle validation errors (e.g., chat not found)
        error_msg = str(exc)
        if "not found" in error_msg:
            logging.warning(f"Chat not found: {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    except Exception as exc:
        # Log full stacktrace for easier debugging
        logging.exception(f"Query endpoint failed: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc))
