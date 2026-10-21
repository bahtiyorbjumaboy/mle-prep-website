import math

import numpy as np

from solution import LogisticRegression, linear_regression_gd


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _data(seed=0, n=200, d=3, separable=False):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, d))
    w = np.linspace(1.0, -1.5, d)
    z = x @ w + 0.3
    y = (z > 0).astype(int) if separable else (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    return x, y


def _newton_optimum(x, y, l2, iters=50):
    """Independent reference: Newton's method on the same objective."""
    n, d = x.shape
    xa = np.column_stack([x, np.ones(n)])
    reg = np.diag([l2] * d + [0.0])
    theta = np.zeros(d + 1)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(xa @ theta)))
        grad = xa.T @ (p - y) / n + reg @ theta
        hess = (xa * (p * (1 - p))[:, None]).T @ xa / n + reg
        theta -= np.linalg.solve(hess, grad)
    return theta[:d], theta[d]


def _set_params(model, w, b):
    model.weights_ = np.asarray(w, dtype=float)
    model.bias_ = float(b)
    return model


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("linear_regression_gd", "LogisticRegression"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_linear_regression_one_step_and_convergence():
    x = np.array([[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]])
    y = np.array([1.0, 2.0, 4.0])
    w, b, history = linear_regression_gd(x, y, learning_rate=0.1, steps=1)
    assert np.allclose(w, [0.1 * 5 / 3, 0.1 * 8 / 3]) and math.isclose(b, 0.1 * 7 / 3)
    r = x @ w + b - y
    assert len(history) == 1 and math.isclose(history[0], np.mean(r ** 2) / 2)
    rng = np.random.default_rng(1)
    xs = rng.normal(size=(100, 3))
    ys = xs @ np.array([2.0, -1.0, 0.5]) + 3.0 + 0.1 * rng.normal(size=100)
    w, b, history = linear_regression_gd(xs, ys, learning_rate=0.1, steps=2000)
    sol = np.linalg.lstsq(np.column_stack([xs, np.ones(100)]), ys, rcond=None)[0]
    assert np.allclose(w, sol[:3], atol=1e-6) and math.isclose(b, sol[3], abs_tol=1e-6)
    assert all(a >= c - 1e-12 for a, c in zip(history, history[1:]))


def test_loss_is_stable_bce_plus_l2_without_intercept():
    model = _set_params(LogisticRegression(l2=0.5), [2.0, -1.0], 3.0)
    x = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1, 0])
    z = np.array([5.0, 2.0])
    bce = np.mean(np.log1p(np.exp(-z)) * (y == 1) + np.log1p(np.exp(z)) * (y == 0))
    assert math.isclose(model.loss(x, y), bce + 0.25 * 5.0)
    huge = _set_params(LogisticRegression(), [1.0], 0.0)
    out = huge.loss(np.array([[1e4], [-1e4], [1e4]]), np.array([0, 1, 1]))
    assert math.isfinite(out) and math.isclose(out, 2e4 / 3, rel_tol=1e-12)


def test_gradient_matches_centered_finite_differences():
    x, y = _data(2, n=30, d=4)
    model = _set_params(LogisticRegression(l2=0.3), [0.2, -0.4, 0.1, 0.7], -0.25)
    gw, gb = model.gradient(x, y)
    assert gw.shape == (4,)
    h = 1e-6
    for j in range(4):
        e = np.zeros(4)
        e[j] = h
        plus = _set_params(LogisticRegression(l2=0.3), model.weights_ + e, model.bias_).loss(x, y)
        minus = _set_params(LogisticRegression(l2=0.3), model.weights_ - e, model.bias_).loss(x, y)
        assert math.isclose(gw[j], (plus - minus) / (2 * h), rel_tol=1e-5, abs_tol=1e-8)
    plus = _set_params(LogisticRegression(l2=0.3), model.weights_, model.bias_ + h).loss(x, y)
    minus = _set_params(LogisticRegression(l2=0.3), model.weights_, model.bias_ - h).loss(x, y)
    assert math.isclose(gb, (plus - minus) / (2 * h), rel_tol=1e-5, abs_tol=1e-8)


def test_first_full_batch_step_is_exact():
    x = np.array([[1.0, 2.0], [3.0, -1.0], [0.0, 1.0], [2.0, 2.0]])
    y = np.array([1, 0, 0, 1])
    model = LogisticRegression(learning_rate=0.5, steps=1).fit(x, y)
    residual = 0.5 - y  # sigmoid(0) = 0.5 at the zero initialization
    assert np.allclose(model.weights_, -0.5 * x.T @ residual / 4)
    assert math.isclose(model.bias_, -0.5 * residual.mean())
    assert len(model.loss_history_) == 1 and math.isclose(model.loss_history_[0], model.loss(x, y))


def test_converges_to_newton_optimum_with_and_without_l2():
    x, y = _data(3)
    for l2 in (0.0, 0.1):
        model = LogisticRegression(learning_rate=1.0, steps=3000, l2=l2).fit(x, y)
        w, b = _newton_optimum(x, y, l2)
        assert np.allclose(model.weights_, w, atol=1e-4) and math.isclose(model.bias_, b, abs_tol=1e-4)
        assert all(a >= c - 1e-12 for a, c in zip(model.loss_history_, model.loss_history_[1:]))


