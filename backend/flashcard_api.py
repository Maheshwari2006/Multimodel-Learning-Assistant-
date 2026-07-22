from fastapi import APIRouter
from study_tools.flashcard_generator import (
    FlashcardGenerator
)

router = APIRouter()

@router.post("/flashcards")
def generate_flashcards(text: str):

    generator = FlashcardGenerator()

    flashcards = (
        generator.generate_flashcards(text)
    )

    return {
        "flashcards": flashcards
    }