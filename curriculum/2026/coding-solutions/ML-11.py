import numpy as np

TIE_TOL = 1e-12


def _class_impurity(mass: np.ndarray, criterion: str) -> np.ndarray:
    """Impurity from per-class weight rows: mass has shape (..., C)."""
    total = mass.sum(axis=-1, keepdims=True)
    p = np.divide(mass, total, out=np.zeros_like(mass), where=total > 0)
    if criterion == "gini":
        return 1.0 - np.sum(p * p, axis=-1)
    logp = np.log2(p, out=np.zeros_like(p), where=p > 0)  # 0 log 0 = 0
    return -np.sum(p * logp, axis=-1)


def _leaf(y: np.ndarray, w: np.ndarray, task: str, classes: np.ndarray | None) -> object:
    if task == "regression":
        return float(np.sum(w * y) / w.sum())
    mass = np.array([w[y == c].sum() for c in classes])
    return classes[int(np.argmax(mass))].item()  # argmax -> first max -> smallest label


def best_split(
    x: np.ndarray,
    y: np.ndarray,
    task: str = "classification",
    criterion: str = "gini",
    min_samples_leaf: int = 1,
    sample_weight: np.ndarray | None = None,
) -> dict[str, object] | None:
    """Sort each feature once and sweep cumulative statistics over midpoint thresholds."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y)
    if task not in ("classification", "regression"):
        raise ValueError("task must be 'classification' or 'regression'")
    if criterion not in ("gini", "entropy"):
        raise ValueError("criterion must be 'gini' or 'entropy'")
    if x.ndim != 2 or y.shape != (x.shape[0],):
        raise ValueError("expected x (n, d) and y (n,)")
    if np.isnan(x).any():
        raise ValueError("missing values are not supported")
    if min_samples_leaf < 1:
        raise ValueError("min_samples_leaf must be >= 1")
    n, d = x.shape
    w = np.ones(n) if sample_weight is None else np.asarray(sample_weight, dtype=float)
    if w.shape != (n,) or np.any(w < 0):
        raise ValueError("sample_weight must be (n,) and non-negative")

    if task == "classification":
        classes, codes = np.unique(y, return_inverse=True)
        stats = np.zeros((n, len(classes)))
        stats[np.arange(n), codes.ravel()] = w  # per-row class mass
        parent = _class_impurity(stats.sum(axis=0), criterion)
    else:
        classes = None
        yf = y.astype(float)
        yf = yf - np.sum(w * yf) / w.sum()  # shift-invariant SSE; centering avoids cancellation
        stats = np.column_stack([w, w * yf, w * yf * yf])  # (weight, sum wy, sum wy^2)
        total_w = w.sum()
        parent = stats[:, 2].sum() / total_w - (stats[:, 1].sum() / total_w) ** 2

    best = None  # (gain, feature, threshold)
    for f in range(d):  # O(n log n) per feature
        order = np.argsort(x[:, f], kind="stable")
        xs = x[order, f]
        left = np.cumsum(stats[order], axis=0)[:-1]  # left stats when splitting after row i
        right = stats.sum(axis=0) - left
        n_left = np.arange(1, n)
        valid = (xs[:-1] < xs[1:]) & (n_left >= min_samples_leaf) & (n - n_left >= min_samples_leaf)
        if not valid.any():
            continue
        if task == "classification":
            w_left, w_right = left.sum(axis=1), right.sum(axis=1)
            child = (w_left * _class_impurity(left, criterion) + w_right * _class_impurity(right, criterion))
        else:
            w_left, w_right = left[:, 0], right[:, 0]
            # weighted SSE = sum wy^2 - (sum wy)^2 / sum w, per side
            sse_left = left[:, 2] - np.divide(left[:, 1] ** 2, w_left, out=np.zeros(n - 1), where=w_left > 0)
            sse_right = right[:, 2] - np.divide(right[:, 1] ** 2, w_right, out=np.zeros(n - 1), where=w_right > 0)
            child = sse_left + sse_right
        gains = parent - child / (w_left + w_right)
        gains[~valid] = -np.inf
        i = int(np.argmax(gains))  # first max -> smallest threshold within this feature
        if best is None or gains[i] > best[0] + TIE_TOL:
            best = (float(gains[i]), f, float((xs[i] + xs[i + 1]) / 2))

    if best is None or best[0] <= TIE_TOL:
        return None
    gain, f, threshold = best
    go_left = x[:, f] <= threshold
    return {
        "feature": f,
        "threshold": threshold,
        "gain": gain,
        "left_prediction": _leaf(y[go_left], w[go_left], task, classes),
        "right_prediction": _leaf(y[~go_left], w[~go_left], task, classes),
    }
