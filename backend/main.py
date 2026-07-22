from fastapi import FastAPI

from backend.database.database import Base, engine

from backend.auth.auth_api import router as auth_router

from backend.upload_api import router as upload_router
from backend.chat_api import router as chat_router
from backend.summary_api import router as summary_router
from backend.quiz_api import router as quiz_router
from backend.flashcard_api import router as flashcard_router
from backend.study_plan_api import router as study_plan_router
from backend.recommendation_api import router as recommendation_router
from backend.rag_api import router as rag_router


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multimodal Learning Assistant API",
    version="1.0.0"
)

app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(summary_router)
app.include_router(quiz_router)
app.include_router(flashcard_router)
app.include_router(study_plan_router)
app.include_router(recommendation_router)
app.include_router(rag_router)
app.include_router(auth_router)
app.include_router(auth_router, tags=["Authentication"])

@app.get("/")
def root():
    return {
        "message": "Multimodal Learning Assistant API Running Successfully"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }