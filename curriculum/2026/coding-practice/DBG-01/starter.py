import pandas as pd

# Incident: after a feature refactor the fraud model's offline validation AUC jumped from
# 0.71 to 0.97, but the shadow deployment still scores about 0.70. Reviewers suspect leakage.
#
# Canonical prompt: find and fix three leaks: preprocessing fit before the split, target
# encoding that sees the row's own target, and a recency feature computed with future
# information. Write tests that expose each leak.
# Follow-up: which leak survives grouped/temporal splits?

FEATURES = ["amount_z", "merchant_te", "hours_since_prev_txn"]


def fit_scaler(values: pd.Series) -> dict[str, float]:
    """Population mean/std (ddof=0); a zero std is replaced by 1.0."""
    std = float(values.std(ddof=0))
    return {"mean": float(values.mean()), "std": std if std > 0 else 1.0}


def standardize(values: pd.Series, mean: float, std: float) -> pd.Series:
    return (values - mean) / std


def target_encode(keys: pd.Series, labels: pd.Series, smoothing: float) -> pd.Series:
    """Smoothed mean label per key: (sum + smoothing * prior) / (count + smoothing)."""
    prior = labels.mean()
    stats = labels.groupby(keys).agg(["sum", "count"])
    encoded = (stats["sum"] + smoothing * prior) / (stats["count"] + smoothing)
    return keys.map(encoded).astype(float)


def add_recency(df: pd.DataFrame) -> pd.DataFrame:
    """Adds hours_since_prev_txn per user (-1.0 when there is no previous transaction)."""
    df = df.sort_values(["user_id", "ts"])
    other = df.groupby("user_id")["ts"].shift(-1)
    hours = (other - df["ts"]).abs().dt.total_seconds() / 3600.0
    df["hours_since_prev_txn"] = hours.fillna(-1.0)
    return df


def build_features(
    events: pd.DataFrame, split_time: pd.Timestamp, smoothing: float = 1.0
) -> dict:
    """Builds train/validation feature frames from raw transaction events.

    `events` has columns `user_id`, `merchant`, `amount`, `ts` (datetime64) and `label`
    (0/1), with an arbitrary index. A user's timestamps are unique. The input is not mutated.

    Contract:
    - Rows with `ts < split_time` are training rows; `ts >= split_time` are validation rows.
    - `amount_z = (amount - mean) / std` with mean/std (ddof=0) fit on training rows only.
      `scaler` reports the fitted `{"mean", "std"}`.
    - `merchant_te` is the smoothed merchant fraud rate
      `(sum + smoothing * prior) / (count + smoothing)`, using training labels only, where
      `prior` is the training fraud rate. A training row must not see its own label: its
      `sum`, `count`, and `prior` all exclude that row. Validation rows use every training
      row; a merchant never seen in training encodes to `prior`.
    - `hours_since_prev_txn` is the hours since the same user's previous (strictly earlier)
      transaction, in either split; -1.0 for a user's first transaction.

    Returns:
        `{"train": DataFrame, "validation": DataFrame, "scaler": dict}`. Both frames keep the
        input index labels and have columns `FEATURES + ["label"]`.
    """
    df = events.sort_values("ts", kind="stable").copy()

    scaler = fit_scaler(df["amount"])
    df["amount_z"] = standardize(df["amount"], **scaler)
    df["merchant_te"] = target_encode(df["merchant"], df["label"], smoothing)
    df = add_recency(df)

    is_train = df["ts"] < split_time
    train = df.loc[is_train, FEATURES + ["label"]]
    validation = df.loc[~is_train, FEATURES + ["label"]]
    return {"train": train, "validation": validation, "scaler": scaler}
