import itertools
import math
import os
import sys

import numpy as np

from solution import average_precision, binary_metrics, roc_auc


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


def _pairwise_auc(y, s):
    pos = [b for a, b in zip(y, s) if a == 1]
    neg = [b for a, b in zip(y, s) if a == 0]
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p, n in itertools.product(pos, neg))
    return wins / (len(pos) * len(neg))


def _step_ap(y, s):
    y, s = np.asarray(y), np.asarray(s, dtype=float)
    total_pos, ap, prev_recall = y.sum(), 0.0, 0.0
    for t in sorted(set(s.tolist()), reverse=True):
        pred = s >= t
        tp = (pred & (y == 1)).sum()
        precision, recall = tp / pred.sum(), tp / total_pos
        ap += (recall - prev_recall) * precision
        prev_recall = recall
    return ap


def _trapezoid_pr_auc(y, s):
    """Wrong-for-this-contract PR-AUC: trapezoids through (0, 1) and each (R, P) point."""
    y, s = np.asarray(y), np.asarray(s, dtype=float)
    points = [(0.0, 1.0)]
    for t in sorted(set(s.tolist()), reverse=True):
        pred = s >= t
        tp = (pred & (y == 1)).sum()
        points.append((tp / y.sum(), tp / pred.sum()))
    return sum((r1 - r0) * (p0 + p1) / 2 for (r0, p0), (r1, p1) in zip(points, points[1:]))


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("roc_auc", "average_precision", "binary_metrics"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_confusion_matrix_orientation_and_threshold_metrics():
    y = np.array([1, 1, 1, 0, 0, 0, 0, 1])
    s = np.array([0.9, 0.6, 0.2, 0.7, 0.1, 0.3, 0.55, 0.8])
    out = binary_metrics(y, s, threshold=0.5)
    assert out["confusion_matrix"].tolist() == [[2, 2], [1, 3]]  # [[TN, FP], [FN, TP]]
    assert np.issubdtype(np.asarray(out["confusion_matrix"]).dtype, np.integer)
    assert math.isclose(out["precision"], 3 / 5) and math.isclose(out["recall"], 3 / 4)
    assert math.isclose(out["f1"], 2 * 0.6 * 0.75 / 1.35)


def test_threshold_boundary_is_inclusive_and_multiple_thresholds():
    y = np.array([1, 0, 1, 0])
    s = np.array([0.5, 0.5, 0.7, 0.2])
    assert binary_metrics(y, s, 0.5)["confusion_matrix"].tolist() == [[1, 1], [0, 2]]
    expected = {0.0: (0.5, 1.0), 0.6: (1.0, 0.5), 0.8: (0.0, 0.0)}
    for t, (p, r) in expected.items():
        out = binary_metrics(y, s, t)
        assert math.isclose(out["precision"], p) and math.isclose(out["recall"], r), t


def test_zero_division_is_zero():
    out = binary_metrics(np.array([0, 0, 1]), np.array([0.1, 0.2, 0.3]), threshold=0.9)
    assert out["precision"] == 0.0 and out["recall"] == 0.0 and out["f1"] == 0.0
    out = binary_metrics(np.array([0, 0]), np.array([0.7, 0.1]), threshold=0.5)
    assert out["recall"] == 0.0 and out["precision"] == 0.0 and out["f1"] == 0.0


def test_roc_auc_hand_computed_with_ties():
    # pairs (pos, neg): 0.8>0.3 1, 0.8>0.5 1, 0.5=0.5 0.5, 0.5>0.3 1  -> 3.5 / 4
    assert math.isclose(roc_auc(np.array([1, 1, 0, 0]), np.array([0.8, 0.5, 0.5, 0.3])), 0.875)
    assert math.isclose(roc_auc(np.array([0, 1, 0, 1]), np.array([0.1, 0.9, 0.4, 0.8])), 1.0)
    assert math.isclose(roc_auc(np.array([1, 0]), np.array([0.1, 0.9])), 0.0)


def test_roc_auc_all_scores_equal_is_half_regardless_of_order():
    for y in ([1, 0, 0, 1, 0], [0, 0, 0, 1, 1], [1, 1, 0, 0, 0]):
        assert math.isclose(roc_auc(np.array(y), np.full(5, 0.3)), 0.5)


def test_roc_auc_matches_pairwise_definition_on_heavy_ties():
    rng = np.random.default_rng(0)
    for n in (7, 40, 151):
        y = rng.integers(0, 2, size=n)
        y[:2] = [0, 1]
        s = rng.integers(0, 4, size=n) / 4.0
        assert math.isclose(roc_auc(y, s), _pairwise_auc(y.tolist(), s.tolist()), rel_tol=1e-12)
        assert math.isclose(roc_auc(y, -s), 1 - _pairwise_auc(y.tolist(), s.tolist()), rel_tol=1e-12)


def test_average_precision_is_step_sum_not_trapezoid():
    y = np.array([1, 0, 1, 0, 0, 1])
    s = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4])
    # thresholds hit positives at ranks 1, 3, 6: AP = (1 + 2/3 + 1/2) / 3
    assert math.isclose(average_precision(y, s), (1 + 2 / 3 + 0.5) / 3)
    # The common wrong answer, trapezoids over the PR curve, differs on this fixture.
    assert not math.isclose(_trapezoid_pr_auc(y, s), (1 + 2 / 3 + 0.5) / 3, rel_tol=1e-3)


