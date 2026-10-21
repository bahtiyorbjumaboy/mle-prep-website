import numpy as np

# Incident: the candidate-scoring job passed its unit test (a 4-query x 4-candidate batch)
# and produces plausible-looking numbers, but candidate shares disagree with a hand-checked
# notebook. A batch of 3 queries x 5 candidates crashes, and a single-query batch returns
# probability 1.0 for every candidate.
#
# Canonical prompt: a NumPy scoring function returns plausible but wrong results because
# softmax uses the wrong axis, row weights broadcast along the wrong dimension, and a global
# mean collapses structure. Find, fix, and test all three.
# Follow-up: construct a shape where the bug becomes an error.


def softmax(x: np.ndarray, axis: int) -> np.ndarray:
    """Numerically stable softmax along `axis`."""
    shifted = x - x.max(axis=axis, keepdims=True)
    e = np.exp(shifted)
    return e / e.sum(axis=axis, keepdims=True)


def score_candidates(logits: np.ndarray, query_weights: np.ndarray) -> dict[str, np.ndarray]:
    """Scores a batch of queries against a shared candidate set.

    Args:
        logits: `(B, C)` model scores; row `b` is query `b`, column `c` is candidate `c`.
        query_weights: `(B,)` non-negative traffic weight per query, with a positive sum.

    Returns:
        - `probs` `(B, C)`: softmax over candidates within each query (each row sums to 1).
        - `relative_logits` `(B, C)`: each logit minus the mean logit of its own query.
        - `candidate_share` `(C,)`: traffic-weighted mean of `probs` over queries,
          `sum_b w_b * probs[b, c] / sum_b w_b`.
        Inputs are not mutated.
    """
    logits = np.asarray(logits, dtype=float)
    weights = np.asarray(query_weights, dtype=float)

    probs = softmax(logits, axis=0)
    relative_logits = logits - logits.mean()
    weighted = probs * weights
    candidate_share = weighted.sum(axis=0) / weights.sum()
    return {
        "probs": probs,
        "relative_logits": relative_logits,
        "candidate_share": candidate_share,
    }
