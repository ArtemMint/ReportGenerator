from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Types of data sources for reports."""
    csv = "csv"
    # json = "json"
    # db = "db"
    # api = "api"


class OutputType(str, Enum):
    """Types of outputs formats for reports."""
    json = "json"
    # csv = "csv"
    # api = "api"


class ReportStatus(str, Enum):
    """Status of a report generation process."""
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class FilterType(str, Enum):
    """Types of filters that can be applied to a report."""
    high_salary_employees = "high_salary_employees"
    low_salary_employees = "low_salary_employees"


class FilterConfig(BaseModel):
    """Configuration for a report filters."""
    type: FilterType
    salary_threshold: float | None = 3500


class SourceConfig(BaseModel):
    """Configuration for report data sources."""
    type: SourceType

    # For csv/json: file path or raw content
    path: str | None = "/code/input_data.csv"
    # raw_content: str | None = "user_id,name,salary\n1,John Doe,5000\n2,Jane Smith,3000\n3,Bob Johnson,4000"

    # For db: connection string + query
    # db_connection_string: str | None = "postgresql://user:password@localhost:5432/mydatabase"
    # db_query: str | None = "SELECT user_id, name, salary FROM users"

    # For api: url
    # url: str | None = "http://api.example.com/data"


class OutputConfig(BaseModel):
    """Configuration for report outputs."""
    type: OutputType
    # For csv/json file outputs
    path: str | None = "/code"


class ReportRequest(BaseModel):
    """Request model for generating a report."""
    source: SourceConfig
    filter: FilterConfig
    output: OutputConfig


class BatchRequest(BaseModel):
    """Request model for a batch of reports."""
    reports: list[ReportRequest] = Field(..., min_length=1)


class ReportResult(BaseModel):
    """Result model for an individual report in a batch process."""
    report_id: str
    status: ReportStatus
    data: Any | None = None
    error: str | None = None


class BatchResponse(BaseModel):
    """Response model for a batch of reports."""
    batch_id: str
    results: list[ReportResult]
