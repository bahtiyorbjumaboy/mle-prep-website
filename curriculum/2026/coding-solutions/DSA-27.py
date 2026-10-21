from typing import Any, Hashable


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Hashable = None, value: Any = None) -> None:
        self.key = key
        self.value = value
        self.prev: "_Node" = self
        self.next: "_Node" = self


class LRUCache:
    """LRU cache backed by a hash map and a circular doubly linked list."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.nodes: dict[Hashable, _Node] = {}
        # Sentinel: sentinel.next is least recent, sentinel.prev is most recent.
        self.sentinel = _Node()

    def _unlink(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append(self, node: _Node) -> None:
        last = self.sentinel.prev
        last.next = node
        node.prev = last
        node.next = self.sentinel
        self.sentinel.prev = node

    def get(self, key: Hashable) -> Any:
        node = self.nodes.get(key)
        if node is None:
            return -1
        self._unlink(node)
        self._append(node)
        return node.value

    def put(self, key: Hashable, value: Any) -> None:
        if self.capacity == 0:
            return
        node = self.nodes.get(key)
        if node is not None:
            # Overwrite: update value and recency; size is unchanged.
            node.value = value
            self._unlink(node)
            self._append(node)
            return
        if len(self.nodes) == self.capacity:
            oldest = self.sentinel.next
            self._unlink(oldest)
            del self.nodes[oldest.key]
        node = _Node(key, value)
        self.nodes[key] = node
        self._append(node)
