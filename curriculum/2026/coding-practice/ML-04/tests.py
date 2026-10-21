import math

import numpy as np

from solution import bce_with_logits, cross_entropy, logsumexp, naive_failure_examples, sigmoid, softmax


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _strict(fn, *args, **kwargs):
    """Run with overflow/invalid/divide promoted to errors (underflow is allowed)."""
    with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
        return fn(*args, **kwargs)


def _ref_lse(row):
    m = max(row)
    return m + math.log(sum(math.exp(v - m) for v in row))


EXTREME = np.array([[1e4, 0.0, -1e4], [-1e4, -1e4 + 1.0, -1e4 + 2.0], [1000.0, 999.0, 998.0], [0.0, 0.0, 0.0]])


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("logsumexp", "softmax", "cross_entropy", "sigmoid", "bce_with_logits", "naive_failure_examples"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_logsumexp_extreme_rows_and_reduced_shape():
    out = _strict(logsumexp, EXTREME)
    assert out.shape == (4,)
    for got, row in zip(out, EXTREME):
        assert math.isclose(got, _ref_lse(row.tolist()), rel_tol=1e-12, abs_tol=1e-9)
    assert math.isclose(out[1], -1e4 + 2.0 + math.log(1 + math.exp(-1) + math.exp(-2)), rel_tol=1e-12)


def test_logsumexp_axis_on_non_square_3d_and_masked_entries():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(2, 3, 5)) * 50
    for axis in (0, 1, 2, -1):
        expected = np.log(np.sum(np.exp(x - x.max()), axis=axis)) + x.max()
        got = _strict(logsumexp, x, axis=axis)
        assert got.shape == expected.shape and np.allclose(got, expected)
    masked = np.array([[-np.inf, 0.0, np.log(3.0)], [5.0, -np.inf, -np.inf]])
    assert np.allclose(_strict(logsumexp, masked), [np.log(4.0), 5.0])


def test_softmax_extreme_logits_axis_and_normalization():
    p = _strict(softmax, EXTREME)
    assert p.shape == EXTREME.shape and np.all(np.isfinite(p))
    assert np.allclose(p.sum(axis=1), 1.0)
    assert np.allclose(p[0], [1.0, 0.0, 0.0]) and np.allclose(p[3], 1 / 3)
    e = np.exp([0.0, -1.0, -2.0])
    assert np.allclose(p[2], e / e.sum()) and np.allclose(p[1], e[::-1] / e.sum())
    x = np.arange(6, dtype=float).reshape(2, 3)
    col = _strict(softmax, x, axis=0)
    assert np.allclose(col.sum(axis=0), 1.0) and not np.allclose(col.sum(axis=1), 1.0)
    assert np.allclose(col[:, 0], np.exp([0.0, 3.0]) / np.exp([0.0, 3.0]).sum())


def test_softmax_is_not_applied_twice_and_shift_invariant():
    x = np.array([[2.0, 1.0, 0.0]])
    e = np.exp([2.0, 1.0, 0.0])
    assert np.allclose(softmax(x), e / e.sum())
    assert np.allclose(softmax(x + 1e4), softmax(x))


