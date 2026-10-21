import numpy as np

# Repair of the DBG-08 starter. Profiling the old loop (n rows, u users, m known merchants):
# - one Python iteration per row, each scanning all n user ids (`user_ids == user_ids[i]`):
#   O(n^2) comparisons; this term dominates and is why 20x more rows cost ~400x more time;
# - a fresh copy and sort of the user's amounts per row: the same group sorted once per
#   member instead of once;
# - `merchants[i] in known` on a list: O(m) per row, O(n * m) overall.
# Fix: group once with `np.unique` and one `lexsort` (O(n log n)), aggregate with
# `bincount`, read "amount <= mine" off the end of each tie run, and test merchant
# membership with sorted-set `np.isin` (O((n + m) log)). Peak memory stays O(n); the
# tempting `user_ids[:, None] == user_ids[None, :]` vectorization would be O(n^2) memory.


def user_amount_features(
    user_ids: np.ndarray,
    amounts: np.ndarray,
    merchants: np.ndarray,
    known_merchants: list[str],
) -> np.ndarray:
    """Per-event `[user_total, user_count, amount_pct, known_merchant]` in input row order."""
    user_ids = np.asarray(user_ids)
    amounts = np.asarray(amounts, dtype=float)
    merchants = np.asarray(merchants)
    n = len(amounts)
    if n == 0:
        return np.empty((0, 4))

    _, user_index, counts = np.unique(user_ids, return_inverse=True, return_counts=True)
    user_index = user_index.reshape(-1)
    totals = np.bincount(user_index, weights=amounts)

    # Sort by (user, amount); within a user, the rows with amount <= a_i end at the last
    # position of a_i's tie run, so the count is that position minus the user's start + 1.
    order = np.lexsort((amounts, user_index))
    sorted_user, sorted_amount = user_index[order], amounts[order]
    run_starts = np.ones(n, dtype=bool)
    run_starts[1:] = (sorted_user[1:] != sorted_user[:-1]) | (sorted_amount[1:] != sorted_amount[:-1])
    run_ends = np.append(np.flatnonzero(run_starts)[1:], n) - 1
    user_starts = np.cumsum(counts) - counts
    at_or_below = run_ends[np.cumsum(run_starts) - 1] - user_starts[sorted_user] + 1
    amount_pct = np.empty(n)
    amount_pct[order] = at_or_below / counts[sorted_user]

    known_list = list(known_merchants)
    known = np.isin(merchants, np.asarray(known_list)) if known_list else np.zeros(n, dtype=bool)
    return np.column_stack(
        [totals[user_index], counts[user_index].astype(float), amount_pct, known.astype(float)]
    )
