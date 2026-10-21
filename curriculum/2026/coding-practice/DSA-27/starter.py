from typing import Any, Hashable


class LRUCache:
    """Fixed-capacity least-recently-used cache with O(1) average `get` and `put`.

    Implement the recency order yourself (do not use `collections.OrderedDict` or rely on
    `dict` insertion order for the core version).

    Semantics:
        * `get` of a present key returns its value and marks it most recently used.
        * `get` of a missing key returns -1 and changes nothing.
        * `put` of a new key inserts it as most recently used; if the cache then exceeds
          `capacity`, the least recently used key is evicted.
        * `put` of an existing key overwrites its value, marks it most recently used, and
          never evicts or changes the number of stored keys.
        * With `capacity == 0`, `put` stores nothing.
    """

    def __init__(self, capacity: int) -> None:
        """Create an empty cache holding at most `capacity` keys (`capacity >= 0`)."""
        raise NotImplementedError("TODO: implement DSA-27")

    def get(self, key: Hashable) -> Any:
        """Return the value for `key` (refreshing its recency), or -1 if absent."""
        raise NotImplementedError("TODO: implement DSA-27")

    def put(self, key: Hashable, value: Any) -> None:
        """Insert or overwrite `key`, evicting the least recently used key if needed."""
        raise NotImplementedError("TODO: implement DSA-27")
