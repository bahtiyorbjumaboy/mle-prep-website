import pandas as pd

# Repair of the DBG-01 starter. The three leaks and their fixes:
# 1. The scaler was fit on all rows before the split, so validation amounts shaped the
#    training features. Fix: split first, fit on training rows, transform both splits.
# 2. Target encoding ran on all rows (validation labels leaked in) and each training row's
#    own label was part of its encoding. Fix: training rows use leave-one-out statistics
#    (sum, count, and prior all exclude the row); validation rows use training statistics.
# 3. Recency looked at the user's *next* transaction (`shift(-1)`, with `abs()` hiding the
#    sign). Fix: `shift(1)`, the previous transaction. Recency stays computed over the full
#    event history because it only uses strictly earlier rows, which is point-in-time correct.

FEATURES = ["amount_z", "merchant_te", "hours_since_prev_txn"]


def fit_scaler(values: pd.Series) -> dict[str, float]:
    """Population mean/std (ddof=0); a zero std is replaced by 1.0."""
    std = float(values.std(ddof=0))
    return {"mean": float(values.mean()), "std": std if std > 0 else 1.0}


def standardize(values: pd.Series, mean: float, std: float) -> pd.Series:
    return (values - mean) / std


def target_encode(
    train_keys: pd.Series, train_labels: pd.Series, keys: pd.Series, smoothing: float
) -> pd.Series:
    """Encodes `keys` (rows outside the fit) with smoothed training statistics."""
    prior = train_labels.mean()
    stats = train_labels.groupby(train_keys).agg(["sum", "count"])
    sums = keys.map(stats["sum"]).fillna(0.0)
    counts = keys.map(stats["count"]).fillna(0.0)
    return ((sums + smoothing * prior) / (counts + smoothing)).astype(float)


def target_encode_loo(keys: pd.Series, labels: pd.Series, smoothing: float) -> pd.Series:
    """Leave-one-out encoding for the rows the statistics are fit on."""
    labels = labels.astype(float)
    prior = (labels.sum() - labels) / (len(labels) - 1)
    sums = labels.groupby(keys).transform("sum") - labels
    counts = labels.groupby(keys).transform("count") - 1
    return (sums + smoothing * prior) / (counts + smoothing)


def add_recency(df: pd.DataFrame) -> pd.DataFrame:
    """Adds hours_since_prev_txn per user (-1.0 when there is no previous transaction)."""
    df = df.sort_values(["user_id", "ts"])
    previous = df.groupby("user_id")["ts"].shift(1)
    hours = (df["ts"] - previous).dt.total_seconds() / 3600.0
    df["hours_since_prev_txn"] = hours.fillna(-1.0)
    return df


def build_features(
    events: pd.DataFrame, split_time: pd.Timestamp, smoothing: float = 1.0
) -> dict:
    """Builds leakage-safe train/validation feature frames (see the DBG-01 contract)."""
    df = events.sort_values("ts", kind="stable").copy()
    df = add_recency(df)

    is_train = df["ts"] < split_time
    train, validation = df.loc[is_train].copy(), df.loc[~is_train].copy()

    scaler = fit_scaler(train["amount"])
    train["amount_z"] = standardize(train["amount"], **scaler)
    validation["amount_z"] = standardize(validation["amount"], **scaler)

    train["merchant_te"] = target_encode_loo(train["merchant"], train["label"], smoothing)
    validation["merchant_te"] = target_encode(
        train["merchant"], train["label"], validation["merchant"], smoothing
    )
    return {
        "train": train[FEATURES + ["label"]],
        "validation": validation[FEATURES + ["label"]],
        "scaler": scaler,
    }
