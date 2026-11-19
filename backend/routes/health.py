"""Health and service configuration route."""

from fastapi import APIRouter
from backend.schemas.models import HealthResponse
from backend.services.gemini_service import (
    DEFAULT_GEMINI_MODEL,
    SUPPORTED_MODELS,
    gemini_service,
)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Return API health status, active Gemini model, and configuration state."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        gemini_configured=gemini_service.is_configured(),
        active_model=gemini_service.get_model_name(),
        supported_models=SUPPORTED_MODELS,
    )
