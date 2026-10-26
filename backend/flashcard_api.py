"""Persistent flashcard decks with known / needs-review tracking.

``POST /flashcards`` (text as a query parameter) is the original endpoint and still works.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.learning_logic import build_flashcards
from backend.llm import llm
from backend.services import ids_dump, iso, jloads, map_llm_errors, source_chunks, text_chunks

router = APIRouter(tags=["Flashcards"])

STATUSES = {"new", "known", "review"}


class DeckGenerate(BaseModel):
    document_ids: List[int] = []
    text: Optional[str] = None
    count: int = Field(10, ge=1, le=40)
    language: str = "english"


class CardIn(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class DeckCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    cards: List[CardIn] = Field(..., min_length=1)


class DeckRename(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class CardStatus(BaseModel):
    status: str


def deck_summary(d: models.FlashcardDeck) -> dict:
    total = len(d.items)
    known = sum(1 for c in d.items if c.status == "known")
    review = sum(1 for c in d.items if c.status == "review")
    return {"id": d.id, "title": d.title, "total": total, "known": known, "review": review,
            "new": total - known - review, "created_at": iso(d.created_at), "document_ids": jloads(d.document_ids)}


def deck_full(d: models.FlashcardDeck) -> dict:
    return {**deck_summary(d), "cards": [
        {"id": c.id, "question": c.question, "answer": c.answer, "status": c.status} for c in d.items]}


def _own_deck(db: Session, user, deck_id: int) -> models.FlashcardDeck:
    d = db.query(models.FlashcardDeck).filter_by(id=deck_id, user_id=user.id).first()
    if d is None:
        raise HTTPException(status_code=404, detail="Deck not found.")
    return d


def _make_deck(db, user, title, cards, document_ids=(), language="english") -> models.FlashcardDeck:
    deck = models.FlashcardDeck(user_id=user.id, title=title[:240], document_ids=ids_dump(document_ids), language=language)
    deck.items = [models.FlashcardItem(idx=i, question=c["question"], answer=c["answer"], status="new")
                  for i, c in enumerate(cards)]
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


@router.post("/flashcards/generate")
def generate_deck(request: DeckGenerate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _, chunks, label = source_chunks(db, user, request.document_ids, request.text)
    cards = map_llm_errors(lambda: build_flashcards(llm, chunks, request.count, request.language))
    return deck_full(_make_deck(db, user, label, cards, request.document_ids, request.language))


@router.post("/flashcards/decks", status_code=201)
def create_deck(body: DeckCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cards = [{"question": c.question.strip(), "answer": c.answer.strip()} for c in body.cards]
    return deck_full(_make_deck(db, user, body.title.strip(), cards))


@router.get("/flashcards/decks")
def list_decks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    decks = (db.query(models.FlashcardDeck).filter_by(user_id=user.id)
             .order_by(models.FlashcardDeck.created_at.desc()).all())
    return [deck_summary(d) for d in decks]


@router.get("/flashcards/decks/{deck_id}")
def get_deck(deck_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return deck_full(_own_deck(db, user, deck_id))


@router.patch("/flashcards/decks/{deck_id}")
def rename_deck(deck_id: int, body: DeckRename, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = _own_deck(db, user, deck_id)
    d.title = body.title.strip()
    db.commit()
    return deck_summary(d)


@router.delete("/flashcards/decks/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.delete(_own_deck(db, user, deck_id))
    db.commit()
    return {"deleted": deck_id}


@router.post("/flashcards/decks/{deck_id}/reset")
def reset_deck(deck_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = _own_deck(db, user, deck_id)
    for c in d.items:
        c.status, c.reviewed_at = "new", None
    db.commit()
    return deck_full(d)


@router.patch("/flashcards/items/{item_id}")
def mark_card(item_id: int, body: CardStatus, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if body.status not in STATUSES:
        raise HTTPException(status_code=400, detail="Status must be one of: new, known, review.")
    from datetime import datetime
    item = (db.query(models.FlashcardItem).join(models.FlashcardDeck, models.FlashcardItem.deck_id == models.FlashcardDeck.id)
            .filter(models.FlashcardItem.id == item_id, models.FlashcardDeck.user_id == user.id).first())
    if item is None:
        raise HTTPException(status_code=404, detail="Card not found.")
    item.status = body.status
    item.reviewed_at = None if body.status == "new" else datetime.utcnow()
    db.commit()
    return {"id": item.id, "status": item.status}


@router.post("/flashcards")
def legacy_generate(text: str, user=Depends(get_current_user)):
    """Original endpoint: flashcards from raw text, nothing stored."""
    cards = map_llm_errors(lambda: build_flashcards(llm, text_chunks(text), 10, "english"))
    return {"flashcards": cards}
