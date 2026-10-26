from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.services import doc_dict, iso

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
@router.get("/")
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    uid = user.id
    docs = db.query(models.Document).filter_by(user_id=uid).order_by(models.Document.created_at.desc()).all()
    sessions = db.query(models.ChatSession).filter_by(user_id=uid).order_by(models.ChatSession.updated_at.desc()).all()
    attempts = (db.query(models.QuizAttempt)
                .filter(models.QuizAttempt.user_id == uid, models.QuizAttempt.submitted_at.isnot(None))
                .order_by(models.QuizAttempt.submitted_at.desc()).all())
    decks = db.query(models.FlashcardDeck).filter_by(user_id=uid).order_by(models.FlashcardDeck.created_at.desc()).all()
    plans = db.query(models.StudyPlan).filter_by(user_id=uid).order_by(models.StudyPlan.created_at.desc()).all()
    summaries = db.query(models.StudySummary).filter_by(user_id=uid).order_by(models.StudySummary.created_at.desc()).all()

    cards = [i for d in decks for i in d.items]
    tasks = [t for p in plans for t in p.tasks]
    today = date.today().isoformat()

    activity = []
    for d in docs[:8]:
        activity.append({"type": "upload", "text": f"Uploaded {d.original_name}", "at": iso(d.created_at), "path": "/upload"})
    for s in sessions[:8]:
        activity.append({"type": "chat", "text": f"Chat: {s.title}", "at": iso(s.updated_at), "path": f"/chat?session={s.id}"})
    for a in attempts[:8]:
        activity.append({"type": "quiz", "text": f"Quiz on {a.title}: {round(a.score_pct or 0)}%", "at": iso(a.submitted_at), "path": "/quiz"})
    for d in decks[:8]:
        activity.append({"type": "flashcards", "text": f"Created deck {d.title}", "at": iso(d.created_at), "path": f"/flashcards?deck={d.id}"})
    for p in plans[:8]:
        activity.append({"type": "plan", "text": f"Created study plan {p.title}", "at": iso(p.created_at), "path": f"/study-plan?plan={p.id}"})
    for s in summaries[:8]:
        activity.append({"type": "summary", "text": f"Summarised {s.title}", "at": iso(s.created_at), "path": "/summary"})
    for t in tasks:
        if t.done and t.completed_at:
            activity.append({"type": "task", "text": f"Completed: {t.title}", "at": iso(t.completed_at), "path": "/study-plan"})
    activity.sort(key=lambda a: a["at"] or "", reverse=True)

    return {
        "user": {"username": user.username, "email": user.email},
        "stats": {
            "documents": len(docs),
            "documents_ready": sum(1 for d in docs if d.status == "ready"),
            "documents_processing": sum(1 for d in docs if d.status in ("processing", "uploaded")),
            "documents_failed": sum(1 for d in docs if d.status == "failed"),
            "conversations": len(sessions),
            "quizzes_taken": len(attempts),
            "average_quiz_score": round(sum(a.score_pct or 0 for a in attempts) / len(attempts)) if attempts else None,
            "flashcards_total": len(cards),
            "flashcards_known": sum(1 for c in cards if c.status == "known"),
            "tasks_total": len(tasks),
            "tasks_done": sum(1 for t in tasks if t.done),
            "tasks_overdue": sum(1 for t in tasks if not t.done and t.scheduled_date and t.scheduled_date < today),
        },
        "recent_documents": [doc_dict(d) for d in docs[:5]],
        "recent_conversations": [{"id": s.id, "title": s.title, "updated_at": iso(s.updated_at)} for s in sessions[:5]],
        "activity": activity[:10],
    }
