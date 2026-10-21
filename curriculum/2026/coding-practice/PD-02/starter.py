import pandas as pd


def attach_profiles(profiles: pd.DataFrame, orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Attach point-in-time profile state to orders, and return the latest profile per user.

    Args:
        profiles: historical profile updates with columns user_id, profile_ts and one or more
            profile attribute columns (e.g. tier, country). Timestamps may be strings. Rows are
            in arbitrary order; a later row in the frame wins when a user has two updates with
            the same profile_ts.
        orders: columns user_id, order_ts plus any other order columns. Timestamps may be
            strings. Rows are in arbitrary order.

    Returns:
        (attached, latest)
        attached: every order row, in the original order with a fresh RangeIndex, with all
            order columns followed by profile_ts and the profile attribute columns of that
            user's most recent update with profile_ts <= order_ts (an update at exactly the
            order time applies). Orders with no such update get missing values.
            order_ts and profile_ts are returned as datetimes.
        latest: one row per user in `profiles` holding their most recent update (same tie rule),
            sorted by user_id with a fresh RangeIndex and the same columns as `profiles`.
        The inputs must not be modified.
    """
    raise NotImplementedError("TODO: implement PD-02")
