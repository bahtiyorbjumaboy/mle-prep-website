import numpy as np

# Canonical prompt: warm up with linear-regression gradient descent, then implement
# binary logistic regression with intercept, stable BCE, L2, mini-batches, loss
# history, `predict_proba`, and thresholded prediction.


def linear_regression_gd(
    x: np.ndarray, y: np.ndarray, learning_rate: float = 0.1, steps: int = 1000
) -> tuple[np.ndarray, float, list[float]]:
    """Warm-up: full-batch gradient descent on `J = mean((x @ w + b - y)^2) / 2`.

    Start from `w = 0`, `b = 0`; each step uses `grad_w = x.T @ r / n`, `grad_b = mean(r)`
    with residual `r = x @ w + b - y`. `history[t]` is `J` after step `t`.

    Returns:
        `(w, b, history)`: `(d,)` float array, float, list of `steps` floats.
    """
    raise NotImplementedError("TODO: implement ML-06")


class LogisticRegression:
    """Binary logistic regression trained by (mini-batch) gradient descent.

    Contract:
    - Labels are 0/1 (bools allowed); anything else raises ValueError.
    - Objective: `J(w, b) = mean_i BCE(x_i @ w + b, y_i) + (l2 / 2) * ||w||^2`. The
      intercept `b` is NOT regularized. BCE must be computed from logits stably
      (finite for logits of +/-1e4, e.g. unscaled features or a diverging learning rate).
    - Gradient on a batch of size m: `grad_w = x_B.T @ (sigmoid(z_B) - y_B) / m + l2 * w`,
      `grad_b = mean(sigmoid(z_B) - y_B)`.
    - `fit` starts from `w = 0`, `b = 0` and runs `steps` epochs. With
      `batch_size=None` an epoch is one full-batch step. Otherwise each epoch shuffles
      the rows with a single `np.random.default_rng(seed)` created at the start of
      `fit` and takes one step per consecutive batch (the last may be smaller).
    - `loss_history_[t]` is the full-data objective `J` after epoch `t`.
    - `predict(x, threshold)` returns int 0/1 with 1 iff `predict_proba(x) >= threshold`.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        steps: int = 1000,
        l2: float = 0.0,
        batch_size: int | None = None,
        seed: int = 0,
    ) -> None:
        raise NotImplementedError("TODO: implement ML-06")

    def loss(self, x: np.ndarray, y: np.ndarray) -> float:
        """Objective `J` at the current `weights_` / `bias_`."""
        raise NotImplementedError("TODO: implement ML-06")

    def gradient(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
        """`(grad_w, grad_b)` of `J` on the given rows at the current parameters."""
        raise NotImplementedError("TODO: implement ML-06")

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LogisticRegression":
        """Train; sets `weights_` `(d,)`, `bias_` (float), `loss_history_` (list)."""
        raise NotImplementedError("TODO: implement ML-06")

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        """`(n,)` probabilities of class 1 (stable sigmoid)."""
        raise NotImplementedError("TODO: implement ML-06")

    def predict(self, x: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """`(n,)` int predictions."""
        raise NotImplementedError("TODO: implement ML-06")
