from solution import build_user_features
import math
import pandas as pd

AS_OF = pd.Timestamp("2026-01-11 00:00:00")


def _items():
    return pd.DataFrame({"item_id": [10, 11, 12, 13], "category": ["b", "a", "c", "a"], "price": [2.0, 4.0, 10.0, 6.0]})


def _events():
    # Rows are intentionally unsorted; user 1's category 'b' is clicked first, but 'a' ties it.
    return pd.DataFrame({
        "user_id":    [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 1],
        "session_id": [100, 100, 101, 101, 102, 102, 200, 200, 201, 300, 103],
        "item_id":    [10, 11, 10, 13, 12, None, 99, 12, 12, 11, 11],
        "event_type": ["click", "click", "click", "click", "purchase", "view", "click", "view", "purchase", "view", "purchase"],
        "amount":     [None, None, None, None, 30.0, None, 5.0, None, None, None, 999.0],
        "event_ts": pd.to_datetime(["2026-01-03 10:00:00", "2026-01-02 09:00:00", "2026-01-04 12:00:00", "2026-01-05 08:00:00",
                                    "2026-01-09 12:00:00", "2026-01-10 18:00:00", "2026-01-06 00:00:00", "2026-01-06 01:00:00",
                                    "2026-01-07 00:00:00", "2026-01-01 00:00:00", "2026-01-11 00:00:01"]),
    })


def _row(out, user_id):
    rows = out[out["user_id"] == user_id]
    assert len(rows) == 1, f"expected exactly one row for user {user_id}, found {len(rows)}"
    return rows.iloc[0]


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "build_user_features"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_user_grain_sorted_with_range_index():
    out = build_user_features(_events(), _items(), AS_OF)
    assert out["user_id"].tolist() == [1, 2, 3]
    assert list(out.index) == [0, 1, 2]


def test_counts_and_distincts():
    out = build_user_features(_events(), _items(), AS_OF)
    u1, u2 = _row(out, 1), _row(out, 2)
    assert (u1["n_events"], u1["n_sessions"], u1["n_items"], u1["n_purchases"]) == (6, 3, 4, 1)
    assert (u2["n_events"], u2["n_sessions"], u2["n_items"], u2["n_purchases"]) == (3, 2, 2, 1)


def test_events_after_as_of_are_ignored():
    out = build_user_features(_events(), _items(), AS_OF)
    assert _row(out, 1)["purchase_spend"] == 30.0


def test_missing_purchase_amount_counts_as_zero():
    out = build_user_features(_events(), _items(), AS_OF)
    assert _row(out, 2)["purchase_spend"] == 0.0 and _row(out, 3)["purchase_spend"] == 0.0


def test_clicked_item_mean_price_is_per_click_and_ignores_unknown_items():
    out = build_user_features(_events(), _items(), AS_OF)
    assert math.isclose(_row(out, 1)["clicked_item_mean_price"], (2 + 4 + 2 + 6) / 4)
    assert pd.isna(_row(out, 2)["clicked_item_mean_price"])
    assert pd.isna(_row(out, 3)["clicked_item_mean_price"])


def test_top_category_tie_breaks_alphabetically_regardless_of_row_order():
    events = _events()
    for frame in (events, events.iloc[::-1].reset_index(drop=True), events.sample(frac=1, random_state=7)):
        out = build_user_features(frame, _items(), AS_OF)
        assert _row(out, 1)["top_clicked_category"] == "a"
        assert pd.isna(_row(out, 2)["top_clicked_category"]) and pd.isna(_row(out, 3)["top_clicked_category"])


def test_recency_features():
    out = build_user_features(_events(), _items(), AS_OF)
    u1, u2, u3 = _row(out, 1), _row(out, 2), _row(out, 3)
    assert math.isclose(u1["days_since_last_event"], 0.25)
    assert math.isclose(u1["days_since_last_purchase"], 1.5)
    assert math.isclose(u2["days_since_last_purchase"], 4.0)
    assert math.isclose(u3["days_since_last_event"], 10.0) and pd.isna(u3["days_since_last_purchase"])


def test_duplicate_item_ids_raise_instead_of_fanning_out():
    items = pd.concat([_items(), pd.DataFrame({"item_id": [10], "category": ["z"], "price": [100.0]})], ignore_index=True)
    try:
        build_user_features(_events(), items, AS_OF)
    except ValueError:
        return
    raise AssertionError("duplicate item_id in items must raise ValueError")


def test_inputs_are_not_mutated():
    events, items = _events(), _items()
    events_before, items_before = events.copy(deep=True), items.copy(deep=True)
    build_user_features(events, items, AS_OF)
    pd.testing.assert_frame_equal(events, events_before)
    pd.testing.assert_frame_equal(items, items_before)
