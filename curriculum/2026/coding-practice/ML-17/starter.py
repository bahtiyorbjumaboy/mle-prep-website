from collections.abc import Callable

import numpy as np

# Canonical prompt: implement forward and backward passes for a tiny two-layer NumPy
# network and verify selected analytic gradients with centered finite differences.
# Include a stable loss.
#
# Network (B examples, D inputs, H hidden units, C classes):
#   z1 = x @ W1 + b1        x: (B, D), W1: (D, H), b1: (H,)
#   h  = tanh(z1)           (smooth, so finite differences are well behaved)
#   logits = h @ W2 + b2    W2: (H, C), b2: (C,)
#   loss = mean_i [logsumexp(logits_i) - logits_i[y_i]]     (stable cross-entropy)
# Params are a dict with keys "W1", "b1", "W2", "b2".


def init_params(d_in: int, d_hidden: int, n_classes: int, seed: int = 0) -> dict[str, np.ndarray]:
    """Weights ~ N(0, 1 / fan_in) from `np.random.default_rng(seed)` (W1 drawn before W2);
    biases zero. Same seed -> identical params."""
    raise NotImplementedError("TODO: implement ML-17")


def forward_backward(
    params: dict[str, np.ndarray], x: np.ndarray, y: np.ndarray
) -> tuple[float, dict[str, np.ndarray]]:
    """Return `(loss, grads)` where `grads[k]` has the shape of `params[k]`.

    Cache the forward intermediates and apply the chain rule (no numerical shortcuts).
    The loss must stay finite for logits around +/-1e4.

    Raises:
        ValueError: on shape mismatches or labels outside `[0, C)`.
    """
    raise NotImplementedError("TODO: implement ML-17")


def numerical_gradient(f: Callable[[], float], array: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Centered finite differences of `f()` with respect to every entry of `array`.

    `f` takes no arguments and reads `array`, so perturb entries in place one at a
    time: `(f(a + eps) - f(a - eps)) / (2 * eps)`. Restore each entry afterwards so
    `array` ends bit-for-bit identical. Works for arrays of any shape.
    """
    raise NotImplementedError("TODO: implement ML-17")


def relative_error(analytic: np.ndarray, numeric: np.ndarray) -> float:
    """`max_i |a_i - n_i| / max(|a_i| + |n_i|, 1e-8)` (0.0 when both are zero)."""
    raise NotImplementedError("TODO: implement ML-17")


def gradient_check(
    loss_and_grads: Callable[[dict[str, np.ndarray]], tuple[float, dict[str, np.ndarray]]],
    params: dict[str, np.ndarray],
    eps: float = 1e-5,
) -> dict[str, float]:
    """For every parameter name, the relative error between the analytic gradient from
    `loss_and_grads(params)` and `numerical_gradient` of its loss. `params` must be
    unchanged afterwards. A correct implementation scores < 1e-6 on smooth fixtures;
    a sign error or a missing chain-rule factor must score far higher."""
    raise NotImplementedError("TODO: implement ML-17")
