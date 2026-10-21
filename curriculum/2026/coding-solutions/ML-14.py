import numpy as np


class PCA:
    """PCA from the thin SVD of centered data (equivalently eigh of the sample covariance)."""

    def __init__(self, n_components: int | None = None) -> None:
        self.n_components = n_components

    def fit(self, x: np.ndarray) -> "PCA":
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[0] < 2:
            raise ValueError("x must be (n, d) with n >= 2")
        n, d = x.shape
        k = min(n, d) if self.n_components is None else self.n_components
        if not 1 <= k <= min(n, d):
            raise ValueError("n_components must satisfy 1 <= k <= min(n, d)")
        self.mean_ = x.mean(axis=0)
        # Xc = U S Vt; rows of Vt are the principal axes, already sorted by singular value.
        # Same axes as eigh(Xc^T Xc / (n - 1)) without forming (and squaring) the covariance.
        _, s, vt = np.linalg.svd(x - self.mean_, full_matrices=False)
        variance = s ** 2 / (n - 1)
        self.components_ = vt[:k]
        self.explained_variance_ = variance[:k]
        total = variance.sum()
        self.explained_variance_ratio_ = variance[:k] / total if total > 0 else np.zeros(k)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[1] != len(self.mean_):
            raise ValueError("feature dimension does not match the fitted data")
        return (x - self.mean_) @ self.components_.T

    def inverse_transform(self, z: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        if z.ndim != 2 or z.shape[1] != len(self.components_):
            raise ValueError("z must have one column per component")
        return z @ self.components_ + self.mean_
