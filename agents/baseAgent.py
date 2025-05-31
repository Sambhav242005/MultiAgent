from abc import ABC, abstractmethod
from typing import Any, Mapping
from memory import Memory

class BaseAgent(ABC):
    memory = Memory()          

    @abstractmethod
    def handle(self, data: Any, meta: Mapping[str, str]) -> Mapping[str, Any]:
        """Process data and return structured dict."""
