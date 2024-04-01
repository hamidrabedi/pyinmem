from typing import Any, Dict

from .base import DataTypeStrategy


class ListStrategy(DataTypeStrategy):
    """Strategy for handling list data types"""

    def is_valid_type(self, value: Any) -> bool:
        """Check if the given value is a list."""
        return isinstance(value, list)

    def ensure_list(self, store: Dict[str, Any], key: str) -> None:
        """Ensure the value for the given key is a list in the store."""
        if key not in store or not isinstance(store[key], list):
            store[key] = []

    def lpush(self, store: Dict[str, Any], key: str, value: Any) -> int:
        """Push a value to the beginning of the list at the given key."""
        self.ensure_list(store, key)
        store[key].insert(0, value)
        return len(store[key])

    def rpop(self, store: Dict[str, Any], key: str) -> Any:
        """Pop a value from the end of the list at the given key."""
        self.ensure_list(store, key)
        if store[key]:
            return store[key].pop()

    def llen(self, store: Dict[str, Any], key: str) -> int:
        """Return the length of the list at the given key."""
        self.ensure_list(store, key)
        return len(store[key])
