import numpy as np


def normalize_rows(x: np.ndarray) -> np.ndarray:
    """Return a float64 copy of `x` `(n, d)` whose nonzero rows have unit L2 norm.

    All-zero rows stay all zeros (no NaN). The input is not modified.
    """
    raise NotImplementedError("TODO: implement NP-02")


def batched_cosine_topk(
    queries: np.ndarray,
    candidates: np.ndarray,
    k: int,
    chunk_size: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Top-k candidates per query by cosine similarity.

    Canonical prompt: given `Q(m,d)` and `X(n,d)`, return `(m,k)` candidate indices and
    cosine scores for the top-k candidates per query without Python loops over
    queries/candidates. Support chunking when the full score matrix does not fit memory.

    Contract:
    - Cosine similarity involving a zero vector is defined as 0.0 (never NaN).
    - Each output row is sorted by descending score; equal scores are ordered by
      ascending candidate index. Results must not depend on `chunk_size`.
    - `chunk_size=None` scores all candidates at once. A positive `chunk_size` scores
      at most `chunk_size` candidate rows at a time (an `(m, chunk_size)` block) and
      merges a running top-k, so extra memory is O(m * (k + chunk_size) + n * d),
      never O(m * n). A Python loop over chunks is fine; loops over individual
      queries or candidates are not.

    Args:
        queries: Real array `(m, d)`.
        candidates: Real array `(n, d)` with the same `d`.
        k: Number of results per query, `1 <= k <= n`.
        chunk_size: `None` or a positive int.

    Returns:
        `(indices, scores)`: an integer array `(m, k)` and a float64 array `(m, k)`.

    Raises:
        ValueError: on non-2-D inputs, mismatched `d`, `k` outside `[1, n]`, or a
            non-positive `chunk_size`.
    """
    raise NotImplementedError("TODO: implement NP-02")
