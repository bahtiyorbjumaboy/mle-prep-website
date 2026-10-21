import tracemalloc
from collections import defaultdict

import numpy as np

from solution import sample_negatives


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _positives(interactions):
    pos = defaultdict(set)
    for u, i in interactions:
        pos[u].add(i)
    return pos


def _assert_valid(out, interactions, n_neg, n_items):
    pos = _positives(interactions)
    assert out.shape == (len(interactions), n_neg) and np.issubdtype(out.dtype, np.integer)
    for row, (u, _) in zip(out, interactions):
        assert len(set(row.tolist())) == n_neg, "negatives within a row must be distinct"
        assert not set(row.tolist()) & pos[u], "a negative is a known positive of the user"
        assert row.min() >= 0 and row.max() < n_items


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "sample_negatives"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_excludes_all_user_positives_not_just_current_item():
    interactions = [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1)]
    for seed in range(20):
        out = sample_negatives(interactions, 8, 4, seed)
        _assert_valid(out, interactions, 4, 8)


def test_deterministic_and_seed_dependent():
    interactions = [(u, (3 * u) % 50) for u in range(30)]
    a = sample_negatives(interactions, 50, 5, seed=7)
    assert np.array_equal(a, sample_negatives(interactions, 50, 5, seed=7))
    assert not np.array_equal(a, sample_negatives(interactions, 50, 5, seed=8))
    w = np.arange(1, 51, dtype=float)
    b = sample_negatives(interactions, 50, 5, seed=7, popularity=w)
    assert np.array_equal(b, sample_negatives(interactions, 50, 5, seed=7, popularity=w))


def test_uniform_distribution_over_allowed_items():
    interactions = [(0, 0), (0, 1)] + [(0, 0)] * 9998
    out = sample_negatives(interactions, 6, 1, seed=1)
    freq = np.bincount(out[:, 0], minlength=6) / len(out)
    assert np.allclose(freq, [0, 0, 0.25, 0.25, 0.25, 0.25], atol=0.02)


def test_popularity_weighted_distribution_and_zero_weight_items():
    popularity = np.array([5.0, 1.0, 0.0, 2.0, 2.0, 10.0])
    interactions = [(0, 5)] * 20000
    out = sample_negatives(interactions, 6, 1, seed=2, popularity=popularity)
    freq = np.bincount(out[:, 0], minlength=6) / len(out)
    assert np.allclose(freq, [0.5, 0.1, 0.0, 0.2, 0.2, 0.0], atol=0.015)
    assert not (out == 2).any() and not (out == 5).any()


def test_without_replacement_within_row_follows_sequential_weights():
    # P(second = 2 | first = 1) = 1 / (1 + 8) when weights are [_, 1, 1, 8] and item 0 is positive.
    popularity = np.array([3.0, 1.0, 1.0, 8.0])
    out = sample_negatives([(0, 0)] * 30000, 4, 2, seed=3, popularity=popularity)
    _assert_valid(out[:200], [(0, 0)] * 200, 2, 4)
    first_is_1 = out[:, 0] == 1
    assert abs(np.mean(out[first_is_1, 1] == 2) - 1 / 9) < 0.02
    assert abs(np.mean(out[:, 0] == 3) - 0.8) < 0.01


def test_near_full_catalog_user_gets_exact_complement():
    positives = [i for i in range(200) if i not in (17, 123, 199)]
    interactions = [(9, i) for i in positives]
    out = sample_negatives(interactions, 200, 3, seed=4)
    assert all(sorted(row.tolist()) == [17, 123, 199] for row in out)
    weighted = sample_negatives(interactions, 200, 2, seed=4, popularity=np.ones(200))
    assert all(set(row.tolist()) <= {17, 123, 199} for row in weighted)
    no_123 = np.ones(200)
    no_123[123] = 0.0  # zero weight: never eligible, even when sampling the complement
    weighted = sample_negatives(interactions, 200, 2, seed=5, popularity=no_123)
    assert all(sorted(row.tolist()) == [17, 199] for row in weighted)


def test_insufficient_negative_pool_raises():
    assert _raises(ValueError, sample_negatives, [(0, 0), (0, 1), (0, 2)], 4, 2, 0)
    popularity = np.array([1.0, 0.0, 0.0, 1.0])
    # Items 1, 2 have zero weight, so only item 3 is eligible for a user who has item 0.
    assert _raises(ValueError, sample_negatives, [(0, 0)], 4, 2, 0, popularity)
    assert sample_negatives([(0, 0)], 4, 1, 0, popularity).tolist() == [[3]]


def test_validation():
    assert _raises(ValueError, sample_negatives, [(0, 5)], 5, 1, 0)
    assert _raises(ValueError, sample_negatives, [(0, -1)], 5, 1, 0)
    assert _raises(ValueError, sample_negatives, [(0, 1)], 5, 0, 0)
    assert _raises(ValueError, sample_negatives, [(0, 1)], 5, 1, 0, np.ones(4))
    assert _raises(ValueError, sample_negatives, [(0, 1)], 5, 1, 0, np.array([1.0, -1.0, 1.0, 1.0, 1.0]))
    assert _raises(ValueError, sample_negatives, [(0, 1)], 5, 1, 0, np.array([1.0, np.nan, 1.0, 1.0, 1.0]))
    assert sample_negatives([], 5, 2, 0).shape == (0, 2)


def test_large_catalog_uniform_sampling_avoids_per_user_catalog_arrays():
    rng = np.random.default_rng(5)
    n_items = 5_000_000
    interactions = [(u, int(i)) for u in range(40) for i in rng.integers(0, n_items, size=5)]
    tracemalloc.start()
    try:
        out = sample_negatives(interactions, n_items, 10, seed=6)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    _assert_valid(out, interactions, 10, n_items)
    assert peak < 2_000_000, f"peak {peak} bytes: a boolean catalog mask alone is {n_items} bytes"


def test_global_rng_untouched():
    np.random.seed(0)
    state = np.random.get_state()[1].copy()
    sample_negatives([(0, 1), (1, 2)], 20, 3, seed=1)
    sample_negatives([(0, 1), (1, 2)], 20, 3, seed=1, popularity=np.ones(20))
    assert np.array_equal(np.random.get_state()[1], state)
