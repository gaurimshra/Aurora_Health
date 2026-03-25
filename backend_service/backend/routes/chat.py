from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.agentic_ai_service import generate_chat_reply


load_dotenv()

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


@router.post("/chat")
def chat(data: ChatRequest):
    reply = generate_chat_reply(data.message)
    return {"reply": reply}
