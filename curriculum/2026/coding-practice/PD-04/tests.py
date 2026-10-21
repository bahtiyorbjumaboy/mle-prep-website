from solution import rolling_user_features
import math
import numpy as np
import pandas as pd

COLUMNS = ["user_id", "date", "count", "spend", "count_7d", "count_28d", "spend_28d", "spend_per_event_28d", "first_active_day"]


def _activity():
    return pd.DataFrame({
        "user_id": [1, 2, 1, 3, 1, 1, 2, 1],
        "date": pd.to_datetime(["2026-01-07 00:00:00", "2026-01-20 00:00:00", "2026-01-01 00:00:00", "2026-01-25 00:00:00",
                                "2026-01-08 00:00:00", "2026-01-28 13:00:00", "2026-01-30 00:00:00", "2026-01-01 09:30:00"]),
        "count": [1, 2, 1, 0, 4, 1, 1, 2],
        "spend": [1.0, 8.0, 2.0, 5.0, 4.0, 10.0, 1.0, 3.0],
    })


def _bruteforce(activity):
    act = activity.assign(date=activity["date"].dt.normalize())
    end = act["date"].max()
    rows = []
    for user in sorted(act["user_id"].unique()):
        mine = act[act["user_id"] == user]
        for day in pd.date_range(mine["date"].min(), end, freq="D"):
            in_days = lambda n: mine[(mine["date"] > day - pd.Timedelta(days=n)) & (mine["date"] <= day)]
            c28, s28 = in_days(28)["count"].sum(), in_days(28)["spend"].sum()
            rows.append({"user_id": user, "date": day, "count": mine.loc[mine["date"] == day, "count"].sum(),
                         "spend": mine.loc[mine["date"] == day, "spend"].sum(), "count_7d": in_days(7)["count"].sum(),
                         "count_28d": c28, "spend_28d": s28, "spend_per_event_28d": s28 / c28 if c28 else np.nan,
                         "first_active_day": day == mine["date"].min()})
    return pd.DataFrame(rows)


def _at(out, user_id, day):
    rows = out[(out["user_id"] == user_id) & (out["date"] == pd.Timestamp(day))]
    assert len(rows) == 1, f"expected one row for user {user_id} on {day}, found {len(rows)}"
    return rows.iloc[0]


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "rolling_user_features"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_dense_grid_per_user_to_dataset_end():
    out = rolling_user_features(_activity())
    assert list(out.columns) == COLUMNS and list(out.index) == list(range(len(out)))
    assert out.groupby("user_id").size().to_dict() == {1: 30, 2: 11, 3: 6}
    assert not out.duplicated(["user_id", "date"]).any()
    assert out.sort_values(["user_id", "date"]).index.tolist() == list(range(len(out)))


def test_same_day_rows_are_summed_and_time_of_day_ignored():
    out = rolling_user_features(_activity())
    jan1, jan28 = _at(out, 1, "2026-01-01"), _at(out, 1, "2026-01-28")
    assert (jan1["count"], jan1["spend"]) == (3, 5.0) and (jan28["count"], jan28["spend"]) == (1, 10.0)
    assert _at(out, 1, "2026-01-02")["count"] == 0 and _at(out, 1, "2026-01-02")["spend"] == 0.0


def test_7_day_window_is_calendar_days():
    out = rolling_user_features(_activity())
    assert _at(out, 1, "2026-01-07")["count_7d"] == 4
    assert _at(out, 1, "2026-01-08")["count_7d"] == 5
    assert _at(out, 1, "2026-01-14")["count_7d"] == 4 and _at(out, 1, "2026-01-15")["count_7d"] == 0


def test_28_day_window_boundary():
    out = rolling_user_features(_activity())
    assert math.isclose(_at(out, 1, "2026-01-28")["spend_28d"], 20.0)
    assert math.isclose(_at(out, 1, "2026-01-29")["spend_28d"], 15.0)
    assert _at(out, 1, "2026-01-29")["count_28d"] == 6


def test_safe_ratio():
    out = rolling_user_features(_activity())
    assert math.isclose(_at(out, 1, "2026-01-28")["spend_per_event_28d"], 20.0 / 9)
    assert out.loc[out["user_id"] == 3, "spend_per_event_28d"].isna().all()
    assert not np.isinf(out["spend_per_event_28d"].to_numpy(dtype=float)).any()


def test_windows_do_not_leak_across_users():
    out = rolling_user_features(_activity())
    first2 = _at(out, 2, "2026-01-20")
    assert (first2["count_7d"], first2["count_28d"], first2["spend_28d"]) == (2, 2, 8.0)


def test_first_active_day_flag():
    out = rolling_user_features(_activity())
    flagged = out[out["first_active_day"].astype(bool)]
    assert flagged[["user_id", "date"]].values.tolist() == [[1, pd.Timestamp("2026-01-01")], [2, pd.Timestamp("2026-01-20")], [3, pd.Timestamp("2026-01-25")]]


def test_matches_bruteforce_on_shuffled_input():
    activity = _activity().sample(frac=1, random_state=4)
    out = rolling_user_features(activity)
    expected = _bruteforce(activity)
    assert out[["user_id", "date"]].values.tolist() == expected[["user_id", "date"]].values.tolist()
    for col in COLUMNS[2:]:
        assert np.allclose(out[col].to_numpy(dtype=float), expected[col].to_numpy(dtype=float), equal_nan=True), col


def test_input_is_not_mutated():
    activity = _activity()
    before = activity.copy(deep=True)
    rolling_user_features(activity)
    pd.testing.assert_frame_equal(activity, before)
