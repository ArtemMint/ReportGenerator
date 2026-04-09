from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AbstractSource(ABC):
    def __init__(self, source: str):
        """Initialize the sources with a string that can be a file path or raw content."""
        self.source = source

    @abstractmethod
    async def read(self) -> List[Dict[str, Any]]:
        """Read from the sources and return the data"""
        pass