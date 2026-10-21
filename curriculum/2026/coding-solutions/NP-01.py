import numpy as np


def array_operations(
    x: np.ndarray,
    weights: np.ndarray | None = None,
    mask: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """Vectorized row normalization, column standardization, masked and weighted means."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 2:
        raise ValueError("x must have shape (B, D)")
    b, d = x.shape

    # (B, 1) norms broadcast against (B, D); zero rows keep the zero-initialized output.
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    row_normalized = np.divide(x, norms, out=np.zeros_like(x), where=norms > 0)

    # (1, D) column statistics. Exact equality detects constant columns; std > 0 does not
    # (std of [0.1, 0.1, 0.1] is ~1e-17 from rounding in the mean).
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True)
    varying = ~np.all(x == x[:1], axis=0, keepdims=True)
    col_standardized = np.divide(x - mean, std, out=np.zeros_like(x), where=varying)

    if mask is None:
        mask = np.ones((b, d), dtype=bool)
    else:
        mask = np.asarray(mask)
        if mask.shape != (b, d):
            raise ValueError("mask must have shape (B, D)")
        mask = mask.astype(bool)  # never use a 0/1 int mask as a fancy index
    counts = mask.sum(axis=1)
    sums = np.where(mask, x, 0.0).sum(axis=1)
    masked_mean = np.full(b, np.nan)
    np.divide(sums, counts, out=masked_mean, where=counts > 0)

    if weights is None:
        w = np.ones(d)
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != (d,):
            raise ValueError("weights must have shape (D,)")
        if np.any(w < 0) or w.sum() <= 0:
            raise ValueError("weights must be non-negative with a positive sum")
    weighted_row_mean = x @ w / w.sum()

    return {
        "row_normalized": row_normalized,
        "col_standardized": col_standardized,
        "masked_mean": masked_mean,
        "weighted_row_mean": weighted_row_mean,
    }
