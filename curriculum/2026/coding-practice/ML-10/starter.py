import numpy as np

# Canonical prompt: implement entropy and Gini impurity from either class labels or
# class probabilities. Then compute weighted child impurity and information gain for a
# proposed binary split.
#
# Shared contract:
# - Pass exactly one of `labels` (1-D class labels of any hashable kind: ints,
#   negative ints, strings) or `probs` (1-D non-negative, summing to 1 within 1e-9).
#   Anything else raises ValueError, as do empty labels.
# - Optional `weights` (only with `labels`): non-negative per-sample weights with a
#   positive total; class probabilities become weighted class shares. A weight of 2
#   must behave exactly like duplicating the sample.
# - `0 * log(0) = 0`: zero-probability classes contribute nothing (never NaN).
# - Entropy uses log base `base` (2 -> bits, `np.e` -> nats).


def entropy(
    labels: np.ndarray | None = None,
    probs: np.ndarray | None = None,
    weights: np.ndarray | None = None,
    base: float = 2.0,
) -> float:
    """`H = -sum_k p_k log_base(p_k)`."""
    raise NotImplementedError("TODO: implement ML-10")


def gini(
    labels: np.ndarray | None = None,
    probs: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> float:
    """`G = 1 - sum_k p_k^2`."""
    raise NotImplementedError("TODO: implement ML-10")


def weighted_child_impurity(
    labels: np.ndarray,
    left_mask: np.ndarray,
    criterion: str = "entropy",
    weights: np.ndarray | None = None,
    base: float = 2.0,
) -> float:
    """`(W_L / W) * I(left) + (W_R / W) * I(right)` for a binary split.

    `W_L`, `W_R` are the children's total sample weights (row counts when `weights`
    is None) and `I` is `"entropy"` or `"gini"`.

    Raises:
        ValueError: if a child is empty (no rows or zero total weight), the mask is
            not boolean with the same length as `labels`, or the criterion is unknown.
    """
    raise NotImplementedError("TODO: implement ML-10")


def information_gain(
    labels: np.ndarray,
    left_mask: np.ndarray,
    criterion: str = "entropy",
    weights: np.ndarray | None = None,
    base: float = 2.0,
) -> float:
    """`I(parent) - weighted_child_impurity(...)` (same validation)."""
    raise NotImplementedError("TODO: implement ML-10")
