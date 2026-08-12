from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.domain.models import SearchResult
from app.services.semantic_retriever import SemanticRetriever
from app.api.dependencies import get_semantic_retriever

router = APIRouter(tags=["search"])


class SearchRequest(BaseModel):
    """Request payload for semantic quote search."""
    query: str = Field(..., description="Personal situation, emotion, or abstract thought string")


@router.post("/search", response_model=SearchResult, summary="Semantic Quote Search")
def search_quotes(
    request: SearchRequest,
    retriever: SemanticRetriever = Depends(get_semantic_retriever)
) -> SearchResult:
    """
    Executes pure semantic search for a given query string against indexed quote embeddings.
    Returns the top 3 most semantically relevant quotes.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty or whitespace."
        )

    cleaned_query = request.query.strip()

    try:
        matches = retriever.search(query=cleaned_query, top_k=3)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during search processing."
        )

    return SearchResult(
        query=cleaned_query,
        matches=matches,
        total_found=len(matches)
    )
