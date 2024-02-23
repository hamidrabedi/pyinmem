from .base import DataTypeStrategy


class StringStrategy(DataTypeStrategy):
    @classmethod
    def is_valid_type(cls, value):
        return isinstance(value, str)
