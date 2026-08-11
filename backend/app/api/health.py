from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
def get_health():
    """Returns basic service health status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
