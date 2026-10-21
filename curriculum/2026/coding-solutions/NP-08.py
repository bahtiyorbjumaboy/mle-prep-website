from collections.abc import Callable

import numpy as np


def sample_categorical(probs: np.ndarray, n_samples: int, rng: np.random.Generator) -> np.ndarray:
    """Vectorized inverse-CDF sampling: one uniform per draw, counted against each row's CDF."""
    p = np.asarray(probs, dtype=float)
    if p.ndim != 2 or not np.all(np.isfinite(p)) or np.any(p < 0):
        raise ValueError("probs must be a finite non-negative (B, C) array")
    sums = p.sum(axis=1, keepdims=True)
    if np.any(np.abs(sums - 1.0) > 1e-4):
        raise ValueError("each probability row must sum to 1")
    cdf = np.cumsum(p / sums, axis=1)
    cdf[:, -1] = 1.0  # rounding must never leave u > cdf[-1] (which would yield id C)
    u = rng.random((len(p), n_samples))
    # id = #{c : cdf[c] <= u}; zero-mass categories repeat the previous cdf value and are skipped.
    # Memory O(B * n_samples * C); for large C use searchsorted on cdf + row offsets instead.
    return (u[:, :, None] >= cdf[:, None, :]).sum(axis=2)


def sample_weighted(weights: np.ndarray, n_samples: int, rng: np.random.Generator) -> np.ndarray:
    """Sample indices proportional to unnormalized weights without overflow or mutation."""
    w = np.array(weights, dtype=float)  # a copy: never normalize the caller's array in place
    if w.ndim != 1 or not np.all(np.isfinite(w)) or np.any(w < 0) or not np.any(w > 0):
        raise ValueError("weights must be 1-D, finite, non-negative, and not all zero")
    w = w / w.max()  # rescale first: sum([1e308, 1e308]) overflows to inf
    return rng.choice(len(w), size=n_samples, p=w / w.sum())


def monte_carlo_expectation(
    f: Callable[[np.ndarray], np.ndarray],
    sampler: Callable[[np.random.Generator, int], np.ndarray],
    n_samples: int,
    rng: np.random.Generator,
    batch_size: int | None = None,
) -> tuple[float, float]:
    """Mean and standard error of f(X), merging per-batch (count, mean, M2) with Chan's formula."""
    if n_samples < 2:
        raise ValueError("n_samples must be >= 2")
    if batch_size is None:
        batch_size = n_samples
    elif batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    count, mean, m2 = 0, 0.0, 0.0
    for start in range(0, n_samples, batch_size):
        values = np.asarray(f(sampler(rng, min(batch_size, n_samples - start))), dtype=float)
        b_count, b_mean = len(values), values.mean()
        b_m2 = np.sum((values - b_mean) ** 2)  # two-pass within the batch: no cancellation
        delta = b_mean - mean
        total = count + b_count
        mean += delta * b_count / total
        m2 += b_m2 + delta ** 2 * count * b_count / total
        count = total
    return float(mean), float(np.sqrt(m2 / (count - 1)) / np.sqrt(count))


def bootstrap_means(data: np.ndarray, n_resamples: int, rng: np.random.Generator) -> np.ndarray:
    """Resample rows with replacement via one (n_resamples, n) index matrix."""
    data = np.asarray(data, dtype=float)
    if data.shape[0] == 0 or n_resamples < 1:
        raise ValueError("need non-empty data and n_resamples >= 1")
    idx = rng.integers(0, len(data), size=(n_resamples, len(data)))
    return data[idx].mean(axis=1)  # data[idx] keeps whole rows together


def spawn_streams(seed: int, n_streams: int) -> list[np.random.Generator]:
    """Independent child streams from one SeedSequence."""
    return [np.random.default_rng(child) for child in np.random.SeedSequence(seed).spawn(n_streams)]
