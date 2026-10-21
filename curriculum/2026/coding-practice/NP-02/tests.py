import os
import sys
import tracemalloc

import numpy as np

from solution import batched_cosine_topk, normalize_rows


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


def _reference(queries, candidates, k):
    """Scalar full-sort reference: per pair cosine, then sort by (-score, index)."""
    out_i, out_s = [], []
    for q in queries:
        scored = []
        for j, x in enumerate(candidates):
            denom = np.linalg.norm(q) * np.linalg.norm(x)
            scored.append((-(float(q @ x) / denom if denom > 0 else 0.0), j))
        scored.sort()
        out_i.append([j for _, j in scored[:k]])
        out_s.append([-s for s, _ in scored[:k]])
    return np.array(out_i), np.array(out_s)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("normalize_rows", "batched_cosine_topk"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_normalize_rows_unit_norm_and_zero_rows():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(6, 3)) * np.array([[1e-3], [1], [1e3], [5], [1], [1]])
    x[4] = 0.0
    before = x.copy()
    out = normalize_rows(x)
    assert out.shape == (6, 3) and out.dtype == np.float64
    assert np.all(np.isfinite(out)) and np.allclose(out[4], 0.0)
    assert np.allclose(np.linalg.norm(out[[0, 1, 2, 3, 5]], axis=1), 1.0)
    assert np.allclose(out[0], x[0] / np.linalg.norm(x[0]))
    assert np.array_equal(x, before)
    assert np.allclose(normalize_rows(np.array([[3, 4]])), [[0.6, 0.8]])


def test_hand_computed_cosine_not_dot_product():
    q = np.array([[1.0, 0.0], [0.0, 2.0]])
    x = np.array([[10.0, 10.0], [1.0, 0.0], [0.0, 0.5], [-3.0, 0.0]])
    idx, scores = batched_cosine_topk(q, x, 2)
    assert idx.shape == (2, 2) and scores.shape == (2, 2)
    assert idx.tolist() == [[1, 0], [2, 0]]
    assert np.allclose(scores, [[1.0, np.sqrt(0.5)], [1.0, np.sqrt(0.5)]])
    assert np.issubdtype(idx.dtype, np.integer) and scores.dtype == np.float64


def test_matches_full_sort_reference_non_square():
    rng = np.random.default_rng(1)
    q = rng.normal(size=(7, 5))
    x = rng.normal(size=(23, 5))
    for k in (1, 4, 23):
        idx, scores = batched_cosine_topk(q, x, k)
        ref_i, ref_s = _reference(q, x, k)
        assert idx.shape == (7, k)
        assert np.array_equal(idx, ref_i) and np.allclose(scores, ref_s)


def test_single_query_keeps_two_dimensional_output():
    idx, scores = batched_cosine_topk(np.array([[1.0, 1.0]]), np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]), 3)
    assert idx.shape == (1, 3) and scores.shape == (1, 3)
    assert idx[0, 0] == 1


def test_ties_are_ordered_by_candidate_index():
    # Exact ties: these dot products and norms are exactly representable.
    x = np.array([[0.0, 1.0], [2.0, 0.0], [1.0, 0.0], [0.0, 3.0], [4.0, 0.0], [-1.0, 0.0]])
    idx, scores = batched_cosine_topk(np.array([[5.0, 0.0]]), x, 5)
    assert idx.tolist() == [[1, 2, 4, 0, 3]]
    assert np.allclose(scores, [[1, 1, 1, 0, 0]])


def test_many_ties_stable_ordering():
    rng = np.random.default_rng(2)
    labels = rng.integers(0, 3, size=200)
    x = np.eye(3)[labels] * 2.0  # three exact score levels for query e0
    q = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    idx, _ = batched_cosine_topk(q, x, 120)
    for row, axis in zip(idx, (0, 2)):
        order = sorted(range(200), key=lambda j: (-int(labels[j] == axis), j))
        assert row.tolist() == order[:120]


