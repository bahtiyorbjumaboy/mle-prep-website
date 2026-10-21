import heapq
from itertools import count
from typing import Hashable

Graph = dict[Hashable, list[tuple[Hashable, float]]]


def dijkstra(graph: Graph, source: Hashable, target: Hashable) -> tuple[dict[Hashable, float], list[Hashable]]:
    """Return shortest distances from source and one shortest path to target."""
    if any(weight < 0 for edges in graph.values() for _, weight in edges):
        raise ValueError("Dijkstra requires nonnegative edge weights")

    dist: dict[Hashable, float] = {source: 0}
    previous: dict[Hashable, Hashable] = {}
    settled: set[Hashable] = set()
    tie = count()  # breaks distance ties without comparing node objects
    heap = [(0, next(tie), source)]
    while heap:
        d, _, node = heapq.heappop(heap)
        if node in settled:
            continue  # stale entry: a shorter distance was already settled
        settled.add(node)
        for neighbor, weight in graph.get(node, []):
            candidate = d + weight
            if candidate < dist.get(neighbor, float("inf")):
                dist[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(heap, (candidate, next(tie), neighbor))

    if target not in dist:
        return dist, []
    path = [target]
    while path[-1] != source:
        path.append(previous[path[-1]])
    return dist, path[::-1]
