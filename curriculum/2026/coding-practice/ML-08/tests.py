import math
import os
import sys

import numpy as np

from solution import calibration_metrics


def _line_events(fn, *args, **kwargs):
    """Count Python line events executed inside solution.py (timing-free loop detector)."""
    count = 0

    def local(frame, event, arg):
        nonlocal count
        if event == "line":
            count += 1
        return local

    def global_trace(frame, event, arg):
        return local if os.path.basename(frame.f_code.co_filename) == "solution.py" else None

    previous = sys.gettrace()
    sys.settrace(global_trace)
    try:
        result = fn(*args, **kwargs)
    finally:
        sys.settrace(previous)
    return result, count


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "calibration_metrics"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_bins_and_weighted_ece():
    y = np.array([0, 0, 1, 1, 1, 0, 1])
    p = np.array([0.1, 0.2, 0.3, 0.6, 0.7, 0.8, 0.9])
    out = calibration_metrics(y, p, n_bins=2)
    assert np.allclose(out["bin_edges"], [0.0, 0.5, 1.0])
    assert out["bin_counts"].tolist() == [3, 4] and np.issubdtype(out["bin_counts"].dtype, np.integer)
    assert np.allclose(out["bin_confidence"], [0.2, 0.75])
    assert np.allclose(out["bin_accuracy"], [1 / 3, 0.75])
    assert math.isclose(out["ece"], 3 / 7 * (2 / 15) + 4 / 7 * 0.0)
    assert math.isclose(out["mce"], 2 / 15)
    assert math.isclose(out["brier"], np.mean((p - y) ** 2))


def test_ece_weights_bins_by_count_not_equally():
    # 9 samples perfectly calibrated at 0.25 (bin 0), 1 sample badly off at 0.95 (bin 1).
    y = np.array([1, 0, 0, 0, 1, 0, 0, 0, 0, 0])
    p = np.array([0.25] * 4 + [0.25] * 4 + [0.25, 0.95])
    out = calibration_metrics(y, p, n_bins=2)
    assert np.allclose(out["bin_accuracy"], [2 / 9, 0.0])
    expected = 0.9 * abs(2 / 9 - 0.25) + 0.1 * 0.95
    assert math.isclose(out["ece"], expected)
    assert not math.isclose(out["ece"], (abs(2 / 9 - 0.25) + 0.95) / 2)
    assert math.isclose(out["mce"], 0.95)


def test_boundary_probabilities_follow_the_floor_rule():
    p = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 0.2499999])
    out = calibration_metrics(np.array([0, 0, 1, 1, 1, 0]), p, n_bins=4)
    # bins: 0 -> {0.0, 0.2499999}, 1 -> {0.25}, 2 -> {0.5}, 3 -> {0.75, 1.0}
    assert out["bin_counts"].tolist() == [2, 1, 1, 2]
    assert np.allclose(out["bin_confidence"], [0.12499995, 0.25, 0.5, 0.875])


def test_empty_bins_are_nan_and_excluded():
    y = np.array([1, 0, 1, 1])
    p = np.array([0.05, 0.05, 0.95, 0.95])
    out = calibration_metrics(y, p, n_bins=10)
    assert out["bin_counts"].tolist() == [2] + [0] * 8 + [2]
    assert np.isnan(out["bin_confidence"][1:9]).all() and np.isnan(out["bin_accuracy"][1:9]).all()
    assert math.isclose(out["ece"], 0.5 * 0.45 + 0.5 * 0.05)
    assert math.isclose(out["mce"], 0.45) and math.isfinite(out["ece"])


def test_perfect_and_severe_miscalibration():
    y = np.array([1, 0, 0, 0, 1, 1, 1, 0])
    p = np.array([0.25] * 4 + [0.75] * 4)
    out = calibration_metrics(y, p, n_bins=10)
    assert math.isclose(out["ece"], 0.0, abs_tol=1e-12) and math.isclose(out["mce"], 0.0, abs_tol=1e-12)
    bad = calibration_metrics(np.zeros(50, dtype=int), np.full(50, 0.99), n_bins=10)
    assert math.isclose(bad["ece"], 0.99) and math.isclose(bad["mce"], 0.99)
    assert math.isclose(bad["brier"], 0.99 ** 2)


def test_quantile_bins_equal_counts_for_distinct_probabilities():
    rng = np.random.default_rng(0)
    p = rng.permutation(np.linspace(0.01, 0.99, 100))
    y = (rng.random(100) < p).astype(int)
    out = calibration_metrics(y, p, n_bins=5, strategy="quantile")
    assert out["bin_counts"].tolist() == [20] * 5
    assert out["bin_edges"][0] == 0.0 and out["bin_edges"][-1] == 1.0
    assert np.allclose(out["bin_edges"][1:-1], np.quantile(p, [0.2, 0.4, 0.6, 0.8]))
    order = np.argsort(p)
    for b in range(5):
        members = order[20 * b:20 * (b + 1)]
        assert math.isclose(out["bin_confidence"][b], p[members].mean())
        assert math.isclose(out["bin_accuracy"][b], y[members].mean())


def test_identical_probabilities_share_a_bin():
    y = np.array([1, 0, 1, 1, 0, 0])
    p = np.full(6, 0.4)
    for strategy in ("uniform", "quantile"):
        out = calibration_metrics(y, p, n_bins=4, strategy=strategy)
        assert sorted(out["bin_counts"].tolist()) == [0, 0, 0, 6], strategy
        assert math.isclose(out["ece"], 0.1) and math.isclose(out["mce"], 0.1)


def test_validation():
    y, p = np.array([0, 1]), np.array([0.2, 0.8])
    assert _raises(ValueError, calibration_metrics, y, np.array([0.2, 1.2]))
    assert _raises(ValueError, calibration_metrics, y, np.array([-0.1, 0.5]))
    assert _raises(ValueError, calibration_metrics, np.array([0, 2]), p)
    assert _raises(ValueError, calibration_metrics, y, np.array([0.5]))
    assert _raises(ValueError, calibration_metrics, y, p, n_bins=0)
    assert _raises(ValueError, calibration_metrics, y, p, strategy="kmeans")
    assert _raises(ValueError, calibration_metrics, np.array([], dtype=int), np.array([]))


def test_uniform_binning_is_vectorized():
    rng = np.random.default_rng(1)
    p = rng.random(50000)
    y = (rng.random(50000) < p).astype(int)
    out, lines = _line_events(calibration_metrics, y, p, 200)
    assert lines <= 60, f"executed {lines} Python lines; expected O(n + B) array work"
    assert out["bin_counts"].sum() == 50000
    bins = np.minimum((p * 200).astype(int), 199)
    ref = sum(abs(y[bins == b].mean() - p[bins == b].mean()) * np.sum(bins == b) for b in range(200) if np.any(bins == b))
    assert math.isclose(out["ece"], ref / 50000, rel_tol=1e-9)
