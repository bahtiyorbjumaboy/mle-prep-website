import random

from solution import UnionFind


def _depth(parent, x):
    depth = 0
    while parent[x] != x:
        x = parent[x]
        depth += 1
    return depth


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.UnionFind)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    dsu = UnionFind(5)
    dsu.union(0, 1)
    dsu.union(1, 2)
    dsu.union(3, 4)
    assert dsu.connected(0, 2) and not dsu.connected(0, 4)
    assert dsu.count == 2


def test_initial_state_and_singletons():
    assert UnionFind(0).count == 0
    dsu = UnionFind(3)
    assert dsu.count == 3
    assert [dsu.find(i) for i in range(3)] == [0, 1, 2]
    assert dsu.connected(1, 1)


def test_union_reports_whether_it_merged():
    dsu = UnionFind(4)
    assert dsu.union(0, 1) is True
    assert dsu.union(1, 0) is False
    assert dsu.union(2, 2) is False
    assert dsu.count == 3


def test_redundant_unions_do_not_change_count():
    dsu = UnionFind(4)
    for a, b in [(0, 1), (1, 2), (2, 0), (0, 2), (3, 3)]:
        dsu.union(a, b)
    assert dsu.count == 2


def test_merging_two_multi_node_sets_links_roots():
    # Linking a non-root node instead of its root leaves members behind.
    dsu = UnionFind(6)
    dsu.union(0, 1)
    dsu.union(2, 3)
    dsu.union(1, 3)
    assert all(dsu.connected(0, x) for x in (1, 2, 3))
    dsu.union(4, 5)
    dsu.union(5, 0)
    assert all(dsu.connected(4, x) for x in range(6)) and dsu.count == 1


def test_incremental_connectivity_queries_match_brute_force():
    rng = random.Random(29)
    n = 30
    dsu = UnionFind(n)
    labels = list(range(n))
    for _ in range(300):
        a, b = rng.randrange(n), rng.randrange(n)
        if rng.random() < 0.4:
            merged = labels[a] != labels[b]
            assert dsu.union(a, b) is merged
            old, new = labels[a], labels[b]
            labels = [new if x == old else x for x in labels]
        else:
            assert dsu.connected(a, b) == (labels[a] == labels[b]), (a, b)
        assert dsu.count == len(set(labels))


def test_union_by_rank_or_size_keeps_trees_shallow():
    # Always hanging the first root under the second builds an O(n) chain here.
    n = 1024
    dsu = UnionFind(n)
    for i in range(1, n):
        dsu.union(i, 0)
    assert max(_depth(dsu.parent, x) for x in range(n)) <= 1
    dsu = UnionFind(n)
    for i in range(n - 1):
        dsu.union(i, i + 1)
    assert max(_depth(dsu.parent, x) for x in range(n)) <= 10


def test_find_compresses_the_path():
    n = 64
    dsu = UnionFind(n)
    for size in (1, 2, 4, 8, 16, 32):
        for start in range(0, n, 2 * size):
            dsu.union(start, start + size)
    deepest = max(range(n), key=lambda x: _depth(dsu.parent, x))
    path = [deepest]
    while dsu.parent[path[-1]] != path[-1]:
        path.append(dsu.parent[path[-1]])
    root = dsu.find(deepest)
    assert root == path[-1]
    assert all(dsu.parent[x] == root for x in path), "every node on the find path must point at the root"
