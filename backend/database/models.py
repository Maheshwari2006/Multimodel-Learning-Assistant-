from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database.database import Base


# ==========================
# User
# ==========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================
# Uploaded Files
# ==========================

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    filepath = Column(String(500), nullable=False)

    filetype = Column(String(100), nullable=False)

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================
# Summary
# ==========================

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    summary = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================
# Quiz
# ==========================

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    questions = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================
# Flashcards
# ==========================

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    cards = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================
# Chat History
# ==========================

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ======================================================================
# Document intelligence + learning features (all rows belong to a user)
# ======================================================================

class Document(Base):
    """An uploaded file. ``status``: processing -> ready | failed."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)      # generated id on disk, never the user's filename
    ext = Column(String(20), nullable=False)
    mime_type = Column(String(120))
    size_bytes = Column(Integer, default=0)
    status = Column(String(20), default="processing", index=True)
    error = Column(Text)
    warnings = Column(Text)                                # JSON list
    page_count = Column(Integer)
    char_count = Column(Integer)
    chunk_count = Column(Integer)
    ocr_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    chunks = relationship("DocumentChunk", cascade="all, delete-orphan", passive_deletes=False)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True, nullable=False)
    idx = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page = Column(Integer)
    section = Column(String(300))
    kind = Column(String(20), default="text")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(200), default="New chat")
    document_ids = Column(Text)                            # JSON list
    language = Column(String(20), default="english")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ChatMessage", cascade="all, delete-orphan", order_by="ChatMessage.id")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), index=True, nullable=False)
    role = Column(String(20), nullable=False)              # user | assistant
    content = Column(Text, nullable=False)
    mode = Column(String(20))                              # document | general (assistant only)
    sources = Column(Text)                                 # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)


class StudySummary(Base):
    __tablename__ = "study_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(250))
    length = Column(String(20))
    language = Column(String(20))
    document_ids = Column(Text)                            # JSON list
    content = Column(Text)                                 # JSON: summary, key_points, definitions, sections, coverage
    created_at = Column(DateTime, default=datetime.utcnow)


class QuizAttempt(Base):
    """One generated quiz = one attempt row. Retaking creates a new row with the same questions."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(250))
    difficulty = Column(String(20))
    language = Column(String(20))
    document_ids = Column(Text)                            # JSON list
    questions = Column(Text)                               # JSON, includes the answers (never sent before submit)
    answers = Column(Text)                                 # JSON list of chosen indexes / null
    correct = Column(Integer)
    total = Column(Integer)
    score_pct = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)


class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(250))
    document_ids = Column(Text)                            # JSON list
    language = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("FlashcardItem", cascade="all, delete-orphan", order_by="FlashcardItem.idx")


class FlashcardItem(Base):
    __tablename__ = "flashcard_items"

    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"), index=True, nullable=False)
    idx = Column(Integer, default=0)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    status = Column(String(10), default="new")             # new | known | review
    reviewed_at = Column(DateTime)


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(250))
    topic = Column(String(250))
    document_ids = Column(Text)                            # JSON list
    days = Column(Integer, default=7)
    hours_per_day = Column(Float, default=1)
    start_date = Column(String(10))                        # ISO date
    language = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("StudyTask", cascade="all, delete-orphan", order_by="(StudyTask.day, StudyTask.id)")


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id"), index=True, nullable=False)
    day = Column(Integer, default=1)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    minutes = Column(Integer, default=30)
    done = Column(Boolean, default=False)
    scheduled_date = Column(String(10))                    # ISO date -> plain string compare works
    completed_at = Column(DateTime)
