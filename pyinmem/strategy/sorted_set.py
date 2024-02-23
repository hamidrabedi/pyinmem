from .base import DataTypeStrategy


class SortedSetStrategy(DataTypeStrategy):
    @classmethod
    def is_valid_type(cls, value):
        return isinstance(value, dict)

    def check_sorted_set(self, store, key):
        if key in store and self.is_valid_type(store[key]):
            return True
        return False

    def zadd(self, store, key, scores):
        if key not in store or not isinstance(store[key], dict):
            store[key] = {}

        for member, score in scores.items():
            store[key][member] = score

    def zrange(self, store, key, start, stop):
        if self.check_sorted_set(store, key):
            sorted_members = sorted(store[key].items(), key=lambda item: item[1])
            return [member for member, score in sorted_members][start : stop + 1]

        return []

    def zscore(self, store, key, member):
        if self.check_sorted_set(store, key):
            return store[key].get(member)

        return None
