import numpy as np


def kmeans(
    x: np.ndarray,
    k: int,
    seed: int = 0,
    max_iter: int = 100,
    tol: float = 1e-6,
    init: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, list[float]]:
    """Lloyd's k-means.

    Canonical prompt: implement Lloyd's k-means algorithm including initialization,
    assignment, update, convergence, max iterations, and deterministic seeding.

    Contract:
    - Initialization: if `init` is given, copy it as the starting `(k, d)` centers.
      Otherwise k-means++ with `rng = np.random.default_rng(seed)` (the only randomness;
      never the global `np.random`): first center uniform over rows, each next center
      a row drawn with probability proportional to its squared distance to the nearest
      chosen center; if all those distances are 0 (identical points), draw uniformly.
    - Each iteration: assign every point to its nearest center (squared Euclidean;
      ties -> lowest center index), then move each center to the mean of its points.
    - Empty clusters must never produce NaN. Keeping the old center or relocating it
      to a data point are both acceptable (the reference relocates it to the point
      farthest from its current center).
    - `history[t]` is the objective after iteration `t`'s update:
      `sum_i min_j ||x_i - c_j||^2`. It must be non-increasing.
    - Stop after the first iteration whose largest center shift (Euclidean) is
      `<= tol`, or after `max_iter` iterations.
    - Returned `labels` are the nearest-center assignment to the returned centers.
    - Vectorized assignment/update: O(n k d) array work per iteration, no Python loop
      over points (a loop over the k centers is fine).

    Args:
        x: `(n, d)` data. k: `1 <= k <= n`. max_iter: `>= 1`. init: optional `(k, d)`.

    Returns:
        `(labels, centers, history)`: integer `(n,)`, float64 `(k, d)`, list of floats.

    Raises:
        ValueError: if `k` is outside `[1, n]`, `max_iter < 1`, `x` is not 2-D, or
            `init` has the wrong shape.
    """
    raise NotImplementedError("TODO: implement ML-05")
