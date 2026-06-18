from langgraph.graph import StateGraph, START, END
from graph.state import ChatState
from agents.chat_agent import chat_agent

builder = StateGraph(ChatState)
builder.add_node("chat_agent", chat_agent)
builder.add_edge(START, "chat_agent")
builder.add_edge("chat_agent", END)

chat_graph = builder.compile()