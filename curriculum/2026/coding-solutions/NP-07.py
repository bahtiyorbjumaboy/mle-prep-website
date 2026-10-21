import numpy as np


def _as_samples(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2:
        raise ValueError("x must be 2-D (n, d) with n >= 2")
    return x


def standardize(x: np.ndarray) -> np.ndarray:
    """Column z-scores with ddof=1; constant columns map to 0."""
    x = _as_samples(x)
    centered = x - x.mean(axis=0)
    std = x.std(axis=0, ddof=1)
    # Exact equality, not std > 0: rounding makes std([0.1] * 4) ~1e-17.
    varying = ~np.all(x == x[:1], axis=0)
    return np.divide(centered, std, out=np.zeros_like(x), where=varying)


def covariance(x: np.ndarray) -> np.ndarray:
    """Sample covariance (ddof=1), centered first for numerical stability."""
    x = _as_samples(x)
    centered = x - x.mean(axis=0)
    return centered.T @ centered / (len(x) - 1)


def correlation(x: np.ndarray) -> np.ndarray:
    """Pearson correlation; zero-variance columns get 0 off-diagonal and 1 on the diagonal."""
    x = _as_samples(x)
    z = standardize(x)  # constant columns are already all zeros
    r = z.T @ z / (len(x) - 1)
    np.fill_diagonal(r, 1.0)
    return np.clip(r, -1.0, 1.0)  # rounding can push |r| slightly above 1


def whiten(x: np.ndarray, method: str = "zca", eps: float = 1e-8) -> np.ndarray:
    """PCA or ZCA whitening using the eigendecomposition of the sample covariance."""
    if method not in ("zca", "pca"):
        raise ValueError("method must be 'zca' or 'pca'")
    if eps <= 0:
        raise ValueError("eps must be positive")
    x = _as_samples(x)
    centered = x - x.mean(axis=0)
    lam, v = np.linalg.eigh(covariance(x))  # symmetric -> real eigenpairs
    scale = 1.0 / np.sqrt(np.clip(lam, 0.0, None) + eps)
    rotated = (centered @ v) * scale  # (n, d) @ (d, d), then scale each component
    return rotated if method == "pca" else rotated @ v.T


def standardize_and_whiten(x: np.ndarray, eps: float = 1e-8) -> tuple[np.ndarray, np.ndarray]:
    """Return the ddof=1 standardization and the ZCA-whitened data."""
    return standardize(x), whiten(x, "zca", eps)
