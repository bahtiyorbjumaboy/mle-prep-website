import numpy as np

# Canonical prompt: implement linear regression with intercept using gradient descent,
# then add ridge regularization. Separately compute a closed-form reference with a
# numerically appropriate solver rather than explicit matrix inversion. Compare
# predictions/coefficients on a small well-conditioned fixture.
#
# Objective shared by every function (x: (n, d), y: (n,), w: (d,), b: float):
#     J(w, b) = mean((x @ w + b - y) ** 2) / 2 + (alpha / 2) * ||w||^2
# The intercept b is NOT regularized. alpha >= 0 (ValueError otherwise).


def ridge_loss(x: np.ndarray, y: np.ndarray, w: np.ndarray, b: float, alpha: float = 0.0) -> float:
    """The objective J above."""
    raise NotImplementedError("TODO: implement ML-12")


def ridge_gradient(
    x: np.ndarray, y: np.ndarray, w: np.ndarray, b: float, alpha: float = 0.0
) -> tuple[np.ndarray, float]:
    """`(dJ/dw, dJ/db)`; O(n d)."""
    raise NotImplementedError("TODO: implement ML-12")


def fit_ridge_gd(
    x: np.ndarray, y: np.ndarray, alpha: float = 0.0, learning_rate: float = 0.1, steps: int = 1000
) -> tuple[np.ndarray, float, list[float]]:
    """Full-batch gradient descent from `w = 0, b = 0`; `history[t] = J` after step `t`."""
    raise NotImplementedError("TODO: implement ML-12")


def ridge_closed_form(x: np.ndarray, y: np.ndarray, alpha: float = 0.0) -> tuple[np.ndarray, float]:
    """Exact minimizer of J.

    Center `x` and `y` to remove the (unregularized) intercept, solve
    `(Xc^T Xc / n + alpha I) w = Xc^T yc / n`, then `b = mean(y) - mean(x) @ w`.
    Use `np.linalg.solve` for `alpha > 0`; for `alpha == 0` return the minimum-norm
    least-squares solution (`np.linalg.lstsq`), which stays finite when `x` is rank
    deficient. Never form an explicit inverse (`np.linalg.inv`).
    """
    raise NotImplementedError("TODO: implement ML-12")
