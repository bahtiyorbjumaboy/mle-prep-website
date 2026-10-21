import pandas as pd


def point_in_time_features(labels: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Compute leakage-free features for every label row.

    Args:
        labels: columns user_id, label_ts (datetime) plus any other label columns. Rows are
            in arbitrary order and may repeat.
        events: columns user_id, event_ts (datetime), event_type, amount (may be NaN), in
            arbitrary order.

    Only events strictly before the label time are used (event_ts < label_ts). An N-day
    window covers label_ts - N days <= event_ts < label_ts.

    Returns:
        One row per label row, in the same order and with the same index as `labels`: all
        label columns followed by
            count_1d, count_7d, count_30d   events in each window
            amount_30d                      sum of non-missing amounts in the 30-day window (0.0 if none)
            days_since_prev_event           (label_ts - latest prior event_ts) in fractional days,
                                            using any prior event; NaN if there is none
            distinct_event_types_30d        distinct event_type values in the 30-day window
        The inputs must not be modified.
    """
    raise NotImplementedError("TODO: implement PD-03")
