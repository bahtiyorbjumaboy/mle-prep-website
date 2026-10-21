import numpy as np


def score_ragged(
    user_vectors: np.ndarray,
    item_vectors: np.ndarray,
    item_ids: np.ndarray,
    lengths: np.ndarray,
) -> np.ndarray:
    """Vectorized per-segment softmax of user-item dot products over a CSR ragged batch."""
    users = np.asarray(user_vectors, dtype=float)
    items = np.asarray(item_vectors, dtype=float)
    ids = np.asarray(item_ids, dtype=np.intp)  # intp: np.repeat rejects int64 on wasm32
    lengths = np.asarray(lengths, dtype=np.intp)
    n_users = len(users)
    if users.ndim != 2 or items.ndim != 2 or users.shape[1] != items.shape[1]:
        raise ValueError("user_vectors (U, d) and item_vectors (I, d) must share d")
    if lengths.shape != (n_users,) or np.any(lengths < 0) or lengths.sum() != len(ids):
        raise ValueError("lengths must be U non-negative counts summing to len(item_ids)")
    if ids.size and (ids.min() < 0 or ids.max() >= len(items)):
        raise ValueError("item ids out of range")

    # segment[t] = owning user of flat slot t; empty segments simply never appear.
    segment = np.repeat(np.arange(n_users), lengths)
    scores = np.einsum("nd,nd->n", users[segment], items[ids])  # gather, then rowwise dot

    # Per-segment max for stability. maximum.at handles empty segments, unlike reduceat.
    seg_max = np.full(n_users, -np.inf)
    np.maximum.at(seg_max, segment, scores)
    exp = np.exp(scores - seg_max[segment])
    seg_sum = np.bincount(segment, weights=exp, minlength=n_users)
    return exp / seg_sum[segment]
