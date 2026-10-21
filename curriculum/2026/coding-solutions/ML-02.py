import numpy as np


def _validate(y_true: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(y_true)
    s = np.asarray(scores, dtype=float)
    if y.ndim != 1 or s.shape != y.shape or y.size == 0:
        raise ValueError("y_true and scores must be non-empty 1-D arrays of equal length")
    if not np.all((y == 0) | (y == 1)):
        raise ValueError("labels must be 0/1")
    return y.astype(np.intp), s


def roc_auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Mann-Whitney AUC from average ranks; ties get the mean of their ranks (count 1/2)."""
    y, s = _validate(y_true, scores)
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    # Tie groups in ascending score order; a group occupying ranks a+1..a+c has mean rank a + (c+1)/2.
    _, group, counts = np.unique(s, return_inverse=True, return_counts=True)
    ranks_before = np.cumsum(counts) - counts
    avg_rank = ranks_before + (counts + 1) / 2.0
    pos_rank_sum = avg_rank[group][y == 1].sum()
    return float((pos_rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def average_precision(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Step-sum AP over distinct thresholds (descending); tied items enter together."""
    y, s = _validate(y_true, scores)
    n_pos = int(y.sum())
    if n_pos == 0:
        return float("nan")
    # Unique of -s sorts thresholds from highest score to lowest.
    _, group, counts = np.unique(-s, return_inverse=True, return_counts=True)
    tp = np.cumsum(np.bincount(group, weights=y))  # positives predicted at each threshold
    predicted = np.cumsum(counts)  # items predicted at each threshold
    precision = tp / predicted
    recall = tp / n_pos
    return float(np.sum(np.diff(recall, prepend=0.0) * precision))


def binary_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> dict[str, object]:
    """Threshold metrics (score >= threshold is positive) plus ROC-AUC and AP."""
    y, s = _validate(y_true, scores)
    pred = (s >= threshold).astype(np.intp)
    tp = int(np.sum((pred == 1) & (y == 1)))
    fp = int(np.sum((pred == 1) & (y == 0)))
    fn = int(np.sum((pred == 0) & (y == 1)))
    tn = len(y) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "confusion_matrix": np.array([[tn, fp], [fn, tp]]),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc(y, s),
        "average_precision": average_precision(y, s),
    }
