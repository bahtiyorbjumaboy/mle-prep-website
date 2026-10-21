import numpy as np


def linear_regression_gd(
    x: np.ndarray, y: np.ndarray, learning_rate: float = 0.1, steps: int = 1000
) -> tuple[np.ndarray, float, list[float]]:
    """Full-batch GD on mean squared error / 2."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n, d = x.shape
    w, b = np.zeros(d), 0.0
    history = []
    for _ in range(steps):
        r = x @ w + b - y
        w = w - learning_rate * (x.T @ r / n)
        b = b - learning_rate * r.mean()
        history.append(float(np.mean((x @ w + b - y) ** 2) / 2))
    return w, float(b), history


def _sigmoid(z: np.ndarray) -> np.ndarray:
    e = np.exp(-np.abs(z))  # <= 1, so neither branch overflows
    return np.where(z >= 0, 1.0 / (1.0 + e), e / (1.0 + e))


def _bce_from_logits(z: np.ndarray, y: np.ndarray) -> np.ndarray:
    # -[y log s(z) + (1 - y) log(1 - s(z))] = max(z, 0) - z y + log(1 + exp(-|z|))
    return np.maximum(z, 0.0) - z * y + np.log1p(np.exp(-np.abs(z)))


class LogisticRegression:
    """Binary logistic regression with unregularized intercept and optional mini-batches."""

    def __init__(
        self,
        learning_rate: float = 0.1,
        steps: int = 1000,
        l2: float = 0.0,
        batch_size: int | None = None,
        seed: int = 0,
    ) -> None:
        self.learning_rate = learning_rate
        self.steps = steps
        self.l2 = l2
        self.batch_size = batch_size
        self.seed = seed

    @staticmethod
    def _validate(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y)
        if x.ndim != 2 or y.shape != (x.shape[0],):
            raise ValueError("expected x (n, d) and y (n,)")
        if not np.all((y == 0) | (y == 1)):
            raise ValueError("labels must be 0/1")
        return x, y.astype(float)

    def loss(self, x: np.ndarray, y: np.ndarray) -> float:
        x, y = self._validate(x, y)
        z = x @ self.weights_ + self.bias_
        return float(_bce_from_logits(z, y).mean() + 0.5 * self.l2 * self.weights_ @ self.weights_)

    def gradient(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
        x, y = self._validate(x, y)
        residual = _sigmoid(x @ self.weights_ + self.bias_) - y  # dBCE/dz
        grad_w = x.T @ residual / len(y) + self.l2 * self.weights_  # no penalty on the bias
        return grad_w, float(residual.mean())

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LogisticRegression":
        x, y = self._validate(x, y)
        n, d = x.shape
        self.weights_, self.bias_ = np.zeros(d), 0.0
        self.loss_history_ = []
        rng = np.random.default_rng(self.seed)
        for _ in range(self.steps):
            if self.batch_size is None:
                batches = [np.arange(n)]
            else:
                order = rng.permutation(n)
                batches = [order[i:i + self.batch_size] for i in range(0, n, self.batch_size)]
            for idx in batches:
                grad_w, grad_b = self.gradient(x[idx], y[idx])
                self.weights_ = self.weights_ - self.learning_rate * grad_w
                self.bias_ = self.bias_ - self.learning_rate * grad_b
            self.loss_history_.append(self.loss(x, y))
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        return _sigmoid(np.asarray(x, dtype=float) @ self.weights_ + self.bias_)

    def predict(self, x: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(x) >= threshold).astype(np.intp)
