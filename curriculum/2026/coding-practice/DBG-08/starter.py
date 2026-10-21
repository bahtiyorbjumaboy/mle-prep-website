import numpy as np

# Incident: `user_amount_features` is correct (its outputs feed a model that is already in
# production), but after the event log grew from 20k to 400k rows the feature job went
# from 3 minutes to over an hour. Nothing else changed.
#
# Canonical prompt: a correct NumPy/pandas feature function became 20x slower after a
# data-size increase. Profile enough to localize Python loops, repeated merges/sorts,
# unnecessary copies, and an accidental quadratic membership check. Improve it without
# changing outputs.
# Follow-ups: vectorization that increases memory too much; chunking; benchmark noise.


def user_amount_features(
    user_ids: np.ndarray,
    amounts: np.ndarray,
    merchants: np.ndarray,
    known_merchants: list[str],
) -> np.ndarray:
    """Per-event user features, returned as an `(n, 4)` float array in input row order.

    Columns:
        0. `user_total`: sum of `amounts` over all events of the row's user.
        1. `user_count`: number of events of the row's user.
        2. `amount_pct`: fraction of the user's events with amount <= this row's amount.
        3. `known_merchant`: 1.0 if the row's merchant is in `known_merchants`, else 0.0.

    Outputs must match the current implementation (up to float summation order, ~1e-12
    relative). Performance contract for the fix: no per-row (or per-user) Python-level
    iteration, and peak memory linear in `n` (no `(n, n)` intermediates).
    """
    user_ids = np.asarray(user_ids)
    amounts = np.asarray(amounts, dtype=float)
    merchants = np.asarray(merchants)
    known = list(known_merchants)

    rows = []
    for i in range(len(amounts)):
        same_user = user_ids == user_ids[i]
        user_amounts = np.sort(amounts[same_user].copy())
        rows.append(
            [
                user_amounts.sum(),
                float(same_user.sum()),
                np.searchsorted(user_amounts, amounts[i], side="right") / len(user_amounts),
                1.0 if merchants[i] in known else 0.0,
            ]
        )
    return np.array(rows, dtype=float).reshape(-1, 4)
