import math

import numpy as np

from solution import evaluate

# Hand-labelled fixture: 12 examples, 5 positives (natural prevalence 5/12).
LOGITS = np.array([2.0, 0.3, -0.2, 0.0, 1.0, -3.0, 0.4, -1.0, 0.1, 3.0, -0.5, 0.2])
LABELS = np.array([1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0])
# At threshold 0.5 (sigmoid(logit) >= 0.5  <=>  logit >= 0), hand-counted:
#   predicted positive: idx 0, 1, 3, 4, 6, 8, 9, 11
#   TP = {0, 1, 3, 9} = 4, FP = {4, 6, 8, 11} = 4, FN = {7} = 1
#   precision = 4/8, recall = 4/5, f1 = 2 * 0.5 * 0.8 / 1.3


def _close(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def _check(out, tp, fp, fn, n, positives):
    assert (out["tp"], out["fp"], out["fn"], out["n"]) == (tp, fp, fn, n), out
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    assert _close(out["precision"], precision), (out["precision"], precision)
    assert _close(out["recall"], recall), (out["recall"], recall)
    assert _close(out["f1"], f1), (out["f1"], f1)
    assert _close(out["positive_rate"], positives / n), out["positive_rate"]


def test_hand_computed_metrics_at_default_threshold():
    out = evaluate(LOGITS, LABELS, batch_size=12)
    _check(out, tp=4, fp=4, fn=1, n=12, positives=5)
    assert _close(out["precision"], 0.5) and _close(out["recall"], 0.8)
    assert _close(out["f1"], 0.8 / 1.3)


def test_threshold_is_a_probability_applied_to_sigmoid_of_logits():
    # sigmoid(logit) >= 0.8  <=>  logit >= log(4) ~= 1.386: only idx 0 and 9 qualify.
    _check(evaluate(LOGITS, LABELS, threshold=0.8, batch_size=12), tp=2, fp=0, fn=3, n=12, positives=5)
    # sigmoid(logit) >= 0.3  <=>  logit >= -0.847: everything except idx 5 and 7.
    _check(evaluate(LOGITS, LABELS, threshold=0.3, batch_size=12), tp=4, fp=6, fn=1, n=12, positives=5)


def test_probability_exactly_at_threshold_is_positive():
    out = evaluate(np.array([0.0, 0.0, -1e-9]), np.array([1, 0, 1]), batch_size=3)
    _check(out, tp=1, fp=1, fn=1, n=3, positives=2)


def test_metrics_do_not_depend_on_batch_size_or_seed():
    reference = evaluate(LOGITS, LABELS, batch_size=12)
    # batch_size=4 is the case where averaging per-batch precision gives 4/9 instead of 1/2.
    for batch_size in (1, 3, 4, 5, 7, 256):
        for seed in (0, 1, 2):
            out = evaluate(LOGITS, LABELS, batch_size=batch_size, seed=seed)
            assert out == reference, (batch_size, seed, out, reference)


def test_validation_population_is_natural_not_oversampled():
    rng = np.random.default_rng(0)
    labels = (rng.random(400) < 0.05).astype(int)  # rare positives, as in production
    logits = np.where(labels == 1, 1.0, -1.0) + rng.normal(0, 1.2, size=400)
    positives = int(labels.sum())
    for seed in range(8):
        out = evaluate(logits, labels, batch_size=64, seed=seed)
        assert out["n"] == 400, "each validation example must be counted exactly once"
        assert out["tp"] + out["fn"] == positives
        assert _close(out["positive_rate"], positives / 400)
        pred = logits >= 0
        expected_precision = int(np.sum(pred & (labels == 1))) / int(np.sum(pred))
        assert _close(out["precision"], expected_precision)


def test_every_positive_is_evaluated_once_in_a_small_split():
    # 5 positives vs 7 negatives: resampling positives with replacement drops some of them.
    for seed in range(10):
        out = evaluate(LOGITS, LABELS, batch_size=5, seed=seed)
        _check(out, tp=4, fp=4, fn=1, n=12, positives=5)


def test_missing_class_and_no_prediction_edge_cases():
    # No positives at all: recall is 0/0 -> 0.0, precision has FP only.
    _check(evaluate(np.array([0.5, -2.0, 1.0]), np.array([0, 0, 0])), tp=0, fp=2, fn=0, n=3, positives=0)
    # Nothing predicted positive: precision is 0/0 -> 0.0.
    _check(evaluate(np.array([-5.0, -1.0, -0.1]), np.array([1, 0, 1])), tp=0, fp=0, fn=2, n=3, positives=2)


def test_extreme_logits_are_classified_correctly():
    out = evaluate(np.array([1000.0, -1000.0, 750.0, -750.0]), np.array([1, 0, 0, 1]))
    _check(out, tp=1, fp=1, fn=1, n=4, positives=2)
