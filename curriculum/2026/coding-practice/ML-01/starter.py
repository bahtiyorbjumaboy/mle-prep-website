import numpy as np

# Canonical prompt: given one query vector and `n` candidate vectors, return top-k by
# cosine similarity. First write the arithmetic directly; then vectorize and batch
# multiple queries.
#
# Shared contract: cosine with a zero vector is 0.0 (never NaN). Results are sorted by
# descending score with ties broken by ascending candidate index. `1 <= k <= n`, else
# ValueError (also for mismatched dimensions).


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Step 1: cosine(a, b) = a.b / (|a| |b|) written with plain Python arithmetic.

    Accepts equal-length sequences of numbers; returns a Python float. Raises
    ValueError on a length mismatch.
    """
    raise NotImplementedError("TODO: implement ML-01")


def cosine_retrieve(query: np.ndarray, candidates: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Step 2: one query `(d,)` against `(n, d)` candidates, vectorized (no loop over n).

    Returns:
        `(indices, scores)`, each 1-D of shape `(k,)`.
    """
    raise NotImplementedError("TODO: implement ML-01")


def cosine_retrieve_batch(
    queries: np.ndarray, candidates: np.ndarray, k: int
) -> tuple[np.ndarray, np.ndarray]:
    """Step 3: `(m, d)` queries at once (no loop over queries or candidates).

    Normalize the candidates once (the precomputation an index would store), then
    score every query with a single matmul.

    Returns:
        `(indices, scores)`, each of shape `(m, k)` (still 2-D when `m == 1`).
    """
    raise NotImplementedError("TODO: implement ML-01")
