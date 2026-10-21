import numpy as np

# Canonical prompt: given parameter arrays and gradients, implement one optimizer step
# for vanilla SGD, momentum, RMSProp, Adam with bias correction, and AdamW-style
# decoupled weight decay. Keep optimizer state explicit.
#
# Contract for every function:
# - Pure: never modify `params`, `grads`, or the passed state; return new arrays and a
#   new state. A state of `None` means "first step" (all-zero buffers, t = 0).
# - Update equations (PyTorch conventions; g = grads, p = params, all elementwise):
#   SGD:       g' = g + weight_decay * p;  p <- p - lr * g'
#   Momentum:  v <- beta * v + g;  p <- p - lr * v              (no dampening, no Nesterov)
#   RMSProp:   s <- rho * s + (1 - rho) * g^2;  p <- p - lr * g / (sqrt(s) + eps)
#   Adam:      g' = g + weight_decay * p   (coupled L2: decay goes through the moments)
#              t <- t + 1;  m <- b1 m + (1 - b1) g';  v <- b2 v + (1 - b2) g'^2
#              m_hat = m / (1 - b1^t);  v_hat = v / (1 - b2^t)
#              p <- p - lr * m_hat / (sqrt(v_hat) + eps)        (eps OUTSIDE the sqrt)
#   AdamW:     same moments on the raw g (no decay in g), then
#              p <- p - lr * weight_decay * p - lr * m_hat / (sqrt(v_hat) + eps)
#              (decoupled: both terms use the pre-step p)
# - Adam/AdamW state is a dict `{"m": array, "v": array, "t": int}`.
# - Raise ValueError when grads (or state buffers) do not match the params' shape.


def sgd_step(params: np.ndarray, grads: np.ndarray, lr: float, weight_decay: float = 0.0) -> np.ndarray:
    """Returns the new params."""
    raise NotImplementedError("TODO: implement ML-16")


def momentum_step(
    params: np.ndarray, grads: np.ndarray, velocity: np.ndarray | None, lr: float, beta: float = 0.9
) -> tuple[np.ndarray, np.ndarray]:
    """Returns `(new_params, new_velocity)`."""
    raise NotImplementedError("TODO: implement ML-16")


def rmsprop_step(
    params: np.ndarray, grads: np.ndarray, sq_avg: np.ndarray | None, lr: float, rho: float = 0.9, eps: float = 1e-8
) -> tuple[np.ndarray, np.ndarray]:
    """Returns `(new_params, new_sq_avg)`."""
    raise NotImplementedError("TODO: implement ML-16")


def adam_step(
    params: np.ndarray,
    grads: np.ndarray,
    state: dict | None,
    lr: float = 1e-3,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    weight_decay: float = 0.0,
) -> tuple[np.ndarray, dict]:
    """Returns `(new_params, new_state)`; `weight_decay` is coupled L2."""
    raise NotImplementedError("TODO: implement ML-16")


def adamw_step(
    params: np.ndarray,
    grads: np.ndarray,
    state: dict | None,
    lr: float = 1e-3,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    weight_decay: float = 1e-2,
) -> tuple[np.ndarray, dict]:
    """Returns `(new_params, new_state)`; `weight_decay` is decoupled."""
    raise NotImplementedError("TODO: implement ML-16")
