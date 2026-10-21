import numpy as np
import pandas as pd


def rolling_user_features(activity: pd.DataFrame) -> pd.DataFrame:
    """Dense per-user daily rows with rolling calendar-day features; see the PD-04 starter."""
    daily = (
        activity.assign(date=activity["date"].dt.normalize())
        .groupby(["user_id", "date"], as_index=False)[["count", "spend"]]
        .sum()
    )
    end = daily["date"].max()
    frames = []
    for user_id, group in daily.groupby("user_id"):
        days = pd.date_range(group["date"].min(), end, freq="D", name="date")
        dense = group.set_index("date")[["count", "spend"]].reindex(days, fill_value=0)
        # The frame is dense now, but an offset window ("7D") stays correct even if it were not.
        dense["count_7d"] = dense["count"].rolling("7D").sum()
        dense["count_28d"] = dense["count"].rolling("28D").sum()
        dense["spend_28d"] = dense["spend"].rolling("28D").sum()
        frames.append(dense.reset_index().assign(user_id=user_id))
    out = pd.concat(frames, ignore_index=True)
    out[["count_7d", "count_28d"]] = out[["count_7d", "count_28d"]].astype(np.int64)
    out["spend_per_event_28d"] = out["spend_28d"] / out["count_28d"].where(out["count_28d"] > 0)
    out["first_active_day"] = ~out.duplicated("user_id")
    columns = ["user_id", "date", "count", "spend", "count_7d", "count_28d", "spend_28d", "spend_per_event_28d", "first_active_day"]
    return out[columns].sort_values(["user_id", "date"]).reset_index(drop=True)
