"""Study plans generated from a topic or from documents, with editable, trackable tasks.

``POST /study-plan/`` ({topic, days}) is the original endpoint and still works.
"""
import json
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.learning_logic import build_plan, schedule_dates
from backend.llm import llm
from backend.services import ids_dump, iso, jloads, load_chunks, get_user_docs, docs_label, map_llm_errors

router = APIRouter(prefix="/study-plan", tags=["Study Planner"])


class PlanGenerate(BaseModel):
    topic: Optional[str] = None
    document_ids: List[int] = []
    days: int = Field(7, ge=1, le=60)
    hours_per_day: float = Field(1, ge=0.25, le=8)
    language: str = "english"
    start_date: Optional[str] = None
    weekdays: Optional[List[int]] = None        # Monday=0 ... Sunday=6


class TaskPatch(BaseModel):
    done: Optional[bool] = None
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    minutes: Optional[int] = Field(None, ge=5, le=480)


class TaskCreate(BaseModel):
    day: int = Field(1, ge=1)
    title: str = Field(..., min_length=1, max_length=300)
    description: str = ""
    minutes: int = Field(30, ge=5, le=480)


class LegacyPlan(BaseModel):
    topic: str
    days: int


def task_dict(t: models.StudyTask) -> dict:
    return {"id": t.id, "plan_id": t.plan_id, "day": t.day, "title": t.title, "description": t.description or "",
            "minutes": t.minutes, "done": bool(t.done), "scheduled_date": t.scheduled_date,
            "completed_at": iso(t.completed_at)}


def plan_stats(p: models.StudyPlan) -> dict:
    today = date.today().isoformat()
    total = len(p.tasks)
    done = sum(1 for t in p.tasks if t.done)
    overdue = sum(1 for t in p.tasks if not t.done and t.scheduled_date and t.scheduled_date < today)
    return {"id": p.id, "title": p.title, "topic": p.topic, "days": p.days, "hours_per_day": p.hours_per_day,
            "start_date": p.start_date, "document_ids": jloads(p.document_ids), "created_at": iso(p.created_at),
            "total": total, "done": done, "overdue": overdue,
            "progress": round(100 * done / total) if total else 0}


def plan_full(p: models.StudyPlan) -> dict:
    return {**plan_stats(p), "tasks": [task_dict(t) for t in p.tasks]}


def _own_plan(db: Session, user, plan_id: int) -> models.StudyPlan:
    p = db.query(models.StudyPlan).filter_by(id=plan_id, user_id=user.id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Study plan not found.")
    return p


def _own_task(db: Session, user, task_id: int) -> models.StudyTask:
    t = (db.query(models.StudyTask).join(models.StudyPlan, models.StudyTask.plan_id == models.StudyPlan.id)
         .filter(models.StudyTask.id == task_id, models.StudyPlan.user_id == user.id).first())
    if t is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return t


def _day_dates(plan: models.StudyPlan, weekdays) -> dict:
    start = date.fromisoformat(plan.start_date) if plan.start_date else date.today()
    return {i + 1: d.isoformat() for i, d in enumerate(schedule_dates(plan.days, start, weekdays))}


@router.post("/generate")
def generate(request: PlanGenerate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    topic = (request.topic or "").strip()
    if not topic and not request.document_ids:
        raise HTTPException(status_code=400, detail="Enter a topic or select a document.")
    try:
        start = date.fromisoformat(request.start_date) if request.start_date else date.today()
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date must look like 2026-12-31.")
    if request.weekdays is not None and (not request.weekdays or any(not 0 <= w <= 6 for w in request.weekdays)):
        raise HTTPException(status_code=400, detail="Choose at least one study weekday (0=Monday ... 6=Sunday).")

    docs, chunks = [], []
    if request.document_ids:
        docs = get_user_docs(db, user, request.document_ids)
        chunks = load_chunks(db, docs)
    subject = topic or docs_label(docs)
    data = map_llm_errors(lambda: build_plan(llm, chunks, subject, request.days, request.hours_per_day, request.language))

    plan = models.StudyPlan(
        user_id=user.id, title=data["title"], topic=topic or None, document_ids=ids_dump(request.document_ids),
        days=request.days, hours_per_day=request.hours_per_day, start_date=start.isoformat(), language=request.language,
    )
    dates = _day_dates(plan, request.weekdays)
    plan.tasks = [models.StudyTask(day=t["day"], title=t["title"], description=t["description"], minutes=t["minutes"],
                                   scheduled_date=dates.get(t["day"])) for t in data["tasks"]]
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan_full(plan)


@router.get("/plans")
def list_plans(db: Session = Depends(get_db), user=Depends(get_current_user)):
    plans = db.query(models.StudyPlan).filter_by(user_id=user.id).order_by(models.StudyPlan.created_at.desc()).all()
    return [plan_stats(p) for p in plans]


@router.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return plan_full(_own_plan(db, user, plan_id))


@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.delete(_own_plan(db, user, plan_id))
    db.commit()
    return {"deleted": plan_id}


@router.patch("/tasks/{task_id}")
def patch_task(task_id: int, body: TaskPatch, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = _own_task(db, user, task_id)
    if body.title is not None:
        t.title = body.title.strip()
    if body.description is not None:
        t.description = body.description.strip()
    if body.minutes is not None:
        t.minutes = body.minutes
    if body.done is not None:
        t.done = body.done
        t.completed_at = datetime.utcnow() if body.done else None
    db.commit()
    return task_dict(t)


@router.post("/plans/{plan_id}/tasks", status_code=201)
def add_task(plan_id: int, body: TaskCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    plan = _own_plan(db, user, plan_id)
    day = min(body.day, plan.days)
    same_day = [t.scheduled_date for t in plan.tasks if t.day == day and t.scheduled_date]
    t = models.StudyTask(plan_id=plan.id, day=day, title=body.title.strip(), description=body.description.strip(),
                         minutes=body.minutes, scheduled_date=same_day[0] if same_day else None)
    db.add(t)
    db.commit()
    db.refresh(t)
    return task_dict(t)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.delete(_own_task(db, user, task_id))
    db.commit()
    return {"deleted": task_id}


@router.post("/")
def legacy_plan(request: LegacyPlan, user=Depends(get_current_user)):
    """Original endpoint: plan from a topic, nothing stored."""
    from learning_assistant.study_planner import StudyPlanner
    return {"study_plan": StudyPlanner().generate_plan(request.topic, request.days)}
