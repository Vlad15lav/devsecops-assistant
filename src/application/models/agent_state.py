from typing import List, TypedDict, NotRequired, Annotated
from langchain_core.messages import BaseMessage
from src.application.models.sql_agent_models import SQLAgentOutput
from src.application.models.moderation_agent_models import (
    ModerationAgentOutput
)
from src.application.models.writer_agent_models import WriterAgentOutput
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Состояние графа, разделяемое между всеми агентами"""
    messages: NotRequired[Annotated[List[BaseMessage], add_messages]]
    moderation_output: NotRequired[ModerationAgentOutput]
    sql_agent_output: NotRequired[SQLAgentOutput]
    writer_agent_output: NotRequired[WriterAgentOutput]
