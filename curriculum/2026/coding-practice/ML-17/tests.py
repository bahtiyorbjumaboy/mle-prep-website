import math

import numpy as np

from solution import forward_backward, gradient_check, init_params, numerical_gradient, relative_error


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _fixture(seed=0, b=5, d=3, h=4, c=3):
    rng = np.random.default_rng(seed)
    params = {
        "W1": rng.normal(size=(d, h)) * 0.7,
        "b1": rng.normal(size=h) * 0.1,
        "W2": rng.normal(size=(h, c)) * 0.7,
        "b2": rng.normal(size=c) * 0.1,
    }
    return params, rng.normal(size=(b, d)), rng.integers(0, c, size=b)


def _reference(params, x, y):
    """Independent forward/backward written from the equations."""
    z1 = x @ params["W1"] + params["b1"]
    h = np.tanh(z1)
    logits = h @ params["W2"] + params["b2"]
    m = logits.max(axis=1, keepdims=True)
    logp = logits - m - np.log(np.exp(logits - m).sum(axis=1, keepdims=True))
    b = len(y)
    loss = -logp[np.arange(b), y].mean()
    dlogits = np.exp(logp)
    dlogits[np.arange(b), y] -= 1
    dlogits /= b
    dh = dlogits @ params["W2"].T
    dz1 = dh * (1 - h ** 2)
    return loss, {"W1": x.T @ dz1, "b1": dz1.sum(0), "W2": h.T @ dlogits, "b2": dlogits.sum(0)}


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("init_params", "forward_backward", "numerical_gradient", "relative_error", "gradient_check"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_init_params_shapes_scale_and_determinism():
    p = init_params(30, 20, 4, seed=3)
    assert {k: v.shape for k, v in p.items()} == {"W1": (30, 20), "b1": (20,), "W2": (20, 4), "b2": (4,)}
    assert np.all(p["b1"] == 0) and np.all(p["b2"] == 0)
    q = init_params(30, 20, 4, seed=3)
    assert all(np.array_equal(p[k], q[k]) for k in p)
    rng = np.random.default_rng(3)
    assert np.allclose(p["W1"], rng.normal(size=(30, 20)) / math.sqrt(30))
    assert np.allclose(p["W2"], rng.normal(size=(20, 4)) / math.sqrt(20))


def test_forward_backward_shapes_and_values_match_reference():
    params, x, y = _fixture()
    loss, grads = forward_backward(params, x, y)
    ref_loss, ref_grads = _reference(params, x, y)
    assert isinstance(loss, float) and math.isclose(loss, ref_loss, rel_tol=1e-12)
    assert set(grads) == {"W1", "b1", "W2", "b2"}
    for k in grads:
        assert grads[k].shape == params[k].shape, k
        assert np.allclose(grads[k], ref_grads[k], rtol=1e-10, atol=1e-12), k


def test_hand_computed_zero_hidden_case():
    params = {"W1": np.zeros((1, 2)), "b1": np.zeros(2), "W2": np.array([[5.0, -5.0], [1.0, 2.0]]), "b2": np.array([1.0, 0.0])}
    loss, grads = forward_backward(params, np.array([[3.0]]), np.array([1]))
    p = np.exp([1.0, 0.0]) / np.exp([1.0, 0.0]).sum()
    assert math.isclose(loss, -math.log(p[1]))
    assert np.allclose(grads["b2"], p - [0.0, 1.0]) and np.allclose(grads["W2"], 0.0)
    dh = (p - [0.0, 1.0]) @ params["W2"].T  # tanh'(0) = 1
    assert np.allclose(grads["b1"], dh) and np.allclose(grads["W1"], 3.0 * dh[None, :])


def test_batch_gradient_is_mean_of_per_example_gradients():
    params, x, y = _fixture(1, b=6)
    loss, grads = forward_backward(params, x, y)
    singles = [forward_backward(params, x[i:i + 1], y[i:i + 1]) for i in range(6)]
    assert math.isclose(loss, np.mean([s[0] for s in singles]), rel_tol=1e-12)
    for k in grads:
        assert np.allclose(grads[k], np.mean([s[1][k] for s in singles], axis=0))


def test_stable_loss_with_huge_logits():
    params, x, y = _fixture(2)
    params["W2"] = params["W2"] * 1e4
    with np.errstate(over="raise", invalid="raise"):
        loss, grads = forward_backward(params, x, y)
    ref_loss, _ = _reference(params, x, y)
    assert math.isfinite(loss) and math.isclose(loss, ref_loss, rel_tol=1e-9)
    assert all(np.all(np.isfinite(g)) for g in grads.values())


def test_numerical_gradient_is_centered_and_restores_array():
    w = np.array([[0.5, -1.2, 2.0], [1.5, 0.3, -0.7]])
    before = w.copy()
    num = numerical_gradient(lambda: float(np.sum(w ** 3)), w, eps=1e-4)
    assert num.shape == w.shape
    # Centered error is O(eps^2) ~ 1e-8 here; a forward difference is off by ~3*w*eps ~ 1e-4.
    assert np.allclose(num, 3 * before ** 2, rtol=1e-7, atol=1e-9)
    assert np.array_equal(w, before)


def test_relative_error_definition():
    assert relative_error(np.array([1.0, 2.0]), np.array([1.0, 2.0])) == 0.0
    assert math.isclose(relative_error(np.array([1.0, 0.0]), np.array([3.0, 0.0])), 0.5)
    assert math.isclose(relative_error(np.array([1e-9]), np.array([0.0])), 1e-9 / 1e-8)
    assert relative_error(np.zeros(3), np.zeros(3)) == 0.0
    assert math.isclose(relative_error(np.array([1.0, -1.0]), np.array([1.0, 1.0])), 1.0)


def test_gradient_check_passes_correct_backprop_and_leaves_params_intact():
    params, x, y = _fixture(3)
    snapshot = {k: v.copy() for k, v in params.items()}
    errors = gradient_check(lambda p: forward_backward(p, x, y), params)
    assert set(errors) == {"W1", "b1", "W2", "b2"}
    assert max(errors.values()) < 1e-6, errors
    assert all(np.array_equal(params[k], snapshot[k]) for k in params)


def test_gradient_check_flags_sign_error_missing_chain_rule_and_wrong_reduction():
    params, x, y = _fixture(4)

    def sign_error(p):
        loss, g = _reference(p, x, y)
        return loss, {**g, "W2": -g["W2"]}

    def missing_tanh_derivative(p):
        loss, g = _reference(p, x, y)
        h = np.tanh(x @ p["W1"] + p["b1"])
        logits = h @ p["W2"] + p["b2"]
        probs = np.exp(logits - logits.max(1, keepdims=True))
        probs /= probs.sum(1, keepdims=True)
        probs[np.arange(len(y)), y] -= 1
        dz1 = (probs / len(y)) @ p["W2"].T  # forgot * (1 - h**2)
        return loss, {**g, "W1": x.T @ dz1, "b1": dz1.sum(0)}

    def sum_not_mean(p):
        loss, g = _reference(p, x, y)
        return loss, {k: v * len(y) for k, v in g.items()}

    assert gradient_check(sign_error, params)["W2"] > 0.5
    errors = gradient_check(missing_tanh_derivative, params)
    assert errors["W1"] > 1e-2 and errors["b1"] > 1e-2 and errors["W2"] < 1e-6
    assert min(gradient_check(sum_not_mean, params).values()) > 0.3


def test_validation():
    params, x, y = _fixture(5)
    assert _raises(ValueError, forward_backward, params, x[:, :2], y)
    assert _raises(ValueError, forward_backward, params, x, np.array([0, 1, 2, 3, 0]))
    assert _raises(ValueError, forward_backward, params, x, y[:3])
