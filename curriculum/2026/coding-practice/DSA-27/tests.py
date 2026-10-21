import random

from solution import LRUCache


class Key:
    """Hashable key that counts equality comparisons, exposing linear scans."""

    comparisons = 0

    def __init__(self, ident):
        self.ident = ident

    def __hash__(self):
        return hash(self.ident)

    def __eq__(self, other):
        Key.comparisons += 1
        return isinstance(other, Key) and self.ident == other.ident


class ModelLRU:
    """Obviously-correct O(n) reference model."""

    def __init__(self, capacity):
        self.capacity, self.items = capacity, []

    def get(self, key):
        for i, (k, v) in enumerate(self.items):
            if k == key:
                self.items.append(self.items.pop(i))
                return v
        return -1

    def put(self, key, value):
        self.items = [(k, v) for k, v in self.items if k != key] + [(key, value)]
        if len(self.items) > self.capacity:
            self.items.pop(0)


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.LRUCache)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_sequence():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)  # evicts 2
    assert cache.get(2) == -1
    cache.put(4, 4)  # evicts 1
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4


def test_capacity_zero_stores_nothing():
    cache = LRUCache(0)
    cache.put(1, 1)
    assert cache.get(1) == -1


def test_capacity_one():
    cache = LRUCache(1)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == -1 and cache.get("b") == 2
    cache.put("b", 3)
    assert cache.get("b") == 3


def test_overwrite_refreshes_recency():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 10)  # 1 becomes most recent, so 2 is the eviction victim
    cache.put(3, 3)
    assert cache.get(2) == -1
    assert cache.get(1) == 10 and cache.get(3) == 3


def test_overwrite_does_not_grow_size_or_evict():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    for value in range(5):
        cache.put(2, value)
    assert cache.get(1) == 1 and cache.get(2) == 4


def test_repeated_gets_move_entries():
    cache = LRUCache(3)
    for key in (1, 2, 3):
        cache.put(key, key)
    assert cache.get(1) == 1
    assert cache.get(2) == 2
    assert cache.get(1) == 1
    cache.put(4, 4)  # LRU is now 3
    assert cache.get(3) == -1
    cache.put(5, 5)  # LRU is now 2
    assert cache.get(2) == -1
    assert [cache.get(k) for k in (1, 4, 5)] == [1, 4, 5]


def test_missing_get_does_not_change_state():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(99) == -1
    cache.put(3, 3)
    assert cache.get(1) == -1 and cache.get(2) == 2


def test_falsy_values_are_stored():
    cache = LRUCache(2)
    cache.put("zero", 0)
    cache.put("none", None)
    assert cache.get("zero") == 0
    assert cache.get("none") is None


def test_deterministic_eviction_matches_model():
    rng = random.Random(27)
    for capacity in (1, 2, 3, 5):
        cache, model = LRUCache(capacity), ModelLRU(capacity)
        for step in range(400):
            key = rng.randint(0, 7)
            if rng.random() < 0.5:
                assert cache.get(key) == model.get(key), (capacity, step, key)
            else:
                cache.put(key, step)
                model.put(key, step)


def test_operations_do_not_scan_entries():
    n = 2000
    cache = LRUCache(n)
    Key.comparisons = 0
    for i in range(n):
        cache.put(Key(i), i)
    # Most-recent-first access defeats a front-of-list shortcut in list-based recency.
    for i in reversed(range(n)):
        assert cache.get(Key(i)) == i
    for i in range(n, 2 * n):
        cache.put(Key(i), i)
    assert cache.get(Key(n - 1)) == -1
    assert Key.comparisons <= 8 * n, f"{Key.comparisons} key comparisons for {3 * n} operations; expected O(1) each"


def test_core_does_not_use_ordered_dict():
    from collections import OrderedDict
    cache = LRUCache(3)
    for key in range(5):
        cache.put(key, key)
    assert not any(isinstance(v, OrderedDict) for v in vars(cache).values()), "build the recency list yourself"
