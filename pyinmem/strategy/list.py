from ..exceptions import DataTypeError
from .base import DataTypeStrategy


class ListStrategy(DataTypeStrategy):
    """Strategy for handling list data types"""

    @classmethod
    def is_valid_type(cls, value):
        """Check if the given value is a list."""
        return isinstance(value, list)

    def ensure_list(self, store, key):
        """Ensure the value for the given key is a list in the store."""
        if key not in store or not isinstance(store[key], list):
            store[key] = []

    def lpush(self, store, key, value):
        """Push a value to the beginning of the list at the given key."""
        try:
            self.ensure_list(store, key)
            store[key].insert(0, value)
            return len(store[key])
        except TypeError as exc:
            raise DataTypeError(f"Value for key '{key}' is not a list.") from exc

    def rpop(self, store, key):
        """Pop a value from the end of the list at the given key."""
        self.ensure_list(store, key)
        if store[key]:
            return store[key].pop()
        return None

    def llen(self, store, key):
        """Return the length of the list at the given key."""
        self.ensure_list(store, key)
        return len(store[key])