def test_zero_vectors_score_zero_not_nan():
    q = np.array([[0.0, 0.0], [1.0, 0.0]])
    x = np.array([[0.0, 0.0], [-1.0, 0.0], [1.0, 1.0]])
    idx, scores = batched_cosine_topk(q, x, 3)
    assert np.all(np.isfinite(scores))
    assert idx[0].tolist() == [0, 1, 2] and np.allclose(scores[0], 0.0)
    assert idx[1].tolist() == [2, 0, 1] and np.allclose(scores[1], [np.sqrt(0.5), 0.0, -1.0])


def test_large_and_tiny_magnitudes_are_finite():
    q = np.array([[1e150, 1e150], [1e-150, 0.0]])
    x = np.array([[3e150, 0.0], [0.0, 2e-150], [1e-150, 1e-150]])
    idx, scores = batched_cosine_topk(q, x, 3)
    assert np.all(np.isfinite(scores)) and np.all(np.abs(scores) <= 1 + 1e-12)
    assert idx[0].tolist() == [2, 0, 1] and idx[1].tolist() == [0, 2, 1]


def test_chunking_gives_identical_results_including_ties():
    x = np.array([[0.0, 1.0], [2.0, 0.0], [1.0, 0.0], [0.0, 3.0], [4.0, 0.0], [-1.0, 0.0], [8.0, 0.0]])
    q = np.array([[5.0, 0.0], [0.0, 1.0]])
    full = batched_cosine_topk(q, x, 4)
    for chunk in (1, 2, 3, 7, 50):
        idx, scores = batched_cosine_topk(q, x, 4, chunk_size=chunk)
        assert np.array_equal(idx, full[0]), f"chunk_size={chunk}"
        assert np.allclose(scores, full[1])
    assert full[0].tolist() == [[1, 2, 4, 6], [0, 3, 1, 2]]
    rng = np.random.default_rng(3)
    q, x = rng.normal(size=(9, 4)), rng.normal(size=(101, 4))
    ref = _reference(q, x, 10)
    idx, scores = batched_cosine_topk(q, x, 10, chunk_size=8)
    assert np.array_equal(idx, ref[0]) and np.allclose(scores, ref[1])


def test_chunking_bounds_peak_memory():
    rng = np.random.default_rng(4)
    q = rng.normal(size=(50, 4))
    x = rng.normal(size=(20000, 4))
    tracemalloc.start()
    try:
        idx, _ = batched_cosine_topk(q, x, 5, chunk_size=500)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    full_matrix = 50 * 20000 * 8
    assert peak < 0.4 * full_matrix, f"peak {peak} bytes; the (m, n) score matrix alone is {full_matrix}"
    assert idx.shape == (50, 5)


def test_k_bounds_and_validation():
    q, x = np.ones((2, 3)), np.ones((4, 3))
    assert batched_cosine_topk(q, x, 4)[0].shape == (2, 4)
    assert _raises(ValueError, batched_cosine_topk, q, x, 0)
    assert _raises(ValueError, batched_cosine_topk, q, x, 5)
    assert _raises(ValueError, batched_cosine_topk, q, np.ones((4, 2)), 1)
    assert _raises(ValueError, batched_cosine_topk, np.ones(3), x, 1)
    assert _raises(ValueError, batched_cosine_topk, q, x, 1, chunk_size=0)


def test_inputs_not_modified():
    rng = np.random.default_rng(5)
    q, x = rng.normal(size=(3, 4)), rng.normal(size=(8, 4))
    q0, x0 = q.copy(), x.copy()
    batched_cosine_topk(q, x, 3)
    batched_cosine_topk(q, x, 3, chunk_size=3)
    assert np.array_equal(q, q0) and np.array_equal(x, x0)


def test_vectorized_no_python_loops_over_queries_or_candidates():
    rng = np.random.default_rng(6)
    q, x = rng.normal(size=(300, 8)), rng.normal(size=(400, 8))
    (idx, _), lines = _line_events(batched_cosine_topk, q, x, 5)
    assert lines <= 120, f"executed {lines} Python lines with chunk_size=None"
    (idx2, _), lines = _line_events(batched_cosine_topk, q, x, 5, chunk_size=200)
    assert lines <= 200, f"executed {lines} Python lines for 2 chunks"
    assert np.array_equal(idx, idx2)
