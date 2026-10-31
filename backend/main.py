
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import Base, engine

from backend.upload_api import router as upload_router
from backend.chat_api import router as chat_router
from backend.summary_api import router as summary_router
from backend.quiz_api import router as quiz_router
from backend.flashcard_api import router as flashcard_router
from backend.study_plan_api import router as study_plan_router
from backend.recommendation_api import router as recommendation_router
from backend.rag_api import router as rag_router
from backend.auth.auth_api import router as auth_router
from backend.documents_api import router as documents_router
from backend.dashboard_api import router as dashboard_router


app = FastAPI(
    title="Multimodal Learning Assistant API",
    description="Backend API for Multimodal Learning Assistant",
    version="2.0.0",
)


# CORS configuration
allowed_origins = [
    "https://multimodel-learning-assistant.vercel.app",
    "https://multimodal-learning-assistant.vercel.app",
    "https://multimodal-learning-assistant-6biloys96-innovators-f783.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_origin = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")

if frontend_origin and frontend_origin not in allowed_origins:
    allowed_origins.append(frontend_origin)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://multimodel-learning-assistant-[a-zA-Z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(dashboard_router)
app.include_router(chat_router)
app.include_router(summary_router)
app.include_router(quiz_router)
app.include_router(flashcard_router)
app.include_router(study_plan_router)
app.include_router(recommendation_router)
app.include_router(rag_router)
app.include_router(auth_router, tags=["Authentication"])


@app.get("/")
def root():
    return {
        "message": "Multimodal Learning Assistant API Running Successfully"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# Database table creation (optional)
if os.getenv("CREATE_TABLES_ON_STARTUP", "false").lower() == "true":
    Base.metadata.create_all(bind=engine)
