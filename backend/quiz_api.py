"""Quizzes generated from documents, with scoring, explanations, history and retake.

The correct answers stay on the server until the attempt is submitted.
The original ``POST /quiz`` ({text}) endpoint is kept for backwards compatibility.
"""
import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.learning_logic import build_quiz
from backend.llm import llm
from backend.services import ids_dump, iso, jloads, map_llm_errors, source_chunks

router = APIRouter(tags=["Quiz"])


class QuizGenerate(BaseModel):
    document_ids: List[int] = []
    text: Optional[str] = None
    count: int = Field(5, ge=1, le=20)
    difficulty: str = "medium"
    language: str = "english"


class QuizSubmit(BaseModel):
    answers: List[Optional[int]]


class LegacyQuizRequest(BaseModel):
    text: str = Field(..., min_length=1)


def public_quiz(a: models.QuizAttempt) -> dict:
    questions = jloads(a.questions)
    return {
        "id": a.id, "title": a.title, "difficulty": a.difficulty, "language": a.language,
        "questions": [{"question": q["question"], "options": q["options"]} for q in questions],
    }


def _own_attempt(db: Session, user, attempt_id: int) -> models.QuizAttempt:
    a = db.query(models.QuizAttempt).filter_by(id=attempt_id, user_id=user.id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return a


@router.post("/quiz/generate")
def generate_quiz(request: QuizGenerate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _, chunks, label = source_chunks(db, user, request.document_ids, request.text)
    questions = map_llm_errors(
        lambda: build_quiz(llm, chunks, request.count, request.difficulty, request.language)
    )
    attempt = models.QuizAttempt(
        user_id=user.id, title=label[:240], difficulty=request.difficulty, language=request.language,
        document_ids=ids_dump(request.document_ids), questions=json.dumps(questions), total=len(questions),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return public_quiz(attempt)


@router.post("/quiz/attempts/{attempt_id}/submit")
def submit_quiz(attempt_id: int, body: QuizSubmit, db: Session = Depends(get_db), user=Depends(get_current_user)):
    attempt = _own_attempt(db, user, attempt_id)
    if attempt.submitted_at is not None:
        raise HTTPException(status_code=409, detail="This quiz was already submitted. Use retry to take it again.")
    questions = jloads(attempt.questions)
    if len(body.answers) != len(questions):
        raise HTTPException(status_code=400, detail=f"Expected {len(questions)} answers, got {len(body.answers)}.")
    results, correct = [], 0
    for q, chosen in zip(questions, body.answers):
        if chosen is not None and not 0 <= chosen < len(q["options"]):
            raise HTTPException(status_code=400, detail="An answer refers to a non-existent option.")
        ok = chosen == q["answer_index"]
        correct += ok
        results.append({**q, "chosen": chosen, "is_correct": ok})
    attempt.answers = json.dumps(list(body.answers))
    attempt.correct, attempt.total = correct, len(questions)
    attempt.score_pct = round(100.0 * correct / max(len(questions), 1), 1)
    attempt.submitted_at = datetime.utcnow()
    db.commit()
    return {"id": attempt.id, "title": attempt.title, "correct": correct, "total": attempt.total,
            "score_pct": attempt.score_pct, "results": results}


@router.post("/quiz/attempts/{attempt_id}/retake")
def retake_quiz(attempt_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    old = _own_attempt(db, user, attempt_id)
    new = models.QuizAttempt(
        user_id=user.id, title=old.title, difficulty=old.difficulty, language=old.language,
        document_ids=old.document_ids, questions=old.questions, total=old.total,
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return public_quiz(new)


@router.get("/quiz/attempts")
def quiz_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (db.query(models.QuizAttempt)
            .filter(models.QuizAttempt.user_id == user.id, models.QuizAttempt.submitted_at.isnot(None))
            .order_by(models.QuizAttempt.submitted_at.desc()).limit(50).all())
    return [{"id": a.id, "title": a.title, "difficulty": a.difficulty, "correct": a.correct, "total": a.total,
             "score_pct": a.score_pct, "submitted_at": iso(a.submitted_at)} for a in rows]


@router.post("/quiz")
def legacy_quiz(request: LegacyQuizRequest, user=Depends(get_current_user)):
    """Original endpoint: quiz from raw text, nothing stored."""
    from backend.services import text_chunks
    questions = map_llm_errors(lambda: build_quiz(llm, text_chunks(request.text), 5, "medium", "english"))
    return {"quiz": questions}
