from ..exceptions import DataTypeError
from .base import DataTypeStrategy


class ListStrategy(DataTypeStrategy):
    @classmethod
    def is_valid_type(cls, value):
        return isinstance(value, list)

    def ensure_list(self, store, key):
        if key not in store or not isinstance(store[key], list):
            store[key] = []

    def lpush(self, store, key, value):
        try:
            self.ensure_list(store, key)
            store[key].insert(0, value)
            return len(store[key])
        except TypeError as exc:
            raise DataTypeError(f"Value for key '{key}' is not a list.") from exc

    def rpop(self, store, key):
        self.ensure_list(store, key)
        if store[key]:
            return store[key].pop()
        return None

    def llen(self, store, key):
        self.ensure_list(store, key)
        return len(store[key])
