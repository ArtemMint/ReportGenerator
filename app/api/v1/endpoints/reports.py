from fastapi import APIRouter

from app.schemas import BatchRequest, BatchResponse
from app.services import run_batch

router = APIRouter()


@router.post("/batch", response_model=BatchResponse, status_code=202)
async def generate_batch(batch: BatchRequest) -> BatchResponse:
    """
    Launch one or more reports in parallel.

    :param
        batch: A BatchRequest object containing a list of reports to generate.
    :return
        A BatchResponse object containing the batch ID and a list of
        ReportResponse objects with the status of each report.
    """
    return await run_batch(batch)
