import pandas as pd

from .abstract import Filter


class LowSalaryEmployeeFilter(Filter):
    """Filter employees with salary below a specified threshold."""
    def __init__(self, salary_threshold):
        """Initialize the filter with a salary threshold."""
        self.salary_threshold = salary_threshold

    def apply(self, employees: pd.DataFrame) -> pd.DataFrame:
        """Filter employees with salary below the specified threshold."""
        filtered_data = employees[employees['Salary'] < self.salary_threshold]
        return filtered_data[['Name', 'Job']]
