"""
Evaluate endpoint: ESG evaluation with structured report.
"""
import logging
from fastapi import APIRouter, HTTPException

from app.api.schemas import EvaluateRequest, EvaluateResponse
from app.services.evaluate_service import evaluate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_esg(request: EvaluateRequest):
    """Generate an ESG evaluation report."""
    try:
        result = await evaluate(
            company=request.company,
            criterion=request.criterion,
            query=request.query,
            top_k=request.top_k,
            format=request.format
        )
        return result
    except Exception as e:
        logger.error(f"Evaluate error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
