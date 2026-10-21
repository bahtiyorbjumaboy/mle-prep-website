from collections.abc import Callable

import numpy as np


def init_params(d_in: int, d_hidden: int, n_classes: int, seed: int = 0) -> dict[str, np.ndarray]:
    """N(0, 1/fan_in) weights, zero biases, one seeded generator."""
    rng = np.random.default_rng(seed)
    return {
        "W1": rng.normal(size=(d_in, d_hidden)) / np.sqrt(d_in),
        "b1": np.zeros(d_hidden),
        "W2": rng.normal(size=(d_hidden, n_classes)) / np.sqrt(d_hidden),
        "b2": np.zeros(n_classes),
    }


def forward_backward(
    params: dict[str, np.ndarray], x: np.ndarray, y: np.ndarray
) -> tuple[float, dict[str, np.ndarray]]:
    """tanh MLP with fused log-softmax cross-entropy; manual backprop from cached activations."""
    w1, b1, w2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]
    x = np.asarray(x, dtype=float)
    y = np.asarray(y)
    if x.ndim != 2 or x.shape[1] != w1.shape[0] or y.shape != (x.shape[0],):
        raise ValueError("expected x (B, D) matching W1 and y (B,)")
    n_classes = w2.shape[1]
    if np.any((y < 0) | (y >= n_classes)):
        raise ValueError("labels must lie in [0, C)")
    batch = len(y)
    rows = np.arange(batch)

    # Forward, caching what backward needs.
    h = np.tanh(x @ w1 + b1)  # (B, H)
    logits = h @ w2 + b2  # (B, C)
    shifted = logits - logits.max(axis=1, keepdims=True)
    log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))  # stable log-softmax
    loss = float(-log_probs[rows, y].mean())

    # Backward: dL/dlogits = (softmax - onehot) / B for the mean loss.
    dlogits = np.exp(log_probs)
    dlogits[rows, y] -= 1.0
    dlogits /= batch
    dh = dlogits @ w2.T  # (B, H)
    dz1 = dh * (1.0 - h * h)  # tanh'(z) = 1 - tanh(z)^2
    grads = {"W1": x.T @ dz1, "b1": dz1.sum(axis=0), "W2": h.T @ dlogits, "b2": dlogits.sum(axis=0)}
    return loss, grads


def numerical_gradient(f: Callable[[], float], array: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Centered differences, perturbing one entry at a time and restoring it exactly."""
    grad = np.zeros_like(array, dtype=float)
    for idx in np.ndindex(array.shape):  # intentionally O(#entries) loss evaluations
        original = array[idx]
        array[idx] = original + eps
        plus = f()
        array[idx] = original - eps
        minus = f()
        array[idx] = original  # restore the saved value, not original + eps - eps
        grad[idx] = (plus - minus) / (2.0 * eps)
    return grad


def relative_error(analytic: np.ndarray, numeric: np.ndarray) -> float:
    analytic = np.asarray(analytic, dtype=float)
    numeric = np.asarray(numeric, dtype=float)
    denom = np.maximum(np.abs(analytic) + np.abs(numeric), 1e-8)
    return float(np.max(np.abs(analytic - numeric) / denom)) if analytic.size else 0.0


def gradient_check(
    loss_and_grads: Callable[[dict[str, np.ndarray]], tuple[float, dict[str, np.ndarray]]],
    params: dict[str, np.ndarray],
    eps: float = 1e-5,
) -> dict[str, float]:
    """Per-parameter max relative error between analytic and centered numeric gradients."""
    _, analytic = loss_and_grads(params)
    errors = {}
    for name, array in params.items():
        numeric = numerical_gradient(lambda: loss_and_grads(params)[0], array, eps)
        errors[name] = relative_error(analytic[name], numeric)
    return errors
