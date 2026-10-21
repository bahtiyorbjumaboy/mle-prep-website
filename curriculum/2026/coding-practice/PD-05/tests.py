from solution import build_modeling_table
import math
import numpy as np
import pandas as pd

AS_OF = pd.Timestamp("2026-02-01 00:00:00")
COLUMNS = ["user_id", "country", "tenure_days", "n_events", "events_view", "events_click", "events_add_to_cart",
           "n_orders", "total_spend", "avg_order_value", "days_since_last_order", "top_category", "spend_rank_in_country"]


def _users():
    return pd.DataFrame({
        "user_id": [1, 1, 2, 3, 4, 5, 6],
        "signup_ts": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-10", "2026-01-15", "2026-01-20", "2026-02-05", "2026-01-05"]),
        "country": [" US", " US", "ca", None, "US ", "us", "us"],
        "churned_at": pd.to_datetime(["2026-03-01", "2026-03-01", None, "2026-02-10", None, None, None]),
    })


def _events():
    return pd.DataFrame({
        "event_id": [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "user_id": [1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 99],
        "item_id": [100, 100, 101, 102, 100, 103, 100, 103, 999, 102, 102, 100, 100],
        "event_type": ["click", "click", "Click ", "view", "add_to_cart", "click", "click", "VIEW", "click", "click", " click", "click", "click"],
        "event_ts": pd.to_datetime(["2026-01-02 00:00:00", "2026-01-02 00:00:00", "2026-01-03 00:00:00", "2026-01-03 00:00:00",
                                    "2026-01-04 00:00:00", "2026-01-05 00:00:00", "2026-02-01 00:00:01", "2026-01-12 00:00:00",
                                    "2026-01-13 00:00:00", "2026-01-20 00:00:00", "2026-01-21 00:00:00", "2026-01-22 00:00:00",
                                    "2026-01-22 00:00:00"]),
    })


def _orders():
    return pd.DataFrame({
        "order_id": [1, 1, 2, 3, 4, 5, 6, 8],
        "user_id": [1, 1, 1, 1, 1, 2, 3, 6],
        "order_ts": pd.to_datetime(["2026-01-05", "2026-01-05", "2026-01-20", "2026-01-25", "2026-02-03", "2026-01-15", "2026-01-30", "2026-01-10"]),
        "amount": [20.0, 20.0, 30.0, 100.0, 500.0, np.nan, 50.0, 50.0],
        "status": ["paid", "paid", "paid", " Cancelled", "paid", "paid", "paid", "PAID"],
    })


def _items():
    return pd.DataFrame({"item_id": [100, 101, 102, 103], "category": ["shoes", "books", "books", "toys"]})


def _run(**overrides):
    frames = {"users": _users(), "events": _events(), "orders": _orders(), "items": _items()}
    frames.update(overrides)
    return build_modeling_table(frames["users"], frames["events"], frames["orders"], frames["items"], AS_OF)


def _row(out, user_id):
    rows = out[out["user_id"] == user_id]
    assert len(rows) == 1, f"expected one row for user {user_id}, found {len(rows)}"
    return rows.iloc[0]


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "build_modeling_table"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_row_grain_unique_key_and_columns():
    out = _run()
    assert out["user_id"].tolist() == [1, 2, 3, 4, 6] and out["user_id"].is_unique
    assert list(out.index) == list(range(5)) and list(out.columns) == COLUMNS


def test_hand_computed_user_fixture():
    u1 = _row(_run(), 1)
    assert u1["country"] == "us" and math.isclose(u1["tenure_days"], 31.0)
    assert (u1["n_events"], u1["events_view"], u1["events_click"], u1["events_add_to_cart"]) == (5, 1, 3, 1)
    assert (u1["n_orders"], u1["total_spend"], u1["avg_order_value"], u1["days_since_last_order"]) == (2, 50.0, 25.0, 12.0)
    assert u1["top_category"] == "books" and u1["spend_rank_in_country"] == 1


def test_missing_values_and_unknown_items():
    out = _run()
    u2, u3, u4 = _row(out, 2), _row(out, 3), _row(out, 4)
    assert u2["country"] == "ca" and u3["country"] == "unknown"
    assert (u2["n_orders"], u2["total_spend"], u2["avg_order_value"]) == (1, 0.0, 0.0)
    assert pd.isna(u2["top_category"]) and (u2["n_events"], u2["events_click"]) == (2, 1)
    assert (u4["n_events"], u4["n_orders"], u4["total_spend"]) == (0, 0, 0.0)
    assert pd.isna(u4["avg_order_value"]) and pd.isna(u4["days_since_last_order"]) and pd.isna(u4["top_category"])


def test_rank_within_country_shares_ties_and_skips():
    out = _run()
    ranks = dict(zip(out["user_id"], out["spend_rank_in_country"]))
    assert ranks == {1: 1, 2: 1, 3: 1, 4: 3, 6: 1}


def test_top_category_is_deterministic_under_shuffles():
    for seed in (0, 1, 2):
        out = _run(events=_events().sample(frac=1, random_state=seed), items=_items().sample(frac=1, random_state=seed))
        assert _row(out, 1)["top_category"] == "books" and _row(out, 3)["top_category"] == "books"


def test_no_future_timestamp_contribution():
    base = _run()
    future_events = pd.DataFrame({"event_id": [500, 501], "user_id": [2, 4], "item_id": [100, 100], "event_type": ["click", "view"],
                                  "event_ts": pd.to_datetime(["2026-02-01 00:00:01", "2026-03-01 00:00:00"])})
    future_orders = pd.DataFrame({"order_id": [900], "user_id": [4], "order_ts": pd.to_datetime(["2026-02-02"]), "amount": [999.0], "status": ["paid"]})
    later = _run(events=pd.concat([_events(), future_events], ignore_index=True), orders=pd.concat([_orders(), future_orders], ignore_index=True))
    pd.testing.assert_frame_equal(base, later)


def test_leaky_column_excluded_and_ignored():
    base = _run()
    assert "churned_at" not in base.columns
    users = _users()
    users["churned_at"] = pd.Timestamp("2026-01-02")
    pd.testing.assert_frame_equal(base, _run(users=users))


def test_conflicting_user_rows_raise():
    users = pd.concat([_users(), pd.DataFrame({"user_id": [2], "signup_ts": pd.to_datetime(["2026-01-11"]), "country": ["ca"], "churned_at": [pd.NaT]})], ignore_index=True)
    try:
        _run(users=users)
    except ValueError:
        return
    raise AssertionError("conflicting rows for one user_id must raise ValueError")


def test_duplicate_item_ids_raise():
    try:
        _run(items=pd.concat([_items(), pd.DataFrame({"item_id": [100], "category": ["toys"]})], ignore_index=True))
    except ValueError:
        return
    raise AssertionError("duplicate item_id must raise ValueError")


def test_inputs_are_not_mutated():
    frames = (_users(), _events(), _orders(), _items())
    before = [f.copy(deep=True) for f in frames]
    build_modeling_table(*frames, AS_OF)
    for after, original in zip(frames, before):
        pd.testing.assert_frame_equal(after, original)
