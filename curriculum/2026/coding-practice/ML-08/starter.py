import numpy as np


def calibration_metrics(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    n_bins: int = 10,
    strategy: str = "uniform",
) -> dict[str, np.ndarray | float]:
    """Reliability bins, ECE, MCE, and Brier score for binary predictions.

    Canonical prompt: given probabilities and labels, compute reliability bins,
    observed positive rate, mean predicted probability, ECE, MCE, and a
    quantile-binning alternative.

    Binning contract (`B = n_bins`):
    - `"uniform"`: edges `np.linspace(0, 1, B + 1)`; sample `i` goes to bin
      `min(floor(p_i * B), B - 1)`, so bins are `[e_b, e_{b+1})` except that the last
      bin also contains 1.0.
    - `"quantile"`: edges `np.quantile(p, np.linspace(0, 1, B + 1))` with the first and
      last edges then set to 0.0 and 1.0; sample `i` goes to bin
      `np.searchsorted(edges[1:-1], p_i, side="right")`. Identical probabilities
      always share a bin, so some quantile bins may be empty.

    Metrics (with `n_b` samples in bin `b`, `n` in total):
    - `bin_confidence[b]` = mean predicted probability, `bin_accuracy[b]` = observed
      positive rate; both NaN for an empty bin.
    - `ece = sum_b (n_b / n) * |bin_accuracy[b] - bin_confidence[b]|` over non-empty
      bins (count-weighted, not a plain average over bins).
    - `mce = max_b |bin_accuracy[b] - bin_confidence[b]|` over non-empty bins.
    - `brier = mean((p - y)^2)`.

    Returns:
        dict with `"bin_edges"` `(B + 1,)`, `"bin_counts"` int `(B,)`,
        `"bin_confidence"` `(B,)`, `"bin_accuracy"` `(B,)`, and floats `"ece"`,
        `"mce"`, `"brier"`. O(n + B) for uniform bins.

    Raises:
        ValueError: on empty or mismatched inputs, labels outside {0, 1},
            probabilities outside [0, 1], `n_bins < 1`, or an unknown strategy.
    """
    raise NotImplementedError("TODO: implement ML-08")
