from sqlalchemy.orm import Session

from backend.database import models
from backend.auth.hashing import hash_password, verify_password


# ==========================
# User Authentication
# ==========================

def create_user(db: Session, user):

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_by_email(db: Session, email: str):

    return (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.password):
        return None

    return user


# ==========================
# Uploaded Files
# ==========================

def save_uploaded_file(db: Session, filename, filepath, filetype):

    file = models.UploadedFile(
        filename=filename,
        filepath=filepath,
        filetype=filetype
    )

    db.add(file)
    db.commit()
    db.refresh(file)

    return file


# ==========================
# Summary
# ==========================

def save_summary(db: Session, filename, summary):

    obj = models.Summary(
        filename=filename,
        summary=summary
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# ==========================
# Quiz
# ==========================

def save_quiz(db: Session, filename, questions):

    obj = models.Quiz(
        filename=filename,
        questions=questions
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# ==========================
# Flashcards
# ==========================

def save_flashcards(db: Session, filename, cards):

    obj = models.Flashcard(
        filename=filename,
        cards=cards
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# ==========================
# Chat History
# ==========================

def save_chat(db: Session, question, answer):

    chat = models.ChatHistory(
        question=question,
        answer=answer
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat