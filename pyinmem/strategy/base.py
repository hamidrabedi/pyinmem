from abc import ABC, abstractmethod


class DataTypeStrategy(ABC):
    """
    An abstract base class representing a strategy for handling a specific data type.
    """

    @abstractmethod
    def is_valid_type(value): ...

    @classmethod
    def supports_operation(cls, operation):
        """Check if the strategy supports a given operation"""
        return hasattr(cls, operation)
