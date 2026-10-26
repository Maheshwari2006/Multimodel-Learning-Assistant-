"""Recommendations built only from the user's real learning history.

``POST /recommendation/`` ({quiz_scores, completed_topics}) is the original endpoint and still works.
"""
from datetime import date
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.learning_logic import compute_recommendations
from backend.services import jloads

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])


class RecommendationRequest(BaseModel):
    quiz_scores: Dict[str, int]
    completed_topics: List[str]


@router.get("/")
@router.get("")
def recommendations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    uid = user.id
    docs = db.query(models.Document).filter_by(user_id=uid).all()
    attempts = (db.query(models.QuizAttempt)
                .filter(models.QuizAttempt.user_id == uid, models.QuizAttempt.submitted_at.isnot(None)).all())
    decks = db.query(models.FlashcardDeck).filter_by(user_id=uid).all()
    plans = db.query(models.StudyPlan).filter_by(user_id=uid).all()
    summaries = db.query(models.StudySummary).filter_by(user_id=uid).all()

    used = {}                                   # document id -> number of learning activities built from it
    for row in [*attempts, *decks, *plans, *summaries]:
        for doc_id in jloads(row.document_ids):
            used[doc_id] = used.get(doc_id, 0) + 1

    attempt_rows = []
    for a in attempts:
        questions, answers = jloads(a.questions), jloads(a.answers)
        missed = [q["question"] for q, chosen in zip(questions, answers) if chosen != q.get("answer_index")]
        attempt_rows.append({
            "id": a.id, "title": a.title, "score_pct": a.score_pct or 0, "correct": a.correct or 0,
            "total": a.total or 0, "when": a.submitted_at.isoformat(), "document_ids": jloads(a.document_ids),
            "missed": missed,
        })
    deck_rows = []
    for d in decks:
        total = len(d.items)
        review = sum(1 for c in d.items if c.status == "review")
        new = sum(1 for c in d.items if c.status == "new")
        deck_rows.append({"id": d.id, "title": d.title, "total": total, "review": review, "new": new})
    today = date.today().isoformat()
    plan_rows = [{
        "id": p.id, "title": p.title, "total": len(p.tasks), "done": sum(1 for t in p.tasks if t.done),
        "overdue": sum(1 for t in p.tasks if not t.done and t.scheduled_date and t.scheduled_date < today),
    } for p in plans]
    doc_rows = [{"id": d.id, "name": d.original_name, "status": d.status, "activity": used.get(d.id, 0)} for d in docs]

    return {
        "recommendations": compute_recommendations(doc_rows, attempt_rows, deck_rows, plan_rows),
        "basis": {"documents": len(docs), "quizzes_taken": len(attempts),
                  "flashcard_decks": len(decks), "study_plans": len(plans)},
    }


@router.post("/")
def legacy_recommend(request: RecommendationRequest, user=Depends(get_current_user)):
    """Original endpoint: rule-based advice from scores the caller supplies."""
    from learning_assistant.recommendation_engine import RecommendationEngine
    return {"recommendations": RecommendationEngine().recommend(request.quiz_scores, request.completed_topics)}
