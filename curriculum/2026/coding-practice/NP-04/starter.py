import math

import numpy as np


def score_ragged_slow(
    user_vectors: np.ndarray,
    item_vectors: np.ndarray,
    item_ids: np.ndarray,
    lengths: np.ndarray,
) -> np.ndarray:
    """Given: correct but slow nested-loop reference. Do not edit; match it exactly.

    User `u` owns the next `lengths[u]` entries of the flat `item_ids` array (a
    CSR-style ragged batch). Each candidate is scored with `dot(user, item)` and the
    scores are softmaxed within that user's segment. Output order matches `item_ids`.
    """
    probs = []
    start = 0
    for u, length in enumerate(lengths):
        segment = item_ids[start:start + length]
        start += length
        scores = []
        for item in segment:
            s = 0.0
            for j in range(len(user_vectors[u])):
                s += float(user_vectors[u][j]) * float(item_vectors[item][j])
            scores.append(s)
        if scores:
            top = max(scores)
            exps = [math.exp(s - top) for s in scores]
            total = sum(exps)
            probs.extend(e / total for e in exps)
    return np.array(probs, dtype=float)


def score_ragged(
    user_vectors: np.ndarray,
    item_vectors: np.ndarray,
    item_ids: np.ndarray,
    lengths: np.ndarray,
) -> np.ndarray:
    """Vectorized equivalent of `score_ragged_slow`.

    Canonical prompt: you are given correct but slow nested-loop code that scores
    ragged user-item candidate lists with dot products and softmax. Vectorize it,
    preserve output order, and prove equivalence with a tolerance.

    Contract (no Python loops over users, candidates, or features):
    - Output equals `score_ragged_slow` within `rtol=1e-9` for float64 inputs and
      `atol=1e-5` for float32 inputs; output dtype is float64, shape `(len(item_ids),)`.
    - Users with zero candidates contribute nothing; segments may be empty anywhere.
    - Must stay finite for large scores (e.g. dot products around 1e3).
    - Duplicate item ids within a segment are scored independently, in place.

    Args:
        user_vectors: `(U, d)` user embeddings.
        item_vectors: `(I, d)` item embeddings.
        item_ids: 1-D integer array of length `N` with ids in `[0, I)`.
        lengths: 1-D non-negative integer array of length `U` summing to `N`.
            The browser runtime is 32-bit: keep index/count arrays as `np.intp`
            (not int64), e.g. for `np.repeat` counts.

    Returns:
        Float64 array `(N,)` of per-segment softmax probabilities.

    Raises:
        ValueError: if `len(lengths) != U`, a length is negative, `sum(lengths) != N`,
            an item id is out of range, or the embedding dimensions differ.
    """
    raise NotImplementedError("TODO: implement NP-04")
