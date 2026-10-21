import numpy as np

# Canonical prompt: given user-level control/treatment metrics, compute a percentile
# bootstrap CI for difference in means, a two-sided permutation-test p-value, and a
# bootstrap CI for a ratio metric.
#
# Shared contract:
# - Users are the resampling unit; control and treatment are independent (unpaired)
#   samples and may have different sizes. Each bootstrap replicate resamples control
#   users with replacement to size n_c and treatment users to size n_t, separately.
# - Differences are always treatment minus control.
# - Percentile CI: `(np.quantile(reps, alpha / 2), np.quantile(reps, 1 - alpha / 2))`.
# - All randomness comes from one `np.random.default_rng(seed)`; the same inputs and
#   seed reproduce the same result. Inputs are never modified.
# - Raise ValueError for an empty group, `alpha` outside (0, 1), or a non-positive
#   number of resamples/permutations.


def bootstrap_diff_ci(
    control: np.ndarray, treatment: np.ndarray, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float]:
    """Percentile bootstrap CI for `mean(treatment) - mean(control)`."""
    raise NotImplementedError("TODO: implement ML-09")


def permutation_pvalue(control: np.ndarray, treatment: np.ndarray, n_perm: int = 2000, seed: int = 0) -> float:
    """Two-sided Monte Carlo permutation test of the difference in means.

    Statistic `T = mean(treatment) - mean(control)`. Each permutation randomly
    reassigns the pooled users to groups of the original sizes n_c and n_t. Return
    `(1 + #{|T_perm| >= |T_obs|}) / (1 + n_perm)`; the +1 counts the observed labeling,
    so the p-value is never 0. Compare with a tiny tolerance (`|T_perm| >= |T_obs| - 1e-12`)
    so float noise cannot drop exact ties.
    """
    raise NotImplementedError("TODO: implement ML-09")


def bootstrap_ratio_diff_ci(
    numerator_control: np.ndarray,
    denominator_control: np.ndarray,
    numerator_treatment: np.ndarray,
    denominator_treatment: np.ndarray,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the difference in ratio metrics `R_t - R_c`.

    A group's ratio metric is `sum(numerator) / sum(denominator)` over its users (for
    example clicks / views), not the mean of per-user ratios. Resample users, keeping
    each user's numerator and denominator together. Denominators must be positive
    (ValueError otherwise, or on length mismatch within a group).
    """
    raise NotImplementedError("TODO: implement ML-09")
