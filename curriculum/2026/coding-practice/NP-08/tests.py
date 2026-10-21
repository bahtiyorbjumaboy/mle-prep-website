import os
import sys

import numpy as np

from solution import bootstrap_means, monte_carlo_expectation, sample_categorical, sample_weighted, spawn_streams


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


def _uniform(rng, size):
    return rng.random(size)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("sample_categorical", "sample_weighted", "monte_carlo_expectation", "bootstrap_means", "spawn_streams"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_categorical_shape_replay_and_rng_advances():
    probs = np.array([[0.25, 0.75], [0.5, 0.5], [1.0, 0.0]])
    a = sample_categorical(probs, 20, np.random.default_rng(7))
    b = sample_categorical(probs, 20, np.random.default_rng(7))
    assert a.shape == (3, 20) and np.issubdtype(a.dtype, np.integer)
    assert np.array_equal(a, b)
    rng = np.random.default_rng(7)
    first, second = sample_categorical(probs, 50, rng), sample_categorical(probs, 50, rng)
    assert not np.array_equal(first, second), "successive calls must advance the passed rng"
    assert not np.array_equal(sample_categorical(probs, 50, np.random.default_rng(8)), first)
    assert np.all(a[2] == 0)


def test_categorical_frequencies_per_row():
    probs = np.array([[0.1, 0.2, 0.7], [0.6, 0.0, 0.4], [1 / 3, 1 / 3, 1 / 3], [0.0, 0.0, 1.0]])
    draws = sample_categorical(probs, 100_000, np.random.default_rng(1))
    freq = np.stack([np.bincount(row, minlength=3) for row in draws]) / 100_000
    assert np.allclose(freq, probs, atol=0.01)
    assert np.all(draws[1] != 1) and np.all(draws[3] == 2)


def test_categorical_renormalizes_rows_within_tolerance():
    # Sums to 0.99991: an un-renormalized inverse CDF returns id C ~9e-5 of the time.
    probs = np.array([[0.3, 0.3, 0.39991], [0.5, 0.49991, 0.0]])
    draws = sample_categorical(probs, 200_000, np.random.default_rng(2))
    assert draws.min() >= 0 and draws.max() <= 2
    assert np.all(draws[1] != 2)


def test_categorical_tiny_probabilities_and_validation():
    probs = np.array([[1e-12, 1 - 1e-12], [0.0, 1.0]])
    draws = sample_categorical(probs, 1000, np.random.default_rng(3))
    assert np.all(draws[1] == 1) and np.mean(draws[0] == 1) > 0.99
    rng = np.random.default_rng(0)
    assert _raises(ValueError, sample_categorical, np.array([[0.5, 0.6]]), 3, rng)
    assert _raises(ValueError, sample_categorical, np.array([[1.2, -0.2]]), 3, rng)
    assert _raises(ValueError, sample_categorical, np.array([[np.nan, 1.0]]), 3, rng)
    assert _raises(ValueError, sample_categorical, np.array([0.5, 0.5]), 3, rng)


def test_categorical_vectorized():
    rng = np.random.default_rng(4)
    probs = rng.dirichlet(np.ones(5), size=2000)
    out, lines = _line_events(sample_categorical, probs, 50, rng)
    assert out.shape == (2000, 50)
    assert lines <= 40, f"executed {lines} Python lines; expected no loop over rows or draws"


def test_weighted_unnormalized_ints_and_lists():
    w = np.array([1, 3, 0, 6])
    draws = sample_weighted(w, 100_000, np.random.default_rng(5))
    assert draws.shape == (100_000,) and np.issubdtype(draws.dtype, np.integer)
    assert np.allclose(np.bincount(draws, minlength=4) / 100_000, [0.1, 0.3, 0.0, 0.6], atol=0.01)
    assert np.all(draws != 2)
    assert np.array_equal(w, [1, 3, 0, 6])
    listed = sample_weighted([2.0, 2.0], 10, np.random.default_rng(5))
    assert listed.shape == (10,)


def test_weighted_extreme_magnitudes():
    huge = sample_weighted(np.array([1e308, 1e308, 0.0]), 20_000, np.random.default_rng(6))
    assert np.all(huge != 2) and abs(np.mean(huge == 0) - 0.5) < 0.02
    tiny = sample_weighted(np.array([1e-310, 3e-310]), 20_000, np.random.default_rng(6))
    assert abs(np.mean(tiny == 1) - 0.75) < 0.02


def test_weighted_does_not_mutate_and_validates():
    w = np.array([2.0, 6.0])
    sample_weighted(w, 5, np.random.default_rng(0))
    assert np.array_equal(w, [2.0, 6.0])
    rng = np.random.default_rng(0)
    assert _raises(ValueError, sample_weighted, np.zeros(3), 5, rng)
    assert _raises(ValueError, sample_weighted, np.array([1.0, -1.0, 2.0]), 5, rng)
    assert _raises(ValueError, sample_weighted, np.array([1.0, np.inf]), 5, rng)
    assert _raises(ValueError, sample_weighted, np.ones((2, 2)), 5, rng)


def test_monte_carlo_estimates_known_expectations():
    est, se = monte_carlo_expectation(lambda x: x ** 2, lambda r, n: r.normal(size=n), 200_000, np.random.default_rng(9))
    assert abs(est - 1.0) < 5 * se and 0.002 < se < 0.005  # sd of X^2 is sqrt(2)
    est, se = monte_carlo_expectation(lambda u: (u < 0.3).astype(float), _uniform, 100_000, np.random.default_rng(9))
    assert abs(est - 0.3) < 5 * se
    assert np.isclose(se, np.sqrt(0.3 * 0.7 / 100_000), rtol=0.05)


def test_monte_carlo_standard_error_definition_and_replay():
    rng = np.random.default_rng(10)
    est, se = monte_carlo_expectation(lambda u: 3 * u, _uniform, 1000, rng)
    values = 3 * np.random.default_rng(10).random(1000)
    assert np.isclose(est, values.mean())
    assert np.isclose(se, values.std(ddof=1) / np.sqrt(1000))


def test_monte_carlo_batches_respect_memory_and_match_unbatched():
    sizes = []

    def recording(rng, size):
        sizes.append(size)
        return rng.random(size)

    unbatched = monte_carlo_expectation(lambda u: u, _uniform, 10_007, np.random.default_rng(11))
    batched = monte_carlo_expectation(lambda u: u, recording, 10_007, np.random.default_rng(11), batch_size=1000)
    assert max(sizes) <= 1000 and sum(sizes) == 10_007
    assert np.allclose(batched, unbatched, rtol=1e-10, atol=0)


def test_monte_carlo_batched_variance_is_numerically_stable():
    f = lambda u: 1e8 + u  # noqa: E731
    unbatched = monte_carlo_expectation(f, _uniform, 20_000, np.random.default_rng(12))
    batched = monte_carlo_expectation(f, _uniform, 20_000, np.random.default_rng(12), batch_size=777)
    expected_se = np.sqrt(1 / 12 / 20_000)
    assert np.isclose(unbatched[1], expected_se, rtol=0.05)
    assert np.isclose(batched[1], unbatched[1], rtol=1e-6), "merge batch variances exactly, not via E[f^2]-E[f]^2"
    assert _raises(ValueError, monte_carlo_expectation, f, _uniform, 1, np.random.default_rng(0))
    assert _raises(ValueError, monte_carlo_expectation, f, _uniform, 10, np.random.default_rng(0), 0)


def test_bootstrap_resamples_rows_with_replacement():
    data = np.column_stack([np.arange(50.0), 10 * np.arange(50.0)])
    means = bootstrap_means(data, 400, np.random.default_rng(13))
    assert means.shape == (400, 2)
    assert np.allclose(means[:, 1], 10 * means[:, 0]), "rows are the resampling unit"
    assert np.unique(means[:, 0]).size > 50, "with replacement, not a permutation"
    one_d = bootstrap_means(np.arange(50.0), 400, np.random.default_rng(13))
    assert one_d.shape == (400,)


def test_bootstrap_distribution_and_replay():
    data = np.random.default_rng(14).exponential(size=200)
    means = bootstrap_means(data, 4000, np.random.default_rng(15))
    assert abs(means.mean() - data.mean()) < 0.01
    assert np.isclose(means.std(), data.std() / np.sqrt(200), rtol=0.1)
    assert np.array_equal(means, bootstrap_means(data, 4000, np.random.default_rng(15)))
    assert np.all(bootstrap_means(np.array([4.2]), 3, np.random.default_rng(0)) == 4.2)
    assert _raises(ValueError, bootstrap_means, np.array([]), 3, np.random.default_rng(0))
    assert _raises(ValueError, bootstrap_means, data, 0, np.random.default_rng(0))


def test_bootstrap_vectorized():
    data = np.random.default_rng(16).normal(size=300)
    out, lines = _line_events(bootstrap_means, data, 2000, np.random.default_rng(17))
    assert out.shape == (2000,)
    assert lines <= 30, f"executed {lines} Python lines; expected no loop over resamples"


def test_global_numpy_rng_untouched():
    np.random.seed(123)
    before = np.random.get_state()[1].copy(), np.random.get_state()[2]
    rng = np.random.default_rng(0)
    sample_categorical(np.array([[0.5, 0.5]]), 10, rng)
    sample_weighted(np.array([1.0, 2.0]), 10, rng)
    monte_carlo_expectation(lambda u: u, _uniform, 10, rng, batch_size=3)
    bootstrap_means(np.arange(5.0), 3, rng)
    after = np.random.get_state()
    assert np.array_equal(before[0], after[1]) and before[1] == after[2]


def test_spawn_streams_independent_and_reproducible():
    a = [g.random(5) for g in spawn_streams(42, 3)]
    b = [g.random(5) for g in spawn_streams(42, 3)]
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    assert not np.allclose(a[0], a[1]) and not np.allclose(a[1], a[2])
    naive = [np.random.default_rng(42 + i).random(5) for i in range(3)]
    assert not any(np.array_equal(x, y) for x, y in zip(a, naive))
    assert not np.array_equal(a[0], np.random.default_rng(42).random(5))
