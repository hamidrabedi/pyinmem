from collections import deque
from typing import Any, Dict

from .base import DataTypeStrategy


class ListStrategy(DataTypeStrategy):
    """Strategy for handling list data types"""

    def is_valid_type(self, value: Any) -> bool:
        """Check if the given value is a list."""
        return isinstance(value, deque)

    def ensure_linked_list(self, store: Dict[str, Any], key: str) -> None:
        """Ensure the value for the given key is a list in the store."""
        if key not in store or not isinstance(store[key], deque):
            store[key] = deque()

    def lpush(self, store: Dict[str, Any], key: str, value: Any) -> int:
        """Push a value to the beginning of the list at the given key."""
        self.ensure_linked_list(store, key)
        linked_list: deque = store[key]
        linked_list.appendleft(value)
        return len(linked_list)

    def rpop(self, store: Dict[str, Any], key: str) -> Any:
        """Pop a value from the end of the list at the given key."""
        self.ensure_linked_list(store, key)
        linked_list: deque = store[key]
        if linked_list:
            return linked_list.pop()
        return None

    def llen(self, store: Dict[str, Any], key: str) -> int:
        """Return the length of the list at the given key."""
        self.ensure_linked_list(store, key)
        return len(store[key])
