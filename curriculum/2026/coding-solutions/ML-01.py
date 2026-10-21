import math

import numpy as np


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Direct arithmetic: dot / (|a| |b|), with a zero vector giving 0.0."""
    if len(a) != len(b):
        raise ValueError("vectors must have equal length")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def _normalize_rows(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=-1, keepdims=True)
    return np.divide(x, norms, out=np.zeros_like(x), where=norms > 0)


def _validate(queries: np.ndarray, candidates: np.ndarray, k: int) -> None:
    if candidates.ndim != 2 or queries.shape[-1] != candidates.shape[1]:
        raise ValueError("queries and candidates must share the last dimension d")
    if not 1 <= k <= len(candidates):
        raise ValueError("k must satisfy 1 <= k <= n")


def cosine_retrieve_batch(
    queries: np.ndarray, candidates: np.ndarray, k: int
) -> tuple[np.ndarray, np.ndarray]:
    """(m, k) top-k cosine indices/scores: normalize once, one matmul, stable sort."""
    queries = np.asarray(queries, dtype=float)
    candidates = np.asarray(candidates, dtype=float)
    if queries.ndim != 2:
        raise ValueError("queries must be (m, d)")
    _validate(queries, candidates, k)
    scores = _normalize_rows(queries) @ _normalize_rows(candidates).T  # (m, n)
    order = np.argsort(-scores, axis=1, kind="stable")[:, :k]  # stable: ties by index
    return order, np.take_along_axis(scores, order, axis=1)


def cosine_retrieve(query: np.ndarray, candidates: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Single (d,) query: the batch path with m = 1, returned as 1-D arrays."""
    query = np.asarray(query, dtype=float)
    if query.ndim != 1:
        raise ValueError("query must be (d,)")
    indices, scores = cosine_retrieve_batch(query[None, :], candidates, k)
    return indices[0], scores[0]