def test_cross_entropy_hand_computed_and_reductions():
    logits = np.array([[2.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
    targets = np.array([0, 2])
    per = np.array([_ref_lse([2.0, 1.0, 0.0]) - 2.0, math.log(3.0)])
    assert np.allclose(cross_entropy(logits, targets, "none"), per)
    assert math.isclose(cross_entropy(logits, targets), per.mean())
    assert math.isclose(cross_entropy(logits, targets, "sum"), per.sum())
    assert isinstance(cross_entropy(logits, targets), float)


def test_cross_entropy_targets_index_rows_not_columns():
    logits = np.array([[3.0, 0.0, 0.0, 1.0], [0.0, 5.0, 0.0, 0.0], [1.0, 1.0, 4.0, 0.0]])
    targets = np.array([3, 1, 0])
    expected = [_ref_lse(row) - row[t] for row, t in zip(logits.tolist(), targets)]
    assert np.allclose(cross_entropy(logits, targets, "none"), expected)


def test_cross_entropy_extreme_logits_is_finite_and_exact():
    logits = np.array([[0.0, -1e4], [1e4, -1e4], [-1e4, 1e4]])
    out = _strict(cross_entropy, logits, np.array([1, 0, 0]), "none")
    assert np.allclose(out, [1e4, 0.0, 2e4], rtol=1e-12, atol=1e-12)
    assert math.isclose(_strict(cross_entropy, np.array([[1000.0, 999.0]]), np.array([1])), 1.0 + math.log1p(math.exp(-1)))


def test_sigmoid_values_symmetry_and_no_overflow():
    x = np.array([-1e4, -800.0, -30.0, -1.0, 0.0, 1.0, 30.0, 800.0, 1e4])
    s = _strict(sigmoid, x)
    assert s.shape == x.shape and np.all(np.isfinite(s))
    assert np.allclose(s, [0.0, 0.0, 1 / (1 + math.exp(30)), 1 / (1 + math.e), 0.5, 1 / (1 + math.exp(-1)), 1 / (1 + math.exp(-30)), 1.0, 1.0], rtol=1e-12, atol=0)
    assert np.allclose(s + _strict(sigmoid, -x), 1.0)
    assert s[2] > 0 and math.isclose(s[2], math.exp(-30) / (1 + math.exp(-30)), rel_tol=1e-12)


def test_bce_matches_definition_on_moderate_values():
    z = np.array([-3.0, -0.5, 0.0, 0.7, 4.0])
    y = np.array([0.0, 1.0, 0.3, 1.0, 0.0])
    p = 1 / (1 + np.exp(-z))
    expected = -(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert np.allclose(bce_with_logits(z, y, "none"), expected)
    assert math.isclose(bce_with_logits(z, y), expected.mean())
    assert math.isclose(bce_with_logits(z, y, "sum"), expected.sum())


def test_bce_extreme_logits_finite_and_exact():
    z = np.array([1e4, 1e4, -1e4, -1e4, 40.0])
    y = np.array([1.0, 0.0, 0.0, 1.0, 0.0])
    out = _strict(bce_with_logits, z, y, "none")
    assert np.allclose(out, [0.0, 1e4, 0.0, 1e4, 40.0 + math.log1p(math.exp(-40))], rtol=1e-12, atol=1e-12)


def test_bce_keeps_relative_precision_for_confident_correct_predictions():
    # True loss is log1p(exp(-|z|)) ~ 4e-18 at |z| = 40; log(1 + tiny) rounds it to 0.
    z = np.array([20.0, 40.0, -40.0])
    y = np.array([1.0, 1.0, 0.0])
    expected = [math.log1p(math.exp(-20)), math.log1p(math.exp(-40)), math.log1p(math.exp(-40))]
    assert np.allclose(_strict(bce_with_logits, z, y, "none"), expected, rtol=1e-12, atol=0)


def test_bce_equals_two_class_cross_entropy():
    rng = np.random.default_rng(1)
    z = rng.normal(size=8) * 30
    y = rng.integers(0, 2, size=8)
    two_class = np.column_stack([np.zeros(8), z])
    assert np.allclose(bce_with_logits(z, y.astype(float), "none"), cross_entropy(two_class, y, "none"))


def test_validation():
    logits = np.zeros((2, 3))
    assert _raises(ValueError, cross_entropy, logits, np.array([0, 3]))
    assert _raises(ValueError, cross_entropy, logits, np.array([0, -1]))
    assert _raises(ValueError, cross_entropy, logits, np.array([0]))
    assert _raises(ValueError, cross_entropy, logits, np.array([0, 1]), "avg")
    assert _raises(ValueError, bce_with_logits, np.zeros(2), np.array([0.0, 1.5]))
    assert _raises(ValueError, bce_with_logits, np.zeros(2), np.zeros(3))
    assert _raises(ValueError, bce_with_logits, np.zeros(2), np.zeros(2), "max")


def test_inputs_not_modified():
    x = EXTREME.copy()
    t = np.array([0, 1, 2, 0])
    softmax(x), logsumexp(x), cross_entropy(x, t), sigmoid(x), bce_with_logits(x[:, 0], np.ones(4))
    assert np.array_equal(x, EXTREME) and t.tolist() == [0, 1, 2, 0]


def test_naive_failure_examples_really_break_naive_code():
    ex = naive_failure_examples()
    logits, xs = np.asarray(ex["softmax"], dtype=float), np.asarray(ex["sigmoid"], dtype=float)
    with np.errstate(all="ignore"):
        naive_softmax = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
        naive_sigmoid = np.exp(xs) / (1 + np.exp(xs))
    assert np.isnan(naive_softmax).any() and np.all(np.isfinite(_strict(softmax, logits)))
    assert np.isnan(naive_sigmoid).any() and np.all(np.isfinite(_strict(sigmoid, xs)))