def test_intercept_learned_and_not_regularized():
    x = np.zeros((10, 2))
    y = np.array([1] * 8 + [0] * 2)
    model = LogisticRegression(learning_rate=1.0, steps=2000, l2=10.0).fit(x, y)
    assert math.isclose(model.bias_, math.log(0.8 / 0.2), abs_tol=1e-6)
    assert np.allclose(model.weights_, 0.0)
    assert np.allclose(model.predict_proba(x), 0.8, atol=1e-6)


def test_perfect_separation_weights_grow_without_l2_but_stay_bounded_with_l2():
    x, y = _data(4, n=60, d=2, separable=True)
    short = LogisticRegression(learning_rate=1.0, steps=200).fit(x, y)
    long = LogisticRegression(learning_rate=1.0, steps=2000).fit(x, y)
    assert np.linalg.norm(long.weights_) > np.linalg.norm(short.weights_) + 1.0
    assert long.loss_history_[-1] < short.loss_history_[-1]
    reg = LogisticRegression(learning_rate=1.0, steps=3000, l2=0.1).fit(x, y)
    gw, gb = reg.gradient(x, y)
    assert np.linalg.norm(gw) < 1e-6 and abs(gb) < 1e-6


def test_unscaled_features_and_diverging_lr_stay_finite():
    x, y = _data(5, n=50, d=2)
    model = LogisticRegression(learning_rate=1e3, steps=20).fit(x * 1e3, y)
    assert np.all(np.isfinite(model.loss_history_)) and np.all(np.isfinite(model.weights_))
    p = model.predict_proba(x * 1e3)
    assert np.all((p >= 0) & (p <= 1)) and np.all(np.isfinite(p))


def test_mini_batch_deterministic_and_full_batch_equivalence():
    x, y = _data(6, n=64, d=3)
    a = LogisticRegression(learning_rate=0.2, steps=5, batch_size=8, seed=1).fit(x, y)
    b = LogisticRegression(learning_rate=0.2, steps=5, batch_size=8, seed=1).fit(x, y)
    c = LogisticRegression(learning_rate=0.2, steps=5, batch_size=8, seed=2).fit(x, y)
    assert np.array_equal(a.weights_, b.weights_) and a.loss_history_ == b.loss_history_
    assert not np.allclose(a.weights_, c.weights_)
    assert len(a.loss_history_) == 5
    full = LogisticRegression(learning_rate=0.2, steps=5).fit(x, y)
    as_one_batch = LogisticRegression(learning_rate=0.2, steps=5, batch_size=64, seed=3).fit(x, y)
    assert np.allclose(full.weights_, as_one_batch.weights_) and math.isclose(full.bias_, as_one_batch.bias_)
    # 8 updates per epoch move further than 1 full-batch update.
    assert a.loss_history_[0] < full.loss_history_[0]


def test_mini_batch_uses_every_row_each_epoch_with_partial_last_batch():
    x = np.zeros((7, 1))
    y = np.array([1, 0, 1, 1, 0, 0, 1])
    model = LogisticRegression(learning_rate=0.5, steps=3, batch_size=3, seed=0).fit(x, y)
    # Bias-only problem: per-batch gradients are mean(sigmoid(b) - y_B); 3 steps per epoch
    # (3, 3, 1 rows); one generator for the whole fit gives a fresh order each epoch.
    rng = np.random.default_rng(0)
    b = 0.0
    for _ in range(3):
        order = rng.permutation(7)
        for start in range(0, 7, 3):
            batch = y[order[start:start + 3]]
            b -= 0.5 * np.mean(1 / (1 + np.exp(-b)) - batch)
    assert math.isclose(model.bias_, b, rel_tol=1e-12)


def test_predict_proba_and_thresholded_predict():
    model = _set_params(LogisticRegression(), [1.0, -2.0], 0.5)
    x = np.array([[0.0, 0.25], [2.0, 0.0], [-800.0, 0.0], [0.0, 0.0]])
    p = model.predict_proba(x)
    assert p.shape == (4,) and np.allclose(p, [0.5, 1 / (1 + math.exp(-2.5)), 0.0, 1 / (1 + math.exp(-0.5))])
    assert model.predict(x).tolist() == [1, 1, 0, 1]
    assert model.predict(x, threshold=0.7).tolist() == [0, 1, 0, 0]
    assert np.issubdtype(model.predict(x).dtype, np.integer)


def test_validation_and_bool_labels():
    x = np.ones((3, 2))
    assert _raises(ValueError, LogisticRegression(steps=1).fit, x, np.array([0, 1, 2]))
    assert _raises(ValueError, LogisticRegression(steps=1).fit, x, np.array([-1, 1, 1]))
    assert _raises(ValueError, LogisticRegression(steps=1).fit, x, np.array([0, 1]))
    assert _raises(ValueError, LogisticRegression(steps=1).fit, np.ones(3), np.array([0, 1, 1]))
    model = LogisticRegression(steps=1).fit(x, np.array([True, False, True]))
    assert model.weights_.shape == (2,)
