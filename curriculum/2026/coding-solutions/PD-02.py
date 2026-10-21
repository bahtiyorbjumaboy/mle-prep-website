import pandas as pd


def attach_profiles(profiles: pd.DataFrame, orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (orders with point-in-time profile state, latest profile per user)."""
    required_profiles = {"user_id", "profile_ts"}
    required_orders = {"user_id", "order_ts"}
    if not required_profiles <= set(profiles) or not required_orders <= set(orders):
        raise ValueError("required user/timestamp columns are missing")
    history = profiles.assign(profile_ts=pd.to_datetime(profiles["profile_ts"]))
    order_rows = orders.assign(order_ts=pd.to_datetime(orders["order_ts"]))

    # merge_asof needs both sides sorted on the time key; a stable sort keeps input order
    # among equal profile_ts, so "backward" picks the later row on ties.
    history = history.sort_values("profile_ts", kind="stable")
    ordered = order_rows.assign(_position=range(len(order_rows))).sort_values("order_ts", kind="stable")
    attached = pd.merge_asof(
        ordered, history, left_on="order_ts", right_on="profile_ts",
        by="user_id", direction="backward", allow_exact_matches=True,
    )
    attached = attached.sort_values("_position").drop(columns="_position").reset_index(drop=True)

    latest = (
        history.sort_values(["user_id", "profile_ts"], kind="stable")
        .drop_duplicates("user_id", keep="last")
        .reset_index(drop=True)
    )
    return attached, latest
