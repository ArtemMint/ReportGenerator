import asyncio
import uuid

import pandas as pd
from pydantic import ValidationError

from app.core import get_logger
from app.schemas import BatchRequest, BatchResponse, ReportStatus
from app.schemas import ReportRequest, ReportResult
from app.schemas.employee import EmployeeRecord
from app.services.registry import SOURCE_REGISTRY, FILTER_REGISTRY, OUTPUT_REGISTRY

logger = get_logger(__name__)


def _validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate each row via Pydantic EmployeeRecord.
    Invalid rows are logged and dropped — valid rows are returned as a clean DataFrame.
    """
    valid_rows = []
    errors = []

    for i, row in df.iterrows():
        try:
            record = EmployeeRecord(**row.to_dict())
            valid_rows.append(record.model_dump())
        except ValidationError as exc:
            errors.append(i)
            for error in exc.errors():
                logger.warning(
                    "validation.row_invalid",
                    row=i,
                    field=error["loc"][0],
                    error=error["msg"],
                )

    if errors:
        logger.warning("validation.summary", invalid_rows=len(errors), dropped=errors)

    if not valid_rows:
        raise ValueError("No valid rows after validation")

    return pd.DataFrame(valid_rows)


async def run_report(request: ReportRequest, report_id: str) -> ReportResult:
    """
    Placeholder function for running an individual report.

    This function should implement the logic to execute a single report based on the
    provided ReportRequest, handle its status, and return a ReportResult object.

    return
        A ReportResult object containing the report ID, status, data, and any error message.
    """
    try:
        logger.info("report.start", report_id=report_id)
        # 1. Resolve classes from registry
        SourceClass = SOURCE_REGISTRY.get(request.source.type)
        FilterClass = FILTER_REGISTRY.get(request.filter.type)
        OutputClass = OUTPUT_REGISTRY.get(request.output.type)

        if not SourceClass:
            raise ValueError(f"Unsupported source type: {request.source.type}")
        if not FilterClass:
            raise ValueError(f"Unsupported filter: {request.filter}")
        if not OutputClass:
            raise ValueError(f"Unsupported output type: {request.output.type}")

        # 2. Fetch data
        source = SourceClass(request.source.path)
        raw_data = await source.read()
        validated_raw_data = _validate_dataframe(raw_data)

        logger.info("report.fetched", report_id=report_id, record_count=len(validated_raw_data))

        # 3. Apply filters
        report_filter = FilterClass(salary_threshold=request.filter.salary_threshold)
        # filtered = report_filter.apply(validated_raw_data)   # 1.16s, blocks event loop - 90 reports
        filtered = await asyncio.to_thread(report_filter.apply, validated_raw_data)  # 1.03s, non-blocking - 90 reports
        logger.info("report.filtered", report_id=report_id, filtered_count=len(filtered))

        # 4. Write outputs
        output = OutputClass(request.output, report_id)
        report_path = await output.write(filtered)

        logger.info("report.done", report_id=report_id)
        return ReportResult(report_id=report_id, status=ReportStatus.done,
                            data={"message": f"Report generated with {len(filtered)} records at {report_path}"})
    except Exception as exc:
        logger.exception("report.failed", error=str(exc))
        return ReportResult(
            report_id=report_id,
            status=ReportStatus.failed,
            error=str(exc),
        )


async def run_batch(batch: BatchRequest) -> BatchResponse:
    """
    Placeholder function for running a batch of reports.

    This function should implement the logic to execute multiple reports in parallel,
    handle their statuses, and return a BatchResponse object with the results.

    return
        A BatchResponse object containing the batch ID and a list of ReportResponse objects.
    """
    batch_id = str(uuid.uuid4())
    logger.info("batch.start", batch_id=batch_id, report_count=len(batch.reports))

    # Generate a unique ID per report upfront
    report_ids = [str(uuid.uuid4()) for _ in batch.reports]

    # Create a list of tasks and run all reports concurrently
    tasks = [
        run_report(request, report_id)
        for request, report_id in zip(batch.reports, report_ids)
    ]
    results: list[ReportResult] = list(await asyncio.gather(*tasks, return_exceptions=False))

    logger.info(
        "batch.done",
        batch_id=batch_id,
        done=sum(1 for r in results if r.status == ReportStatus.done),
        failed=sum(1 for r in results if r.status == ReportStatus.failed),
    )

    return BatchResponse(batch_id=batch_id, results=results)
