import numpy as np


def _safe_div(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    """Elementwise num / den with 0/0 (and x/0) defined as 0.0."""
    num = np.asarray(num, dtype=float)
    return np.divide(num, den, out=np.zeros_like(num), where=den > 0)


def confusion_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    num_classes: int,
) -> tuple[np.ndarray, dict[str, np.ndarray | float]]:
    """Confusion matrix (rows truth, columns prediction) plus per-class and micro/macro F1."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.ndim != 1 or y_pred.shape != y_true.shape:
        raise ValueError("y_true and y_pred must be 1-D with equal length")
    c = int(num_classes)
    labels = np.concatenate([y_true, y_pred])
    if labels.size and (labels.min() < 0 or labels.max() >= c):
        raise ValueError("labels must lie in [0, num_classes)")

    # Encode each (truth, prediction) pair as one flat cell id, then count all cells at once.
    cm = np.bincount(y_true.astype(np.int64) * c + y_pred, minlength=c * c).reshape(c, c)

    tp = np.diag(cm)
    predicted = cm.sum(axis=0)  # column sums: TP + FP
    actual = cm.sum(axis=1)  # row sums: TP + FN
    precision = _safe_div(tp, predicted)
    recall = _safe_div(tp, actual)
    f1 = _safe_div(2 * tp, predicted + actual)  # == 2PR / (P + R), with 0/0 -> 0

    total_tp = tp.sum()
    # Single-label: pooled FP == pooled FN == n - TP, so micro P == micro R == micro F1.
    micro_f1 = float(_safe_div(2 * total_tp, predicted.sum() + actual.sum()))
    metrics = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "micro_f1": micro_f1,
        "macro_f1": float(f1.mean()),
    }
    return cm, metrics
