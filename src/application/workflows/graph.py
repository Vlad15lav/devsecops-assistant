from langgraph.graph import StateGraph, START, END

from src.application.models.agent_state import AgentState
from langchain_core.messages import AIMessage

from src.application.agents.moderation_agent import ModerationAgent
from src.application.agents.rag_agent import RAGAgent
from src.application.agents.writer_agent import WriterAgent

from src.application.tools.sql_tool import SQLTool
from langgraph.prebuilt import ToolNode


def _needs_tool(state: AgentState) -> bool:
    """Return True if the last AI message in history requests tool calls."""
    messages = state.get("messages") or []
    if not messages:
        return False
    last = messages[-1]

    tool_calls = getattr(last, "tool_calls", None)
    return isinstance(last, AIMessage) and bool(tool_calls)


def _is_query_relevant(state: AgentState) -> bool:
    """Return True if the query passed moderation (is relevant)."""
    moderation_output = state.get("moderation_output")
    if moderation_output is None:
        print("Moderation output not found in state, treating as irrelevant")
        return False
    return moderation_output.is_relevant


def get_compiled_graph():
    graph = StateGraph(
        state_schema=AgentState
    )

    tools = [SQLTool()]

    # Add agents
    graph.add_node("moderation_agent", ModerationAgent())
    graph.add_node("rag_agent", RAGAgent())
    graph.add_node("writer_agent", WriterAgent())
    # # Tool execution node
    graph.add_node("tools", ToolNode(tools=tools))

    graph.add_edge(START, "moderation_agent")
    graph.add_conditional_edges(
        "moderation_agent",
        _is_query_relevant,
        {True: "rag_agent", False: END}
    )
    graph.add_conditional_edges(
        "rag_agent",
        _needs_tool,
        {True: "tools", False: END}
    )
    graph.add_edge("tools", "rag_agent")
    graph.add_edge("rag_agent", "writer_agent")
    graph.add_edge("writer_agent", END)

    compiled_graph = graph.compile()

    return compiled_graph
