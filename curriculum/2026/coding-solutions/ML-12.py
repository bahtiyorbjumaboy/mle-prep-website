import numpy as np


def _validate(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 2 or y.shape != (x.shape[0],):
        raise ValueError("expected x (n, d) and y (n,)")
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    return x, y


def ridge_loss(x: np.ndarray, y: np.ndarray, w: np.ndarray, b: float, alpha: float = 0.0) -> float:
    """mean squared error / 2 + alpha / 2 * ||w||^2 (intercept unpenalized)."""
    x, y = _validate(x, y, alpha)
    residual = x @ w + b - y
    return float(np.mean(residual ** 2) / 2 + 0.5 * alpha * w @ w)


def ridge_gradient(
    x: np.ndarray, y: np.ndarray, w: np.ndarray, b: float, alpha: float = 0.0
) -> tuple[np.ndarray, float]:
    """dJ/dw = X^T r / n + alpha w, dJ/db = mean(r)."""
    x, y = _validate(x, y, alpha)
    residual = x @ w + b - y
    return x.T @ residual / len(y) + alpha * w, float(residual.mean())


def fit_ridge_gd(
    x: np.ndarray, y: np.ndarray, alpha: float = 0.0, learning_rate: float = 0.1, steps: int = 1000
) -> tuple[np.ndarray, float, list[float]]:
    """Full-batch gradient descent from zeros."""
    x, y = _validate(x, y, alpha)
    w, b = np.zeros(x.shape[1]), 0.0
    history = []
    for _ in range(steps):
        grad_w, grad_b = ridge_gradient(x, y, w, b, alpha)
        w = w - learning_rate * grad_w
        b = b - learning_rate * grad_b
        history.append(ridge_loss(x, y, w, b, alpha))
    return w, b, history


def ridge_closed_form(x: np.ndarray, y: np.ndarray, alpha: float = 0.0) -> tuple[np.ndarray, float]:
    """Center to remove the intercept, then solve (never invert) the normal equations."""
    x, y = _validate(x, y, alpha)
    n, d = x.shape
    x_mean, y_mean = x.mean(axis=0), y.mean()
    xc, yc = x - x_mean, y - y_mean
    if alpha == 0:
        # lstsq works on Xc directly (SVD): min-norm for rank deficiency, and it avoids
        # squaring the condition number the way forming Xc^T Xc does.
        w = np.linalg.lstsq(xc, yc, rcond=None)[0]
    else:
        w = np.linalg.solve(xc.T @ xc / n + alpha * np.eye(d), xc.T @ yc / n)
    return w, float(y_mean - x_mean @ w)
