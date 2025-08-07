from abc import ABC, abstractmethod
from typing import Dict, Any


class Connector(ABC):
    """Abstract base class for all connectors."""

    @abstractmethod
    def get_details(self, origin: str, destination: str, date: str, transportation_mode: str, payment_type: str) -> \
    Dict[str, Any]:
        pass

    def get_price(self, origin: str, destination: str, date: str) -> float:
        """Optional method to get the price of a flight."""
        pass
