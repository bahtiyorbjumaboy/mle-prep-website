import numpy as np


class PCA:
    """PCA via SVD of the centered data.

    Canonical prompt: implement PCA `fit`, `transform`, and `inverse_transform`: center
    data, learn components using SVD (and explain the covariance-eigendecomposition
    equivalent), return explained-variance ratios, and reconstruct data from `k`
    components.

    Contract:
    - `fit(x)` with `x` `(n, d)`, `n >= 2`: `mean_` `(d,)`; `components_` `(k, d)` with
      orthonormal rows (right singular vectors of `x - mean_`), sorted by decreasing
      variance; `explained_variance_` `(k,)` = `s^2 / (n - 1)` (the eigenvalues of the
      ddof=1 sample covariance); `explained_variance_ratio_` = variance / total variance
      of ALL directions (so it sums to <= 1, and to 1 when k = rank).
    - `n_components=None` keeps `min(n, d)` components; it must otherwise satisfy
      `1 <= k <= min(n, d)`. `k` may exceed the data rank: the extra components have
      zero variance.
    - Component signs are arbitrary (tests are sign-invariant). Use SVD, not sklearn.
    - `transform(x) = (x - mean_) @ components_.T`; `inverse_transform(z) = z @ components_ + mean_`.

    Raises:
        ValueError: invalid `n_components`, `n < 2`, non-2-D input, or a feature-dimension
            mismatch in `transform` / component-count mismatch in `inverse_transform`.
    """

    def __init__(self, n_components: int | None = None) -> None:
        raise NotImplementedError("TODO: implement ML-14")

    def fit(self, x: np.ndarray) -> "PCA":
        raise NotImplementedError("TODO: implement ML-14")

    def transform(self, x: np.ndarray) -> np.ndarray:
        raise NotImplementedError("TODO: implement ML-14")

    def inverse_transform(self, z: np.ndarray) -> np.ndarray:
        raise NotImplementedError("TODO: implement ML-14")
