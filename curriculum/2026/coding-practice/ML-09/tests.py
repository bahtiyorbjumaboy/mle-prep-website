import itertools
import math

import numpy as np

from solution import bootstrap_diff_ci, bootstrap_ratio_diff_ci, permutation_pvalue


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _exact_two_sided_p(control, treatment):
    pooled = np.concatenate([control, treatment])
    n_t = len(treatment)
    observed = abs(np.mean(treatment) - np.mean(control))
    hits = total = 0
    for idx in itertools.combinations(range(len(pooled)), n_t):
        mask = np.zeros(len(pooled), dtype=bool)
        mask[list(idx)] = True
        hits += abs(pooled[mask].mean() - pooled[~mask].mean()) >= observed - 1e-12
        total += 1
    return hits / total


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("bootstrap_diff_ci", "permutation_pvalue", "bootstrap_ratio_diff_ci"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_bootstrap_ci_deterministic_ordered_and_covers_observed_difference():
    rng = np.random.default_rng(0)
    control, treatment = rng.normal(10, 2, size=80), rng.normal(11, 2, size=120)
    low, high = bootstrap_diff_ci(control, treatment, n_boot=3000, seed=4)
    assert (low, high) == bootstrap_diff_ci(control, treatment, n_boot=3000, seed=4)
    assert isinstance(low, float) and low < high
    diff = treatment.mean() - control.mean()
    assert low < diff < high and abs((low + high) / 2 - diff) < 0.15 * (high - low)
    wider = bootstrap_diff_ci(control, treatment, n_boot=3000, alpha=0.01, seed=4)
    assert wider[0] < low and wider[1] > high


def test_bootstrap_ci_width_matches_unpaired_standard_error_with_unequal_groups():
    rng = np.random.default_rng(1)
    control, treatment = rng.normal(0, 1, size=50), rng.normal(0, 3, size=400)
    low, high = bootstrap_diff_ci(control, treatment, n_boot=4000, seed=2)
    se = math.sqrt(control.var() / 50 + treatment.var() / 400)
    assert math.isclose(high - low, 2 * 1.96 * se, rel_tol=0.12)


def test_bootstrap_ci_large_effect_is_not_centered_on_zero():
    control = np.arange(30, dtype=float)
    treatment = np.arange(30, dtype=float) + 100
    low, high = bootstrap_diff_ci(control, treatment, n_boot=1000, seed=3)
    assert 90 < low < 100 < high < 110


def test_bootstrap_ci_constant_groups_is_degenerate():
    assert bootstrap_diff_ci(np.full(5, 2.0), np.full(7, 3.5), n_boot=50, seed=0) == (1.5, 1.5)


def test_permutation_pvalue_matches_exact_enumeration():
    control = np.array([1.0, 2.0, 2.5, 3.0, 1.5, 2.2])
    treatment = np.array([2.4, 3.1, 2.9, 4.0, 2.0, 3.3])
    exact = _exact_two_sided_p(control, treatment)
    assert 0.02 < exact < 0.2  # one-sided would be about half of this
    p = permutation_pvalue(control, treatment, n_perm=20000, seed=5)
    assert abs(p - exact) < 0.012
    assert p == permutation_pvalue(control, treatment, n_perm=20000, seed=5)


def test_permutation_pvalue_respects_unequal_group_sizes():
    control = np.array([0.5, 1.0, 0.2, 0.9])
    treatment = np.array([1.1, 1.6, 0.8, 1.9, 1.4, 1.2, 2.2, 0.7])
    exact = _exact_two_sided_p(control, treatment)
    p = permutation_pvalue(control, treatment, n_perm=20000, seed=9)
    assert abs(p - exact) < 0.012


def test_permutation_pvalue_is_two_sided_and_symmetric():
    rng = np.random.default_rng(6)
    control, treatment = rng.normal(0, 1, 40), rng.normal(0.45, 1, 25)
    forward = permutation_pvalue(control, treatment, n_perm=8000, seed=1)
    backward = permutation_pvalue(treatment, control, n_perm=8000, seed=1)
    assert abs(forward - backward) < 0.02
    assert 0.0 < forward < 0.5


def test_permutation_plus_one_correction_and_null_behavior():
    p = permutation_pvalue(np.zeros(20), np.ones(20), n_perm=999, seed=0)
    assert p == 1 / 1000, "the observed labeling counts once: p = (1 + 0) / (1 + 999)"
    same = np.array([1.0, 2.0, 3.0, 4.0])
    assert permutation_pvalue(same, same.copy(), n_perm=500, seed=0) == 1.0
    rng = np.random.default_rng(7)
    null_p = [permutation_pvalue(rng.normal(size=15), rng.normal(size=15), n_perm=300, seed=s) for s in range(40)]
    assert 0.3 < np.mean(null_p) < 0.7


def test_ratio_metric_resamples_users_as_pairs():
    rng = np.random.default_rng(8)
    den_c, den_t = rng.integers(1, 50, size=60).astype(float), rng.integers(1, 50, size=70).astype(float)
    low, high = bootstrap_ratio_diff_ci(0.1 * den_c, den_c, 0.25 * den_t, den_t, n_boot=500, seed=1)
    # Every user has the same ratio inside a group, so every paired replicate is exactly 0.15.
    assert math.isclose(low, 0.15, abs_tol=1e-12) and math.isclose(high, 0.15, abs_tol=1e-12)


def test_ratio_metric_is_sum_over_sum_not_mean_of_ratios():
    # Heavy users (large denominators) convert at 1%, light users at 90%.
    den = np.array([1000.0] * 10 + [1.0] * 10)
    num_c = np.concatenate([np.full(10, 10.0), np.full(10, 0.9)])
    num_t = np.concatenate([np.full(10, 20.0), np.full(10, 0.9)])
    low, high = bootstrap_ratio_diff_ci(num_c, den, num_t, den, n_boot=2000, seed=2)
    sum_ratio_diff = num_t.sum() / den.sum() - num_c.sum() / den.sum()
    mean_ratio_diff = np.mean(num_t / den) - np.mean(num_c / den)
    assert low <= sum_ratio_diff <= high
    assert not low <= mean_ratio_diff <= high


def test_ratio_ci_deterministic_and_validation():
    num, den = np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 4.0])
    a = bootstrap_ratio_diff_ci(num, den, num * 2, den, n_boot=100, seed=3)
    assert a == bootstrap_ratio_diff_ci(num, den, num * 2, den, n_boot=100, seed=3)
    assert _raises(ValueError, bootstrap_ratio_diff_ci, num, np.array([1.0, 0.0, 1.0]), num, den)
    assert _raises(ValueError, bootstrap_ratio_diff_ci, num, den[:2], num, den)


def test_validation_and_inputs_not_modified():
    c, t = np.array([1.0, 2.0, 3.0]), np.array([2.0, 3.0])
    c0, t0 = c.copy(), t.copy()
    bootstrap_diff_ci(c, t, n_boot=10), permutation_pvalue(c, t, n_perm=10)
    assert np.array_equal(c, c0) and np.array_equal(t, t0)
    assert _raises(ValueError, bootstrap_diff_ci, np.array([]), t)
    assert _raises(ValueError, bootstrap_diff_ci, c, t, alpha=1.5)
    assert _raises(ValueError, bootstrap_diff_ci, c, t, n_boot=0)
    assert _raises(ValueError, permutation_pvalue, c, np.array([]))
    assert _raises(ValueError, permutation_pvalue, c, t, n_perm=0)


def test_global_rng_untouched():
    np.random.seed(0)
    state = np.random.get_state()[1].copy()
    c, t = np.arange(5.0), np.arange(6.0)
    bootstrap_diff_ci(c, t, n_boot=20), permutation_pvalue(c, t, n_perm=20)
    bootstrap_ratio_diff_ci(c + 1, c + 2, t + 1, t + 2, n_boot=20)
    assert np.array_equal(np.random.get_state()[1], state)
