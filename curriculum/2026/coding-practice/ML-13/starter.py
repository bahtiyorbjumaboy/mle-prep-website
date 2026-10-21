import numpy as np


class KNearestNeighbors:
    """Exact kNN classifier/regressor.

    Canonical prompt: build `fit/predict` kNN for classification and regression using
    exact distances. Support uniform and inverse-distance weighting with deterministic
    tie handling.

    Contract:
    - Distance is Euclidean. Neighbors are ordered by ascending distance; equal
      distances are ordered by ascending training-row index (also at the k-th slot).
    - `weights="uniform"`: each of the k neighbors counts 1.
      `weights="distance"`: each counts `1 / distance`. If any of the k neighbors is at
      distance exactly 0, only the zero-distance neighbors count (equally) - no inf/NaN.
    - Classification: the class with the largest total weight; ties -> smallest label
      (labels may be ints or strings). Regression: weighted mean of neighbor targets.
    - `fit` stores copies (later changes to the caller's arrays have no effect).
    - Prediction is vectorized over queries: O(q * n * d) array work, no Python loop
      over queries or training rows.

    Raises:
        ValueError: `k < 1`, unknown `task`/`weights`, `k > n_train` at fit, mismatched
            shapes, or a feature-dimension mismatch at predict.
    """

    def __init__(self, k: int = 5, task: str = "classification", weights: str = "uniform") -> None:
        raise NotImplementedError("TODO: implement ML-13")

    def fit(self, x: np.ndarray, y: np.ndarray) -> "KNearestNeighbors":
        raise NotImplementedError("TODO: implement ML-13")

    def kneighbors(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """`(distances, indices)`, both `(q, k)`, ordered as described above."""
        raise NotImplementedError("TODO: implement ML-13")

    def predict(self, x: np.ndarray) -> np.ndarray:
        """`(q,)` predicted labels (classification) or float targets (regression)."""
        raise NotImplementedError("TODO: implement ML-13")
