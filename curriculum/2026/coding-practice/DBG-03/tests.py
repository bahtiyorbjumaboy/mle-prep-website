import math

import numpy as np

from solution import score_candidates


def _reference(logits, weights):
    """Independent per-query loop implementation of the documented contract."""
    probs, relative = [], []
    for row in logits:
        peak = max(row)
        exps = [math.exp(v - peak) for v in row]
        total = sum(exps)
        probs.append([e / total for e in exps])
        mean = sum(row) / len(row)
        relative.append([v - mean for v in row])
    share = [
        sum(w * p[c] for w, p in zip(weights, probs)) / sum(weights) for c in range(len(logits[0]))
    ]
    return np.array(probs), np.array(relative), np.array(share)


def _logits(b, c, seed):
    rng = np.random.default_rng(seed)
    # Rows on very different scales/offsets, so per-row vs global structure matters.
    return rng.normal(size=(b, c)) * rng.uniform(0.5, 4.0, size=(b, 1)) + rng.normal(0, 5, (b, 1))


def _check_against_reference(logits, weights):
    out = score_candidates(logits, weights)
    probs, relative, share = _reference(logits.tolist(), list(weights))
    b, c = logits.shape
    assert out["probs"].shape == (b, c), out["probs"].shape
    assert out["relative_logits"].shape == (b, c), out["relative_logits"].shape
    assert out["candidate_share"].shape == (c,), out["candidate_share"].shape
    assert np.allclose(out["probs"], probs, atol=1e-12), "probs differ from per-query softmax"
    assert np.allclose(out["relative_logits"], relative, atol=1e-12), "relative_logits wrong"
    assert np.allclose(out["candidate_share"], share, atol=1e-12), "candidate_share wrong"


def test_square_batch_matches_reference():
    # B == C: every bug broadcasts silently here.
    _check_against_reference(_logits(4, 4, 0), np.array([1.0, 3.0, 0.5, 2.0]))


def test_rectangular_batch_matches_reference():
    _check_against_reference(_logits(3, 5, 1), np.array([2.0, 1.0, 7.0]))
    _check_against_reference(_logits(6, 2, 2), np.array([1.0, 0.0, 2.0, 3.0, 1.0, 5.0]))


def test_single_query_batch():
    _check_against_reference(np.array([[0.5, -1.0, 2.0, 0.0]]), np.array([3.0]))


def test_rows_are_probability_distributions():
    out = score_candidates(_logits(5, 7, 3), np.ones(5))
    assert np.all(out["probs"] >= 0)
    assert np.allclose(out["probs"].sum(axis=1), 1.0)
    assert math.isclose(out["candidate_share"].sum(), 1.0, rel_tol=1e-12)


def test_per_query_offsets_do_not_change_scores():
    logits, weights = _logits(4, 6, 4), np.array([1.0, 2.0, 3.0, 4.0])
    offsets = np.array([[100.0], [-40.0], [0.0], [7.5]])
    base, shifted = score_candidates(logits, weights), score_candidates(logits + offsets, weights)
    for key in ("probs", "relative_logits", "candidate_share"):
        assert np.allclose(base[key], shifted[key], atol=1e-9), f"{key} depends on row offsets"


def test_one_query_does_not_affect_another():
    logits, weights = _logits(4, 4, 5), np.array([1.0, 1.0, 2.0, 0.5])
    alone = score_candidates(logits[:1], weights[:1])
    batched = score_candidates(logits, weights)
    for key in ("probs", "relative_logits"):
        assert np.allclose(batched[key][:1], alone[key]), f"{key} of query 0 depends on the batch"


def test_query_and_candidate_permutation_equivariance():
    logits, weights = _logits(5, 5, 6), np.array([0.2, 1.0, 3.0, 0.7, 2.0])
    rows, cols = np.array([3, 0, 4, 1, 2]), np.array([1, 4, 0, 2, 3])
    base = score_candidates(logits, weights)
    perm = score_candidates(logits[rows][:, cols], weights[rows])
    assert np.allclose(perm["probs"], base["probs"][rows][:, cols])
    assert np.allclose(perm["relative_logits"], base["relative_logits"][rows][:, cols])
    assert np.allclose(perm["candidate_share"], base["candidate_share"][cols])


def test_query_weights_are_relative_traffic():
    logits = _logits(3, 3, 7)
    out = score_candidates(logits, np.array([0.0, 1.0, 0.0]))
    assert np.allclose(out["candidate_share"], out["probs"][1]), "zero-weight queries must not count"
    scaled = score_candidates(logits, np.array([2.0, 5.0, 1.0]) * 10)
    assert np.allclose(scaled["candidate_share"], score_candidates(logits, [2.0, 5.0, 1.0])["candidate_share"])


def test_extreme_logits_stay_finite_and_exact():
    logits = np.array([[1000.0, 999.0, -1000.0], [-1000.0, -1001.0, -1002.0]])
    out = score_candidates(logits, np.array([1.0, 1.0]))
    assert all(np.isfinite(v).all() for v in out.values())
    _check_against_reference(logits, np.array([1.0, 1.0]))


def test_inputs_are_not_mutated():
    logits, weights = _logits(4, 4, 8), np.array([1.0, 2.0, 3.0, 4.0])
    before = logits.copy(), weights.copy()
    score_candidates(logits, weights)
    assert np.array_equal(logits, before[0]) and np.array_equal(weights, before[1])
