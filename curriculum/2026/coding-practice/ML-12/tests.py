import math

import numpy as np

from solution import fit_ridge_gd, ridge_closed_form, ridge_gradient, ridge_loss


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _fixture(seed=0, n=60, d=3):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, d))
    y = x @ np.linspace(2.0, -1.0, d) + 3.0 + 0.1 * rng.normal(size=n)
    return x, y


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("ridge_loss", "ridge_gradient", "fit_ridge_gd", "ridge_closed_form"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_no_explicit_inverse():
    import ast
    import inspect
    import solution
    tree = ast.parse(inspect.getsource(solution))
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "inv" not in names, "use np.linalg.solve / lstsq instead of forming an inverse"


def test_loss_hand_computed_and_intercept_not_penalized():
    x = np.array([[1.0, 2.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    w, b = np.array([1.0, -1.0]), 5.0
    residual = x @ w + b - y  # [3, 4]
    assert math.isclose(ridge_loss(x, y, w, b, alpha=0.5), np.mean(residual ** 2) / 2 + 0.25 * 2.0)
    assert math.isclose(ridge_loss(x, y, np.zeros(2), 0.0, alpha=10.0), 0.25)


def test_gradient_matches_centered_finite_differences():
    x, y = _fixture(1, n=8, d=3)
    w, b, alpha = np.array([0.3, -0.7, 1.1]), 0.4, 0.25
    gw, gb = ridge_gradient(x, y, w, b, alpha)
    assert gw.shape == (3,) and isinstance(float(gb), float)
    h = 1e-6
    for j in range(3):
        e = np.zeros(3)
        e[j] = h
        numeric = (ridge_loss(x, y, w + e, b, alpha) - ridge_loss(x, y, w - e, b, alpha)) / (2 * h)
        assert math.isclose(gw[j], numeric, rel_tol=1e-6, abs_tol=1e-9)
    numeric_b = (ridge_loss(x, y, w, b + h, alpha) - ridge_loss(x, y, w, b - h, alpha)) / (2 * h)
    assert math.isclose(gb, numeric_b, rel_tol=1e-6, abs_tol=1e-9)


def test_closed_form_exact_on_noiseless_data():
    x = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, -1.0], [-1.0, 3.0]])
    y = x @ np.array([2.0, -3.0]) + 1.0
    w, b = ridge_closed_form(x, y)
    assert w.shape == (2,) and np.allclose(w, [2.0, -3.0]) and math.isclose(b, 1.0)


def test_closed_form_is_stationary_point_for_ridge():
    x, y = _fixture(2)
    for alpha in (0.0, 0.3, 5.0):
        w, b = ridge_closed_form(x, y, alpha)
        gw, gb = ridge_gradient(x, y, w, b, alpha)
        assert np.allclose(gw, 0.0, atol=1e-10) and abs(gb) < 1e-10


def test_gradient_descent_matches_closed_form_on_well_conditioned_fixture():
    x, y = _fixture(3)
    for alpha in (0.0, 0.5):
        w_gd, b_gd, history = fit_ridge_gd(x, y, alpha=alpha, learning_rate=0.2, steps=3000)
        w_cf, b_cf = ridge_closed_form(x, y, alpha)
        assert np.allclose(w_gd, w_cf, atol=1e-8) and math.isclose(b_gd, b_cf, abs_tol=1e-8)
        assert np.allclose(x @ w_gd + b_gd, x @ w_cf + b_cf, atol=1e-8)
        assert len(history) == 3000 and all(a >= c - 1e-12 for a, c in zip(history, history[1:]))


def test_gd_first_step_exact():
    x = np.array([[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]])
    y = np.array([1.0, 2.0, 4.0])
    w, b, history = fit_ridge_gd(x, y, alpha=0.3, learning_rate=0.1, steps=1)
    assert np.allclose(w, [0.1 * 5 / 3, 0.1 * 8 / 3]) and math.isclose(b, 0.1 * 7 / 3)
    assert math.isclose(history[0], ridge_loss(x, y, w, b, 0.3))


def test_ridge_shrinks_correlated_coefficients_and_not_the_intercept():
    rng = np.random.default_rng(4)
    z = rng.normal(size=100)
    x = np.column_stack([z, z + 0.01 * rng.normal(size=100)])
    y = 3 * x[:, 0] - 1 * x[:, 1] + 50.0 + 0.1 * rng.normal(size=100)
    w_ols, _ = ridge_closed_form(x, y, 0.0)
    w_ridge, _ = ridge_closed_form(x, y, 0.1)
    assert np.linalg.norm(w_ridge) < np.linalg.norm(w_ols)
    assert abs(w_ridge[0] - w_ridge[1]) < abs(w_ols[0] - w_ols[1])
    w_big, b_big = ridge_closed_form(x, y, 1e6)
    assert np.allclose(w_big, 0.0, atol=1e-4) and math.isclose(b_big, y.mean(), rel_tol=1e-6)


def test_objective_scale_is_a_mean_so_duplicating_rows_changes_nothing():
    x, y = _fixture(5, n=20)
    a = ridge_closed_form(x, y, 0.7)
    b = ridge_closed_form(np.vstack([x, x]), np.concatenate([y, y]), 0.7)
    assert np.allclose(a[0], b[0]) and math.isclose(a[1], b[1])


def test_rank_deficient_ols_gives_finite_minimum_norm_solution():
    x, y = _fixture(6, n=30, d=2)
    dup = np.column_stack([x, x[:, 0]])  # third column duplicates the first
    w, b = ridge_closed_form(dup, y, 0.0)
    assert np.all(np.isfinite(w))
    w_ref, b_ref = ridge_closed_form(x, y, 0.0)
    assert math.isclose(w[0], w[2], rel_tol=1e-8) and math.isclose(w[0] + w[2], w_ref[0], rel_tol=1e-8)
    assert np.allclose(dup @ w + b, x @ w_ref + b_ref)
    w_r, _ = ridge_closed_form(dup, y, 0.1)
    assert np.all(np.isfinite(w_r)) and math.isclose(w_r[0], w_r[2], rel_tol=1e-8)


def test_ill_conditioned_features_still_accurate():
    rng = np.random.default_rng(7)
    x = rng.normal(size=(200, 3)) * np.array([1e-4, 1.0, 1e4])
    true_w = np.array([500.0, -2.0, 1e-3])
    y = x @ true_w + 4.0
    w, b = ridge_closed_form(x, y, 0.0)
    assert np.allclose(w, true_w, rtol=1e-6) and math.isclose(b, 4.0, rel_tol=1e-8)


def test_validation_and_inputs_not_modified():
    x, y = _fixture(8, n=10)
    x0, y0 = x.copy(), y.copy()
    ridge_closed_form(x, y, 0.5), fit_ridge_gd(x, y, 0.5, steps=3)
    assert np.array_equal(x, x0) and np.array_equal(y, y0)
    assert _raises(ValueError, ridge_closed_form, x, y, -1.0)
    assert _raises(ValueError, ridge_closed_form, x, y[:5])
    assert _raises(ValueError, fit_ridge_gd, x, y, -0.1)
