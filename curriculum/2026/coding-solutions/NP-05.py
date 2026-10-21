import numpy as np


def pad_sequences(sequences: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Right-pad `(L_i, d)` sequences into `(B, T, d)` with a `(B, T)` boolean mask."""
    if not sequences:
        raise ValueError("need at least one sequence")
    arrays = [np.asarray(s, dtype=float) for s in sequences]
    if any(a.ndim != 2 for a in arrays) or len({a.shape[1] for a in arrays}) != 1:
        raise ValueError("every sequence must be 2-D with the same d")
    lengths = np.array([len(a) for a in arrays], dtype=np.intp)
    b, t, d = len(arrays), int(lengths.max()), arrays[0].shape[1]

    mask = np.arange(t)[None, :] < lengths[:, None]  # (B, T)
    padded = np.zeros((b, t, d))
    # Row-major order of mask's True cells matches the concatenated sequences.
    padded[mask] = np.concatenate(arrays, axis=0)
    return padded, mask


def masked_mean_pool(padded: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mean over real positions; rows with no real positions give zeros."""
    weights = mask.astype(float)[..., None]  # (B, T, 1) broadcasts over d
    counts = weights.sum(axis=1)  # (B, 1)
    # where() rather than padded * weights: garbage such as inf/NaN in padding stays out.
    sums = np.where(weights > 0, padded, 0.0).sum(axis=1)
    return sums / np.maximum(counts, 1.0)


def last_n_mean_pool(padded: np.ndarray, mask: np.ndarray, n: int = 5) -> np.ndarray:
    """Mean over the last `n` real positions (by time index), for any mask pattern."""
    if n < 1:
        raise ValueError("n must be >= 1")
    # rank_from_end[b, t] = number of real positions at index >= t (1 for the last one).
    rank_from_end = np.cumsum(mask[:, ::-1], axis=1)[:, ::-1]
    return masked_mean_pool(padded, mask & (rank_from_end <= n))


def masked_max_pool(padded: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Max over real positions; padding is replaced by -inf so it can never win."""
    masked = np.where(mask[..., None], padded, -np.inf)
    out = masked.max(axis=1, initial=-np.inf)  # initial handles T == 0
    return np.where(mask.any(axis=1)[:, None], out, 0.0)


def pad_and_pool(
    sequences: list[np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pad, then return the masked mean and the mean of the last five real positions."""
    padded, mask = pad_sequences(sequences)
    return padded, mask, masked_mean_pool(padded, mask), last_n_mean_pool(padded, mask, 5)
