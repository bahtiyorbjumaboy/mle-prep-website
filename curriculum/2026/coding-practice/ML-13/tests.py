import math
import os
import sys

import numpy as np

from solution import KNearestNeighbors


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


X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0], [3.0, 0.0], [0.0, -1.0], [5.0, 5.0]])
Y_CLS = np.array([0, 1, 1, 2, 0, 2])
Y_REG = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "KNearestNeighbors"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_kneighbors_euclidean_ordering_and_index_ties():
    model = KNearestNeighbors(k=4).fit(X, Y_CLS)
    d, i = model.kneighbors(np.array([[0.0, 0.0], [0.5, 0.0]]))
    assert d.shape == (2, 4) and i.shape == (2, 4)
    assert i[0].tolist() == [0, 1, 4, 2] and np.allclose(d[0], [0.0, 1.0, 1.0, 2.0])
    assert i[1].tolist() == [0, 1, 4, 2]  # 0 and 1 tie at 0.5 -> lower index first
    assert np.allclose(d[1], [0.5, 0.5, math.sqrt(1.25), math.sqrt(4.25)])


def test_uniform_classification_vote_and_smallest_label_tie():
    model = KNearestNeighbors(k=3).fit(X, Y_CLS)
    assert model.predict(np.array([[0.2, -0.1]])).tolist() == [0]  # neighbors 0,1,4 -> {0,1,0}
    two = KNearestNeighbors(k=2).fit(X, Y_CLS)
    assert two.predict(np.array([[0.6, 0.0]])).tolist() == [0]  # neighbors 1 (label 1), 0 (label 0): tie -> 0
    assert two.predict(np.array([[0.4, 0.0]])).tolist() == [0]


def test_string_labels_and_k_equals_n_majority():
    labels = np.array(["cat", "dog", "dog", "bird", "cat", "dog"])
    model = KNearestNeighbors(k=6).fit(X, labels)
    assert model.predict(np.array([[100.0, 100.0], [-3.0, 0.0]])).tolist() == ["dog", "dog"]
    tie = KNearestNeighbors(k=2).fit(np.array([[0.0], [2.0]]), np.array(["zebra", "ant"]))
    assert tie.predict(np.array([[1.0]])).tolist() == ["ant"]


def test_k_one_returns_nearest_label():
    model = KNearestNeighbors(k=1).fit(X, Y_CLS)
    assert model.predict(X).tolist() == Y_CLS.tolist()
    assert model.predict(np.array([[2.9, 0.2], [4.0, 4.0]])).tolist() == [2, 2]


def test_distance_weighting_changes_the_vote():
    x = np.array([[0.0], [3.0], [3.5]])
    y = np.array([1, 0, 0])
    q = np.array([[1.0]])
    assert KNearestNeighbors(k=3).fit(x, y).predict(q).tolist() == [0]
    # weights: 1/1 for label 1 vs 1/2 + 1/2.5 = 0.9 for label 0
    assert KNearestNeighbors(k=3, weights="distance").fit(x, y).predict(q).tolist() == [1]


def test_regression_uniform_and_distance_weighted():
    q = np.array([[0.5, 0.0]])
    uni = KNearestNeighbors(k=3, task="regression").fit(X, Y_REG).predict(q)
    assert uni.shape == (1,) and math.isclose(uni[0], (1.0 + 2.0 + 16.0) / 3)
    dist = KNearestNeighbors(k=3, task="regression", weights="distance").fit(X, Y_REG).predict(q)
    w = np.array([1 / 0.5, 1 / 0.5, 1 / math.sqrt(1.25)])
    assert math.isclose(dist[0], np.dot(w, [1.0, 2.0, 16.0]) / w.sum())


def test_zero_distance_neighbors_dominate_without_inf_or_nan():
    x = np.array([[0.0], [1.0], [1.0], [2.0]])
    y_reg = np.array([10.0, 20.0, 40.0, 80.0])
    with np.errstate(divide="raise", invalid="raise"):
        out = KNearestNeighbors(k=3, task="regression", weights="distance").fit(x, y_reg).predict(np.array([[1.0], [0.5]]))
        cls = KNearestNeighbors(k=3, weights="distance").fit(x, np.array([5, 7, 7, 5])).predict(np.array([[0.0]]))
    assert math.isclose(out[0], 30.0)  # only the two exact matches, equally weighted
    assert np.all(np.isfinite(out)) and math.isclose(out[1], (2 * 10 + 2 * 20 + 2 * 40) / 6)
    assert cls.tolist() == [5]


def test_self_queries_on_float_data_are_exact_matches():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(50, 3)) * 1e3
    y = rng.normal(size=50)
    model = KNearestNeighbors(k=3, task="regression", weights="distance").fit(x, y)
    d, i = model.kneighbors(x)
    assert np.array_equal(i[:, 0], np.arange(50)) and np.all(d[:, 0] == 0.0)
    assert np.array_equal(model.predict(x), y)


def test_fit_stores_copies_and_inputs_not_modified():
    x, y = X.copy(), Y_REG.copy()
    model = KNearestNeighbors(k=2, task="regression").fit(x, y)
    before = model.predict(np.array([[0.0, 0.0]]))
    x[:] = 100.0
    y[:] = -1.0
    assert np.allclose(model.predict(np.array([[0.0, 0.0]])), before)


def test_validation():
    assert _raises(ValueError, KNearestNeighbors, 0)
    assert _raises(ValueError, KNearestNeighbors, 3, "ranking")
    assert _raises(ValueError, KNearestNeighbors, 3, "classification", "gaussian")
    assert _raises(ValueError, KNearestNeighbors(k=7).fit, X, Y_CLS)
    assert _raises(ValueError, KNearestNeighbors(k=2).fit, X, Y_CLS[:3])
    model = KNearestNeighbors(k=2).fit(X, Y_CLS)
    assert _raises(ValueError, model.predict, np.ones((2, 3)))


def test_matches_brute_force_and_is_vectorized():
    rng = np.random.default_rng(0)
    x = rng.integers(0, 4, size=(300, 2)).astype(float)  # many exact distance ties
    y = rng.integers(0, 3, size=300)
    q = rng.integers(0, 4, size=(400, 2)).astype(float) + 0.5
    model = KNearestNeighbors(k=7).fit(x, y)
    pred, lines = _line_events(model.predict, q)
    assert lines <= 80, f"executed {lines} Python lines for 400 queries; vectorize over queries"
    for row in range(0, 400, 37):
        dist = np.sqrt(((x - q[row]) ** 2).sum(axis=1))
        order = sorted(range(300), key=lambda j: (dist[j], j))[:7]
        counts = np.bincount(y[order], minlength=3)
        assert pred[row] == int(np.argmax(counts))
