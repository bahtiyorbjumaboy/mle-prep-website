import numpy as np


def roc_auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Area under the ROC curve with correct tie handling.

    Equals P(score of a random positive > score of a random negative), where a tied
    pair counts 1/2 (equivalently: trapezoids over the ROC curve whose thresholds are
    the distinct score values). Return NaN when there are no positives or no
    negatives. O(n log n): no O(n_pos * n_neg) pair enumeration.
    """
    raise NotImplementedError("TODO: implement ML-02")


def average_precision(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Average precision: `AP = sum_i (R_i - R_{i-1}) * P_i`.

    The sum runs over the distinct score values in descending order; threshold `i`
    predicts positive for every score `>= s_i`, so all items tied at `s_i` enter
    together. This is a step sum, not trapezoidal interpolation of the PR curve.
    `R_0 = 0`. Return NaN when there are no positives. O(n log n).
    """
    raise NotImplementedError("TODO: implement ML-02")


def binary_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> dict[str, object]:
    """Canonical prompt: given binary labels and scores, implement confusion matrix,
    precision, recall, F1, ROC-AUC, and average precision/PR-AUC without sklearn.
    Handle tied scores correctly.

    Args:
        y_true: 1-D labels in {0, 1} (bools allowed).
        scores: 1-D real scores, same length, at least one element.
        threshold: predict positive iff `score >= threshold`.

    Returns:
        A dict with:
        - `"confusion_matrix"`: int array `[[TN, FP], [FN, TP]]` (rows = truth 0/1,
          columns = prediction 0/1);
        - `"precision"`, `"recall"`, `"f1"`: floats; any 0/0 is 0.0;
        - `"roc_auc"`: `roc_auc(y_true, scores)`;
        - `"average_precision"`: `average_precision(y_true, scores)`.

    Raises:
        ValueError: on labels outside {0, 1}, length mismatch, empty or non-1-D input.
    """
    raise NotImplementedError("TODO: implement ML-02")
