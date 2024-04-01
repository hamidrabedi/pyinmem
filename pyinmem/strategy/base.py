from abc import ABC, abstractmethod


class DataTypeStrategy(ABC):
    """
    An abstract base class representing a strategy for handling a specific data type.
    """

    @abstractmethod
    def is_valid_type(self, value: object) -> bool:
        """Determine if the data type is valid"""

    @classmethod
    def supports_operation(cls, operation: str) -> bool:
        """Check if the strategy supports a given operation"""
        return hasattr(cls, operation)
