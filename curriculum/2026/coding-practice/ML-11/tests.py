import math

import numpy as np

from solution import best_split


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _impurity(y, w, task, criterion):
    if task == "regression":
        mean = np.sum(w * y) / w.sum()
        return np.sum(w * (y - mean) ** 2) / w.sum()
    classes = np.unique(y)
    p = np.array([w[y == c].sum() for c in classes]) / w.sum()
    p = p[p > 0]
    return 1 - np.sum(p * p) if criterion == "gini" else -np.sum(p * np.log2(p))


def _brute(x, y, task="classification", criterion="gini", min_leaf=1, w=None):
    """Naive reference: rescore every midpoint partition from scratch."""
    w = np.ones(len(y)) if w is None else w
    parent = _impurity(y, w, task, criterion)
    best = None
    for f in range(x.shape[1]):
        values = np.unique(x[:, f])
        for t in (values[:-1] + values[1:]) / 2:
            left = x[:, f] <= t
            if left.sum() < min_leaf or (~left).sum() < min_leaf:
                continue
            child = (w[left].sum() * _impurity(y[left], w[left], task, criterion)
                     + w[~left].sum() * _impurity(y[~left], w[~left], task, criterion)) / w.sum()
            gain = parent - child
            if best is None or gain > best[0] + 1e-12:
                best = (gain, f, t)
    return None if best is None or best[0] <= 1e-12 else best


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "best_split"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_gini_split_and_leaf_predictions():
    out = best_split(np.array([[1.0], [2.0], [3.0], [4.0]]), np.array([0, 0, 1, 1]))
    assert out["feature"] == 0 and out["threshold"] == 2.5
    assert math.isclose(out["gain"], 0.5)
    assert out["left_prediction"] == 0 and out["right_prediction"] == 1
    assert isinstance(out["feature"], int)


def test_threshold_is_midpoint_between_distinct_values_never_inside_ties():
    x = np.array([[0.0], [0.0], [0.0], [1.0], [1.0], [3.0]])
    y = np.array([0, 0, 1, 1, 1, 1])
    out = best_split(x, y)
    assert out["threshold"] == 0.5  # the third 0.0 row cannot be split from the others
    assert math.isclose(out["gain"], _brute(x, y)[0])
    assert not best_split(np.array([[2.0], [2.0], [2.0]]), np.array([0, 1, 0]))


def test_best_feature_chosen_on_non_square_input():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(12, 3))
    y = (x[:, 2] > 0.1).astype(int)
    out = best_split(x, y)
    assert out["feature"] == 2 and math.isclose(out["gain"], _impurity(y, np.ones(12), "classification", "gini"))
    s = np.sort(x[:, 2])
    k = np.searchsorted(s, 0.1)
    assert math.isclose(out["threshold"], (s[k - 1] + s[k]) / 2)


def test_deterministic_tie_breaks():
    x = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0]])
    y = np.array([0, 1, 1, 0])
    out = best_split(x, y)
    assert out["feature"] == 0 and out["threshold"] == 1.5  # 1.5 and 3.5 tie; both features tie


def test_matches_brute_force_on_random_tied_features():
    rng = np.random.default_rng(1)
    for trial in range(6):
        x = rng.integers(0, 5, size=(40, 3)).astype(float)
        for task, criterion in (("classification", "gini"), ("classification", "entropy"), ("regression", "gini")):
            y = rng.integers(0, 3, size=40) if task == "classification" else rng.normal(size=40) + x[:, 1]
            ref = _brute(x, y, task, criterion)
            out = best_split(x, y, task=task, criterion=criterion)
            assert (out["feature"], out["threshold"]) == (ref[1], ref[2]), (trial, task, criterion)
            assert math.isclose(out["gain"], ref[0], rel_tol=1e-9, abs_tol=1e-12)


def test_min_samples_leaf():
    x = np.arange(1.0, 7.0)[:, None]
    y = np.array([1, 0, 0, 0, 0, 0])
    assert best_split(x, y)["threshold"] == 1.5
    out = best_split(x, y, min_samples_leaf=2)
    ref = _brute(x, y, min_leaf=2)
    assert out["threshold"] == ref[2] == 2.5
    assert best_split(x, y, min_samples_leaf=4) is None


