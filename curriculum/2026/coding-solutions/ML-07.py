from collections import defaultdict

import numpy as np

# Below this acceptance rate, rejection sampling is replaced by sampling the explicit complement.
MIN_ACCEPTANCE = 0.1


def sample_negatives(
    interactions: list[tuple[int, int]],
    n_items: int,
    n_neg: int,
    seed: int,
    popularity: np.ndarray | None = None,
) -> np.ndarray:
    """Per-interaction negatives that exclude all of the user's positives (rejection sampling)."""
    if n_neg < 1:
        raise ValueError("n_neg must be >= 1")
    positives: dict[object, set[int]] = defaultdict(set)
    for user, item in interactions:
        if not 0 <= item < n_items:
            raise ValueError(f"item {item} outside [0, {n_items})")
        positives[user].add(int(item))

    rng = np.random.default_rng(seed)
    if popularity is None:
        probs, cdf = None, None
    else:
        weights = np.asarray(popularity, dtype=float)
        if weights.shape != (n_items,) or not np.all(np.isfinite(weights)) or np.any(weights < 0):
            raise ValueError("popularity must be (n_items,) finite and non-negative")
        if weights.sum() == 0:
            raise ValueError("popularity has no positive mass")
        probs = weights / weights.sum()
        cdf = np.cumsum(probs)  # O(n_items) setup, shared by all users
        cdf[-1] = 1.0

    out = np.empty((len(interactions), n_neg), dtype=np.int64)
    for row, (user, _) in enumerate(interactions):
        out[row] = _draw(positives[user], n_items, n_neg, rng, probs, cdf)
    return out


def _draw(
    excluded: set[int],
    n_items: int,
    n_neg: int,
    rng: np.random.Generator,
    probs: np.ndarray | None,
    cdf: np.ndarray | None,
) -> list[int]:
    """n_neg distinct items, each drawn proportionally to its weight among the remaining ones."""
    excluded_ids = np.fromiter(excluded, dtype=np.int64, count=len(excluded))
    if probs is None:
        eligible = n_items - len(excluded)
        acceptance = eligible / n_items
    else:
        eligible = int(np.count_nonzero(probs)) - int(np.count_nonzero(probs[excluded_ids]))
        acceptance = 1.0 - probs[excluded_ids].sum()
    if eligible < n_neg:
        raise ValueError("not enough eligible negatives for a user")

    if acceptance - n_neg / max(n_items, 1) < MIN_ACCEPTANCE:
        # Near-full-catalog user: sample the explicit complement (O(n_items) for this user only).
        allowed = np.setdiff1d(np.arange(n_items), excluded_ids)
        p = None if probs is None else probs[allowed] / probs[allowed].sum()
        if p is not None:
            allowed, p = allowed[p > 0], p[p > 0]
        return rng.choice(allowed, size=n_neg, replace=False, p=p).tolist()

    # Rejection: drawing from the full distribution and discarding excluded or already
    # chosen items is exactly sequential sampling without replacement from the rest.
    chosen: list[int] = []
    seen = set(excluded)
    while len(chosen) < n_neg:
        size = 2 * (n_neg - len(chosen)) + 4
        if probs is None:
            candidates = rng.integers(0, n_items, size=size)
        else:
            candidates = np.searchsorted(cdf, rng.random(size), side="right")
        for item in candidates.tolist():
            if item not in seen:
                seen.add(item)
                chosen.append(item)
                if len(chosen) == n_neg:
                    break
    return chosen
