"""
Health check endpoint.
"""
from fastapi import APIRouter, HTTPException

from app.db.connection import health_check
from app.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Health check endpoint."""
    try:
        result = await health_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
