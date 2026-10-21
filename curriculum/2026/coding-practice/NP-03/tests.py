import os
import sys

import numpy as np

from solution import confusion_metrics


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


def _reference(y_true, y_pred, c):
    cm = np.zeros((c, c), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    prec, rec, f1 = [], [], []
    for k in range(c):
        tp, fp, fn = cm[k, k], cm[:, k].sum() - cm[k, k], cm[k, :].sum() - cm[k, k]
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        prec.append(p), rec.append(r), f1.append(2 * p * r / (p + r) if p + r else 0.0)
    tp = np.trace(cm)
    micro = tp / len(y_true) if len(y_true) else 0.0
    return cm, np.array(prec), np.array(rec), np.array(f1), micro, float(np.mean(f1))


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "confusion_metrics"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_rows_are_truth_columns_are_predictions():
    cm, m = confusion_metrics(np.array([0, 1, 1, 2, 2, 2]), np.array([0, 0, 1, 2, 2, 1]), 3)
    assert cm.tolist() == [[1, 0, 0], [1, 1, 0], [0, 1, 2]]
    assert np.issubdtype(cm.dtype, np.integer)
    assert np.allclose(m["precision"], [0.5, 0.5, 1.0])
    assert np.allclose(m["recall"], [1.0, 0.5, 2 / 3])
    assert np.allclose(m["f1"], [2 / 3, 0.5, 0.8])
    assert np.isclose(m["micro_f1"], 4 / 6)
    assert np.isclose(m["macro_f1"], (2 / 3 + 0.5 + 0.8) / 3)


def test_absent_highest_class_keeps_full_shape_and_counts_in_macro():
    cm, m = confusion_metrics([0, 1, 0], [0, 1, 1], 4)
    assert cm.shape == (4, 4) and cm[2:].sum() == 0 and cm[:, 2:].sum() == 0
    assert m["precision"].shape == (4,) and m["f1"].shape == (4,)
    assert np.allclose(m["f1"][2:], 0.0)
    assert np.isclose(m["macro_f1"], (2 / 3 + 2 / 3 + 0 + 0) / 4)


def test_zero_division_is_zero_not_nan():
    # Class 1 is never predicted (precision 0/0) and class 2 never occurs (recall 0/0).
    cm, m = confusion_metrics([0, 1, 1], [0, 0, 2], 3)
    for key in ("precision", "recall", "f1"):
        assert np.all(np.isfinite(m[key])), key
    assert np.allclose(m["precision"], [0.5, 0.0, 0.0])
    assert np.allclose(m["recall"], [1.0, 0.0, 0.0])
    assert np.isfinite(m["macro_f1"]) and np.isfinite(m["micro_f1"])


def test_matches_reference_on_random_imbalanced_data():
    rng = np.random.default_rng(0)
    for c, n in [(2, 50), (5, 200), (7, 33)]:
        y_true = rng.choice(c, size=n, p=np.linspace(1, 3, c) / np.linspace(1, 3, c).sum())
        y_pred = np.where(rng.random(n) < 0.6, y_true, rng.integers(0, c, n))
        cm, m = confusion_metrics(y_true, y_pred, c)
        ref = _reference(y_true, y_pred, c)
        assert np.array_equal(cm, ref[0])
        assert np.allclose(m["precision"], ref[1]) and np.allclose(m["recall"], ref[2])
        assert np.allclose(m["f1"], ref[3])
        assert np.isclose(m["micro_f1"], ref[4]) and np.isclose(m["macro_f1"], ref[5])


def test_micro_f1_equals_accuracy_and_differs_from_macro_when_imbalanced():
    y_true = np.array([0] * 8 + [1, 2])
    y_pred = np.array([0] * 8 + [0, 0])
    _, m = confusion_metrics(y_true, y_pred, 3)
    assert np.isclose(m["micro_f1"], 0.8)
    assert np.isclose(m["macro_f1"], (2 * 0.8 / 1.8) / 3)


def test_single_class_and_empty_input():
    cm, m = confusion_metrics([0, 0, 0], [0, 0, 0], 1)
    assert cm.tolist() == [[3]] and np.allclose(m["f1"], [1.0]) and np.isclose(m["macro_f1"], 1.0)
    cm, m = confusion_metrics(np.array([], dtype=int), np.array([], dtype=int), 2)
    assert cm.tolist() == [[0, 0], [0, 0]]
    assert np.allclose(m["f1"], 0.0) and m["micro_f1"] == 0.0 and m["macro_f1"] == 0.0


def test_invalid_inputs_raise():
    assert _raises(ValueError, confusion_metrics, [0, 1], [0], 2)
    assert _raises(ValueError, confusion_metrics, [0, 2], [0, 1], 2)
    assert _raises(ValueError, confusion_metrics, [0, -1], [0, 1], 2)
    assert _raises(ValueError, confusion_metrics, [[0, 1]], [[0, 1]], 2)
    # Out-of-range labels whose flat cell id t*C+p still lands inside the C*C grid.
    assert _raises(ValueError, confusion_metrics, [0, 1], [3, 1], 3)
    assert _raises(ValueError, confusion_metrics, [1, 2], [-1, 2], 3)


def test_vectorized_no_python_loops():
    rng = np.random.default_rng(1)
    y_true = rng.integers(0, 60, size=20000)
    y_pred = rng.integers(0, 60, size=20000)
    (cm, _), lines = _line_events(confusion_metrics, y_true, y_pred, 60)
    assert lines <= 50, f"executed {lines} Python lines; expected no loops over samples or classes"
    assert cm.sum() == 20000
