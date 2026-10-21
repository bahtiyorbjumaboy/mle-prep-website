import numpy as np

# Canonical prompt: implement grouped split, temporal split with embargo, deterministic
# hash-based group assignment, and a checker that reports violated leakage invariants.


def hash_bucket(group: object, salt: str = "", n_buckets: int = 10_000) -> int:
    """Deterministic bucket for a group id, identical across processes and machines.

    Contract: `int(sha256(f"{salt}:{group}".encode("utf-8")).hexdigest(), 16) % n_buckets`
    (use `hashlib`). Python's built-in `hash()` is salted per process for strings,
    so it is not acceptable here.
    """
    raise NotImplementedError("TODO: implement ML-03")


def group_hash_split(groups: list[object], test_fraction: float, salt: str = "") -> np.ndarray:
    """Return a boolean `is_test` mask per row: a group is test iff
    `hash_bucket(group, salt) < test_fraction * 10_000`.

    Assignment depends only on (group, salt, test_fraction), so existing groups keep
    their side when new groups arrive and rows of one group never split.

    Raises:
        ValueError: unless `0 < test_fraction < 1`.
    """
    raise NotImplementedError("TODO: implement ML-03")


def grouped_split(groups: list[object], test_fraction: float, seed: int) -> np.ndarray:
    """Seeded random group split; returns a boolean `is_test` mask per row.

    Contract: take the distinct groups in sorted order (so row order cannot change the
    result), shuffle them with `np.random.default_rng(seed).permutation`, and send the
    first `n_test = min(G - 1, max(1, round(test_fraction * G)))` groups to test, where
    `G` is the number of distinct groups. The fraction is over groups, not rows: one
    giant group stays whole.

    Raises:
        ValueError: if `G < 2` or not `0 < test_fraction < 1`.
    """
    raise NotImplementedError("TODO: implement ML-03")


def temporal_split(times: np.ndarray, cutoff: object, embargo: object = 0) -> tuple[np.ndarray, np.ndarray]:
    """Boolean `(train, test)` masks for a time split with an embargo gap.

    `test = times >= cutoff`; `train = times < cutoff - embargo`. Rows in
    `[cutoff - embargo, cutoff)` belong to neither. Works for numeric times and for
    `datetime64` times with a `timedelta64` embargo.

    Raises:
        ValueError: if `embargo` is negative.
    """
    raise NotImplementedError("TODO: implement ML-03")


def check_leakage(
    train_mask: np.ndarray,
    test_mask: np.ndarray,
    groups: list[object] | None = None,
    times: np.ndarray | None = None,
    embargo: object = 0,
) -> list[str]:
    """Report violated invariants as a sorted list drawn from:

    - `"row_overlap"`: some row is in both train and test;
    - `"group_overlap"`: some group has rows in both (only if `groups` is given);
    - `"temporal_order"`: `max(train time) >= min(test time)` (only if `times` given);
    - `"embargo"`: the order holds but `min(test) - max(train) <= embargo`
      (only if `times` is given and `embargo > 0`).

    Returns `[]` for a clean split or when either side is empty.
    """
    raise NotImplementedError("TODO: implement ML-03")
