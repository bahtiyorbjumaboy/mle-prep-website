import numpy as np

from solution import correlation, covariance, standardize, standardize_and_whiten, whiten


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _data(seed=0, n=200, d=4):
    rng = np.random.default_rng(seed)
    mix = rng.normal(size=(d, d))
    return rng.normal(size=(n, d)) @ mix + rng.normal(size=d) * 10


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("standardize", "covariance", "correlation", "whiten", "standardize_and_whiten"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_does_not_call_library_cov_or_corrcoef():
    import ast
    import inspect
    import solution
    tree = ast.parse(inspect.getsource(solution))
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not names & {"cov", "corrcoef"}, "implement covariance/correlation from primitives"


def test_hand_computed_covariance_uses_ddof_1():
    x = np.array([[1.0, 2.0], [3.0, 6.0], [5.0, 4.0]])
    c = covariance(x)
    assert c.shape == (2, 2)
    assert np.allclose(c, [[4.0, 2.0], [2.0, 4.0]])


def test_covariance_non_square_shape_symmetry_and_reference():
    x = _data(1, n=30, d=5)
    c = covariance(x)
    xc = x - x.mean(axis=0)
    assert c.shape == (5, 5) and np.allclose(c, c.T)
    assert np.allclose(c, xc.T @ xc / 29)
    assert np.all(np.linalg.eigvalsh(c) > -1e-10)


def test_covariance_centers_before_multiplying_large_means():
    rng = np.random.default_rng(2)
    base = rng.normal(size=(100, 2))
    shifted = base + 1e8  # E[x^2] - E[x]^2 loses every significant digit here
    assert np.allclose(covariance(shifted), covariance(base), rtol=1e-6, atol=1e-6)


def test_standardize_ddof_1_and_constant_columns():
    x = np.array([[1.0, 0.1, 5.0], [2.0, 0.1, 7.0], [4.0, 0.1, 6.0], [5.0, 0.1, 10.0]])
    z = standardize(x)
    assert z.shape == x.shape and np.all(np.isfinite(z))
    assert np.allclose(z[:, 1], 0.0)
    # With 3 rows the mean of [0.1]*3 rounds, so std is ~1.7e-17 rather than 0.
    z3 = standardize(np.array([[1.0, 0.1, 0.7], [2.0, 0.1, 0.7], [4.0, 0.1, 0.7]]))
    assert np.array_equal(z3[:, 1:], np.zeros((3, 2)))
    assert np.allclose(z[:, [0, 2]].mean(axis=0), 0.0)
    assert np.allclose(z[:, [0, 2]].std(axis=0, ddof=1), 1.0)
    assert np.allclose(z[:, 0], (x[:, 0] - 3.0) / np.sqrt(10.0 / 3.0))


def test_correlation_matches_definition_and_bounds():
    x = _data(3, n=50, d=4)
    r = correlation(x)
    xc = x - x.mean(axis=0)
    sd = np.sqrt((xc ** 2).sum(axis=0))
    assert r.shape == (4, 4) and np.allclose(r, r.T)
    assert np.allclose(r, (xc.T @ xc) / np.outer(sd, sd))
    assert np.allclose(np.diag(r), 1.0) and np.all(np.abs(r) <= 1 + 1e-12)
    assert np.allclose(r, covariance(standardize(x)))  # same ddof everywhere


def test_correlation_zero_variance_policy_and_perfect_correlation():
    x = np.array([[1.0, 3.0, 2.0, -1.0], [2.0, 3.0, 4.0, -2.0], [3.0, 3.0, 6.0, -3.0]])
    r = correlation(x)
    assert np.all(np.isfinite(r))
    assert np.allclose(r[1], [0.0, 1.0, 0.0, 0.0]) and np.allclose(r[:, 1], [0.0, 1.0, 0.0, 0.0])
    assert np.isclose(r[0, 2], 1.0) and np.isclose(r[0, 3], -1.0)


def test_zca_whitening_identity_covariance_and_symmetric_transform():
    x = _data(4)
    w = whiten(x, "zca")
    assert w.shape == x.shape
    assert np.allclose(w.mean(axis=0), 0.0, atol=1e-10)
    assert np.allclose(covariance(w), np.eye(4), atol=1e-6)
    xc = x - x.mean(axis=0)
    transform = np.linalg.lstsq(xc, w, rcond=None)[0]
    assert np.allclose(transform, transform.T, atol=1e-8), "ZCA uses the symmetric V S V^T"


def test_pca_whitening_is_rotation_of_zca_sign_invariant():
    x = _data(5)
    z, p = whiten(x, "zca"), whiten(x, "pca")
    assert np.allclose(covariance(p), np.eye(4), atol=1e-6)
    # PCA = ZCA @ V: same row norms and same Gram matrix regardless of eigenvector signs.
    assert np.allclose(np.linalg.norm(p, axis=1), np.linalg.norm(z, axis=1))
    assert np.allclose(p @ p.T, z @ z.T, atol=1e-8)
    transform = np.linalg.lstsq(x - x.mean(axis=0), p, rcond=None)[0]
    assert not np.allclose(transform, transform.T, atol=1e-3), "PCA whitening should not be the symmetric ZCA map"


def test_whitening_rank_deficient_and_wide_data_stay_finite():
    x = _data(6, n=40, d=3)
    deficient = np.column_stack([x, x[:, 0] + x[:, 1]])  # rank 3 in 4 columns
    for method in ("zca", "pca"):
        w = whiten(deficient, method)
        assert np.all(np.isfinite(w))
        eig = np.linalg.eigvalsh(covariance(w))
        assert np.allclose(np.sort(eig), [0.0, 1.0, 1.0, 1.0], atol=1e-4)
    wide = _data(7, n=5, d=12)  # d >> n
    w = whiten(wide, "zca")
    assert np.all(np.isfinite(w)) and w.shape == (5, 12)
    assert np.allclose(np.sort(np.linalg.eigvalsh(covariance(w)))[-4:], 1.0, atol=1e-4)


def test_eps_regularizes_small_eigenvalues():
    x = np.column_stack([np.linspace(-1, 1, 21), 1e-3 * np.sin(np.arange(21))])
    w = whiten(x, "zca", eps=1e-2)
    c = covariance(x)
    lam = np.linalg.eigvalsh(c)
    assert np.allclose(np.sort(np.linalg.eigvalsh(covariance(w))), np.sort(lam / (lam + 1e-2)), atol=1e-8)


def test_validation_and_wrapper():
    x = _data(8, n=10, d=2)
    assert _raises(ValueError, whiten, x, "pcaa")
    assert _raises(ValueError, whiten, x, "zca", 0.0)
    assert _raises(ValueError, covariance, np.ones((1, 3)))
    assert _raises(ValueError, standardize, np.ones(3))
    s, w = standardize_and_whiten(x)
    assert np.allclose(s, standardize(x)) and np.allclose(w, whiten(x, "zca"))


def test_inputs_not_modified():
    x = _data(9, n=20, d=3)
    x0 = x.copy()
    standardize(x), covariance(x), correlation(x), whiten(x, "zca"), whiten(x, "pca")
    assert np.array_equal(x, x0)
