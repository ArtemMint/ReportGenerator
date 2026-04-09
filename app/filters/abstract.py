from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Filter(ABC):
    @abstractmethod
    def apply(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process the data"""
        pass