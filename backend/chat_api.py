"""Document-grounded chat (RAG) with persisted conversations.

POST /chat/query is backwards compatible: the old ``{message, context}`` body still works.
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
from backend.learning_logic import build_general_messages, build_rag_messages, retrieval_query
from backend.llm import llm
from backend.services import (get_user_docs, ids_dump, iso, jloads, load_chunks, map_llm_errors, retrieve,
                              text_chunks)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: Optional[int] = None
    document_ids: List[int] = []
    language: Optional[str] = "english"
    context: Optional[str] = None          # legacy: raw text instead of stored documents


def msg_dict(m: models.ChatMessage) -> dict:
    return {
        "id": m.id, "role": m.role, "content": m.content, "mode": m.mode,
        "sources": jloads(m.sources), "created_at": iso(m.created_at),
    }


def _own_session(db: Session, user, session_id: int) -> models.ChatSession:
    s = db.query(models.ChatSession).filter_by(id=session_id, user_id=user.id).first()
    if s is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return s


@router.post("/query")
def chat(request: ChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    question = request.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please enter a question.")

    session = _own_session(db, user, request.session_id) if request.session_id else None
    history = [{"role": m.role, "content": m.content} for m in session.messages] if session else []
    language = request.language or "english"

    docs = get_user_docs(db, user, request.document_ids) if request.document_ids else []
    chunks = load_chunks(db, docs) if docs else []
    if not chunks and request.context and request.context.strip():
        chunks = text_chunks(request.context, "Provided text")

    if chunks:
        picked = retrieve(chunks, retrieval_query(question, history))
        messages, sources = build_rag_messages(question, history, picked, language)
        mode = "document"
    else:
        if request.document_ids:
            raise HTTPException(status_code=409, detail="The selected documents contain no readable text.")
        messages, sources, mode = build_general_messages(question, history, language), [], "general"

    answer = map_llm_errors(lambda: llm.chat(messages, temperature=0.3)).strip()
    if not answer:
        raise HTTPException(status_code=502, detail="The model returned an empty answer. Please try again.")

    # Persist only after a successful answer, so a failed request can be retried without duplicates.
    now = datetime.utcnow()
    if session is None:
        session = models.ChatSession(user_id=user.id, title=question[:60], created_at=now)
        db.add(session)
    session.document_ids = ids_dump(request.document_ids)
    session.language = language
    session.updated_at = now
    db.flush()
    db.add(models.ChatMessage(session_id=session.id, role="user", content=question, created_at=now))
    reply = models.ChatMessage(session_id=session.id, role="assistant", content=answer, mode=mode,
                               sources=json.dumps(sources), created_at=now)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return {"session_id": session.id, "message": msg_dict(reply),
            # legacy field names
            "question": question, "response": answer}


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (db.query(models.ChatSession).filter_by(user_id=user.id)
            .order_by(models.ChatSession.updated_at.desc()).limit(100).all())
    return [{"id": s.id, "title": s.title, "updated_at": iso(s.updated_at), "document_ids": jloads(s.document_ids)}
            for s in rows]


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = _own_session(db, user, session_id)
    existing = {d.id for d in db.query(models.Document.id).filter_by(user_id=user.id).all()}
    return {
        "id": s.id, "title": s.title, "language": s.language,
        "document_ids": [i for i in jloads(s.document_ids) if i in existing],   # skip documents deleted since
        "messages": [msg_dict(m) for m in s.messages],
    }


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = _own_session(db, user, session_id)
    db.delete(s)
    db.commit()
    return {"deleted": session_id}
