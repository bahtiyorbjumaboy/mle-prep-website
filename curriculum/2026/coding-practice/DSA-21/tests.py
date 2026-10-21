import random

from solution import count_components


def _brute(n, edges):
    label = list(range(n))
    changed = True
    while changed:
        changed = False
        for u, v in edges:
            low = min(label[u], label[v])
            if label[u] != low or label[v] != low:
                label[u] = label[v] = low
                changed = True
    return len(set(label))


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "count_components")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2


def test_no_nodes_and_no_edges():
    assert count_components(0, []) == 0
    assert count_components(1, []) == 1
    assert count_components(4, []) == 4


def test_isolated_nodes_are_counted():
    assert count_components(6, [[0, 1], [2, 3]]) == 4


def test_edges_are_undirected():
    # Traversing a one-directional adjacency list from node 0 misses node 1 here.
    assert count_components(2, [[1, 0]]) == 1
    assert count_components(4, [[3, 2], [2, 1], [1, 0]]) == 1


def test_cycles_duplicates_and_self_loops():
    assert count_components(3, [[0, 1], [1, 2], [2, 0]]) == 1
    assert count_components(3, [[0, 1], [0, 1], [1, 0]]) == 2
    assert count_components(3, [[0, 0], [1, 1]]) == 3


def test_components_merge_through_later_edges():
    # Union-find that links u directly to v (instead of root to root) breaks here.
    assert count_components(6, [[0, 1], [2, 3], [4, 5], [1, 3], [5, 3]]) == 1


def test_long_chain():
    n = 5000
    assert count_components(n, [[i, i + 1] for i in range(n - 1)]) == 1


def test_matches_label_propagation_on_random_graphs():
    rng = random.Random(21)
    for _ in range(300):
        n = rng.randint(1, 15)
        edges = [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(0, 15))]
        assert count_components(n, [e[:] for e in edges]) == _brute(n, edges), (n, edges)
