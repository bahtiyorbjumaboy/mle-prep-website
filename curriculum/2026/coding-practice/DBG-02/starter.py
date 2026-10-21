import numpy as np
import pandas as pd

# Incident: a churn model's validation AUC swings between 0.52 and 0.99 depending on the
# seed, validation recall is sometimes undefined, and a model trained on a perfectly
# predictive `signal` column scores barely above chance.
#
# Canonical prompt: you receive code that shuffles X and y independently, deduplicates after
# splitting, and creates a tiny-positive validation fold. Diagnose the resulting metric
# behavior and fix the pipeline.
# Follow-up: why can misalignment still appear above chance?


def split_train_validation(
    features: pd.DataFrame, labels: pd.Series, valid_frac: float = 0.25, seed: int = 0
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Shuffles and splits a labelled dataset into train/validation folds.

    `features` has an `event_id` column plus feature columns and an arbitrary unique index.
    `labels` is a 0/1 Series keyed by the same index labels; it may arrive in a different
    row order. Neither input is mutated.

    Contract:
    - Labels belong to rows by index label, never by position. If the index sets of
      `features` and `labels` differ, raise `ValueError`.
    - Rows sharing an `event_id` are replayed copies of one event. Keep only the first
      occurrence (input order) before splitting, so an event lands in exactly one fold.
      Copies of one event with conflicting labels raise `ValueError`.
    - The validation fold is stratified: for each class, `round(valid_frac * n_class)` of
      that class's deduplicated rows go to validation, chosen at random from `seed`.
    - The result is deterministic for a given `seed`.

    Returns:
        `(X_train, X_valid, y_train, y_valid)`. Each `y` has exactly the index of its `X`
        (original index labels, any order).
    """
    rng = np.random.default_rng(seed)
    X = features.iloc[rng.permutation(len(features))].reset_index(drop=True)
    y = labels.iloc[rng.permutation(len(labels))].reset_index(drop=True)

    n_valid = int(round(valid_frac * len(X)))
    X_valid, X_train = X.iloc[:n_valid], X.iloc[n_valid:]
    y_valid, y_train = y.iloc[:n_valid], y.iloc[n_valid:]

    X_train = X_train.drop_duplicates(subset="event_id")
    X_valid = X_valid.drop_duplicates(subset="event_id")
    y_train, y_valid = y_train.loc[X_train.index], y_valid.loc[X_valid.index]
    return X_train, X_valid, y_train, y_valid