def test_average_precision_tied_scores_enter_together():
    y = np.array([1, 0, 0, 1])
    assert math.isclose(average_precision(y, np.full(4, 0.5)), 0.5)  # equals prevalence
    y = np.array([0, 1, 1, 0, 1])
    s = np.array([0.9, 0.9, 0.5, 0.5, 0.1])
    # t=0.9: P=1/2 R=1/3; t=0.5: P=2/4 R=2/3; t=0.1: P=3/5 R=1
    assert math.isclose(average_precision(y, s), (1 / 3) * 0.5 + (1 / 3) * 0.5 + (1 / 3) * 0.6)


def test_average_precision_matches_reference_on_random_ties():
    rng = np.random.default_rng(1)
    for n in (5, 33, 200):
        y = rng.integers(0, 2, size=n)
        y[0] = 1
        s = rng.integers(0, 5, size=n) / 5.0
        assert math.isclose(average_precision(y, s), _step_ap(y, s), rel_tol=1e-12)


def test_undefined_aucs_are_nan_and_all_positive():
    out = binary_metrics(np.array([0, 0, 0]), np.array([0.2, 0.6, 0.4]))
    assert math.isnan(out["roc_auc"]) and math.isnan(out["average_precision"])
    out = binary_metrics(np.array([1, 1]), np.array([0.2, 0.6]))
    assert math.isnan(out["roc_auc"]) and math.isclose(out["average_precision"], 1.0)
    assert math.isclose(out["recall"], 0.5) and math.isclose(out["precision"], 1.0)


def test_rank_metrics_are_invariant_to_monotone_transforms_and_row_order():
    rng = np.random.default_rng(2)
    y = rng.integers(0, 2, size=60)
    s = rng.integers(0, 10, size=60) / 10.0
    perm = rng.permutation(60)
    for metric in (roc_auc, average_precision):
        base = metric(y, s)
        assert math.isclose(metric(y, np.exp(5 * s)), base, rel_tol=1e-12)
        assert math.isclose(metric(y[perm], s[perm]), base, rel_tol=1e-12)


def test_validation_and_bool_labels():
    assert _raises(ValueError, binary_metrics, np.array([0, 2]), np.array([0.1, 0.2]))
    assert _raises(ValueError, binary_metrics, np.array([0, 1]), np.array([0.1]))
    assert _raises(ValueError, binary_metrics, np.array([], dtype=int), np.array([]))
    out = binary_metrics(np.array([True, False]), np.array([0.9, 0.1]))
    assert out["confusion_matrix"].tolist() == [[1, 0], [0, 1]] and math.isclose(out["roc_auc"], 1.0)


def test_rank_metrics_are_n_log_n_not_pairwise_or_per_threshold_loops():
    rng = np.random.default_rng(3)
    y = rng.integers(0, 2, size=20000)
    s = np.round(rng.random(20000), 3)
    for metric in (roc_auc, average_precision):
        _, lines = _line_events(metric, y, s)
        assert lines <= 60, f"{metric.__name__} executed {lines} Python lines; vectorize the sweep"
