from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.domain.models import DebateResponse
from app.services.debate_service import DebateService
from app.api.dependencies import get_debate_service

router = APIRouter(tags=["debate"])


class DebateApiRequest(BaseModel):
    """Request payload for evidence-based debate generation."""
    topic: str = Field(..., description="Debate topic or statement to analyze")
    min_evidence_score: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Optional minimum cosine similarity score threshold for evidence relevance"
    )


@router.post("/debate", response_model=DebateResponse, summary="Generate Evidence-Backed Debate")
def generate_debate(
    request: DebateApiRequest,
    service: DebateService = Depends(get_debate_service)
) -> DebateResponse:
    """
    Generates a structured debate response grounded strictly in retrieved quote evidence.
    If evidence relevance is insufficient, returns a controlled refusal message.
    """
    if not request.topic or not request.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debate topic cannot be empty or whitespace."
        )

    cleaned_topic = request.topic.strip()

    try:
        response = service.generate_debate(
            topic=cleaned_topic,
            override_min_score=request.min_evidence_score
        )
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during debate generation."
        )
