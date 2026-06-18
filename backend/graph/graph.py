from langgraph.graph import StateGraph, START, END
from graph.state import ChatState, PipelineState
from agents.chat_agent import chat_agent
from agents.extractor import extract_agent
from agents.validator import validator_agent
from agents.router import router_agent

# 1. Chat Graph (Existing - kept for backward compatibility)
chat_builder = StateGraph(ChatState)
chat_builder.add_node("chat_agent", chat_agent)
chat_builder.add_edge(START, "chat_agent")
chat_builder.add_edge("chat_agent", END)
chat_graph = chat_builder.compile()

# 2. Document Pipeline Graph (New - Bypassing DB Saver for Testing)
pipeline_builder = StateGraph(PipelineState)
pipeline_builder.add_node("extract", extract_agent)
pipeline_builder.add_node("validate", validator_agent)
pipeline_builder.add_node("route", router_agent)

pipeline_builder.add_edge(START, "extract")
pipeline_builder.add_edge("extract", "validate")
pipeline_builder.add_edge("validate", "route")
pipeline_builder.add_edge("route", END)  # Go directly to END

pipeline_graph = pipeline_builder.compile()