import math

import numpy as np

from solution import adam_step, adamw_step, momentum_step, rmsprop_step, sgd_step


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _ref_adam(p, grads, lr, b1, b2, eps, wd, decoupled):
    """Independent multi-step reference written from the equations."""
    m = np.zeros_like(p)
    v = np.zeros_like(p)
    for t, g in enumerate(grads, start=1):
        g_eff = g if decoupled else g + wd * p
        m = b1 * m + (1 - b1) * g_eff
        v = b2 * v + (1 - b2) * g_eff ** 2
        step = lr * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + eps)
        p = p - lr * wd * p - step if decoupled else p - step
    return p, m, v


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("sgd_step", "momentum_step", "rmsprop_step", "adam_step", "adamw_step"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_sgd_with_and_without_coupled_weight_decay():
    p, g = np.array([1.0, -2.0]), np.array([0.5, 0.5])
    assert np.allclose(sgd_step(p, g, lr=0.1), [0.95, -2.05])
    assert np.allclose(sgd_step(p, g, lr=0.1, weight_decay=0.1), [1 - 0.1 * 0.6, -2 - 0.1 * 0.3])


def test_momentum_two_steps_hand_computed():
    p, v = momentum_step(np.array([1.0]), np.array([1.0]), None, lr=0.1, beta=0.9)
    assert np.allclose(v, [1.0]) and np.allclose(p, [0.9])
    p, v = momentum_step(p, np.array([1.0]), v, lr=0.1, beta=0.9)
    assert np.allclose(v, [1.9]) and np.allclose(p, [0.71])
    p, v = momentum_step(p, np.array([-3.0]), v, lr=0.1, beta=0.9)
    assert np.allclose(v, [1.71 - 3.0]) and np.allclose(p, [0.71 + 0.129])


def test_rmsprop_two_steps_and_eps_outside_sqrt():
    p, s = rmsprop_step(np.array([1.0]), np.array([2.0]), None, lr=0.01, rho=0.9, eps=1e-8)
    assert np.allclose(s, [0.4]) and np.allclose(p, [1 - 0.01 * 2 / (math.sqrt(0.4) + 1e-8)])
    p2, s2 = rmsprop_step(p, np.array([-1.0]), s, lr=0.01, rho=0.9, eps=1e-8)
    assert np.allclose(s2, [0.36 + 0.1]) and np.allclose(p2, p + 0.01 / (math.sqrt(0.46) + 1e-8))
    tiny, _ = rmsprop_step(np.array([0.0]), np.array([1e-10]), None, lr=1.0, rho=0.9, eps=1e-8)
    expected = -1e-10 / (math.sqrt(0.1) * 1e-10 + 1e-8)
    assert math.isclose(tiny[0], expected, rel_tol=1e-9)  # eps inside the sqrt gives ~1e-6


def test_adam_first_step_is_lr_times_sign_due_to_bias_correction():
    p = np.array([1.0, -1.0, 0.5])
    g = np.array([0.3, -2.0, 1e-3])
    new, state = adam_step(p, g, None, lr=0.01)
    assert np.allclose(new, p - 0.01 * g / (np.abs(g) + 1e-8))
    assert state["t"] == 1 and np.allclose(state["m"], 0.1 * g) and np.allclose(state["v"], 0.001 * g ** 2)


def test_adam_second_step_hand_computed():
    p, state = adam_step(np.array([1.0]), np.array([1.0]), None, lr=0.1)
    p, state = adam_step(p, np.array([3.0]), state, lr=0.1)
    m = 0.9 * 0.1 + 0.1 * 3.0
    v = 0.999 * 0.001 + 0.001 * 9.0
    m_hat, v_hat = m / (1 - 0.81), v / (1 - 0.999 ** 2)
    assert state["t"] == 2 and np.allclose(state["m"], [m]) and np.allclose(state["v"], [v])
    assert np.allclose(p, [0.9 - 0.1 * m_hat / (math.sqrt(v_hat) + 1e-8)])


def test_adam_eps_outside_sqrt_with_tiny_gradient():
    new, _ = adam_step(np.array([0.0]), np.array([1e-10]), None, lr=1.0, eps=1e-8)
    assert math.isclose(new[0], -1e-10 / (1e-10 + 1e-8), rel_tol=1e-9)


def test_adam_multi_step_matches_reference_on_matrix_params():
    rng = np.random.default_rng(0)
    p0 = rng.normal(size=(2, 3))
    grads = [rng.normal(size=(2, 3)) for _ in range(5)]
    for wd in (0.0, 0.1):
        p, state = p0, None
        for g in grads:
            p, state = adam_step(p, g, state, lr=0.05, weight_decay=wd)
        ref_p, ref_m, ref_v = _ref_adam(p0, grads, 0.05, 0.9, 0.999, 1e-8, wd, decoupled=False)
        assert p.shape == (2, 3) and np.allclose(p, ref_p) and np.allclose(state["m"], ref_m)
        assert np.allclose(state["v"], ref_v) and state["t"] == 5


def test_adamw_matches_reference_and_differs_from_adam_with_l2():
    rng = np.random.default_rng(1)
    p0 = rng.normal(size=4) * 3
    grads = [rng.normal(size=4) for _ in range(4)]
    pw, sw, pa, sa = p0, None, p0, None
    for g in grads:
        pw, sw = adamw_step(pw, g, sw, lr=0.01, weight_decay=0.1)
        pa, sa = adam_step(pa, g, sa, lr=0.01, weight_decay=0.1)
    ref_w, ref_m, _ = _ref_adam(p0, grads, 0.01, 0.9, 0.999, 1e-8, 0.1, decoupled=True)
    ref_a, _, _ = _ref_adam(p0, grads, 0.01, 0.9, 0.999, 1e-8, 0.1, decoupled=False)
    assert np.allclose(pw, ref_w) and np.allclose(sw["m"], ref_m)
    assert np.allclose(pa, ref_a)
    assert not np.allclose(pw, pa, atol=1e-4), "decoupled decay must differ from L2 through the moments"


def test_adamw_first_step_exact_and_zero_decay_equals_adam():
    p, g = np.array([2.0, -4.0]), np.array([0.5, 0.0])
    new, state = adamw_step(p, g, None, lr=0.1, weight_decay=0.5)
    assert np.allclose(new, p - 0.1 * 0.5 * p - 0.1 * g / (np.abs(g) + 1e-8))
    assert np.allclose(state["m"], 0.1 * g)  # the decay never enters the moments
    a, _ = adam_step(p, g, None, lr=0.1)
    w, _ = adamw_step(p, g, None, lr=0.1, weight_decay=0.0)
    assert np.allclose(a, w)


def test_zero_gradients_are_safe():
    p = np.array([1.0, -3.0])
    z = np.zeros(2)
    with np.errstate(invalid="raise", divide="raise"):
        a, sa = adam_step(p, z, None, lr=0.1)
        w, _ = adamw_step(p, z, None, lr=0.1, weight_decay=0.2)
        r, _ = rmsprop_step(p, z, None, lr=0.1)
    assert np.array_equal(a, p) and np.array_equal(r, p) and np.all(sa["v"] == 0)
    assert np.allclose(w, p * (1 - 0.1 * 0.2))


def test_inputs_and_state_are_not_mutated():
    p, g = np.array([1.0, 2.0]), np.array([0.1, -0.2])
    p0, g0 = p.copy(), g.copy()
    _, state = adam_step(p, g, None, lr=0.1)
    snapshot = {"m": state["m"].copy(), "v": state["v"].copy(), "t": state["t"]}
    _, new_state = adam_step(p, g, state, lr=0.1)
    assert np.array_equal(p, p0) and np.array_equal(g, g0)
    assert np.array_equal(state["m"], snapshot["m"]) and np.array_equal(state["v"], snapshot["v"]) and state["t"] == 1
    assert new_state["t"] == 2 and new_state["m"] is not state["m"]
    v = np.array([0.5, 0.5])
    momentum_step(p, g, v, lr=0.1)
    s = np.array([0.5, 0.5])
    rmsprop_step(p, g, s, lr=0.1)
    _, sw = adamw_step(p, g, None, lr=0.1)
    adamw_step(p, g, sw, lr=0.1)
    assert np.array_equal(v, [0.5, 0.5]) and np.array_equal(s, [0.5, 0.5]) and sw["t"] == 1


def test_shape_validation():
    assert _raises(ValueError, sgd_step, np.ones(2), np.ones(3), 0.1)
    assert _raises(ValueError, momentum_step, np.ones(2), np.ones(2), np.ones(3), 0.1)
    assert _raises(ValueError, adam_step, np.ones((2, 2)), np.ones(4), None)
    # Shapes that broadcast silently are still bugs (e.g. a per-row gradient for a matrix).
    assert _raises(ValueError, sgd_step, np.ones((2, 3)), np.ones(3), 0.1)
    assert _raises(ValueError, adamw_step, np.ones((2, 3)), np.ones((1, 3)), None)
