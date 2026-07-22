from fastapi import APIRouter
from pydantic import BaseModel

from rag.qa_system import RAGQuestionAnswering

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


class RAGRequest(BaseModel):
    context: str
    question: str


@router.post("/ask")
def ask_question(request: RAGRequest):

    rag = RAGQuestionAnswering()

    answer = rag.answer_question(
        request.context,
        request.question
    )

    return {
        "question": request.question,
        "answer": answer
    }