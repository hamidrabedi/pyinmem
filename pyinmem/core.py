import random
import threading
import time
from collections import defaultdict

from .exceptions import OperationNotSupportedError, PyInMemStoreError
from .strategy import ListStrategy, SetStrategy, SortedSetStrategy, StringStrategy


class PyInMemStore:
    """
    An in-memory data store that supports various data types and operations
    """

    def __init__(self):
        self.store = {}
        self.ttl_keys = {}
        self.locks = defaultdict(threading.Lock)
        self.active_expire_thread = threading.Thread(
            target=self.active_expire_cycle, daemon=True
        )
        self.active_expire_thread.start()
        self.strategies = [
            StringStrategy(),
            ListStrategy(),
            SetStrategy(),
            SortedSetStrategy(),
        ]

    def __getattr__(self, name):
        """
        Dynamically handles method calls for different data types.
        """
        if not any(hasattr(strategy, name) for strategy in self.strategies):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        def method(key, *args, **kwargs):
            try:
                current_value = self.store.get(key, None)

                for strategy in self.strategies:
                    if strategy.is_valid_type(current_value) or current_value is None:
                        if hasattr(strategy, name):
                            func = getattr(strategy, name)
                            return self._with_key_lock(
                                key, func, self.store, key, *args, **kwargs
                            )

                raise OperationNotSupportedError(
                    f"Operation '{name}' is not supported for"
                    f"the data type of key '{key}'"
                )
            except Exception as exc:
                raise PyInMemStoreError(f"An error occurred: {exc!r}") from exc

        return method

    def _get_lock(self, key):
        return self.locks[key]

    def _with_key_lock(self, key, func, *args, **kwargs):
        """Acquire the lock for a key and execute the function."""
        lock = self._get_lock(key)
        with lock:
            return func(*args, **kwargs)

    def with_key_lock(method):
        def wrapper(self, key, *args, **kwargs):
            lock = self._get_lock(key)
            with lock:
                return method(self, key, *args, **kwargs)

        return wrapper

    @with_key_lock
    def set(self, key, value, ttl=None):
        """Set a value for the key. Optionally, set a TTL (in seconds)."""
        if ttl:
            ttl = int(ttl)

        self.store[key] = value
        if ttl is not None:
            self.ttl_keys[key] = time.time() + ttl
        else:
            self.ttl_keys.pop(key, None)

    @with_key_lock
    def get(self, key):
        if self._check_expiry(key):
            self._delete_key_without_lock(key)
            return None
        return self.store.get(key, None)

    @with_key_lock
    def delete(self, key):
        if key in self.store:
            del self.store[key]
        if key in self.ttl_keys:
            del self.ttl_keys[key]
        if key in self.locks:
            del self.locks[key]

    def _delete_key_without_lock(self, key):
        if key in self.store:
            del self.store[key]
        if key in self.ttl_keys:
            del self.ttl_keys[key]

    @with_key_lock
    def expire(self, key, seconds):
        self._expire(key, seconds)

    def _expire(self, key, seconds):
        if key in self.store:
            self.ttl_keys[key] = time.time() + seconds

    @with_key_lock
    def ttl(self, key):
        return self._ttl(key)

    def _ttl(self, key):
        if key not in self.store:
            return -2
        if key not in self.ttl_keys:
            return -1
        remaining = self.ttl_keys[key] - time.time()
        if remaining <= 0:
            self.delete(key)
            return -2
        return int(remaining)

    def _check_expiry(self, key):
        ttl = self.ttl_keys.get(key)
        if ttl and time.time() > ttl:
            return True
        return False

    def active_expire_cycle(self):
        while True:
            time.sleep(1)
            keys_to_sample = []
            if len(self.ttl_keys) > 0:
                keys_to_sample = random.sample(
                    list(self.ttl_keys.keys()), min(20, len(self.ttl_keys))
                )

            expired = 0
            for key in keys_to_sample:
                lock = self._get_lock(key)
                with lock:
                    if key in self.ttl_keys and time.time() > self.ttl_keys[key]:
                        self._delete_key_without_lock(key)
                        expired += 1

                if expired > len(keys_to_sample) * 0.25:
                    break
