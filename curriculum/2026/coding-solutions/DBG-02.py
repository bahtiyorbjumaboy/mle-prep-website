import numpy as np
import pandas as pd

# Repair of the DBG-02 starter. The defects and their fixes:
# 1. X and y were shuffled with two different permutations (the generator advances between
#    calls) and labels were taken by position, then `reset_index` erased row identity.
#    Fix: align labels to features by index label once, then index both with one order.
# 2. Deduplication ran per fold, so a replayed event could sit in train and validation.
#    Fix: deduplicate by `event_id` before splitting (and reject conflicting labels).
# 3. A plain random cut can leave validation with almost no positives. Fix: sample
#    `round(valid_frac * n_class)` validation rows per class.


def split_train_validation(
    features: pd.DataFrame, labels: pd.Series, valid_frac: float = 0.25, seed: int = 0
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Stratified, deduplicated, row-aligned train/validation split (see the DBG-02 contract)."""
    if not features.index.sort_values().equals(labels.index.sort_values()):
        raise ValueError("features and labels must share the same index labels")
    y_all = labels.loc[features.index]

    conflicts = y_all.groupby(features["event_id"]).nunique()
    if (conflicts > 1).any():
        raise ValueError(f"conflicting labels for event_id(s) {list(conflicts[conflicts > 1].index)}")
    keep = ~features["event_id"].duplicated(keep="first")
    X, y = features.loc[keep], y_all.loc[keep]

    rng = np.random.default_rng(seed)
    valid_index = []
    for cls in sorted(y.unique()):
        members = y.index[y == cls]
        n_valid = int(round(valid_frac * len(members)))
        valid_index.extend(members[rng.permutation(len(members))[:n_valid]])
    is_valid = X.index.isin(valid_index)

    order = rng.permutation(len(X))
    X, y, is_valid = X.iloc[order], y.iloc[order], is_valid[order]
    return X[~is_valid], X[is_valid], y[~is_valid], y[is_valid]
