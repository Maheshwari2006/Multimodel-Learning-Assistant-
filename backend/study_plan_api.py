from fastapi import APIRouter
from pydantic import BaseModel

from learning_assistant.study_planner import StudyPlanner

router = APIRouter(
    prefix="/study-plan",
    tags=["Study Planner"]
)


class StudyPlanRequest(BaseModel):
    topic: str
    days: int


@router.post("/")
def generate_plan(request: StudyPlanRequest):

    planner = StudyPlanner()

    plan = planner.generate_plan(
        request.topic,
        request.days
    )

    return {
        "study_plan": plan
    }