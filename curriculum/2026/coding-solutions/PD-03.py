import numpy as np
import pandas as pd


def point_in_time_features(labels: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Strictly-prior 1/7/30-day features per label row; see the PD-03 starter for the contract."""
    ordered = events.sort_values(["user_id", "event_ts"], kind="stable")
    by_user = {
        user: (
            group["event_ts"].to_numpy(),
            np.concatenate([[0.0], np.cumsum(group["amount"].fillna(0.0).to_numpy())]),
            group["event_type"].to_numpy(),
        )
        for user, group in ordered.groupby("user_id", sort=False)
    }
    windows = {"count_1d": 1, "count_7d": 7, "count_30d": 30}
    features = {name: np.zeros(len(labels), dtype=np.int64) for name in windows}
    amount_30d = np.zeros(len(labels))
    days_since_prev = np.full(len(labels), np.nan)
    distinct_types = np.zeros(len(labels), dtype=np.int64)

    for row, (user, label_ts) in enumerate(zip(labels["user_id"], labels["label_ts"])):
        if user not in by_user:
            continue
        times, amount_prefix, types = by_user[user]
        # side="left" counts events strictly before a bound: the end bound excludes
        # event_ts == label_ts, the start bound keeps event_ts == label_ts - N days.
        end = np.searchsorted(times, np.datetime64(label_ts), side="left")
        for name, days in windows.items():
            start = np.searchsorted(times, np.datetime64(label_ts - pd.Timedelta(days=days)), side="left")
            features[name][row] = end - start
            if days == 30:
                amount_30d[row] = amount_prefix[end] - amount_prefix[start]
                distinct_types[row] = len(set(types[start:end]))
        if end > 0:
            days_since_prev[row] = (label_ts - pd.Timestamp(times[end - 1])) / pd.Timedelta(days=1)

    return labels.assign(
        **features,
        amount_30d=amount_30d,
        days_since_prev_event=days_since_prev,
        distinct_event_types_30d=distinct_types,
    )
