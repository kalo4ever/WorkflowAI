from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any, Generic, Hashable, OrderedDict, TypeVar

_K = TypeVar("_K", bound=Hashable)
_T = TypeVar("_T")


class LRUCache(Generic[_K, _T]):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict[Any, _T]()

    def __getitem__(self, key: _K) -> _T:
        if key not in self.cache:
            raise KeyError(f"Key {key} not found in cache")

        # Move the key to the end to indicate that it was recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def __setitem__(self, key: _K, value: _T) -> None:
        if key in self.cache:
            # Update the value and move the key to the end
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove the first (least recently used) item
            self.cache.popitem(last=False)

    def __delitem__(self, key: _K) -> None:
        del self.cache[key]

    def peek(self, key: _K) -> _T | None:
        try:
            return self.cache[key]
        except KeyError:
            return None


# We should probably inherit from MutableMapping instead
class TLRUCache(Generic[_K, _T]):
    def __init__(self, capacity: int, ttl: Callable[[_K, _T], timedelta]):
        self._cache = LRUCache[_K, tuple[datetime, _T]](capacity)
        self._ttl = ttl

    def __getitem__(self, key: _K) -> _T:
        val = self._cache[key]
        if val[0] < datetime.now():
            del self._cache[key]
            raise KeyError(f"Key {key} was expired in cache")
        return val[1]

    def __setitem__(self, key: _K, value: _T) -> None:
        self._cache[key] = (datetime.now() + self._ttl(key, value), value)

    def get(self, key: _K, default: _T | None = None) -> _T | None:
        try:
            return self[key]
        except KeyError:
            return default
