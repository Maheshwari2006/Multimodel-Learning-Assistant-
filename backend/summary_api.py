from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/summary",
    tags=["Summary"]
)


class SummaryRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str


@router.post("/", response_model=SummaryResponse)
def generate_summary(
    request: SummaryRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate a simple summary.
    Authentication required.
    """

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    # Simple summary (first 200 characters)
    summary = request.text[:200]

    if len(request.text) > 200:
        summary += "..."

    return SummaryResponse(summary=summary)