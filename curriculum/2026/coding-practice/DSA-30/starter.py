from typing import Hashable

Graph = dict[Hashable, list[tuple[Hashable, float]]]


def dijkstra(graph: Graph, source: Hashable, target: Hashable) -> tuple[dict[Hashable, float], list[Hashable]]:
    """Return shortest distances from `source` and one shortest path to `target`.

    Target O((V + E) log V) with a binary heap.

    Args:
        graph: Directed adjacency list `{u: [(v, weight), ...]}`. Nodes may appear only as
            neighbors; parallel edges, self-loops, and zero-weight edges are allowed.
        source: Start node.
        target: Node to reconstruct a path to.

    Returns:
        `(dist, path)` where `dist` maps every node reachable from `source` (including
        `source`, at 0) to its shortest distance, and `path` is a node list from `source` to
        `target` whose total weight equals `dist[target]`, or `[]` if `target` is unreachable.

    Raises:
        ValueError: If any edge in `graph` has a negative weight.
    """
    raise NotImplementedError("TODO: implement DSA-30")
