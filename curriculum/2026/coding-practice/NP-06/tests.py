import os
import sys
import tracemalloc

import numpy as np

from solution import pairwise_knn, pairwise_sq_distances


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


def _double_loop(q, x, k):
    """Required mastery reference: explicit double loop, sort by (distance, index)."""
    dist = np.array([[float(np.sum((qi - xj) ** 2)) for xj in x] for qi in q])
    idx = np.array([sorted(range(len(x)), key=lambda j: (row[j], j))[:k] for row in dist])
    return dist, np.take_along_axis(dist, idx, axis=1), idx


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("pairwise_sq_distances", "pairwise_knn"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_hand_computed_distances_non_square():
    q = np.array([[0.0, 0.0], [1.0, 1.0]])
    x = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, 4.0]])
    d = pairwise_sq_distances(q, x)
    assert d.shape == (2, 3) and d.dtype == np.float64
    assert np.allclose(d, [[1.0, 4.0, 25.0], [1.0, 2.0, 13.0]])


def test_matches_double_loop_reference_exactly_on_integer_grid():
    rng = np.random.default_rng(0)
    q = rng.integers(-4, 5, size=(9, 3)).astype(float)
    x = rng.integers(-4, 5, size=(31, 3)).astype(float)  # many exact ties
    full, ref_d, ref_i = _double_loop(q, x, 7)
    assert np.array_equal(pairwise_sq_distances(q, x), full)
    d, i = pairwise_knn(q, x, 7)
    assert d.shape == (9, 7) and i.shape == (9, 7)
    assert np.array_equal(i, ref_i) and np.array_equal(d, ref_d)
    assert np.issubdtype(i.dtype, np.integer)


def test_ties_at_k_boundary_prefer_lower_index():
    x = np.array([[2.0, 0.0], [0.0, 1.0], [0.0, -1.0], [1.0, 0.0], [-1.0, 0.0], [0.0, 0.0]] + [[5.0, 5.0]] * 30)
    d, i = pairwise_knn(np.array([[0.0, 0.0]]), x, 3)
    assert i.tolist() == [[5, 1, 2]] and np.allclose(d, [[0.0, 1.0, 1.0]])
    d, i = pairwise_knn(np.array([[5.0, 5.0]]), x, 4)
    assert i.tolist() == [[6, 7, 8, 9]]


def test_tiny_negatives_clamped_but_small_positives_preserved():
    rng = np.random.default_rng(1)
    x = 1e4 + rng.normal(size=(50, 8))
    d = pairwise_sq_distances(x, x)
    assert np.all(d >= 0.0)
    assert np.allclose(np.diag(d), 0.0, atol=1e-6)
    assert np.allclose(d, d.T, atol=1e-6)
    # Genuinely small distances must survive (no thresholding away of small values).
    q = np.array([[0.0, 0.0]])
    x_small = np.array([[1e-3, 0.0], [0.0, 2e-3], [3e-4, 4e-4]])
    assert np.allclose(pairwise_sq_distances(q, x_small), [[1e-6, 4e-6, 2.5e-7]], rtol=1e-6, atol=0)


def test_self_neighbor_and_symmetry():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(20, 4))
    d, i = pairwise_knn(x, x, 3)
    assert np.array_equal(i[:, 0], np.arange(20))
    assert np.allclose(d[:, 0], 0.0, atol=1e-12)


def test_cosine_equivalence_after_normalization():
    rng = np.random.default_rng(3)
    q = rng.normal(size=(5, 6))
    x = rng.normal(size=(40, 6))
    qn = q / np.linalg.norm(q, axis=1, keepdims=True)
    xn = x / np.linalg.norm(x, axis=1, keepdims=True)
    d = pairwise_sq_distances(qn, xn)
    assert np.allclose(d, 2.0 - 2.0 * qn @ xn.T)
    _, i = pairwise_knn(qn, xn, 5)
    assert np.array_equal(i, np.argsort(-(qn @ xn.T), axis=1, kind="stable")[:, :5])


def test_k_equals_n_k_one_and_invalid():
    q, x = np.zeros((2, 2)), np.array([[3.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    assert pairwise_knn(q, x, 3)[1].tolist() == [[1, 2, 0], [1, 2, 0]]
    assert pairwise_knn(q, x, 1)[1].shape == (2, 1)
    assert _raises(ValueError, pairwise_knn, q, x, 4)
    assert _raises(ValueError, pairwise_knn, q, x, 0)
    assert _raises(ValueError, pairwise_knn, q, np.ones((3, 3)), 1)
    assert _raises(ValueError, pairwise_knn, q, x, 1, chunk_size=0)


def test_chunked_results_identical():
    rng = np.random.default_rng(4)
    q = rng.integers(-3, 4, size=(23, 2)).astype(float)
    x = rng.integers(-3, 4, size=(40, 2)).astype(float)
    full = pairwise_knn(q, x, 6)
    for chunk in (1, 4, 7, 23, 100):
        d, i = pairwise_knn(q, x, 6, chunk_size=chunk)
        assert np.array_equal(i, full[1]) and np.array_equal(d, full[0]), chunk


def test_chunking_bounds_peak_memory():
    rng = np.random.default_rng(5)
    q = rng.normal(size=(2000, 3))
    x = rng.normal(size=(1000, 3))
    tracemalloc.start()
    try:
        d, _ = pairwise_knn(q, x, 4, chunk_size=100)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    full_block = 2000 * 1000 * 8
    assert peak < 0.35 * full_block, f"peak {peak} bytes; the (m, n) distance matrix alone is {full_block}"
    assert d.shape == (2000, 4)


def test_no_m_n_d_broadcast_tensor():
    rng = np.random.default_rng(6)
    q = rng.normal(size=(100, 64))
    x = rng.normal(size=(300, 64))
    tracemalloc.start()
    try:
        pairwise_sq_distances(q, x)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert peak < 0.25 * (100 * 300 * 64 * 8), f"peak {peak} bytes suggests an (m, n, d) diff tensor"


def test_inputs_not_modified_and_vectorized():
    rng = np.random.default_rng(7)
    q, x = rng.normal(size=(300, 5)), rng.normal(size=(400, 5))
    q0, x0 = q.copy(), x.copy()
    (_, i), lines = _line_events(pairwise_knn, q, x, 3)
    assert lines <= 80, f"executed {lines} Python lines with chunk_size=None"
    (_, i2), lines = _line_events(pairwise_knn, q, x, 3, chunk_size=150)
    assert lines <= 120, f"executed {lines} Python lines for 2 chunks"
    assert np.array_equal(i, i2)
    assert np.array_equal(q, q0) and np.array_equal(x, x0)
