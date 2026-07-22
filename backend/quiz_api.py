from fastapi import APIRouter
from study_tools.quiz_generator import QuizGenerator

router = APIRouter()

@router.post("/quiz")
def generate_quiz(text: str):

    generator = QuizGenerator()

    quiz = generator.generate_quiz(text)

    return {
        "quiz": quiz
    }