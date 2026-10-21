import pandas as pd


def rolling_user_features(activity: pd.DataFrame) -> pd.DataFrame:
    """Densify sparse daily activity and add rolling calendar-day features per user.

    Args:
        activity: columns user_id, date (datetime; any time-of-day is ignored), count (int),
            spend (float). Sparse, unsorted, and a user may have several rows for one day.

    Returns:
        One row per user per calendar day from that user's first active day through the
        latest day in the whole frame, sorted by (user_id, date), fresh RangeIndex, columns:
            user_id, date       date normalized to midnight
            count, spend        that day's totals (0 / 0.0 on inactive days)
            count_7d            sum of count over the 7 calendar days ending on `date`
            count_28d           sum of count over the 28 calendar days ending on `date`
            spend_28d           sum of spend over the same 28 days
            spend_per_event_28d spend_28d / count_28d, NaN when count_28d is 0
            first_active_day    True only on the user's first row
        Windows never cross users; near the start they cover the available days only.
        The input must not be modified.
    """
    raise NotImplementedError("TODO: implement PD-04")
