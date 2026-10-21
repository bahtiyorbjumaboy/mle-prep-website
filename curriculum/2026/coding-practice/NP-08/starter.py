from collections.abc import Callable

import numpy as np

# Canonical prompt: using an explicit RNG object/seed, implement categorical sampling
# from probability rows, weighted sampling without accidental normalization bugs,
# Monte Carlo estimation of an expectation, and a vectorized bootstrap resample
# primitive.
#
# RNG ownership contract for every function: draw randomness only from the `rng`
# argument (a `np.random.Generator`). Never touch the global `np.random.*` state and
# never create a fresh generator inside, so the same seeded rng replays exactly and
# successive calls on one rng advance its stream.


def sample_categorical(probs: np.ndarray, n_samples: int, rng: np.random.Generator) -> np.ndarray:
    """Draw `n_samples` category ids independently from each probability row.

    Args:
        probs: `(B, C)` non-negative finite rows, each summing to 1 within `1e-4`.
            Rows are renormalized before sampling, so ids are always in `[0, C)` and
            zero-probability categories are never drawn.
        n_samples: Number of draws per row, `>= 1`.
        rng: Source of randomness.

    Returns:
        Integer array `(B, n_samples)`. Vectorized: no Python loop over rows or draws
        (`rng.choice` takes one probability vector, so it does not vectorize over rows).

    Raises:
        ValueError: non-2-D probs, negative/non-finite entries, or a row sum off by > 1e-4.
    """
    raise NotImplementedError("TODO: implement NP-08")


def sample_weighted(weights: np.ndarray, n_samples: int, rng: np.random.Generator) -> np.ndarray:
    """Draw `n_samples` indices with replacement, P(i) proportional to `weights[i]`.

    Weights are unnormalized (ints, lists, huge or tiny magnitudes such as `1e308` or
    `1e-310` are valid) and must not be modified in place.

    Returns:
        Integer array `(n_samples,)`.

    Raises:
        ValueError: if weights are not 1-D, contain negative/non-finite values, or are all zero.
    """
    raise NotImplementedError("TODO: implement NP-08")


def monte_carlo_expectation(
    f: Callable[[np.ndarray], np.ndarray],
    sampler: Callable[[np.random.Generator, int], np.ndarray],
    n_samples: int,
    rng: np.random.Generator,
    batch_size: int | None = None,
) -> tuple[float, float]:
    """Estimate `E[f(X)]` and its standard error from `n_samples` draws.

    `sampler(rng, size)` returns `size` samples along axis 0; `f` maps that batch to a
    `(size,)` array. The standard error is `std(f, ddof=1) / sqrt(n_samples)`.

    With `batch_size`, never request more than `batch_size` samples per sampler call
    (memory O(batch_size)) and combine per-batch statistics exactly: the result must
    match the unbatched computation to ~1e-9 relative even when `f` has a huge mean
    (e.g. `1e8 + U`), so `E[f^2] - E[f]^2` is not acceptable.

    Raises:
        ValueError: if `n_samples < 2` or `batch_size < 1`.
    """
    raise NotImplementedError("TODO: implement NP-08")


def bootstrap_means(data: np.ndarray, n_resamples: int, rng: np.random.Generator) -> np.ndarray:
    """Vectorized bootstrap of the mean: resample rows with replacement.

    Args:
        data: `(n,)` or `(n, d)`; the resampling unit is a row, so columns of a
            resampled row stay paired.
        n_resamples: `>= 1`.

    Returns:
        `(n_resamples,)` for 1-D data or `(n_resamples, d)` for 2-D data. No Python
        loop over resamples.

    Raises:
        ValueError: on empty data or `n_resamples < 1`.
    """
    raise NotImplementedError("TODO: implement NP-08")


def spawn_streams(seed: int, n_streams: int) -> list[np.random.Generator]:
    """Return `n_streams` statistically independent, reproducible generators.

    Same `seed` -> same streams; streams must not simply be `seed, seed + 1, ...`
    reseeds of `default_rng` (use `np.random.SeedSequence`).
    """
    raise NotImplementedError("TODO: implement NP-08")
