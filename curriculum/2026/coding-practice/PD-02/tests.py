from solution import attach_profiles
import pandas as pd


def _profiles():
    return pd.DataFrame({
        "user_id": [2, 1, 1, 1, 2, 1],
        "profile_ts": ["2026-01-05 00:00:00", "2026-01-03 00:00:00", "2026-01-01 00:00:00", "2026-01-03 00:00:00",
                       "2026-01-02 00:00:00", "2026-01-09 00:00:00"],
        "tier": ["gold", "silver", "bronze", "silver_plus", "basic", "platinum"],
        "country": ["US", "CA", "CA", "CA", "US", "MX"],
    })


def _orders():
    return pd.DataFrame({
        "order_id": [10, 11, 12, 13, 14, 15, 16, 17],
        "user_id": [1, 2, 1, 1, 3, 2, 1, 2],
        "order_ts": ["2026-01-04 00:00:00", "2026-01-05 00:00:00", "2026-01-02 12:00:00", "2026-01-03 00:00:00",
                     "2026-01-04 00:00:00", "2026-01-01 00:00:00", "2026-01-10 00:00:00", "2026-01-04 23:59:59"],
        "amount": [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
    })


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "attach_profiles"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_order_rows_and_order_preserved():
    attached, _ = attach_profiles(_profiles(), _orders())
    assert attached["order_id"].tolist() == [10, 11, 12, 13, 14, 15, 16, 17]
    assert list(attached.index) == list(range(8))
    assert attached["amount"].tolist() == [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]


def test_profile_state_is_per_user_and_backward_looking():
    attached, _ = attach_profiles(_profiles(), _orders())
    tiers = dict(zip(attached["order_id"], attached["tier"]))
    assert tiers[10] == "silver_plus" and tiers[12] == "bronze" and tiers[16] == "platinum"
    assert tiers[17] == "basic"


def test_update_at_exact_order_time_applies_with_last_row_tie_break():
    attached, _ = attach_profiles(_profiles(), _orders())
    row = attached.loc[attached["order_id"] == 13].iloc[0]
    assert row["tier"] == "silver_plus" and row["profile_ts"] == pd.Timestamp("2026-01-03")
    assert attached.loc[attached["order_id"] == 11, "tier"].iloc[0] == "gold"


def test_orders_without_prior_profile_get_missing_values():
    attached, _ = attach_profiles(_profiles(), _orders())
    for order_id in (14, 15):
        row = attached.loc[attached["order_id"] == order_id].iloc[0]
        assert pd.isna(row["tier"]) and pd.isna(row["country"]) and pd.isna(row["profile_ts"])


def test_output_columns_and_datetimes():
    attached, latest = attach_profiles(_profiles(), _orders())
    assert list(attached.columns) == ["order_id", "user_id", "order_ts", "amount", "profile_ts", "tier", "country"]
    assert pd.api.types.is_datetime64_any_dtype(attached["order_ts"]) and pd.api.types.is_datetime64_any_dtype(attached["profile_ts"])
    assert list(latest.columns) == ["user_id", "profile_ts", "tier", "country"]


def test_latest_profile_per_user():
    _, latest = attach_profiles(_profiles(), _orders())
    assert latest["user_id"].tolist() == [1, 2] and list(latest.index) == [0, 1]
    assert latest["tier"].tolist() == ["platinum", "gold"] and latest["country"].tolist() == ["MX", "US"]


def test_latest_tie_uses_later_row():
    profiles = _profiles()
    profiles.loc[len(profiles)] = [1, "2026-01-09 00:00:00", "diamond", "MX"]
    _, latest = attach_profiles(profiles, _orders())
    assert latest.loc[latest["user_id"] == 1, "tier"].iloc[0] == "diamond"


def test_matches_bruteforce_on_random_data():
    import numpy as np
    rng = np.random.default_rng(3)
    base = pd.Timestamp("2026-01-01")
    profiles = pd.DataFrame({"user_id": rng.integers(0, 6, 60), "profile_ts": base + pd.to_timedelta(rng.integers(0, 40, 60), unit="D"), "tier": [f"t{i}" for i in range(60)]})
    orders = pd.DataFrame({"order_id": range(80), "user_id": rng.integers(0, 7, 80), "order_ts": base + pd.to_timedelta(rng.integers(0, 40, 80), unit="D")})
    attached, _ = attach_profiles(profiles, orders)
    for order, got in zip(orders.itertuples(), attached["tier"]):
        prior = profiles[(profiles["user_id"] == order.user_id) & (profiles["profile_ts"] <= order.order_ts)]
        expected = prior.loc[prior["profile_ts"] == prior["profile_ts"].max(), "tier"].iloc[-1] if len(prior) else None
        assert (pd.isna(got) and expected is None) or got == expected, (order, got, expected)


def test_inputs_are_not_mutated():
    profiles, orders = _profiles(), _orders()
    before = (profiles.copy(deep=True), orders.copy(deep=True))
    attach_profiles(profiles, orders)
    pd.testing.assert_frame_equal(profiles, before[0])
    pd.testing.assert_frame_equal(orders, before[1])
