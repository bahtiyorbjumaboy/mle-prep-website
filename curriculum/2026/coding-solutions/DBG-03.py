import numpy as np

# Repair of the DBG-03 starter. The defects and their fixes:
# 1. `softmax(logits, axis=0)` normalized each candidate across queries. Fix: axis=1, the
#    candidate axis, so every query's row is a distribution.
# 2. `probs * weights` with shapes (B, C) * (B,) aligns the weights with the candidate
#    axis: silently wrong when B == C, an error otherwise. Fix: `weights[:, None]`.
# 3. `logits.mean()` subtracted one global scalar, so a query's relative logits depended on
#    the other queries in the batch. Fix: per-row mean with keepdims.


def softmax(x: np.ndarray, axis: int) -> np.ndarray:
    """Numerically stable softmax along `axis`."""
    shifted = x - x.max(axis=axis, keepdims=True)
    e = np.exp(shifted)
    return e / e.sum(axis=axis, keepdims=True)


def score_candidates(logits: np.ndarray, query_weights: np.ndarray) -> dict[str, np.ndarray]:
    """Per-query candidate probabilities, relative logits, and weighted candidate shares."""
    logits = np.asarray(logits, dtype=float)
    weights = np.asarray(query_weights, dtype=float)

    probs = softmax(logits, axis=1)
    relative_logits = logits - logits.mean(axis=1, keepdims=True)
    weighted = probs * weights[:, None]
    candidate_share = weighted.sum(axis=0) / weights.sum()
    return {
        "probs": probs,
        "relative_logits": relative_logits,
        "candidate_share": candidate_share,
    }
