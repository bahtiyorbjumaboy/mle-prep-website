import numpy as np


def standardize(x: np.ndarray) -> np.ndarray:
    """Column z-scores of `x` `(n, d)` using the sample std (ddof=1).

    A column whose entries are all equal (zero variance) maps to all zeros.
    Requires `n >= 2`; raises ValueError otherwise or if `x` is not 2-D.
    """
    raise NotImplementedError("TODO: implement NP-07")


def covariance(x: np.ndarray) -> np.ndarray:
    """Sample covariance `(d, d)` of the columns: `Xc^T Xc / (n - 1)`, `Xc` centered.

    Center first (do not use the one-pass `E[x^2] - E[x]^2` form, which cancels
    catastrophically for large means). Do not call `np.cov` / `np.corrcoef`.
    Requires `n >= 2`.
    """
    raise NotImplementedError("TODO: implement NP-07")


def correlation(x: np.ndarray) -> np.ndarray:
    """Pearson correlation `(d, d)`.

    Zero-variance policy: entries involving a zero-variance column are 0, except its
    diagonal entry, which is 1. Otherwise the diagonal is exactly 1, the matrix is
    symmetric, and every entry lies in [-1, 1]. No NaN.
    """
    raise NotImplementedError("TODO: implement NP-07")


def whiten(x: np.ndarray, method: str = "zca", eps: float = 1e-8) -> np.ndarray:
    """Whiten `x` `(n, d)` so the sample covariance of the result is ~identity.

    Let `C = covariance(x) = V diag(lam) V^T` (use `np.linalg.eigh`; clip tiny negative
    eigenvalues to 0). With `S = diag(1 / sqrt(lam + eps))`:
    - `"pca"`: `Xc @ V @ S` (decorrelated, rotated onto the principal axes);
    - `"zca"`: `Xc @ V @ S @ V^T` (symmetric transform; stays closest to `x`).
    Rank-deficient input must stay finite. Raises ValueError for an unknown method,
    `eps <= 0`, or `n < 2`.
    """
    raise NotImplementedError("TODO: implement NP-07")


def standardize_and_whiten(x: np.ndarray, eps: float = 1e-8) -> tuple[np.ndarray, np.ndarray]:
    """Canonical prompt: implement column standardization, sample covariance,
    correlation, and a whitening transform from NumPy primitives. Clearly define ddof
    and behavior for zero-variance columns.

    Returns:
        `(standardize(x), whiten(x, "zca", eps))`.
    """
    raise NotImplementedError("TODO: implement NP-07")
