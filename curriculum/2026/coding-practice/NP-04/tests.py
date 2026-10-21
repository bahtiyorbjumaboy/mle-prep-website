import math
import os
import sys

import numpy as np

from solution import score_ragged


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


def _slow(user_vectors, item_vectors, item_ids, lengths):
    """Independent copy of the given slow reference (the learner may edit theirs)."""
    probs, start = [], 0
    for u, length in enumerate(lengths):
        segment = item_ids[start:start + length]
        start += length
        scores = [sum(float(a) * float(b) for a, b in zip(user_vectors[u], item_vectors[i])) for i in segment]
        if scores:
            top = max(scores)
            exps = [math.exp(s - top) for s in scores]
            probs.extend(e / sum(exps) for e in exps)
    return np.array(probs, dtype=float)


def _fixture(seed, users=6, items=9, d=4, max_len=5, scale=1.0):
    rng = np.random.default_rng(seed)
    # intp (the platform index type) keeps np.repeat/indexing valid on 32-bit Pyodide.
    lengths = rng.integers(0, max_len + 1, size=users).astype(np.intp)
    return (
        rng.normal(size=(users, d)) * scale,
        rng.normal(size=(items, d)) * scale,
        rng.integers(0, items, size=int(lengths.sum())).astype(np.intp),
        lengths,
    )


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "score_ragged"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example_preserves_order():
    users = np.array([[1.0, 0.0], [0.0, 1.0]])
    items = np.array([[1.0, 0.0], [0.0, 1.0], [2.0, 2.0]])
    out = score_ragged(users, items, np.array([2, 0, 1]), np.array([2, 1]))
    e = np.exp([2.0, 1.0])
    assert out.shape == (3,) and out.dtype == np.float64
    assert np.allclose(out, [e[0] / e.sum(), e[1] / e.sum(), 1.0])


def test_equivalent_to_slow_reference_on_random_fixtures():
    for seed in range(5):
        args = _fixture(seed)
        assert np.allclose(score_ragged(*args), _slow(*args), rtol=1e-9, atol=1e-12)


def test_empty_segments_at_start_middle_and_end():
    users = np.array([[1.0, 2.0], [0.5, -1.0], [3.0, 0.0], [1.0, 1.0], [-2.0, 1.0]])
    items = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, -1.0], [0.3, 0.3]])
    lengths = np.array([0, 3, 0, 2, 0])
    ids = np.array([1, 3, 0, 2, 2])
    out = score_ragged(users, items, ids, lengths)
    assert out.shape == (5,)
    assert np.allclose(out, _slow(users, items, ids, lengths))
    assert np.allclose([out[:3].sum(), out[3:].sum()], 1.0)


def test_single_candidate_segments_and_all_empty():
    users, items = np.ones((3, 2)), np.ones((2, 2))
    assert np.allclose(score_ragged(users, items, np.array([1, 0, 1]), np.array([1, 1, 1])), 1.0)
    out = score_ragged(users, items, np.array([], dtype=int), np.array([0, 0, 0]))
    assert out.shape == (0,)


def test_duplicate_ids_in_segment_are_scored_in_place():
    users = np.array([[1.0, 0.0]])
    items = np.array([[3.0, 0.0], [0.0, 0.0]])
    out = score_ragged(users, items, np.array([0, 1, 0]), np.array([3]))
    e = np.exp([3.0, 0.0, 3.0])
    assert np.allclose(out, e / e.sum())


def test_segments_each_sum_to_one():
    users, items, ids, lengths = _fixture(11, users=40, items=15, max_len=7)
    out = score_ragged(users, items, ids, lengths)
    assert 0 in lengths  # the fixture exercises empty segments
    starts = np.cumsum(lengths) - lengths
    for s, n in zip(starts, lengths):
        if n:
            assert np.isclose(out[s:s + n].sum(), 1.0)


def test_large_scores_do_not_overflow():
    users, items, ids, lengths = _fixture(3, scale=20.0)  # dot products in the hundreds/thousands
    users[0] = 40.0
    items[:] = np.where(np.arange(items.shape[0])[:, None] % 2 == 0, 40.0, -40.0)
    out = score_ragged(users, items, ids, lengths)
    assert np.all(np.isfinite(out))
    assert np.allclose(out, _slow(users, items, ids, lengths), rtol=1e-9, atol=1e-12)


def test_float32_inputs_within_tolerance():
    users, items, ids, lengths = _fixture(4, users=30, items=12, d=16)
    out = score_ragged(users.astype(np.float32), items.astype(np.float32), ids, lengths)
    assert out.dtype == np.float64
    assert np.allclose(out, _slow(users, items, ids, lengths), atol=1e-5)


def test_inputs_not_modified():
    users, items, ids, lengths = _fixture(5)
    copies = [a.copy() for a in (users, items, ids, lengths)]
    score_ragged(users, items, ids, lengths)
    assert all(np.array_equal(a, b) for a, b in zip((users, items, ids, lengths), copies))


def test_invalid_inputs_raise():
    users, items = np.ones((2, 3)), np.ones((4, 3))
    assert _raises(ValueError, score_ragged, users, items, np.array([0, 1]), np.array([1, 2]))
    assert _raises(ValueError, score_ragged, users, items, np.array([0, 1]), np.array([2]))
    assert _raises(ValueError, score_ragged, users, items, np.array([0, 1]), np.array([3, -1]))
    assert _raises(ValueError, score_ragged, users, items, np.array([0, 4]), np.array([1, 1]))
    assert _raises(ValueError, score_ragged, users, items, np.array([0, -1]), np.array([1, 1]))
    assert _raises(ValueError, score_ragged, users, np.ones((4, 2)), np.array([0, 1]), np.array([1, 1]))
    # np.repeat silently broadcasts a length-1 `lengths` across all users.
    assert _raises(ValueError, score_ragged, users, items, np.array([0, 1, 2, 3]), np.array([2]))


def test_vectorized_no_python_loops():
    users, items, ids, lengths = _fixture(6, users=3000, items=500, d=8, max_len=6)
    out, lines = _line_events(score_ragged, users, items, ids, lengths)
    assert lines <= 80, f"executed {lines} Python lines for 3000 users; expected no per-user loop"
    starts = np.cumsum(lengths) - lengths
    probe = np.flatnonzero(lengths)[:50]
    for u in probe:
        seg = slice(starts[u], starts[u] + lengths[u])
        assert np.allclose(out[seg], _slow(users[u:u + 1], items, ids[seg], lengths[u:u + 1]))
