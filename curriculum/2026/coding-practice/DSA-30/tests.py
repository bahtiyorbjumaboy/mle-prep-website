import random

from solution import dijkstra


def _bellman_ford(graph, source):
    dist = {source: 0}
    for _ in range(len(graph) + 1):
        for u, edges in graph.items():
            if u in dist:
                for v, w in edges:
                    if dist[u] + w < dist.get(v, float("inf")):
                        dist[v] = dist[u] + w
    return dist


def _assert_valid_path(graph, source, target, dist, path):
    assert path[0] == source and path[-1] == target, path
    total = 0
    for u, v in zip(path, path[1:]):
        weights = [w for x, w in graph.get(u, []) if x == v]
        assert weights, f"no edge {u}->{v} in path {path}"
        total += min(weights)
    assert total == dist[target], f"path {path} has weight {total}, expected {dist[target]}"


def _raises_value_error(graph, source, target):
    try:
        dijkstra(graph, source, target)
    except ValueError:
        return True
    return False


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.dijkstra)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    graph = {"a": [("b", 1), ("c", 4)], "b": [("c", 2)], "c": []}
    dist, path = dijkstra(graph, "a", "c")
    assert dist == {"a": 0, "b": 1, "c": 3}
    assert path == ["a", "b", "c"]


def test_source_equals_target():
    dist, path = dijkstra({"a": [("b", 5)]}, "a", "a")
    assert dist == {"a": 0, "b": 5} and path == ["a"]


def test_isolated_source():
    dist, path = dijkstra({"a": []}, "a", "b")
    assert dist == {"a": 0} and path == []


def test_disconnected_graph_omits_unreachable_nodes():
    graph = {"a": [("b", 2)], "b": [], "c": [("d", 1)], "d": [("a", 1)]}
    dist, path = dijkstra(graph, "a", "d")
    assert dist == {"a": 0, "b": 2}
    assert path == []


def test_edges_are_directed():
    dist, path = dijkstra({"a": [], "b": [("a", 1)]}, "a", "b")
    assert dist == {"a": 0} and path == []


def test_stale_heap_entries_are_handled():
    # c is first pushed at distance 10, then improved to 3 via b; d is pushed at 11 then 4.
    # Finalizing a node on its first discovery (or marking visited at push) gives 10 / 11.
    graph = {
        "s": [("c", 10), ("b", 1)],
        "b": [("c", 2)],
        "c": [("d", 1)],
        "d": [],
    }
    dist, path = dijkstra(graph, "s", "d")
    assert dist == {"s": 0, "b": 1, "c": 3, "d": 4}
    assert path == ["s", "b", "c", "d"]


def test_target_must_be_settled_before_stopping():
    # The direct edge discovers t first at distance 10 before the cheaper route.
    graph = {"s": [("t", 10), ("a", 1)], "a": [("b", 1)], "b": [("t", 1)]}
    dist, path = dijkstra(graph, "s", "t")
    assert dist["t"] == 3 and path == ["s", "a", "b", "t"]


def test_multiple_equal_shortest_paths():
    graph = {"s": [("a", 1), ("b", 1)], "a": [("t", 1)], "b": [("t", 1)], "t": []}
    dist, path = dijkstra(graph, "s", "t")
    assert dist["t"] == 2
    assert path in (["s", "a", "t"], ["s", "b", "t"])


def test_zero_weight_edges_cycles_self_loops_and_parallel_edges():
    graph = {
        0: [(1, 0), (0, 0), (2, 5), (2, 1)],
        1: [(0, 0), (2, 3)],
        2: [(3, 0)],
        3: [(2, 0)],
    }
    dist, path = dijkstra(graph, 0, 3)
    assert dist == {0: 0, 1: 0, 2: 1, 3: 1}
    _assert_valid_path(graph, 0, 3, dist, path)


def test_negative_edges_are_rejected():
    assert _raises_value_error({"a": [("b", -1)], "b": []}, "a", "b")
    # Rejected even when the negative edge is unreachable from the source.
    assert _raises_value_error({"a": [("b", 1)], "b": [], "c": [("a", -2)]}, "a", "b")


def test_integer_and_float_weights():
    graph = {"a": [("b", 0.5), ("c", 2)], "b": [("c", 0.25)], "c": []}
    dist, path = dijkstra(graph, "a", "c")
    assert dist["c"] == 0.75 and path == ["a", "b", "c"]


def test_matches_bellman_ford_on_random_graphs():
    rng = random.Random(30)
    for _ in range(200):
        n = rng.randint(1, 9)
        graph = {u: [] for u in range(n)}
        for _ in range(rng.randint(0, 25)):
            graph[rng.randrange(n)].append((rng.randrange(n), rng.randint(0, 9)))
        source, target = rng.randrange(n), rng.randrange(n)
        dist, path = dijkstra(graph, source, target)
        assert dist == _bellman_ford(graph, source), graph
        if target in dist:
            _assert_valid_path(graph, source, target, dist, path)
        else:
            assert path == []


def test_graph_is_not_mutated():
    graph = {"a": [("b", 1)], "b": [("c", 1)]}
    snapshot = {u: list(edges) for u, edges in graph.items()}
    dijkstra(graph, "a", "c")
    assert graph == snapshot
