import json
import logging
import random
import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, Optional

from .exceptions import OperationNotSupportedError, PyInMemStoreError
from .strategy import ListStrategy, SetStrategy, SortedSetStrategy, StringStrategy


class PyInMemStore:
    """
    An in-memory data store that supports various data types and operations
    """

    save_data_file_path: str = "./data.json"

    def __init__(
        self,
        save_data: bool = False,
        save_interval: int = 5,
        file_data_path: Optional[str] = None,
    ):
        self.store: Dict[str, Any] = {}
        self.ttl_keys: Dict[str, float] = {}
        self.locks = defaultdict(threading.Lock)
        self.active_expire_thread = threading.Thread(
            target=self.active_expire_cycle, daemon=True
        )
        self.active_expire_thread.start()
        self.strategies: list = [
            StringStrategy(),
            ListStrategy(),
            SetStrategy(),
            SortedSetStrategy(),
        ]
        if file_data_path:
            self.save_data_file_path = file_data_path
        self.save_data: bool = save_data
        self.save_interval: int = save_interval
        self.last_save_time: float = time.time()
        if self.save_data:
            self._load_data()

    def __getattr__(self, name: str):
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

    def _get_lock(self, key: str) -> threading.Lock:
        """Retrieve a lock for a given key to ensure thread-safe operations."""
        return self.locks[key]

    def _with_key_lock(self, key, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Acquire the lock for a key and execute the function."""
        lock = self._get_lock(key)
        with lock:
            return func(*args, **kwargs)

    def with_key_lock(method: Callable):
        """Decorator to wrap class methods with a key-based lock."""

        def wrapper(self, key, *args: Any, **kwargs: Any) -> Any:
            lock = self._get_lock(key)
            with lock:
                return method(self, key, *args, **kwargs)

        return wrapper

    @with_key_lock
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value for a given key with an optional TTL (time-to-live)."""
        if ttl:
            ttl = int(ttl)

        self.store[key] = value
        if ttl is not None:
            self.ttl_keys[key] = time.time() + ttl
        else:
            self.ttl_keys.pop(key, None)

    @with_key_lock
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value by key, returning None
        if key is expired or doesn't exist.
        """
        if self._check_expiry(key):
            self._delete_key_without_lock(key)
            return None
        return self.store.get(key, None)

    @with_key_lock
    def delete(self, key: str) -> None:
        """Delete a key and its associated value from the store."""
        if key in self.store:
            del self.store[key]
        if key in self.ttl_keys:
            del self.ttl_keys[key]
        if key in self.locks:
            del self.locks[key]

    def _delete_key_without_lock(self, key: str) -> None:
        """
        Helper method to delete a key
        without acquiring a lock. Used in internal processes.
        """
        if key in self.store:
            del self.store[key]
        if key in self.ttl_keys:
            del self.ttl_keys[key]

    @with_key_lock
    def expire(self, key: str, seconds: int) -> None:
        """Set an expiration time (TTL) for a given key."""
        self._expire(key, seconds)

    def _expire(self, key: str, seconds: int) -> None:
        """Internal method to handle setting TTL for a key."""
        if key in self.store:
            self.ttl_keys[key] = time.time() + seconds

    @with_key_lock
    def ttl(self, key: str) -> int:
        """
        Get the remaining TTL for a key, returning -2 if key doesn't exist
        or -1 if no TTL.
        """
        return self._ttl(key)

    def _ttl(self, key: str) -> int:
        """Internal method to compute TTL for a key."""
        if key not in self.store:
            return -2
        if key not in self.ttl_keys:
            return -1
        remaining = self.ttl_keys[key] - time.time()
        if remaining <= 0:
            self.delete(key)
            return -2
        return int(remaining)

    def _check_expiry(self, key: str) -> bool:
        """Check if a key is expired based on its TTL."""
        ttl = self.ttl_keys.get(key)
        if ttl and time.time() > ttl:
            return True
        return False

    def active_expire_cycle(self) -> None:
        """Background thread process to actively check and expire keys based on TTL."""
        while True:
            time.sleep(1)
            current_time = time.time()
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

            if self.save_data and (
                current_time - self.last_save_time >= self.save_interval
            ):
                self._save_data()
                self.last_save_time = current_time

    def _save_data(self) -> None:
        """Save data to the specified file."""
        with open(self.save_data_file_path, "w") as file:
            data = {"store": self.store, "ttl_keys": self.ttl_keys}
            json.dump(data, file)

    def _load_data(self) -> None:
        """
        Load data from the specified file, or create a new file if it doesn't exist.
        """
        try:
            with open(self.save_data_file_path, "r", encoding="utf8") as file:
                data = json.load(file)
                self.store = data.get("store", {})
                self.ttl_keys = data.get("ttl_keys", {})
        except FileNotFoundError:
            logging.info(
                "No data file found at %s. Creating a new file.",
                self.save_data_file_path,
            )
            self._create_empty_data_file()
        except json.JSONDecodeError:
            logging.error(
                "Invalid JSON format in %s. Creating a new file.",
                self.save_data_file_path,
            )
            self._create_empty_data_file()
        except Exception as exc:
            logging.error("An error occurred while loading data: %s", str(exc))

    def _create_empty_data_file(self) -> None:
        """Create an empty JSON file for the store's initial state."""
        with open(self.save_data_file_path, "w", encoding="utf8") as file:
            json.dump({"store": {}, "ttl_keys": {}}, file)