def test_no_valid_split_cases():
    assert best_split(np.array([[1.0], [2.0], [3.0]]), np.array([4, 4, 4])) is None  # pure
    assert best_split(np.array([[1.0, 5.0], [1.0, 5.0]]), np.array([0, 1])) is None  # constant features
    assert best_split(np.array([[1.0]]), np.array([1])) is None


def test_multiclass_majority_with_smallest_label_tie():
    x = np.array([[0.0], [1.0], [2.0], [3.0], [10.0], [11.0], [12.0]])
    y = np.array([2, 1, 2, 1, 0, 0, 0])
    out = best_split(x, y)
    assert out["threshold"] == 6.5
    assert out["left_prediction"] == 1 and out["right_prediction"] == 0


def test_entropy_gain_in_bits():
    out = best_split(np.array([[1.0], [2.0], [3.0], [4.0]]), np.array([0, 0, 1, 1]), criterion="entropy")
    assert math.isclose(out["gain"], 1.0)


def test_regression_mse_reduction_and_mean_leaves():
    x = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 1.0], [4.0, 1.0]])
    y = np.array([1.0, 1.0, 5.0, 7.0])
    out = best_split(x, y, task="regression")
    parent = np.var(y)
    assert out["feature"] == 0 and out["threshold"] == 2.5
    assert math.isclose(out["gain"], parent - 0.5 * 0.0 - 0.5 * 1.0)
    assert math.isclose(out["left_prediction"], 1.0) and math.isclose(out["right_prediction"], 6.0)
    skewed = best_split(np.arange(1.0, 6.0)[:, None], np.array([0.0, 0.0, 5.0, 6.0, 10.0]), task="regression")
    assert skewed["threshold"] == 2.5 and math.isclose(skewed["right_prediction"], 7.0)  # mean, not median 6


def test_regression_is_invariant_to_a_large_target_offset():
    rng = np.random.default_rng(2)
    x = rng.integers(0, 6, size=(60, 2)).astype(float)
    y = 0.5 * x[:, 0] + rng.normal(scale=0.3, size=60)
    base = best_split(x, y, task="regression")
    shifted = best_split(x, y + 1e8, task="regression")  # sum(y^2) - (sum y)^2 / n cancels here
    assert (shifted["feature"], shifted["threshold"]) == (base["feature"], base["threshold"])
    assert math.isclose(shifted["gain"], base["gain"], rel_tol=1e-6)
    assert math.isclose(shifted["left_prediction"] - 1e8, base["left_prediction"], abs_tol=1e-6)


def test_sample_weights_equal_duplication():
    x = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
    y = np.array([0, 1, 0, 1, 1])
    w = np.array([3.0, 1.0, 2.0, 1.0, 1.0])
    dup_x = np.repeat(x, w.astype(int), axis=0)
    dup_y = np.repeat(y, w.astype(int))
    for task, yy, dyy in (("classification", y, dup_y), ("regression", y * 2.5, dup_y * 2.5)):
        a = best_split(x, yy, task=task, sample_weight=w)
        b = best_split(dup_x, dyy, task=task)
        assert (a["feature"], a["threshold"]) == (b["feature"], b["threshold"])
        assert math.isclose(a["gain"], b["gain"])
        assert np.isclose(a["left_prediction"], b["left_prediction"]) and np.isclose(a["right_prediction"], b["right_prediction"])


def test_validation_and_inputs_not_modified():
    x = np.array([[3.0], [1.0], [2.0]])
    y = np.array([1, 0, 1])
    x0, y0 = x.copy(), y.copy()
    best_split(x, y)
    assert np.array_equal(x, x0) and np.array_equal(y, y0)
    assert _raises(ValueError, best_split, np.array([[np.nan], [1.0]]), np.array([0, 1]))
    assert _raises(ValueError, best_split, x, y, task="ranking")
    assert _raises(ValueError, best_split, x, y, criterion="mse")
    assert _raises(ValueError, best_split, x, y[:2])
    assert _raises(ValueError, best_split, x, y, min_samples_leaf=0)
    assert _raises(ValueError, best_split, x, y, sample_weight=np.array([1.0, -1.0, 1.0]))
