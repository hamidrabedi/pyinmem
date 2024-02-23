from .base import DataTypeStrategy


class SortedSetStrategy(DataTypeStrategy):
    """Strategy for handling sorted set data types in PyInMemStore."""

    @classmethod
    def is_valid_type(cls, value):
        """Check if the given value is suitable for a sorted set."""
        return isinstance(value, dict)

    def check_sorted_set(self, store, key):
        """Check if the value at the given key is a valid sorted set."""
        if key in store and self.is_valid_type(store[key]):
            return True
        return False

    def zadd(self, store, key, scores):
        """Add members with scores to the sorted set at the given key."""
        if key not in store or not isinstance(store[key], dict):
            store[key] = {}

        for member, score in scores.items():
            store[key][member] = score

    def zrange(self, store, key, start, stop):
        """Return a range of members from the sorted set at the given key."""
        if self.check_sorted_set(store, key):
            sorted_members = sorted(store[key].items(), key=lambda item: item[1])
            return [member for member, score in sorted_members][start : stop + 1]

        return []

    def zscore(self, store, key, member):
        """
        Get the score associated with a member
        in the sorted set at the given key.
        """
        if self.check_sorted_set(store, key):
            return store[key].get(member)

        return None
