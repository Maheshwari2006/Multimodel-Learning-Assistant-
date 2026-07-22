from sqlalchemy import Column, Integer, String, DateTime, Text
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