from app.schemas.report import SourceType, FilterType, OutputType
from app.sources import CSVSource
from app.outputs import JSONOutput
from app.filters import HighSalaryEmployeeFilter, LowSalaryEmployeeFilter

SOURCE_REGISTRY = {
    SourceType.csv: CSVSource,
    # SourceType.json: JSONSource,
    # SourceType.db: DBSource,
    # SourceType.api: ApiSource,
}

FILTER_REGISTRY = {
    FilterType.high_salary_employees: HighSalaryEmployeeFilter,
    FilterType.low_salary_employees: LowSalaryEmployeeFilter,
}

OUTPUT_REGISTRY = {
    OutputType.json: JSONOutput,
    # OutputType.csv: CsvOutput,
    # OutputType.api: ApiOutput,
}