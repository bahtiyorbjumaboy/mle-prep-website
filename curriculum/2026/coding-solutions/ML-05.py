import numpy as np


def _sq_distances(x: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """(n, k) squared distances via the norm expansion, clamped at 0."""
    d = (x * x).sum(axis=1)[:, None] - 2.0 * x @ centers.T + (centers * centers).sum(axis=1)[None, :]
    return np.maximum(d, 0.0)


def _kmeans_plus_plus(x: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """Seeded k-means++ (loop over k only)."""
    n = len(x)
    centers = [x[rng.integers(n)]]
    closest = _sq_distances(x, centers[0][None, :])[:, 0]
    for _ in range(1, k):
        total = closest.sum()
        # All remaining points coincide with chosen centers: D^2 / sum would be 0/0.
        probs = closest / total if total > 0 else np.full(n, 1.0 / n)
        centers.append(x[rng.choice(n, p=probs)])
        closest = np.minimum(closest, _sq_distances(x, centers[-1][None, :])[:, 0])
    return np.array(centers)


def kmeans(
    x: np.ndarray,
    k: int,
    seed: int = 0,
    max_iter: int = 100,
    tol: float = 1e-6,
    init: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, list[float]]:
    """Lloyd's algorithm with k-means++ (or explicit) init and empty-cluster relocation."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 2:
        raise ValueError("x must be (n, d)")
    n, d = x.shape
    if not 1 <= k <= n:
        raise ValueError("k must satisfy 1 <= k <= n")
    if max_iter < 1:
        raise ValueError("max_iter must be >= 1")
    if init is None:
        centers = _kmeans_plus_plus(x, k, np.random.default_rng(seed))
    else:
        centers = np.array(init, dtype=float)  # copy: never update the caller's array
        if centers.shape != (k, d):
            raise ValueError("init must have shape (k, d)")

    history: list[float] = []
    for _ in range(max_iter):
        dist = _sq_distances(x, centers)
        labels = np.argmin(dist, axis=1)  # argmin returns the first (lowest) index on ties
        counts = np.bincount(labels, minlength=k)
        sums = np.zeros((k, d))
        np.add.at(sums, labels, x)
        new_centers = centers.copy()
        nonempty = counts > 0
        new_centers[nonempty] = sums[nonempty] / counts[nonempty, None]
        # Empty cluster: move it onto the point that is currently worst served.
        point_cost = dist[np.arange(n), labels]
        for j in np.flatnonzero(~nonempty):  # loop over (rare) empty clusters only
            far = int(np.argmax(point_cost))
            new_centers[j] = x[far]
            point_cost[far] = 0.0
        shift = np.sqrt(((new_centers - centers) ** 2).sum(axis=1)).max()
        centers = new_centers
        history.append(float(_sq_distances(x, centers).min(axis=1).sum()))
        if shift <= tol:
            break
    labels = np.argmin(_sq_distances(x, centers), axis=1)
    return labels, centers, history
