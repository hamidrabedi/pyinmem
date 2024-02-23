from .base import DataTypeStrategy


class SetStrategy(DataTypeStrategy):
    @classmethod
    def is_valid_type(cls, value):
        return isinstance(value, set)

    def ensure_set(self, store, key):
        if key not in store or not isinstance(store[key], set):
            store[key] = set()

    def sadd(self, store, key, *values):
        self.ensure_set(store, key)
        count = 0
        for value in values:
            if value not in store[key]:
                store[key].add(value)
                count += 1
        return count

    def srem(self, store, key, *values):
        self.ensure_set(store, key)
        count = 0
        for value in values:
            if value in store[key]:
                store[key].remove(value)
                count += 1
        return count

    def smembers(self, store, key):
        return store.get(key, set())

    def sis_member(self, store, key, value):
        return value in store.get(key, set())
