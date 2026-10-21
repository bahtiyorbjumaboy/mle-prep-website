import math

import numpy as np

from solution import cross_entropy, l2_normalize, loss_and_grad, softmax, train

STRICT = dict(over="raise", divide="raise", invalid="raise")


def _dataset(n=4096, d=6, k=3, zero_rows=6, seed=0):
    """A large batch of three overlapping clusters plus all-zero rows (missing embeddings)."""
    rng = np.random.default_rng(seed)
    centers = rng.normal(0, 1, size=(k, d))
    y = rng.integers(0, k, size=n)
    x = centers[y] + rng.normal(0, 1, size=(n, d))
    x[:zero_rows] = 0.0
    y[:zero_rows] = 0
    return x, y


def _ref_log_softmax_row(row):
    peak = max(row)
    return [v - peak - math.log(sum(math.exp(u - peak) for u in row)) for v in row]


def test_zero_norm_rows_normalize_to_zero_without_fp_errors():
    x = np.array([[3.0, 4.0], [0.0, 0.0], [-1e-3, 0.0]])
    with np.errstate(**STRICT):
        out = l2_normalize(x)
    assert np.allclose(out, [[0.6, 0.8], [0.0, 0.0], [-1.0, 0.0]])
    assert np.array_equal(x, [[3.0, 4.0], [0.0, 0.0], [-1e-3, 0.0]]), "input mutated"


def test_softmax_extreme_logits_are_finite_and_exact():
    logits = np.array([[1000.0, 0.0, -1000.0], [-1000.0, -1001.0, -1003.0], [0.0, 0.0, 0.0]])
    with np.errstate(**STRICT):
        probs = softmax(logits)
    expected = np.exp([_ref_log_softmax_row(r) for r in logits.tolist()])
    assert np.isfinite(probs).all()
    assert np.allclose(probs, expected, rtol=1e-12, atol=0)
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_cross_entropy_is_exact_for_confident_mistakes():
    # True class trails by 1000: the loss is ~1000, not log(0) = inf and not a clipped 27.6.
    logits = np.array([[0.0, 1000.0], [5.0, -5.0], [2.0, 2.0]])
    y = np.array([0, 0, 1])
    with np.errstate(**STRICT):
        loss = cross_entropy(logits, y)
    expected = -sum(_ref_log_softmax_row(r)[c] for r, c in zip(logits.tolist(), y)) / 3
    assert math.isfinite(loss)
    assert math.isclose(loss, expected, rel_tol=1e-12), (loss, expected)
    assert loss > 300


def test_gradient_matches_finite_differences_of_the_mean_loss():
    rng = np.random.default_rng(1)
    x, y = rng.normal(size=(64, 5)), rng.integers(0, 4, size=64)
    W = rng.normal(0, 0.5, size=(5, 4))
    with np.errstate(**STRICT):
        loss, grad = loss_and_grad(W, x, y)
        numeric = np.zeros_like(W)
        eps = 1e-6
        for idx in np.ndindex(*W.shape):
            plus, minus = W.copy(), W.copy()
            plus[idx] += eps
            minus[idx] -= eps
            numeric[idx] = (cross_entropy(x @ plus, y) - cross_entropy(x @ minus, y)) / (2 * eps)
    assert math.isclose(loss, cross_entropy(x @ W, y), rel_tol=1e-12)
    assert np.allclose(grad, numeric, rtol=1e-5, atol=1e-8), np.abs(grad - numeric).max()


def test_step_size_does_not_grow_with_batch_size():
    rng = np.random.default_rng(2)
    x, y = rng.normal(size=(30, 4)), rng.integers(0, 3, size=30)
    W = rng.normal(size=(4, 3))
    loss1, grad1 = loss_and_grad(W, x, y)
    loss4, grad4 = loss_and_grad(W, np.tile(x, (4, 1)), np.tile(y, 4))
    assert math.isclose(loss1, loss4, rel_tol=1e-12)
    assert np.allclose(grad1, grad4), "repeating the batch must not change the update"


def test_every_traced_intermediate_is_finite():
    x, y = _dataset()
    seen = []

    def trace(step, name, value):
        assert np.isfinite(value).all(), f"first non-finite value: {name!r} at step {step}"
        seen.append(name)

    with np.errstate(**STRICT):
        train(x, y, n_classes=3, steps=60, trace=trace)
    assert seen[:5] == ["inputs", "logits", "loss", "grad", "W"]


def test_default_learning_rate_decreases_loss_monotonically_and_learns():
    x, y = _dataset()
    with np.errstate(**STRICT):
        W, losses = train(x, y, n_classes=3, steps=150)
    assert all(math.isfinite(v) for v in losses)
    assert all(b <= a + 1e-12 for a, b in zip(losses, losses[1:])), "loss increased"
    assert losses[-1] < 0.5 * losses[0]
    nonzero = np.abs(x).sum(axis=1) > 0
    accuracy = ((l2_normalize(x) @ W).argmax(axis=1) == y)[nonzero].mean()
    assert accuracy >= 0.8, accuracy
    assert np.abs(W).max() < 100, "weights should stay moderate with the default lr"


def test_training_is_deterministic():
    x, y = _dataset()
    with np.errstate(**STRICT):
        a, la = train(x, y, n_classes=3, steps=20, seed=3)
        b, lb = train(x, y, n_classes=3, steps=20, seed=3)
    assert np.array_equal(a, b) and la == lb
