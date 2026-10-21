import numpy as np
import pandas as pd


def build_user_features(events: pd.DataFrame, items: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Build one row per user; see the PD-01 starter for the full contract."""
    if items["item_id"].duplicated().any():
        raise ValueError("items.item_id must be unique")
    used = events.loc[events["event_ts"] <= as_of].copy()
    used["is_purchase"] = used["event_type"].eq("purchase")
    used["purchase_amount"] = used["amount"].where(used["is_purchase"], 0.0).fillna(0.0)
    used["purchase_ts"] = used["event_ts"].where(used["is_purchase"])

    features = (
        used.groupby("user_id")
        .agg(
            n_events=("event_type", "size"),
            n_sessions=("session_id", "nunique"),
            n_items=("item_id", "nunique"),
            n_purchases=("is_purchase", "sum"),
            purchase_spend=("purchase_amount", "sum"),
            last_event_ts=("event_ts", "max"),
            last_purchase_ts=("purchase_ts", "max"),
        )
        .reset_index()
    )

    # validate= guards the many-to-one assumption even though duplicates were rejected above.
    clicks = used.loc[used["event_type"].eq("click"), ["user_id", "item_id"]].merge(
        items, on="item_id", how="inner", validate="many_to_one"
    )
    mean_price = clicks.groupby("user_id")["price"].mean().rename("clicked_item_mean_price")
    top_category = (
        clicks.groupby(["user_id", "category"]).size().rename("n_clicks").reset_index()
        .sort_values(["user_id", "n_clicks", "category"], ascending=[True, False, True])
        .drop_duplicates("user_id")
        .set_index("user_id")["category"]
        .rename("top_clicked_category")
    )

    features = features.merge(mean_price, on="user_id", how="left").merge(top_category, on="user_id", how="left")
    day = pd.Timedelta(days=1)
    features["days_since_last_event"] = (as_of - features["last_event_ts"]) / day
    features["days_since_last_purchase"] = (as_of - features["last_purchase_ts"]) / day
    features["n_purchases"] = features["n_purchases"].astype(np.int64)
    columns = ["user_id", "n_events", "n_sessions", "n_items", "n_purchases", "purchase_spend",
               "clicked_item_mean_price", "top_clicked_category", "days_since_last_event", "days_since_last_purchase"]
    return features[columns].sort_values("user_id").reset_index(drop=True)
