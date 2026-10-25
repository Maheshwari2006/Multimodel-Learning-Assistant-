
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import ollama

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Optional[str] = None


@router.post("/query")
def chat(request: ChatRequest):
    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    # Use the uploaded learning material when supplied.
    if request.context and request.context.strip():
        system_prompt = (
            "You are a helpful learning assistant. Answer the user's "
            "question using the supplied learning material. Preserve "
            "the material's terminology and explain concepts clearly. "
            "If the answer is not supported by the material, say so "
            "instead of inventing information.\n\n"
            "LEARNING MATERIAL:\n"
            f"{request.context.strip()}"
        )
    else:
        system_prompt = (
            "You are a helpful learning assistant. Answer clearly and "
            "explain concepts in beginner-friendly language. No learning "
            "material was supplied, so do not pretend to know the user's "
            "specific course, assignment, or document."
        )

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return {
            "question": question,
            "response": response["message"]["content"]
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate an AI response. "
                "Check that Ollama is running and llama3 is installed."
            )
        ) from exc
