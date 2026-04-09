from pydantic import BaseModel, field_validator


class EmployeeRecord(BaseModel):
    Name: str
    Age: int
    Job: str
    Salary: float

    @field_validator("Name", "Job")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("Salary", "Age")
    @classmethod
    def salary_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Field must be non-negative")
        return v
