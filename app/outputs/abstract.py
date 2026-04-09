from abc import ABC, abstractmethod
from typing import Any


class AbstractOutput(ABC):
    @abstractmethod
    async def write(self, data: list[dict]) -> Any:
        """
        Persist or return the report data.
        Return value is output-type specific:
          - JSONOutput  → dict (ready to embed in API response)
          - CsvOutput   → str (CSV text)
          - ApiOutput   → bytes (for StreamingResponse)
        """
        pass
