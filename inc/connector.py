from abc import ABC, abstractmethod
from typing import Dict, Any

class Connector(ABC):
    """Abstract base class for all connectors."""
    @abstractmethod
    def search(self, origin: str, destination: str, date: str, transportation_mode: str, payment_type: str) -> Dict[str, Any]:
        pass