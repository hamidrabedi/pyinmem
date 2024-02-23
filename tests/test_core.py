import time

from pyinmem.core import PyInMemStore


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


def test_sorted_set_operations():
    store = PyInMemStore()
    key = "sorted_set_key"
    scores = {"member1": 1, "member2": 2, "member3": 3}

    store.zadd(key, scores)
    assert store.zscore(key, "member1") == 1
    assert store.zrange(key, 0, 1) == ["member1", "member2"]


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
