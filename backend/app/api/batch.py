from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.models import BatchReceipt, BatchRequest
from app.services.batch_optimizer_service import BatchOptimizerService
from app.api.dependencies import get_batch_optimizer_service

router = APIRouter(tags=["batch"])


@router.post("/batch", response_model=BatchReceipt, summary="Optimize Quote Batching")
def optimize_batch(
    request: Optional[BatchRequest] = None,
    service: BatchOptimizerService = Depends(get_batch_optimizer_service)
) -> BatchReceipt:
    """
    Packs quote items into batches respecting unit capacity limits using a greedy algorithm.
    Returns a BatchReceipt detailing batches created, units consumed, and items exceeding capacity.
    """
    req = request or BatchRequest()

    try:
        receipt = service.optimize_batches(
            quote_ids=req.quote_ids,
            override_max_units=req.max_units_per_batch
        )
        return receipt
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during batch optimization processing."
        )
