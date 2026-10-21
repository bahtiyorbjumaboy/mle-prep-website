import numpy as np


class KNearestNeighbors:
    """Exact kNN with stable tie handling and uniform or inverse-distance weights."""

    def __init__(self, k: int = 5, task: str = "classification", weights: str = "uniform") -> None:
        if k < 1:
            raise ValueError("k must be >= 1")
        if task not in ("classification", "regression"):
            raise ValueError("task must be 'classification' or 'regression'")
        if weights not in ("uniform", "distance"):
            raise ValueError("weights must be 'uniform' or 'distance'")
        self.k, self.task, self.weights = k, task, weights

    def fit(self, x: np.ndarray, y: np.ndarray) -> "KNearestNeighbors":
        x = np.array(x, dtype=float)  # copies: the model owns its training data
        y = np.array(y)
        if x.ndim != 2 or y.shape != (x.shape[0],):
            raise ValueError("expected x (n, d) and y (n,)")
        if self.k > len(x):
            raise ValueError("k cannot exceed the number of training rows")
        self.x_, self.y_ = x, y
        if self.task == "classification":
            self.classes_, self.codes_ = np.unique(y, return_inverse=True)  # sorted labels
        return self

    def kneighbors(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[1] != self.x_.shape[1]:
            raise ValueError("query feature dimension does not match training data")
        # Direct differences, O(q n d) memory: unlike the norm expansion, identical points
        # get exactly 0, which the zero-distance weighting rule depends on.
        dist = np.sqrt(((x[:, None, :] - self.x_[None, :, :]) ** 2).sum(axis=2))  # (q, n)
        idx = np.argsort(dist, axis=1, kind="stable")[:, :self.k]  # ties -> lower row index
        return np.take_along_axis(dist, idx, axis=1), idx

    def _neighbor_weights(self, dist: np.ndarray) -> np.ndarray:
        if self.weights == "uniform":
            return np.ones_like(dist)
        exact = dist == 0
        # Rows with an exact match use only those matches; others use 1 / d (d > 0 there).
        inverse = np.divide(1.0, dist, out=np.zeros_like(dist), where=~exact)
        return np.where(exact.any(axis=1, keepdims=True), exact.astype(float), inverse)

    def predict(self, x: np.ndarray) -> np.ndarray:
        dist, idx = self.kneighbors(x)
        w = self._neighbor_weights(dist)
        if self.task == "regression":
            return (w * self.y_[idx]).sum(axis=1) / w.sum(axis=1)
        votes = np.zeros((len(idx), len(self.classes_)))
        rows = np.repeat(np.arange(len(idx)), self.k)
        np.add.at(votes, (rows, self.codes_.ravel()[idx].ravel()), w.ravel())
        return self.classes_[np.argmax(votes, axis=1)]  # first max -> smallest label
