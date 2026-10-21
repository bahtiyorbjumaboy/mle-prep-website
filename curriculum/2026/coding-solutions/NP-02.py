import numpy as np


def normalize_rows(x: np.ndarray) -> np.ndarray:
    """Return a float64 copy of `x` whose nonzero rows have unit L2 norm."""
    x = np.asarray(x, dtype=float)
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return np.divide(x, norms, out=np.zeros_like(x), where=norms > 0)


def _topk_sorted(scores: np.ndarray, indices: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Top-k columns per row by (-score, index); scores/indices are aligned (m, c) arrays."""
    # lexsort sorts by the last key first: primary -score, secondary candidate index.
    order = np.lexsort((indices, -scores), axis=1)[:, :k]
    return np.take_along_axis(indices, order, axis=1), np.take_along_axis(scores, order, axis=1)


def batched_cosine_topk(
    queries: np.ndarray,
    candidates: np.ndarray,
    k: int,
    chunk_size: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Top-k cosine candidates per query; optional candidate chunking with a running merge."""
    queries = np.asarray(queries, dtype=float)
    candidates = np.asarray(candidates, dtype=float)
    if queries.ndim != 2 or candidates.ndim != 2 or queries.shape[1] != candidates.shape[1]:
        raise ValueError("queries (m, d) and candidates (n, d) must be 2-D with equal d")
    m, n = len(queries), len(candidates)
    if not 1 <= k <= n:
        raise ValueError("k must satisfy 1 <= k <= n")
    if chunk_size is None:
        chunk_size = n
    elif chunk_size < 1:
        raise ValueError("chunk_size must be positive")

    q = normalize_rows(queries)
    x = normalize_rows(candidates)
    best_i = np.empty((m, 0), dtype=np.int64)
    best_s = np.empty((m, 0))
    for start in range(0, n, chunk_size):  # loop over chunks only
        block = q @ x[start:start + chunk_size].T  # (m, c)
        block_i = np.broadcast_to(np.arange(start, start + block.shape[1]), block.shape)
        # Merge the running best k with this block: each step sorts only k + c columns per row.
        best_i, best_s = _topk_sorted(
            np.concatenate([best_s, block], axis=1), np.concatenate([best_i, block_i], axis=1), k
        )
    return best_i, best_s
