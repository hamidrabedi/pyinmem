from .base import DataTypeStrategy


class SetStrategy(DataTypeStrategy):
    """Strategy for handling set data types in PyInMemStore."""

    @classmethod
    def is_valid_type(cls, value):
        """Check if the given value is a set."""
        return isinstance(value, set)

    def ensure_set(self, store, key):
        """Ensure the value for the given key is a set in the store."""
        if key not in store or not isinstance(store[key], set):
            store[key] = set()

    def sadd(self, store, key, *values):
        """Add values to the set stored at the given key."""
        self.ensure_set(store, key)
        count = 0
        for value in values:
            if value not in store[key]:
                store[key].add(value)
                count += 1
        return count

    def srem(self, store, key, *values):
        """Remove values from the set stored at the given key."""
        self.ensure_set(store, key)
        count = 0
        for value in values:
            if value in store[key]:
                store[key].remove(value)
                count += 1
        return count

    def smembers(self, store, key):
        """Return all members of the set stored at the given key."""
        return store.get(key, set())

    def sis_member(self, store, key, value):
        """Check if a value is a member of the set at the given key."""
        return value in store.get(key, set())
