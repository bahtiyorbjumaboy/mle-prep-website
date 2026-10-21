import math
import os
import sys

import numpy as np

from solution import cosine_retrieve, cosine_retrieve_batch, cosine_similarity


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


def _reference(q, x, k):
    scores = [cosine_ref(q, row) for row in x]
    order = sorted(range(len(x)), key=lambda j: (-scores[j], j))[:k]
    return np.array(order), np.array([scores[j] for j in order])


def cosine_ref(a, b):
    na, nb = math.sqrt(sum(v * v for v in a)), math.sqrt(sum(v * v for v in b))
    return 0.0 if na == 0 or nb == 0 else sum(x * y for x, y in zip(a, b)) / (na * nb)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("cosine_similarity", "cosine_retrieve", "cosine_retrieve_batch"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_scalar_cosine_hand_computed():
    assert math.isclose(cosine_similarity([1, 0], [0, 1]), 0.0, abs_tol=1e-12)
    assert math.isclose(cosine_similarity([1, 2, 2], [2, 4, 4]), 1.0)
    assert math.isclose(cosine_similarity([1, 0], [-3, 0]), -1.0)
    assert math.isclose(cosine_similarity([3, 4], [4, 3]), 24 / 25)
    assert isinstance(cosine_similarity([1.0, 1.0], [1.0, 0.0]), float)


def test_scalar_cosine_zero_vector_and_validation():
    assert cosine_similarity([0, 0, 0], [1, 2, 3]) == 0.0
    assert cosine_similarity([0, 0], [0, 0]) == 0.0
    assert _raises(ValueError, cosine_similarity, [1, 2], [1, 2, 3])


def test_single_query_cosine_not_dot_and_1d_shapes():
    q = np.array([1.0, 0.0])
    x = np.array([[100.0, 100.0], [0.5, 0.0], [-2.0, 0.0], [0.0, 3.0]])
    idx, scores = cosine_retrieve(q, x, 2)
    assert idx.shape == (2,) and scores.shape == (2,)
    assert idx.tolist() == [1, 0] and np.allclose(scores, [1.0, np.sqrt(0.5)])


def test_single_query_matches_scalar_reference():
    rng = np.random.default_rng(0)
    q, x = rng.normal(size=7), rng.normal(size=(40, 7))
    for k in (1, 5, 40):
        idx, scores = cosine_retrieve(q, x, k)
        ref_i, ref_s = _reference(q.tolist(), x.tolist(), k)
        assert np.array_equal(idx, ref_i) and np.allclose(scores, ref_s)


def test_ties_and_zero_vectors():
    x = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0], [4.0, 0.0], [0.0, 0.0]])
    idx, scores = cosine_retrieve(np.array([3.0, 0.0]), x, 5)
    assert idx.tolist() == [1, 3, 0, 2, 4] and np.all(np.isfinite(scores))
    idx, scores = cosine_retrieve(np.zeros(2), x, 3)
    assert idx.tolist() == [0, 1, 2] and np.allclose(scores, 0.0)


def test_batch_matches_single_query_and_keeps_2d():
    rng = np.random.default_rng(1)
    q, x = rng.normal(size=(6, 5)), rng.normal(size=(30, 5))
    idx, scores = cosine_retrieve_batch(q, x, 4)
    assert idx.shape == (6, 4) and scores.shape == (6, 4)
    for row in range(6):
        single = cosine_retrieve(q[row], x, 4)
        assert np.array_equal(idx[row], single[0]) and np.allclose(scores[row], single[1])
    one = cosine_retrieve_batch(q[:1], x, 3)
    assert one[0].shape == (1, 3)


def test_unit_normalized_candidates_and_scale_invariance():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(25, 4))
    xn = x / np.linalg.norm(x, axis=1, keepdims=True)
    q = rng.normal(size=(3, 4))
    a = cosine_retrieve_batch(q, x, 5)
    b = cosine_retrieve_batch(q * 1e6, xn * 1e-3, 5)
    assert np.array_equal(a[0], b[0]) and np.allclose(a[1], b[1])
    qn = q / np.linalg.norm(q, axis=1, keepdims=True)
    assert np.allclose(a[1], np.sort(qn @ xn.T, axis=1)[:, ::-1][:, :5])


def test_k_bounds_and_dimension_mismatch():
    x = np.ones((3, 2))
    assert _raises(ValueError, cosine_retrieve, np.ones(2), x, 4)
    assert _raises(ValueError, cosine_retrieve, np.ones(2), x, 0)
    assert _raises(ValueError, cosine_retrieve, np.ones(3), x, 1)
    assert _raises(ValueError, cosine_retrieve_batch, np.ones((2, 2)), x, 4)
    assert _raises(ValueError, cosine_retrieve_batch, np.ones((2, 3)), x, 1)


def test_inputs_not_modified():
    rng = np.random.default_rng(3)
    q, x = rng.normal(size=(2, 3)), rng.normal(size=(5, 3))
    q0, x0 = q.copy(), x.copy()
    cosine_retrieve(q[0], x, 2), cosine_retrieve_batch(q, x, 2)
    assert np.array_equal(q, q0) and np.array_equal(x, x0)


def test_vectorized():
    rng = np.random.default_rng(4)
    x = rng.normal(size=(3000, 8))
    _, lines = _line_events(cosine_retrieve, rng.normal(size=8), x, 5)
    assert lines <= 40, f"single query executed {lines} Python lines; no loop over candidates"
    _, lines = _line_events(cosine_retrieve_batch, rng.normal(size=(200, 8)), x[:500], 5)
    assert lines <= 40, f"batch executed {lines} Python lines; no loop over queries"
