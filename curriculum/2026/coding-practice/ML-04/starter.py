import numpy as np

# Canonical prompt: implement `softmax`, `logsumexp`, multiclass cross-entropy from
# logits, BCE-with-logits, and a stable sigmoid. Demonstrate inputs that break naive
# implementations.
#
# Stability contract for every function: inputs as extreme as +/-1e4 must produce
# correct finite results without any floating-point overflow or invalid operation,
# including in intermediate arrays and in the unused branch of `np.where` (tests run
# under `np.errstate(over="raise", invalid="raise", divide="raise")`; underflow to 0
# is fine). Inputs are never modified; outputs are float64.


def logsumexp(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """`log(sum(exp(x), axis))` computed stably; the reduced axis is removed.

    Entries equal to `-inf` (masked logits) contribute 0 as long as each slice has at
    least one finite entry.
    """
    raise NotImplementedError("TODO: implement ML-04")


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Stable softmax along `axis`; same shape as `x`; slices sum to 1."""
    raise NotImplementedError("TODO: implement ML-04")


def cross_entropy(logits: np.ndarray, targets: np.ndarray, reduction: str = "mean") -> np.ndarray | float:
    """Multiclass cross-entropy from raw logits `(B, C)` and integer targets `(B,)`.

    `loss_i = logsumexp(logits_i) - logits_i[targets_i]` (fused: never `log(softmax)`).
    `reduction`: `"none"` -> `(B,)` array, `"mean"` / `"sum"` -> float.

    Raises:
        ValueError: on shape mismatch, targets outside `[0, C)`, or unknown reduction.
    """
    raise NotImplementedError("TODO: implement ML-04")


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Elementwise logistic function, stable for +/-1e4 (see the stability contract)."""
    raise NotImplementedError("TODO: implement ML-04")


def bce_with_logits(logits: np.ndarray, targets: np.ndarray, reduction: str = "mean") -> np.ndarray | float:
    """Binary cross-entropy from logits; targets in [0, 1] (soft labels allowed).

    `loss = -(y * log(sigmoid(z)) + (1 - y) * log(1 - sigmoid(z)))`, computed without
    ever forming `sigmoid(z)` then taking its log. Same `reduction` rules as above.

    Raises:
        ValueError: on shape mismatch, targets outside [0, 1], or unknown reduction.
    """
    raise NotImplementedError("TODO: implement ML-04")


def naive_failure_examples() -> dict[str, np.ndarray]:
    """Demonstrate inputs that break naive implementations.

    Return `{"softmax": logits_2d, "sigmoid": x_1d}` where:
    - `np.exp(l) / np.exp(l).sum(axis=1, keepdims=True)` yields NaN for some row of
      `logits_2d`, while your `softmax` is finite there;
    - `np.exp(x) / (1 + np.exp(x))` yields NaN for some entry of `x_1d`, while your
      `sigmoid` is finite there.
    """
    raise NotImplementedError("TODO: implement ML-04")
