import numpy as np


def _check(groups: list[np.ndarray], n: int, alpha: float = 0.05) -> None:
    if any(len(g) == 0 for g in groups):
        raise ValueError("groups must be non-empty")
    if n < 1:
        raise ValueError("number of resamples must be >= 1")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")


def _percentile_ci(replicates: np.ndarray, alpha: float) -> tuple[float, float]:
    low, high = np.quantile(replicates, [alpha / 2, 1 - alpha / 2])
    return float(low), float(high)


def bootstrap_diff_ci(
    control: np.ndarray, treatment: np.ndarray, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float]:
    """Resample each group's users independently (own size), then take percentiles."""
    c = np.asarray(control, dtype=float)
    t = np.asarray(treatment, dtype=float)
    _check([c, t], n_boot, alpha)
    rng = np.random.default_rng(seed)
    c_means = c[rng.integers(0, len(c), size=(n_boot, len(c)))].mean(axis=1)
    t_means = t[rng.integers(0, len(t), size=(n_boot, len(t)))].mean(axis=1)
    return _percentile_ci(t_means - c_means, alpha)


def permutation_pvalue(control: np.ndarray, treatment: np.ndarray, n_perm: int = 2000, seed: int = 0) -> float:
    """Two-sided Monte Carlo permutation p-value with the +1 correction."""
    c = np.asarray(control, dtype=float)
    t = np.asarray(treatment, dtype=float)
    _check([c, t], n_perm)
    pooled = np.concatenate([c, t])
    n_t = len(t)
    observed = abs(t.mean() - c.mean())
    rng = np.random.default_rng(seed)
    # Each row is a random relabeling: the first n_t shuffled users form "treatment".
    shuffled = rng.permuted(np.broadcast_to(pooled, (n_perm, len(pooled))), axis=1)
    perm_t = shuffled[:, :n_t].mean(axis=1)
    perm_c = shuffled[:, n_t:].mean(axis=1)
    extreme = np.abs(perm_t - perm_c) >= observed - 1e-12
    return float((1 + extreme.sum()) / (1 + n_perm))


def bootstrap_ratio_diff_ci(
    numerator_control: np.ndarray,
    denominator_control: np.ndarray,
    numerator_treatment: np.ndarray,
    denominator_treatment: np.ndarray,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float]:
    """Resample users (numerator and denominator together); ratio = sum(num) / sum(den)."""
    groups = [np.asarray(a, dtype=float) for a in
              (numerator_control, denominator_control, numerator_treatment, denominator_treatment)]
    num_c, den_c, num_t, den_t = groups
    if num_c.shape != den_c.shape or num_t.shape != den_t.shape:
        raise ValueError("numerator and denominator must align per user")
    if np.any(den_c <= 0) or np.any(den_t <= 0):
        raise ValueError("denominators must be positive")
    _check(groups, n_boot, alpha)
    rng = np.random.default_rng(seed)
    idx_c = rng.integers(0, len(num_c), size=(n_boot, len(num_c)))  # one index -> both columns
    idx_t = rng.integers(0, len(num_t), size=(n_boot, len(num_t)))
    ratio_c = num_c[idx_c].sum(axis=1) / den_c[idx_c].sum(axis=1)
    ratio_t = num_t[idx_t].sum(axis=1) / den_t[idx_t].sum(axis=1)
    return _percentile_ci(ratio_t - ratio_c, alpha)
