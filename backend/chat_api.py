from fastapi import APIRouter
from pydantic import BaseModel
import ollama

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/query")
def chat(request: ChatRequest):

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": request.message
            }
        ]
    )

    return {
        "question": request.message,
        "response": response["message"]["content"]
    }