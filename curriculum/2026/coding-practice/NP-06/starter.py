import numpy as np


def pairwise_sq_distances(queries: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Squared Euclidean distances `(m, n)` via the norm expansion.

    Use `||q||^2 - 2 q.x + ||x||^2` (matmul, no Python loop over pairs and no
    `(m, n, d)` broadcast tensor). Floating-point cancellation can produce tiny
    negatives: clamp those to exactly 0, and change nothing else (no abs, no epsilon,
    no rounding of small positive distances).
    """
    raise NotImplementedError("TODO: implement NP-06")


def pairwise_knn(
    queries: np.ndarray,
    candidates: np.ndarray,
    k: int,
    chunk_size: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Exact k nearest candidates per query by squared Euclidean distance.

    Canonical prompt: given query matrix `Q(m,d)` and reference matrix `X(n,d)`,
    compute pairwise squared Euclidean distances without a Python loop over pairs,
    return exact top-k nearest indices, and support chunked queries when `m*n` scores
    do not fit memory.

    Contract:
    - Rows are sorted by ascending distance; equal distances are ordered by ascending
      candidate index (including ties at the k-th boundary).
    - `chunk_size=None` processes all queries at once; a positive `chunk_size`
      processes at most `chunk_size` query rows at a time, so the distance block is
      `(chunk_size, n)` and peak memory is O(chunk_size * n), not O(m * n). Results
      must not depend on `chunk_size`. A loop over chunks is fine.

    Args:
        queries: `(m, d)`. candidates: `(n, d)`. k: `1 <= k <= n`.
        chunk_size: `None` or a positive int.

    Returns:
        `(distances, indices)`: float64 `(m, k)` squared distances and integer `(m, k)`.

    Raises:
        ValueError: on non-2-D inputs, mismatched `d`, `k` outside `[1, n]`
            (`k > n` is an error, not silently clamped), or non-positive `chunk_size`.
    """
    raise NotImplementedError("TODO: implement NP-06")
