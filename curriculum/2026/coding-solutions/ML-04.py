import numpy as np

REDUCTIONS = ("none", "mean", "sum")


def _reduce(losses: np.ndarray, reduction: str) -> np.ndarray | float:
    if reduction == "none":
        return losses
    return float(losses.mean() if reduction == "mean" else losses.sum())


def logsumexp(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """max + log(sum(exp(x - max))): every exponent is <= 0, so nothing overflows."""
    x = np.asarray(x, dtype=float)
    m = np.max(x, axis=axis, keepdims=True)
    out = m + np.log(np.sum(np.exp(x - m), axis=axis, keepdims=True))
    return np.squeeze(out, axis=axis)


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """exp(x - logsumexp(x)) along axis."""
    x = np.asarray(x, dtype=float)
    return np.exp(x - np.expand_dims(logsumexp(x, axis=axis), axis))


def cross_entropy(logits: np.ndarray, targets: np.ndarray, reduction: str = "mean") -> np.ndarray | float:
    """Fused log-softmax + NLL: logsumexp(z_i) - z_i[y_i]."""
    logits = np.asarray(logits, dtype=float)
    targets = np.asarray(targets)
    if logits.ndim != 2 or targets.shape != (logits.shape[0],):
        raise ValueError("expected logits (B, C) and targets (B,)")
    if np.any((targets < 0) | (targets >= logits.shape[1])):
        raise ValueError("targets must lie in [0, C)")
    if reduction not in REDUCTIONS:
        raise ValueError(f"reduction must be one of {REDUCTIONS}")
    # Row-wise gather: logits[i, targets[i]], not logits[:, targets].
    picked = logits[np.arange(len(targets)), targets]
    return _reduce(logsumexp(logits, axis=1) - picked, reduction)


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Uses e = exp(-|x|) <= 1 in both branches, so neither np.where branch can overflow."""
    x = np.asarray(x, dtype=float)
    e = np.exp(-np.abs(x))
    return np.where(x >= 0, 1.0 / (1.0 + e), e / (1.0 + e))


def bce_with_logits(logits: np.ndarray, targets: np.ndarray, reduction: str = "mean") -> np.ndarray | float:
    """max(z, 0) - z*y + log1p(exp(-|z|)): the log-sigmoid identities, never log(sigmoid)."""
    z = np.asarray(logits, dtype=float)
    y = np.asarray(targets, dtype=float)
    if z.shape != y.shape:
        raise ValueError("logits and targets must have the same shape")
    if np.any((y < 0) | (y > 1)):
        raise ValueError("targets must lie in [0, 1]")
    if reduction not in REDUCTIONS:
        raise ValueError(f"reduction must be one of {REDUCTIONS}")
    losses = np.maximum(z, 0.0) - z * y + np.log1p(np.exp(-np.abs(z)))
    return _reduce(losses, reduction)


def naive_failure_examples() -> dict[str, np.ndarray]:
    """exp(1000) = inf, so inf / inf = NaN in both naive formulas."""
    return {"softmax": np.array([[1000.0, 999.0, 0.0]]), "sigmoid": np.array([-5.0, 1000.0])}
