import pandas as pd


def build_user_features(events: pd.DataFrame, items: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Build one row per user from `events` and `items`.

    Args:
        events: columns user_id, session_id, item_id (may be NaN), event_type
            ('view' | 'click' | 'purchase'), amount (purchase value; may be NaN), event_ts.
        items: columns item_id, category, price. item_id must be unique; raise ValueError
            if it is not.
        as_of: reference time. Only events with event_ts <= as_of are used.

    Returns:
        One row per user with at least one used event, sorted by user_id, with a fresh
        RangeIndex and columns:
            user_id
            n_events                  events
            n_sessions                distinct session_id
            n_items                   distinct non-missing item_id
            n_purchases               purchase events
            purchase_spend            sum of purchase amounts (missing amounts count as 0; 0.0 if none)
            clicked_item_mean_price   mean item price over click events whose item is in
                                      `items` (each click counts once); NaN if none
            top_clicked_category      category with the most such clicks; ties go to the
                                      alphabetically smallest category; NaN if none
            days_since_last_event     (as_of - last event_ts) in fractional days
            days_since_last_purchase  same for purchases; NaN if the user never purchased
        The inputs must not be modified.
    """
    raise NotImplementedError("TODO: implement PD-01")
