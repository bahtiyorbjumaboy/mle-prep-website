import pandas as pd


def build_modeling_table(
    users: pd.DataFrame,
    events: pd.DataFrame,
    orders: pd.DataFrame,
    items: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    """Build a user-level modeling table from messy inputs, as known at `as_of`.

    Inputs (all messy: duplicates, missing values, inconsistent strings, future rows):
        users: user_id, signup_ts, country, churned_at. Exact duplicate rows may occur; a
            user_id with conflicting rows is a data error (raise ValueError).
        events: event_id, user_id, item_id, event_type, event_ts. An event_id may appear
            more than once; it is still one event. event_type values may differ in case and
            surrounding whitespace; after cleaning they are 'view', 'click' or 'add_to_cart'.
        orders: order_id, user_id, order_ts, amount, status. An order_id may repeat (one
            order). Orders whose status is 'cancelled' (any case/whitespace) do not count;
            a missing amount counts as 0.0.
        items: item_id, category. item_id must be unique (raise ValueError otherwise).
        as_of: only users who signed up, and events/orders that happened, at or before as_of
            are used.

    Returns:
        One row per eligible user, sorted by user_id, fresh RangeIndex, columns:
            user_id
            country                 stripped, lower-case; 'unknown' when missing
            tenure_days             (as_of - signup_ts) in fractional days
            n_events                events
            events_view, events_click, events_add_to_cart   events of each type (0 if none)
            n_orders, total_spend   counted orders and their total amount (0 / 0.0 if none)
            avg_order_value         total_spend / n_orders; NaN without orders
            days_since_last_order   (as_of - latest counted order_ts) in days; NaN without orders
            top_category            category with the most clicks on items present in `items`;
                                    ties go to the alphabetically smallest; NaN without such clicks
            spend_rank_in_country   rank of total_spend within country, highest = 1, tied users
                                    share the lowest rank and the next rank is skipped (1, 1, 3)
        One supplied column leaks information from after as_of. It must not be used or
        returned; note in a comment why.
        The inputs must not be modified.
    """
    raise NotImplementedError("TODO: implement PD-05")
