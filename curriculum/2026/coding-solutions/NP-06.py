import numpy as np


def pairwise_sq_distances(queries: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """(m, n) squared Euclidean distances via ||q||^2 - 2 q.x + ||x||^2."""
    q = np.asarray(queries, dtype=float)
    x = np.asarray(candidates, dtype=float)
    q_sq = np.einsum("ij,ij->i", q, q)[:, None]  # (m, 1)
    x_sq = np.einsum("ij,ij->i", x, x)[None, :]  # (1, n)
    d = q_sq - 2.0 * (q @ x.T) + x_sq
    # Cancellation can leave tiny negatives; clamp only those.
    return np.maximum(d, 0.0)


def pairwise_knn(
    queries: np.ndarray,
    candidates: np.ndarray,
    k: int,
    chunk_size: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Exact kNN by squared distance, ties by index, optionally chunked over queries."""
    q = np.asarray(queries, dtype=float)
    x = np.asarray(candidates, dtype=float)
    if q.ndim != 2 or x.ndim != 2 or q.shape[1] != x.shape[1]:
        raise ValueError("queries (m, d) and candidates (n, d) must be 2-D with equal d")
    m, n = len(q), len(x)
    if not 1 <= k <= n:
        raise ValueError("k must satisfy 1 <= k <= n")
    if chunk_size is None:
        chunk_size = max(m, 1)
    elif chunk_size < 1:
        raise ValueError("chunk_size must be positive")

    distances = np.empty((m, k))
    indices = np.empty((m, k), dtype=np.intp)
    for start in range(0, m, chunk_size):  # loop over query chunks only
        block = pairwise_sq_distances(q[start:start + chunk_size], x)  # (c, n)
        # Stable argsort gives ascending distance with ties by candidate index.
        # (argpartition is O(n) but may pick an arbitrary index among ties at the k-th slot.)
        order = np.argsort(block, axis=1, kind="stable")[:, :k]
        indices[start:start + chunk_size] = order
        distances[start:start + chunk_size] = np.take_along_axis(block, order, axis=1)
    return distances, indices
