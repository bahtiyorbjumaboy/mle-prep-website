import os
import sys

import numpy as np

from solution import kmeans


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


def _sq(x, c):
    return ((x[:, None, :] - c[None, :, :]) ** 2).sum(-1)


def _objective(x, c):
    return float(_sq(x, c).min(axis=1).sum())


def _blobs(seed=0):
    rng = np.random.default_rng(seed)
    centers = np.array([[0.0, 0.0], [50.0, 0.0], [0.0, 50.0]])
    truth = np.repeat(np.arange(3), 100)
    return centers[truth] + rng.normal(size=(300, 2)), truth


def _line_x():
    return np.array([[0.0], [1.0], [2.0], [10.0], [11.0], [12.0]])


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "kmeans"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_one_lloyd_iteration_hand_computed():
    labels, centers, history = kmeans(_line_x(), 2, init=np.array([[0.0], [1.0]]), max_iter=1)
    assert np.allclose(centers, [[0.0], [7.2]])
    assert len(history) == 1 and np.isclose(history[0], 50.32)
    assert labels.tolist() == [0, 0, 0, 1, 1, 1]


def test_converges_to_fixed_point():
    labels, centers, history = kmeans(_line_x(), 2, init=np.array([[0.0], [1.0]]))
    assert np.allclose(centers, [[1.0], [11.0]])
    assert labels.tolist() == [0, 0, 0, 1, 1, 1]
    assert np.isclose(history[-1], 4.0) and len(history) <= 5


def test_assignment_ties_go_to_lowest_center_index():
    x = np.array([[0.0], [2.0], [1.0]])
    _, centers, _ = kmeans(x, 2, init=np.array([[0.0], [2.0]]), max_iter=1)
    assert np.allclose(centers, [[0.5], [2.0]])


def test_shapes_types_and_label_consistency():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(40, 3))
    labels, centers, history = kmeans(x, 4, seed=2, max_iter=2)
    assert labels.shape == (40,) and np.issubdtype(labels.dtype, np.integer)
    assert centers.shape == (4, 3) and centers.dtype == np.float64
    assert isinstance(history, list) and 1 <= len(history) <= 2
    d = _sq(x, centers)
    assert np.array_equal(labels, np.argmin(d, axis=1))
    assert np.isclose(history[-1], _objective(x, centers))


def test_objective_non_increasing_and_centers_are_cluster_means():
    rng = np.random.default_rng(3)
    x = rng.normal(size=(120, 2)) * np.array([5.0, 1.0])
    labels, centers, history = kmeans(x, 5, seed=4, tol=1e-10, max_iter=300)
    assert np.all(np.diff(history) <= 1e-9 * max(1.0, history[0]))
    for j in range(5):
        members = x[labels == j]
        if len(members):
            assert np.allclose(centers[j], members.mean(axis=0), atol=1e-6)


def test_empty_cluster_never_produces_nan():
    x = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [0.0, 1.0]])
    init = np.array([[0.5, 0.2], [100.0, 100.0], [-100.0, 50.0]])
    labels, centers, history = kmeans(x, 3, init=init, max_iter=20)
    assert np.all(np.isfinite(centers)) and np.all(np.isfinite(history))
    assert np.all(np.diff(history) <= 1e-12)
    for j in range(3):
        if (labels == j).any():
            assert np.allclose(centers[j], x[labels == j].mean(axis=0), atol=1e-6)
        else:  # kept in place or relocated onto a data point
            assert np.allclose(centers[j], init[j]) or np.any(np.all(np.isclose(x, centers[j]), axis=1))


def test_k_equals_one_and_k_equals_n():
    rng = np.random.default_rng(5)
    x = rng.normal(size=(9, 2))
    labels, centers, _ = kmeans(x, 1, seed=0)
    assert np.all(labels == 0) and np.allclose(centers, x.mean(axis=0, keepdims=True))
    labels, centers, history = kmeans(x, 9, seed=0)
    assert np.isclose(history[-1], 0.0) and sorted(labels.tolist()) == list(range(9))
    assert np.allclose(np.sort(centers, axis=0), np.sort(x, axis=0))


def test_identical_and_repeated_points():
    same = np.tile([[3.0, -1.0]], (6, 1))
    labels, centers, history = kmeans(same, 2, seed=1)
    assert np.all(np.isfinite(centers)) and np.allclose(centers, [3.0, -1.0])
    assert np.isclose(history[-1], 0.0) and labels.shape == (6,)
    two = np.array([[0.0]] * 5 + [[10.0]] * 5)
    labels, centers, history = kmeans(two, 2, seed=2)
    assert np.allclose(np.sort(centers[:, 0]), [0.0, 10.0]) and np.isclose(history[-1], 0.0)


def test_kmeans_plus_plus_recovers_separated_blobs():
    x, truth = _blobs()
    labels, centers, _ = kmeans(x, 3, seed=7)
    for blob in range(3):
        assert len(set(labels[truth == blob].tolist())) == 1
    assert len(set(labels.tolist())) == 3


def test_deterministic_seeding_and_global_rng_untouched():
    x, _ = _blobs(1)
    np.random.seed(0)
    state = np.random.get_state()[1].copy()
    a = kmeans(x, 4, seed=11)
    b = kmeans(x, 4, seed=11)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) and a[2] == b[2]
    assert np.array_equal(np.random.get_state()[1], state)


def test_max_iter_and_tol_stopping():
    x, _ = _blobs(2)
    init = x[:3].copy()
    assert len(kmeans(x, 3, init=init, max_iter=2, tol=0.0)[2]) == 2
    assert len(kmeans(x, 3, init=init, tol=1e9)[2]) == 1
    assert np.array_equal(init, x[:3])  # init is copied, not updated in place
    # Shifts on the hand fixture: iteration 1 -> (0, 6.2), iteration 2 -> (1, 3.8), then 0.
    # tol compares the largest Euclidean shift (3.8), not a sum of shifts (4.8).
    line_init = np.array([[0.0], [1.0]])
    assert len(kmeans(_line_x(), 2, init=line_init, tol=4.0)[2]) == 2
    assert len(kmeans(_line_x(), 2, init=line_init, tol=3.7)[2]) == 3


def test_validation():
    x = np.ones((4, 2))
    assert _raises(ValueError, kmeans, x, 0)
    assert _raises(ValueError, kmeans, x, 5)
    assert _raises(ValueError, kmeans, x, 2, max_iter=0)
    assert _raises(ValueError, kmeans, x, 2, init=np.ones((3, 2)))
    assert _raises(ValueError, kmeans, np.ones(4), 2)


def test_vectorized_over_points():
    rng = np.random.default_rng(6)
    x = rng.normal(size=(3000, 4))
    (_, _, history), lines = _line_events(kmeans, x, 4, seed=0, max_iter=5, tol=0.0)
    assert len(history) == 5
    assert lines <= 400, f"executed {lines} Python lines; expected no loop over the 3000 points"
