"""Summaries of selected documents (or pasted text). POST /summary/ still returns ``summary``."""
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.learning_logic import build_summary, language_name
from backend.llm import llm
from backend.services import ids_dump, iso, jloads, map_llm_errors, source_chunks

router = APIRouter(prefix="/summary", tags=["Summary"])


class SummaryRequest(BaseModel):
    document_ids: List[int] = []
    text: Optional[str] = None
    length: str = "medium"
    language: str = "english"


def summary_dict(s: models.StudySummary) -> dict:
    body = jloads(s.content, {}) if s.content else {}
    return {
        "id": s.id, "title": s.title, "length": s.length, "language": language_name(s.language),
        "document_ids": jloads(s.document_ids), "created_at": iso(s.created_at),
        "summary": body.get("summary", ""), "key_points": body.get("key_points", []),
        "definitions": body.get("definitions", []), "sections": body.get("sections", []),
        "coverage": body.get("coverage", "full"),
    }


@router.post("/")
@router.post("")
def generate_summary(request: SummaryRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not request.document_ids and not (request.text or "").strip():
        raise HTTPException(status_code=400, detail="Select a document or paste some text to summarise.")
    _, chunks, label = source_chunks(db, user, request.document_ids, request.text)
    data = map_llm_errors(lambda: build_summary(llm, chunks, request.length, request.language))
    row = models.StudySummary(
        user_id=user.id, title=label[:240], length=data["length"], language=request.language,
        document_ids=ids_dump(request.document_ids), content=json.dumps(data),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return summary_dict(row)


@router.get("/history")
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (db.query(models.StudySummary).filter_by(user_id=user.id)
            .order_by(models.StudySummary.created_at.desc()).limit(50).all())
    return [{"id": s.id, "title": s.title, "length": s.length, "created_at": iso(s.created_at)} for s in rows]


@router.get("/{summary_id}")
def get_summary(summary_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(models.StudySummary).filter_by(id=summary_id, user_id=user.id).first()
    if s is None:
        raise HTTPException(status_code=404, detail="Summary not found.")
    return summary_dict(s)
