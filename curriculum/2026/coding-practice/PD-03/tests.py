from solution import point_in_time_features
import math
import numpy as np
import pandas as pd

FEATURES = ["count_1d", "count_7d", "count_30d", "amount_30d", "days_since_prev_event", "distinct_event_types_30d"]


def _labels():
    return pd.DataFrame({
        "label_id": [1, 2, 3, 4, 5, 6],
        "user_id": [1, 1, 2, 1, 3, 4],
        "label_ts": pd.to_datetime(["2026-02-01 00:00:00", "2026-01-10 12:00:00", "2026-02-01 00:00:00", "2026-02-01 00:00:00",
                                    "2026-01-15 00:00:00", "2026-02-01 00:00:00"]),
    }, index=[40, 30, 20, 10, 0, 50])


def _events():
    return pd.DataFrame({
        "user_id": [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 4],
        "event_ts": pd.to_datetime(["2026-02-01 00:00:00", "2026-01-31 23:59:59", "2026-01-31 00:00:00", "2026-01-30 23:59:59",
                                    "2026-01-25 00:00:00", "2026-01-02 00:00:00", "2026-01-01 23:00:00", "2026-02-05 00:00:00",
                                    "2026-01-20 00:00:00", "2026-01-15 00:00:00", "2026-01-16 00:00:00", "2025-12-01 00:00:00"]),
        "event_type": ["buy", "view", "view", "click", "view", "buy", "view", "buy", "click", "view", "view", "buy"],
        "amount": [1000.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, np.nan, 7.0, 5.0, 3.0],
    }).sample(frac=1, random_state=11)


def _bruteforce(labels, events):
    rows = []
    for label in labels.itertuples():
        prior = events[(events["user_id"] == label.user_id) & (events["event_ts"] < label.label_ts)]
        window = {n: prior[prior["event_ts"] >= label.label_ts - pd.Timedelta(days=n)] for n in (1, 7, 30)}
        rows.append({
            "count_1d": len(window[1]), "count_7d": len(window[7]), "count_30d": len(window[30]),
            "amount_30d": float(window[30]["amount"].sum()),
            "days_since_prev_event": (label.label_ts - prior["event_ts"].max()) / pd.Timedelta(days=1) if len(prior) else np.nan,
            "distinct_event_types_30d": window[30]["event_type"].nunique(),
        })
    return pd.DataFrame(rows, index=labels.index)


def _assert_matches(out, expected):
    for col in FEATURES:
        got, want = out[col].to_numpy(dtype=float), expected[col].to_numpy(dtype=float)
        assert np.allclose(got, want, equal_nan=True), f"{col}: got {got.tolist()}, expected {want.tolist()}"


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "point_in_time_features"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_label_order_index_and_columns_preserved():
    labels = _labels()
    out = point_in_time_features(labels, _events())
    assert list(out.index) == [40, 30, 20, 10, 0, 50] and out["label_id"].tolist() == [1, 2, 3, 4, 5, 6]
    assert list(out.columns) == ["label_id", "user_id", "label_ts", *FEATURES]


def test_event_at_label_time_is_excluded():
    out = point_in_time_features(_labels(), _events()).set_index("label_id")
    assert out.loc[1, "count_1d"] == 2 and out.loc[1, "amount_30d"] < 1000
    assert out.loc[5, "count_30d"] == 0 and pd.isna(out.loc[5, "days_since_prev_event"])


def test_window_lower_bounds_are_inclusive():
    out = point_in_time_features(_labels(), _events()).set_index("label_id")
    assert (out.loc[1, "count_1d"], out.loc[1, "count_7d"], out.loc[1, "count_30d"]) == (2, 4, 6)
    assert (out.loc[2, "count_1d"], out.loc[2, "count_7d"], out.loc[2, "count_30d"]) == (0, 0, 2)


def test_amount_and_distinct_types():
    out = point_in_time_features(_labels(), _events()).set_index("label_id")
    assert math.isclose(out.loc[1, "amount_30d"], 31.0) and math.isclose(out.loc[2, "amount_30d"], 48.0)
    assert out.loc[1, "distinct_event_types_30d"] == 3 and out.loc[2, "distinct_event_types_30d"] == 2


def test_days_since_previous_event_uses_strictly_prior_history():
    out = point_in_time_features(_labels(), _events()).set_index("label_id")
    assert math.isclose(out.loc[1, "days_since_prev_event"], 1 / 86400)
    assert math.isclose(out.loc[2, "days_since_prev_event"], 8.5)
    assert out.loc[6, "count_30d"] == 0 and math.isclose(out.loc[6, "days_since_prev_event"], 62.0)


def test_duplicate_label_rows_and_users_without_history():
    out = point_in_time_features(_labels(), _events()).set_index("label_id")
    assert out.loc[1, FEATURES].tolist() == out.loc[4, FEATURES].tolist()
    assert out.loc[3, "count_30d"] == 0 and out.loc[3, "amount_30d"] == 0.0 and out.loc[3, "distinct_event_types_30d"] == 0
    assert pd.isna(out.loc[3, "days_since_prev_event"])


def test_every_used_event_is_strictly_before_label_on_random_data():
    rng = np.random.default_rng(5)
    base = pd.Timestamp("2026-01-01")
    events = pd.DataFrame({
        "user_id": rng.integers(0, 8, 400),
        "event_ts": base + pd.to_timedelta(rng.integers(0, 60 * 24, 400) * 60, unit="min"),
        "event_type": rng.choice(["view", "click", "buy"], 400),
        "amount": np.where(rng.random(400) < 0.2, np.nan, rng.integers(1, 50, 400).astype(float)),
    })
    # Half of the labels sit exactly on an event timestamp or exactly N days after one.
    picked = events.sample(60, random_state=1)
    shifts = pd.to_timedelta(rng.choice([0, 1, 7, 30], 60), unit="D")
    labels = pd.DataFrame({"user_id": np.concatenate([picked["user_id"].to_numpy(), rng.integers(0, 9, 60)]),
                           "label_ts": np.concatenate([(picked["event_ts"] + shifts).to_numpy(),
                                                       (base + pd.to_timedelta(rng.integers(0, 70 * 24, 60), unit="h")).to_numpy()])})
    labels = labels.sample(frac=1, random_state=2)
    out = point_in_time_features(labels, events)
    assert list(out.index) == list(labels.index)
    _assert_matches(out, _bruteforce(labels, events))


def test_inputs_are_not_mutated():
    labels, events = _labels(), _events()
    before = (labels.copy(deep=True), events.copy(deep=True))
    point_in_time_features(labels, events)
    pd.testing.assert_frame_equal(labels, before[0])
    pd.testing.assert_frame_equal(events, before[1])
