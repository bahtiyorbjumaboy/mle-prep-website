import math
import sys
import time

import numpy as np

import solution
from solution import user_amount_features


def _baseline(user_ids, amounts, merchants, known_merchants):
    """Frozen copy of the pre-regression implementation: the benchmark baseline."""
    known = list(known_merchants)
    rows = []
    for i in range(len(amounts)):
        same_user = user_ids == user_ids[i]
        user_amounts = np.sort(amounts[same_user].copy())
        rows.append(
            [
                user_amounts.sum(),
                float(same_user.sum()),
                np.searchsorted(user_amounts, amounts[i], side="right") / len(user_amounts),
                1.0 if merchants[i] in known else 0.0,
            ]
        )
    return np.array(rows, dtype=float).reshape(-1, 4)


def _reference(user_ids, amounts, merchants, known_merchants):
    """Independent pure-Python oracle for the documented columns."""
    by_user = {}
    for user, amount in zip(user_ids.tolist(), amounts.tolist()):
        by_user.setdefault(user, []).append(amount)
    known = set(known_merchants)
    rows = []
    for user, amount, merchant in zip(user_ids.tolist(), amounts.tolist(), merchants.tolist()):
        group = by_user[user]
        rows.append(
            [math.fsum(group), len(group), sum(x <= amount for x in group) / len(group), float(merchant in known)]
        )
    return np.array(rows, dtype=float).reshape(-1, 4)


def _events(n, n_users, seed=0):
    rng = np.random.default_rng(seed)
    user_ids = rng.integers(0, n_users, size=n) * 7919 + 13  # sparse, non-contiguous ids
    amounts = np.round(rng.gamma(2.0, 30.0, size=n), 0)  # coarse rounding -> many ties
    merchants = np.array([f"m{v}" for v in rng.integers(0, 300, size=n)])
    known = [f"m{v}" for v in range(0, 300, 3)] + ["m2990"]  # "m2990" must not match "m299"
    return user_ids, amounts, merchants, known


def _close(actual, expected):
    assert actual.shape == expected.shape, (actual.shape, expected.shape)
    assert np.allclose(actual, expected, rtol=1e-12, atol=1e-9), np.abs(actual - expected).max()


def test_hand_computed_example():
    out = user_amount_features(
        np.array([5, 5, 5, 9]), np.array([10.0, 30.0, 10.0, 7.0]), np.array(["a", "b", "c", "a"]), ["a", "zz"]
    )
    _close(out, np.array([[50, 3, 2 / 3, 1], [50, 3, 1, 0], [50, 3, 2 / 3, 0], [7, 1, 1, 1]], dtype=float))


def test_matches_reference_on_random_events():
    for n, users, seed in [(3000, 400, 0), (500, 3, 1), (200, 200, 2)]:
        events = _events(n, users, seed)
        _close(user_amount_features(*events), _reference(*events))


def test_outputs_unchanged_from_previous_implementation():
    events = _events(1500, 250, 3)
    _close(user_amount_features(*events), _baseline(*events))


def test_edge_cases():
    empty = user_amount_features(np.array([], dtype=int), np.array([]), np.array([], dtype=str), ["a"])
    assert empty.shape == (0, 4)
    single = user_amount_features(np.array([1]), np.array([4.0]), np.array(["m299"]), ["m2990"])
    _close(single, np.array([[4.0, 1.0, 1.0, 0.0]]))
    no_known = user_amount_features(np.array([1, 1]), np.array([2.0, 2.0]), np.array(["a", "b"]), [])
    _close(no_known, np.array([[4.0, 2.0, 1.0, 0.0], [4.0, 2.0, 1.0, 0.0]]))


def test_row_order_is_preserved():
    user_ids, amounts, merchants, known = _events(800, 90, 4)
    perm = np.random.default_rng(5).permutation(800)
    base = user_amount_features(user_ids, amounts, merchants, known)
    _close(user_amount_features(user_ids[perm], amounts[perm], merchants[perm], known), base[perm])


def _line_events(*args):
    """Counts interpreted line events executed in the solution module during one call."""
    filename = solution.user_amount_features.__code__.co_filename
    count = 0

    def local(frame, event, arg):
        nonlocal count
        if event == "line":
            count += 1
        return local

    def global_trace(frame, event, arg):
        return local if frame.f_code.co_filename == filename else None

    previous = sys.gettrace()
    sys.settrace(global_trace)
    try:
        user_amount_features(*args)
    finally:
        sys.settrace(previous)
    return count


def test_no_per_row_or_per_user_python_iteration():
    small = _line_events(*_events(400, 80, 6))
    large = _line_events(*_events(3200, 640, 6))
    assert large <= small + 10, f"interpreted lines grew from {small} to {large} with 8x rows/users"


def test_peak_memory_is_linear_in_rows():
    try:
        import tracemalloc
    except ImportError:  # some embedded runtimes ship without it
        return
    peaks = []
    for n in (1000, 4000):
        events = _events(n, n // 5, 7)
        tracemalloc.start()
        try:
            user_amount_features(*events)
            peaks.append(tracemalloc.get_traced_memory()[1])
        finally:
            tracemalloc.stop()
    assert peaks[1] < 8 * peaks[0], f"peak memory {peaks[0]} -> {peaks[1]} bytes for 4x rows"


def test_material_speedup_over_previous_implementation():
    events = _events(3000, 600, 8)
    start = time.perf_counter()
    expected = _baseline(*events)
    baseline = time.perf_counter() - start
    candidate = math.inf
    for _ in range(3):
        start = time.perf_counter()
        out = user_amount_features(*events)
        candidate = min(candidate, time.perf_counter() - start)
    _close(out, expected)
    assert baseline / candidate >= 5, f"speedup only {baseline / candidate:.1f}x"
