
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from study_tools.quiz_generator import QuizGenerator

router = APIRouter(tags=["Quiz"])


class QuizRequest(BaseModel):
    text: str = Field(..., min_length=1)


@router.post("/quiz")
def generate_quiz(request: QuizRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Please provide learning material to generate a quiz."
        )

    try:
        generator = QuizGenerator()
        quiz = generator.generate_quiz(text)

        return {"quiz": quiz}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate the quiz. Please check the AI service and try again."
        ) from exc
