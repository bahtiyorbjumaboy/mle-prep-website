import numpy as np


def confusion_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    num_classes: int,
) -> tuple[np.ndarray, dict[str, np.ndarray | float]]:
    """Vectorized multiclass confusion matrix and precision/recall/F1.

    Canonical prompt: given integer `y_true` and `y_pred` over `C` classes, build the
    `(C,C)` confusion matrix without a Python loop and compute per-class
    precision/recall/F1 plus micro/macro F1.

    Contract (no Python loops over samples or classes):
    - `cm[i, j]` counts samples with true class `i` predicted as class `j`
      (rows = truth, columns = prediction); integer dtype, shape `(C, C)`.
    - Any 0/0 ratio is defined as 0.0 (never NaN), including F1 when P + R == 0.
    - `macro_f1` is the unweighted mean of per-class F1 over all `C` classes, including
      classes that never occur. `micro_f1` pools TP/FP/FN over classes.

    Args:
        y_true: 1-D integer labels in `[0, C)`; lists are accepted.
        y_pred: 1-D integer predictions in `[0, C)`, same length as `y_true`.
        num_classes: `C >= 1`.

    Returns:
        `(cm, metrics)` where `metrics` has float64 arrays `"precision"`, `"recall"`,
        `"f1"` of shape `(C,)` and Python/NumPy floats `"micro_f1"`, `"macro_f1"`.

    Raises:
        ValueError: on length mismatch, non-1-D input, or labels outside `[0, C)`.
    """
    raise NotImplementedError("TODO: implement NP-03")
