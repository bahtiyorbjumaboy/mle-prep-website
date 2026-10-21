import numpy as np


def best_split(
    x: np.ndarray,
    y: np.ndarray,
    task: str = "classification",
    criterion: str = "gini",
    min_samples_leaf: int = 1,
    sample_weight: np.ndarray | None = None,
) -> dict[str, object] | None:
    """Best depth-1 split `(feature, threshold)` by impurity decrease.

    Canonical prompt: given dense numeric `X(n,d)` and classification labels, find the
    best `(feature, threshold)` split for a depth-1 tree using information gain or
    Gini decrease. Return child predictions. Then adapt the scorer for regression MSE
    reduction.

    Contract:
    - Candidate thresholds for a feature are midpoints `(v_i + v_{i+1}) / 2` between
      consecutive DISTINCT sorted values, so a threshold never separates equal values.
      Rows with `x[:, f] <= threshold` go left.
    - Impurity: classification `criterion="gini"` (1 - sum p^2) or `"entropy"` (base 2);
      regression uses MSE, the weighted mean squared deviation from the weighted mean.
      `gain = I(parent) - (W_L / W) I(left) - (W_R / W) I(right)` with `W` = total sample
      weight (row counts when `sample_weight` is None).
    - Each child needs at least `min_samples_leaf` ROWS.
    - Pick the largest gain; gains within 1e-12 tie and are broken by smaller feature
      index, then smaller threshold. Return None if there is no candidate that
      satisfies the constraints or the best gain is <= 1e-12 (e.g. pure labels or
      constant features).
    - Leaf predictions: classification -> class with the largest (weighted) count,
      ties -> smallest label; regression -> (weighted) mean.

    Returns:
        None, or `{"feature": int, "threshold": float, "gain": float,
        "left_prediction": ..., "right_prediction": ...}`.

    Raises:
        ValueError: unknown task/criterion, non-2-D `x`, length mismatch, NaN in `x`,
            negative weights, or `min_samples_leaf < 1`.

    Complexity: start from a clear O(d * n^2) baseline if you like; the reference sorts
    each feature once and sweeps cumulative statistics for O(d * n log n).
    """
    raise NotImplementedError("TODO: implement ML-11")
