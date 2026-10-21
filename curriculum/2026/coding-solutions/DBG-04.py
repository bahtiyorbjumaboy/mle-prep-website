import numpy as np

# Repair of the DBG-04 starter. Tracing the first non-finite value walks the failure chain:
# 1. `inputs` at step 0: all-zero rows give 0/0 = NaN in `l2_normalize`. Fix: divide by
#    `max(norm, tiny)`, so zero rows stay exactly zero and nothing divides by zero.
# 2. With finite inputs, `W` explodes: the loss is a batch *mean* but the gradient was the
#    batch *sum*, so every step was `n` times larger than `lr` says (an excessive effective
#    learning rate). Fix: divide the gradient by the batch size; it then matches the loss.
# 3. Large logits overflow `exp` (inf / inf = NaN). Fix: subtract the row max first.
# 4. `log(softmax)` hits `log(0)` once a probability underflows. Fix: compute log-softmax
#    directly (shifted logits minus logsumexp); clipping probabilities would cap the loss
#    at about 27.6 instead of reporting the true value.


def l2_normalize(x: np.ndarray) -> np.ndarray:
    """Scales each row to unit L2 norm. An all-zero row (missing embedding) stays all-zero."""
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(norms, np.finfo(x.dtype).tiny)


def log_softmax(logits: np.ndarray) -> np.ndarray:
    """Row-wise log-softmax via the max-shifted logsumexp."""
    shifted = logits - logits.max(axis=1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))


def softmax(logits: np.ndarray) -> np.ndarray:
    """Row-wise softmax of `(n, k)` logits; finite for any finite input."""
    return np.exp(log_softmax(logits))


def cross_entropy(logits: np.ndarray, y: np.ndarray) -> float:
    """Mean of `-log softmax(logits)[i, y[i]]`, exact even for extreme logits."""
    return float(-np.mean(log_softmax(logits)[np.arange(len(y)), y]))


def loss_and_grad(W: np.ndarray, x: np.ndarray, y: np.ndarray) -> tuple[float, np.ndarray]:
    """Returns `(loss, dloss/dW)` for logits `x @ W`; `loss` is `cross_entropy(x @ W, y)`."""
    logits = x @ W
    probs = softmax(logits)
    onehot = np.eye(W.shape[1])[y]
    grad = x.T @ (probs - onehot) / len(y)
    return cross_entropy(logits, y), grad


def train(
    x: np.ndarray,
    y: np.ndarray,
    n_classes: int,
    lr: float = 0.5,
    steps: int = 100,
    seed: int = 0,
    trace=None,
) -> tuple[np.ndarray, list[float]]:
    """Full-batch gradient descent on L2-normalized inputs.

    Contract: no step produces an IEEE overflow, divide-by-zero, or invalid operation (the
    tests run under `np.errstate(over="raise", divide="raise", invalid="raise")`), and with
    the documented default `lr` the training loss never increases.

    Returns:
        `(W, losses)`: final `(d, n_classes)` weights and the loss before each update.
    """
    rng = np.random.default_rng(seed)
    W = rng.normal(0.0, 0.01, size=(x.shape[1], n_classes))
    inputs = l2_normalize(x)
    losses = []
    for step in range(steps):
        if trace is not None:
            trace(step, "inputs", inputs)
            trace(step, "logits", inputs @ W)
        loss, grad = loss_and_grad(W, inputs, y)
        W = W - lr * grad
        if trace is not None:
            trace(step, "loss", np.array(loss))
            trace(step, "grad", grad)
            trace(step, "W", W)
        losses.append(loss)
    return W, losses
