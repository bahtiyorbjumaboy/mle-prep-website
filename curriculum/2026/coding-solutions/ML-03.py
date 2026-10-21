import hashlib

import numpy as np

N_BUCKETS = 10_000


def hash_bucket(group: object, salt: str = "", n_buckets: int = N_BUCKETS) -> int:
    """Process-independent bucket: sha256 of "salt:group" modulo n_buckets."""
    digest = hashlib.sha256(f"{salt}:{group}".encode("utf-8")).hexdigest()
    return int(digest, 16) % n_buckets


def _check_fraction(test_fraction: float) -> None:
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be in (0, 1)")


def group_hash_split(groups: list[object], test_fraction: float, salt: str = "") -> np.ndarray:
    """Test iff the group's stable bucket falls below the threshold; groups never split."""
    _check_fraction(test_fraction)
    threshold = test_fraction * N_BUCKETS
    # Hash each distinct group once, then broadcast back to rows.
    bucket = {g: hash_bucket(g, salt) for g in set(groups)}
    return np.array([bucket[g] < threshold for g in groups], dtype=bool)


def grouped_split(groups: list[object], test_fraction: float, seed: int) -> np.ndarray:
    """Seeded shuffle of the sorted distinct groups; the first n_test groups go to test."""
    _check_fraction(test_fraction)
    distinct = sorted(set(groups))  # sorting makes the result independent of row order
    g = len(distinct)
    if g < 2:
        raise ValueError("need at least two groups")
    n_test = min(g - 1, max(1, round(test_fraction * g)))
    order = np.random.default_rng(seed).permutation(g)
    test_groups = {distinct[i] for i in order[:n_test]}
    return np.array([x in test_groups for x in groups], dtype=bool)


def temporal_split(times: np.ndarray, cutoff: object, embargo: object = 0) -> tuple[np.ndarray, np.ndarray]:
    """train: time < cutoff - embargo; test: time >= cutoff; the gap in between is dropped."""
    times = np.asarray(times)
    zero = embargo * 0  # a zero of the same type: comparing timedelta64 with a bare 0 is deprecated
    if embargo < zero:
        raise ValueError("embargo must be non-negative")
    return times < cutoff - embargo, times >= cutoff


def check_leakage(
    train_mask: np.ndarray,
    test_mask: np.ndarray,
    groups: list[object] | None = None,
    times: np.ndarray | None = None,
    embargo: object = 0,
) -> list[str]:
    """Sorted names of violated leakage invariants."""
    train = np.asarray(train_mask, dtype=bool)
    test = np.asarray(test_mask, dtype=bool)
    if not train.any() or not test.any():
        return []
    violations = []
    if (train & test).any():
        violations.append("row_overlap")
    if groups is not None:
        groups = np.asarray(groups, dtype=object)
        if set(groups[train]) & set(groups[test]):
            violations.append("group_overlap")
    if times is not None:
        times = np.asarray(times)
        latest_train, earliest_test = times[train].max(), times[test].min()
        if latest_train >= earliest_test:
            violations.append("temporal_order")
        elif embargo > embargo * 0 and earliest_test - latest_train <= embargo:
            violations.append("embargo")
    return sorted(violations)
