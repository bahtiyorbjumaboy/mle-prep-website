import numpy as np
import pandas as pd

EVENT_TYPES = ["view", "click", "add_to_cart"]


def build_modeling_table(
    users: pd.DataFrame,
    events: pd.DataFrame,
    orders: pd.DataFrame,
    items: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    """User-level modeling table as known at `as_of`; see the PD-05 starter for the contract."""
    # churned_at is only known after the user churns, i.e. usually after as_of; using it would
    # leak the label into the features, so it is dropped before anything else.
    people = users.drop(columns="churned_at").drop_duplicates()
    if people["user_id"].duplicated().any():
        raise ValueError("users has conflicting rows for the same user_id")
    if items["item_id"].duplicated().any():
        raise ValueError("items.item_id must be unique")
    people = people.loc[people["signup_ts"] <= as_of].copy()
    people["country"] = people["country"].str.strip().str.lower().fillna("unknown")
    people["tenure_days"] = (as_of - people["signup_ts"]) / pd.Timedelta(days=1)

    used_events = (
        events.loc[(events["event_ts"] <= as_of) & events["user_id"].isin(people["user_id"])]
        .drop_duplicates("event_id")
        .assign(event_type=lambda df: df["event_type"].str.strip().str.lower())
    )
    type_counts = (
        pd.crosstab(used_events["user_id"], used_events["event_type"])
        .reindex(columns=EVENT_TYPES, fill_value=0)
        .add_prefix("events_")
    )
    type_counts["n_events"] = type_counts.sum(axis=1)

    clicks = used_events.loc[used_events["event_type"].eq("click"), ["user_id", "item_id"]].merge(
        items, on="item_id", how="inner", validate="many_to_one"
    )
    top_category = (
        clicks.groupby(["user_id", "category"]).size().rename("n").reset_index()
        .sort_values(["user_id", "n", "category"], ascending=[True, False, True])
        .drop_duplicates("user_id")
        .set_index("user_id")["category"]
        .rename("top_category")
    )

    counted = orders.loc[
        (orders["order_ts"] <= as_of)
        & orders["status"].str.strip().str.lower().ne("cancelled")
        & orders["user_id"].isin(people["user_id"])
    ].drop_duplicates("order_id")
    order_stats = counted.assign(amount=counted["amount"].fillna(0.0)).groupby("user_id").agg(
        n_orders=("order_id", "size"), total_spend=("amount", "sum"), last_order_ts=("order_ts", "max")
    )

    table = (
        people.set_index("user_id")[["country", "tenure_days"]]
        .join(type_counts, how="left")
        .join(order_stats, how="left")
        .join(top_category, how="left")
        .reset_index()
    )
    count_columns = ["n_events", *[f"events_{t}" for t in EVENT_TYPES], "n_orders"]
    table[count_columns] = table[count_columns].fillna(0).astype(np.int64)
    table["total_spend"] = table["total_spend"].fillna(0.0)
    table["avg_order_value"] = table["total_spend"] / table["n_orders"].where(table["n_orders"] > 0)
    table["days_since_last_order"] = (as_of - table["last_order_ts"]) / pd.Timedelta(days=1)
    table["spend_rank_in_country"] = (
        table.groupby("country")["total_spend"].rank(method="min", ascending=False).astype(np.int64)
    )
    columns = ["user_id", "country", "tenure_days", "n_events", "events_view", "events_click", "events_add_to_cart",
               "n_orders", "total_spend", "avg_order_value", "days_since_last_order", "top_category", "spend_rank_in_country"]
    return table[columns].sort_values("user_id").reset_index(drop=True)
