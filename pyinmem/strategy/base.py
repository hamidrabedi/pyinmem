from abc import ABC, abstractmethod
from typing import Any


class DataTypeStrategy(ABC):
    """
    An abstract base class representing a strategy for handling a specific data type.
    """

    @abstractmethod
    def is_valid_type(value: Any) -> bool:
        """An abstract method to determine if the data type is valid"""

    @classmethod
    def supports_operation(cls, operation: str) -> bool:
        """Check if the strategy supports a given operation"""
        return hasattr(cls, operation)
