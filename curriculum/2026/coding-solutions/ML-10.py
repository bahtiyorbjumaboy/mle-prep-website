import numpy as np


def _class_probs(
    labels: np.ndarray | None, probs: np.ndarray | None, weights: np.ndarray | None
) -> np.ndarray:
    """Empirical (optionally weighted) class shares, or validated given probabilities."""
    if (labels is None) == (probs is None):
        raise ValueError("pass exactly one of labels or probs")
    if probs is not None:
        p = np.asarray(probs, dtype=float)
        if p.ndim != 1 or np.any(p < 0) or abs(p.sum() - 1.0) > 1e-9:
            raise ValueError("probs must be non-negative and sum to 1")
        return p
    labels = np.asarray(labels)
    if labels.ndim != 1 or labels.size == 0:
        raise ValueError("labels must be a non-empty 1-D array")
    w = np.ones(len(labels)) if weights is None else np.asarray(weights, dtype=float)
    if w.shape != labels.shape or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("weights must be non-negative with a positive total")
    # np.unique handles strings and negative/large ints; bincount on raw labels would not.
    _, codes = np.unique(labels, return_inverse=True)
    mass = np.bincount(codes.ravel(), weights=w)
    return mass / mass.sum()


def entropy(
    labels: np.ndarray | None = None,
    probs: np.ndarray | None = None,
    weights: np.ndarray | None = None,
    base: float = 2.0,
) -> float:
    """Shannon entropy with 0 log 0 = 0."""
    p = _class_probs(labels, probs, weights)
    p = p[p > 0]  # drop zero classes before the log, so no log(0) is ever evaluated
    return float(max(0.0, -np.sum(p * np.log(p)) / np.log(base)))


def gini(
    labels: np.ndarray | None = None,
    probs: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> float:
    """Gini impurity 1 - sum p^2."""
    p = _class_probs(labels, probs, weights)
    return float(max(0.0, 1.0 - np.sum(p * p)))


def _impurity(labels: np.ndarray, weights: np.ndarray | None, criterion: str, base: float) -> float:
    if criterion == "entropy":
        return entropy(labels=labels, weights=weights, base=base)
    if criterion == "gini":
        return gini(labels=labels, weights=weights)
    raise ValueError("criterion must be 'entropy' or 'gini'")


def weighted_child_impurity(
    labels: np.ndarray,
    left_mask: np.ndarray,
    criterion: str = "entropy",
    weights: np.ndarray | None = None,
    base: float = 2.0,
) -> float:
    """Children's impurities weighted by their share of the parent's sample weight."""
    labels = np.asarray(labels)
    mask = np.asarray(left_mask)
    if mask.dtype != np.bool_ or mask.shape != labels.shape:
        raise ValueError("left_mask must be a boolean array aligned with labels")
    w = np.ones(len(labels)) if weights is None else np.asarray(weights, dtype=float)
    w_left, w_right = w[mask].sum(), w[~mask].sum()
    if w_left <= 0 or w_right <= 0:
        raise ValueError("both children must be non-empty")
    child_w = None if weights is None else w
    left = _impurity(labels[mask], None if child_w is None else child_w[mask], criterion, base)
    right = _impurity(labels[~mask], None if child_w is None else child_w[~mask], criterion, base)
    total = w_left + w_right
    return float(w_left / total * left + w_right / total * right)


def information_gain(
    labels: np.ndarray,
    left_mask: np.ndarray,
    criterion: str = "entropy",
    weights: np.ndarray | None = None,
    base: float = 2.0,
) -> float:
    """Parent impurity minus mass-weighted child impurity."""
    children = weighted_child_impurity(labels, left_mask, criterion, weights, base)
    return float(_impurity(np.asarray(labels), weights, criterion, base) - children)
