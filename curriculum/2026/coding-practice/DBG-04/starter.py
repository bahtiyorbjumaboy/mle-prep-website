import numpy as np

# Incident: the nightly softmax-classifier job reports `loss = nan` from the first logged
# step. This week the batch grew from 256 to 4096 rows and started to include missing
# embeddings (all-zero rows). The loss was recently changed to a batch mean "to make the
# learning rate batch-size independent".
#
# Canonical prompt: a training loss becomes NaN. Instrument the computation to identify the
# first non-finite tensor among unstable softmax, `log(0)`, zero-norm normalization, and an
# excessive learning rate. Fix the root cause and add regression tests.
# Follow-up: why can clipping mask rather than fix the problem?
#
# `train(..., trace=fn)` calls `fn(step, name, array)` for every intermediate, in order;
# use it to find the first non-finite value.


def l2_normalize(x: np.ndarray) -> np.ndarray:
    """Scales each row to unit L2 norm. An all-zero row (missing embedding) stays all-zero."""
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def softmax(logits: np.ndarray) -> np.ndarray:
    """Row-wise softmax of `(n, k)` logits; finite for any finite input."""
    e = np.exp(logits)
    return e / e.sum(axis=1, keepdims=True)


def cross_entropy(logits: np.ndarray, y: np.ndarray) -> float:
    """Mean of `-log softmax(logits)[i, y[i]]`, exact even for extreme logits."""
    probs = softmax(logits)
    return float(-np.mean(np.log(probs[np.arange(len(y)), y])))


def loss_and_grad(W: np.ndarray, x: np.ndarray, y: np.ndarray) -> tuple[float, np.ndarray]:
    """Returns `(loss, dloss/dW)` for logits `x @ W`; `loss` is `cross_entropy(x @ W, y)`."""
    logits = x @ W
    probs = softmax(logits)
    onehot = np.eye(W.shape[1])[y]
    grad = x.T @ (probs - onehot)
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
