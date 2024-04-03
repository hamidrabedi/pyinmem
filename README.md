# PyInMemStore

PyInMemStore is a lightweight, in-memory data store written in Python. It provides a simple way to store and manipulate data structures such as strings, lists, sets, and sorted sets. The store offers thread-safe operations and supports key expiry, similar to Redis.

## Features

- Basic data types: Strings, Lists, Sets, and Sorted Sets.
- Thread-safe operations.
- Key expiry functionality.
- Dynamic method dispatching based on data type.
- Easy extensibility for additional data types and operations.

## How to install
```
pip install pyinmem
```

## Data Types and Operations

### String

- `set(key, value, ttl=None)`: Set a string value under a key. Optionally, specify a Time-To-Live (TTL) in seconds.
- `get(key)`: Retrieve the string value for a given key.

### List

- `lpush(key, value)`: Push a value to the beginning of a list at a given key.
- `rpop(key)`: Pop a value from the end of a list at a given key.
- `llen(key)`: Get the length of the list at a given key.

### Set

- `sadd(key, *values)`: Add one or more values to a set at a given key.
- `srem(key, *values)`: Remove one or more values from a set at a given key.
- `smembers(key)`: Get all the members of the set at a given key.
- `sis_member(key, value)`: Check if a value is a member of the set at a given key.

### Sorted Set

- `zadd(key, scores)`: Add one or more member-score pairs to a sorted set at a given key.
- `zrange(key, start, stop)`: Get a range of members from a sorted set at a given key, sorted by score.
- `zscore(key, member)`: Get the score of a member in a sorted set at a given key.

## Usage

```python
from pyinmemstore import PyInMemStore

store = PyInMemStore(save_data=True)


store.set('hello', 'world')
print(store.get('hello'))


store.lpush('mylist', 'hello')
store.lpush('mylist', 'world')
print(store.rpop('mylist'))


store.sadd('myset', 'hello', 'world')
print(store.smembers('myset'))


store.zadd('my_sorted_set', {'Alice': 100, 'Bob': 90})
print(store.zrange('my_sorted_set', 0, -1))
print(store.zscore('my_sorted_set', 'Alice'))
