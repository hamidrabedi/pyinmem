from typing import Any

from .base import DataTypeStrategy


class StringStrategy(DataTypeStrategy):
    """Strategy for handling string data types in PyInMemStore."""

    @classmethod
    def is_valid_type(cls, value: Any) -> bool:
        """Check if the given value is a string."""
        return isinstance(value, str)
