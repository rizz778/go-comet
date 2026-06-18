from graph.state import ChatState
from config.llm import get_llm

SYSTEM_PROMPT = "You are Nova, a helpful logistics assistant."

def chat_agent(state: ChatState) -> ChatState:
    llm = get_llm()
    response = llm.invoke(
        [{"role": "system", "content": SYSTEM_PROMPT}, *state["messages"]]
    )
    return {"messages": [response]}