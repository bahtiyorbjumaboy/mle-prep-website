import numpy as np


def _arrays(params: np.ndarray, grads: np.ndarray, *buffers: np.ndarray | None) -> tuple[np.ndarray, ...]:
    """Float copies of params/grads, plus zero-initialized (or copied) state buffers."""
    p = np.array(params, dtype=float)
    g = np.asarray(grads, dtype=float)
    if g.shape != p.shape:
        raise ValueError("grads must match params' shape")
    out = [p, g]
    for buf in buffers:
        b = np.zeros_like(p) if buf is None else np.asarray(buf, dtype=float)
        if b.shape != p.shape:
            raise ValueError("optimizer state must match params' shape")
        out.append(b)
    return tuple(out)


def sgd_step(params: np.ndarray, grads: np.ndarray, lr: float, weight_decay: float = 0.0) -> np.ndarray:
    p, g = _arrays(params, grads)
    return p - lr * (g + weight_decay * p)


def momentum_step(
    params: np.ndarray, grads: np.ndarray, velocity: np.ndarray | None, lr: float, beta: float = 0.9
) -> tuple[np.ndarray, np.ndarray]:
    p, g, v = _arrays(params, grads, velocity)
    v = beta * v + g  # new array: the caller's velocity is untouched
    return p - lr * v, v


def rmsprop_step(
    params: np.ndarray, grads: np.ndarray, sq_avg: np.ndarray | None, lr: float, rho: float = 0.9, eps: float = 1e-8
) -> tuple[np.ndarray, np.ndarray]:
    p, g, s = _arrays(params, grads, sq_avg)
    s = rho * s + (1 - rho) * g * g
    return p - lr * g / (np.sqrt(s) + eps), s


def _adam_moments(
    g: np.ndarray, state: dict | None, p: np.ndarray, beta1: float, beta2: float
) -> tuple[np.ndarray, np.ndarray, int, np.ndarray, np.ndarray]:
    m_prev = None if state is None else state["m"]
    v_prev = None if state is None else state["v"]
    _, _, m, v = _arrays(p, g, m_prev, v_prev)
    t = (0 if state is None else state["t"]) + 1
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * g * g
    # Bias correction: at t=1, m_hat = g and v_hat = g^2, so the first step is lr * sign(g).
    return m, v, t, m / (1 - beta1 ** t), v / (1 - beta2 ** t)


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
    p, g = _arrays(params, grads)
    g = g + weight_decay * p  # coupled L2: the decay is rescaled by the adaptive denominator
    m, v, t, m_hat, v_hat = _adam_moments(g, state, p, beta1, beta2)
    return p - lr * m_hat / (np.sqrt(v_hat) + eps), {"m": m, "v": v, "t": t}


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
    p, g = _arrays(params, grads)
    m, v, t, m_hat, v_hat = _adam_moments(g, state, p, beta1, beta2)
    # Decoupled: shrink the weights directly, outside the adaptive update.
    return p - lr * weight_decay * p - lr * m_hat / (np.sqrt(v_hat) + eps), {"m": m, "v": v, "t": t}
