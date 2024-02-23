import json
import os
import time

from pyinmem.core import PyInMemStore
from pyinmem.strategy import SortedSetStrategy


def test_string_strategy():
    store = PyInMemStore()
    key = "test_key"
    value = "test_value"
    store.set(key, value)
    assert store.get(key) == value


def test_list_strategy():
    store = PyInMemStore()
    key = "test_list"
    value = "item1"
    store.lpush(key, value)
    assert store.llen(key) == 1
    assert store.get(key) == [value]
    assert store.rpop(key) == value
    assert store.get(key) == []


def test_string_operations():
    store = PyInMemStore()
    key = "string_key"
    value = "hello"

    store.set(key, value)
    assert store.get(key) == value

    store.delete(key)
    assert store.get(key) is None


def test_list_operations():
    store = PyInMemStore()
    key = "list_key"
    values = ["hello", "world"]

    for v in values:
        store.lpush(key, v)

    assert store.get(key) == list(reversed(values))
    assert store.rpop(key) == values[0]
    assert store.llen(key) == 1


def test_set_operations():
    store = PyInMemStore()
    key = "set_key"
    values = {"hello", "world"}

    for v in values:
        store.sadd(key, v)

    assert store.smembers(key) == values
    assert store.sis_member(key, "hello") is True
    store.srem(key, "hello")
    assert store.sis_member(key, "hello") is False


def test_sorted_set_strategy():
    store = {}
    sorted_set_strategy = SortedSetStrategy()

    # Test adding to sorted set
    sorted_set_strategy.zadd(store, "my_sorted_set", {"Alice": 100, "Bob": 90})
    assert store["my_sorted_set"]["Alice"] == 100
    assert store["my_sorted_set"]["Bob"] == 90

    # Test getting range from sorted set
    assert sorted_set_strategy.zrange(store, "my_sorted_set", 0, 1) == ["Bob", "Alice"]

    # Test getting score of a member
    assert sorted_set_strategy.zscore(store, "my_sorted_set", "Alice") == 100

    # Test getting range from a non-existent key
    assert sorted_set_strategy.zrange(store, "non_existent_key", 0, -1) == []

    # Test getting score of a member from a non-existent key
    assert sorted_set_strategy.zscore(store, "my_sorted_set", "Charlie") is None

    # Test adding to a key that's not a sorted set (should reset to empty dict)
    store["not_a_sorted_set"] = "some_string"
    sorted_set_strategy.zadd(store, "not_a_sorted_set", {"Charlie": 80})
    assert store["not_a_sorted_set"] == {"Charlie": 80}


def test_ttl_and_expire():
    store = PyInMemStore()
    key = "temp_key"
    value = "temp"
    ttl = 2  # seconds

    store.set(key, value, ttl)
    time.sleep(1)
    assert store.ttl(key) <= ttl
    time.sleep(1.5)
    assert store.get(key) is None


def test_delete_method():
    store = PyInMemStore()
    key = "delete_key"
    value = "to_delete"

    store.set(key, value)
    assert store.get(key) == value

    store.delete(key)
    assert store.get(key) is None


def test_save_and_load_data(tmp_path):
    # Temporary file for testing
    test_file = tmp_path / "test_data.json"

    # Initialize store and add some data
    store = PyInMemStore(save_data=True, save_interval=1, file_data_path=test_file)
    store.set("test_key", "test_value")
    store.set("test_key2", "test_value2", 1)  # Key with TTL

    # Save data
    store._save_data()

    # Check if file is created and data is written
    assert os.path.exists(test_file)
    with open(test_file, "r") as file:
        data = json.load(file)
        assert "test_key" in data["store"]
        assert data["store"]["test_key"] == "test_value"

    # Create a new instance and load data
    new_store = PyInMemStore(save_data=True, save_interval=1)
    new_store.save_data_file_path = str(test_file)
    new_store._load_data()

    # Check if data is correctly loaded
    assert new_store.get("test_key") == "test_value"
    assert new_store.get("test_key2") == "test_value2"

    # Optionally, clean up the test file if desired
    os.remove(test_file)
