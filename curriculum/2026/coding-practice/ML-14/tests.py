import math

import numpy as np

from solution import PCA


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _data(seed=0, n=80, d=4, offset=0.0):
    rng = np.random.default_rng(seed)
    mix = rng.normal(size=(d, d)) * np.array([5.0, 2.0, 1.0, 0.3][:d])[:, None]
    return rng.normal(size=(n, d)) @ mix + offset


def _projector(components):
    c = np.asarray(components)
    return c.T @ c


def _reference(x):
    xc = x - x.mean(axis=0)
    lam, vec = np.linalg.eigh(xc.T @ xc / (len(x) - 1))
    order = np.argsort(lam)[::-1]
    return lam[order], vec[:, order].T


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "PCA"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_line_data_first_component_and_ratio():
    t = np.linspace(-2, 2, 9)
    x = np.column_stack([t, 2 * t]) + np.array([10.0, -3.0])
    pca = PCA().fit(x)
    assert pca.components_.shape == (2, 2)
    assert np.allclose(np.abs(pca.components_[0]), np.array([1.0, 2.0]) / math.sqrt(5))
    assert np.allclose(pca.explained_variance_ratio_, [1.0, 0.0], atol=1e-12)
    assert np.allclose(pca.mean_, [10.0, -3.0])


def test_matches_covariance_eigendecomposition_up_to_sign():
    x = _data(1)
    pca = PCA(3).fit(x)
    lam, vec = _reference(x)
    assert np.allclose(pca.explained_variance_, lam[:3])
    assert np.allclose(pca.explained_variance_ratio_, lam[:3] / lam.sum())
    for j in range(3):
        assert math.isclose(abs(pca.components_[j] @ vec[j]), 1.0, rel_tol=1e-9)


def test_components_orthonormal_and_centering_matters():
    x = _data(2, offset=1000.0)
    pca = PCA().fit(x)
    assert np.allclose(pca.components_ @ pca.components_.T, np.eye(4), atol=1e-10)
    lam, vec = _reference(x)
    assert np.allclose(_projector(pca.components_[:1]), _projector(vec[:1]), atol=1e-8)
    assert np.allclose(pca.mean_, x.mean(axis=0))


def test_transformed_covariance_is_diagonal_with_explained_variances():
    x = _data(3)
    pca = PCA().fit(x)
    z = pca.transform(x)
    cov = np.cov(z, rowvar=False)
    assert np.allclose(cov, np.diag(pca.explained_variance_), atol=1e-8)
    assert np.allclose(z.mean(axis=0), 0.0, atol=1e-10)


def test_reconstruction_error_decreases_with_k_and_full_rank_is_exact():
    x = _data(4)
    errors = []
    for k in range(1, 5):
        pca = PCA(k).fit(x)
        recon = pca.inverse_transform(pca.transform(x))
        errors.append(np.sum((x - recon) ** 2))
        lam, _ = _reference(x)
        assert math.isclose(errors[-1], (len(x) - 1) * lam[k:].sum(), rel_tol=1e-8, abs_tol=1e-8)
    assert all(a > b for a, b in zip(errors, errors[1:]))
    assert errors[-1] < 1e-18 * np.sum(x ** 2) + 1e-12


def test_sign_invariant_transform_matches_reference_projection():
    x = _data(5)
    pca = PCA(2).fit(x)
    lam, vec = _reference(x)
    z_ref = (x - x.mean(axis=0)) @ vec[:2].T
    z = pca.transform(x)
    assert np.allclose(np.abs(z), np.abs(z_ref), atol=1e-8)
    assert np.allclose(z @ z.T, z_ref @ z_ref.T, atol=1e-6)


def test_rank_deficient_data_and_k_above_rank():
    rng = np.random.default_rng(6)
    base = rng.normal(size=(30, 2))
    x = np.column_stack([base, base @ np.array([[1.0, 2.0], [-1.0, 0.5]])])  # rank 2 in 4-D
    pca = PCA(4).fit(x)
    assert np.allclose(pca.explained_variance_ratio_[2:], 0.0, atol=1e-12)
    assert math.isclose(pca.explained_variance_ratio_.sum(), 1.0)
    two = PCA(2).fit(x)
    assert np.allclose(two.inverse_transform(two.transform(x)), x, atol=1e-9)
    assert np.allclose(pca.components_ @ pca.components_.T, np.eye(4), atol=1e-8)


def test_repeated_eigenvalues_compare_subspaces():
    a, b = 3.0, 1.0
    x = np.array([[a, 0, 0], [-a, 0, 0], [0, b, 0], [0, -b, 0], [0, 0, b], [0, 0, -b]])
    pca = PCA().fit(x)
    assert np.allclose(pca.explained_variance_, [2 * a * a / 5, 2 * b * b / 5, 2 * b * b / 5])
    assert np.allclose(_projector(pca.components_[:1]), np.diag([1.0, 0.0, 0.0]))
    assert np.allclose(_projector(pca.components_[1:]), np.diag([0.0, 1.0, 1.0]))


def test_wide_data_one_component_and_shapes():
    x = _data(7, n=5, d=4)
    pca = PCA().fit(x)
    assert pca.components_.shape == (4, 4) and pca.explained_variance_.shape == (4,)
    wide = np.random.default_rng(8).normal(size=(4, 10))
    pca = PCA().fit(wide)
    assert pca.components_.shape == (4, 10)
    assert np.allclose(pca.inverse_transform(pca.transform(wide)), wide, atol=1e-10)
    one = PCA(1).fit(_data(9))
    assert one.transform(_data(9)).shape == (80, 1) and one.components_.shape == (1, 4)


def test_validation_and_inputs_not_modified():
    x = _data(10, n=10, d=3)
    x0 = x.copy()
    pca = PCA(2).fit(x)
    pca.transform(x)
    assert np.array_equal(x, x0)
    assert _raises(ValueError, PCA(0).fit, x)
    assert _raises(ValueError, PCA(4).fit, x)
    assert _raises(ValueError, PCA(11).fit, np.ones((10, 20)))  # k > min(n, d) = 10
    assert _raises(ValueError, PCA().fit, x[:1])
    assert _raises(ValueError, pca.transform, np.ones((2, 4)))
    assert _raises(ValueError, pca.inverse_transform, np.ones((2, 3)))
