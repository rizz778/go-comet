from fastapi import APIRouter
from pydantic import BaseModel
from graph.graph import chat_graph

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

router = APIRouter()



@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = chat_graph.invoke({"messages": [{"role": "user", "content": request.message}]})
    return ChatResponse(reply=result["messages"][-1].content)