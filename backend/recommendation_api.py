from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

from learning_assistant.recommendation_engine import RecommendationEngine

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"]
)


class RecommendationRequest(BaseModel):
    quiz_scores: Dict[str, int]
    completed_topics: List[str]


@router.post("/")
def recommend(request: RecommendationRequest):

    engine = RecommendationEngine()

    recommendations = engine.recommend(
        request.quiz_scores,
        request.completed_topics
    )

    return {
        "recommendations": recommendations
    }