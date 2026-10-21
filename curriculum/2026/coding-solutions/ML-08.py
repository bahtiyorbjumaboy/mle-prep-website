import numpy as np


def calibration_metrics(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    n_bins: int = 10,
    strategy: str = "uniform",
) -> dict[str, np.ndarray | float]:
    """Reliability bins plus count-weighted ECE, MCE, and Brier score."""
    y = np.asarray(y_true)
    p = np.asarray(probabilities, dtype=float)
    if y.ndim != 1 or p.shape != y.shape or y.size == 0:
        raise ValueError("y_true and probabilities must be non-empty 1-D arrays of equal length")
    if not np.all((y == 0) | (y == 1)):
        raise ValueError("labels must be 0/1")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must lie in [0, 1]")
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")

    if strategy == "uniform":
        edges = np.linspace(0.0, 1.0, n_bins + 1)
        bins = np.minimum(np.floor(p * n_bins).astype(np.intp), n_bins - 1)  # 1.0 -> last bin
    elif strategy == "quantile":
        edges = np.quantile(p, np.linspace(0.0, 1.0, n_bins + 1))
        edges[0], edges[-1] = 0.0, 1.0
        bins = np.searchsorted(edges[1:-1], p, side="right")  # ties land together
    else:
        raise ValueError("strategy must be 'uniform' or 'quantile'")

    counts = np.bincount(bins, minlength=n_bins)
    sum_p = np.bincount(bins, weights=p, minlength=n_bins)
    sum_y = np.bincount(bins, weights=y.astype(float), minlength=n_bins)
    nonempty = counts > 0
    confidence = np.full(n_bins, np.nan)
    accuracy = np.full(n_bins, np.nan)
    confidence[nonempty] = sum_p[nonempty] / counts[nonempty]
    accuracy[nonempty] = sum_y[nonempty] / counts[nonempty]

    gap = np.abs(accuracy[nonempty] - confidence[nonempty])
    return {
        "bin_edges": edges,
        "bin_counts": counts,
        "bin_confidence": confidence,
        "bin_accuracy": accuracy,
        "ece": float(np.sum(counts[nonempty] / len(p) * gap)),  # weighted by bin mass
        "mce": float(gap.max()),
        "brier": float(np.mean((p - y) ** 2)),
    }
