import math

import pandas as pd

from solution import FEATURES, build_features

T0 = pd.Timestamp("2026-01-01")
SPLIT = T0 + pd.Timedelta(hours=100)
SMOOTHING = 1.0

# (index, user, merchant, amount, hour, label); deliberately unsorted, non-RangeIndex.
ROWS = [
    (402, "u3", "c", 70.0, 150, 0),
    (12, "u2", "a", 250.0, 5, 1),
    (88, "u1", "c", 22.0, 90, 0),
    (301, "u3", "a", 9.0, 100, 1),  # exactly at the split boundary -> validation
    (907, "u1", "a", 12.0, 0, 0),
    (71, "u2", "b", 300.0, 30, 1),
    (19, "u2", "d", 999.0, 130, 1),  # merchant "d" never appears in training
    (450, "u1", "b", 40.0, 20, 0),
    (5, "u1", "a", 15.0, 47, 1),
    (618, "u3", "c", 60.0, 60, 0),
    (77, "u1", "b", 5000.0, 110, 0),
    (240, "u2", "c", 410.0, 75, 1),
    (33, "u3", "a", 8.0, 26, 0),
]


def _events(rows=ROWS) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_id": [r[1] for r in rows],
            "merchant": [r[2] for r in rows],
            "amount": [r[3] for r in rows],
            "ts": [T0 + pd.Timedelta(hours=r[4]) for r in rows],
            "label": [r[5] for r in rows],
        },
        index=[r[0] for r in rows],
    )


def _features(out: dict) -> pd.DataFrame:
    return pd.concat([out["train"], out["validation"]])[FEATURES].sort_index()


def _oracle(rows=ROWS) -> dict[int, dict[str, float]]:
    """Independent loop implementation of the documented contract."""
    train = [r for r in rows if r[4] < 100]
    amounts = [r[3] for r in train]
    mean = sum(amounts) / len(amounts)
    std = math.sqrt(sum((a - mean) ** 2 for a in amounts) / len(amounts)) or 1.0
    expected = {}
    for idx, user, merchant, amount, hour, label in rows:
        pool = [r for r in train if r[0] != idx]  # leave-one-out for training rows
        prior = sum(r[5] for r in pool) / len(pool)
        same = [r[5] for r in pool if r[2] == merchant]
        earlier = [r[4] for r in rows if r[1] == user and r[4] < hour]
        expected[idx] = {
            "amount_z": (amount - mean) / std,
            "merchant_te": (sum(same) + SMOOTHING * prior) / (len(same) + SMOOTHING),
            "hours_since_prev_txn": float(hour - max(earlier)) if earlier else -1.0,
        }
    return expected


def _assert_close(actual: float, expected: float, what: str) -> None:
    assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9), (
        f"{what}: got {actual}, expected {expected}"
    )


def test_split_boundary_and_output_shape():
    out = build_features(_events(), SPLIT, SMOOTHING)
    assert set(out["train"].index) == {r[0] for r in ROWS if r[4] < 100}
    assert set(out["validation"].index) == {r[0] for r in ROWS if r[4] >= 100}
    assert 301 in out["validation"].index, "ts == split_time belongs to validation"
    for part in ("train", "validation"):
        assert list(out[part].columns) == FEATURES + ["label"]
    labels = pd.concat([out["train"], out["validation"]])["label"]
    assert all(labels.loc[r[0]] == r[5] for r in ROWS), "labels must stay attached to rows"


def test_scaler_is_fit_on_training_rows_only():
    out = build_features(_events(), SPLIT, SMOOTHING)
    train_amounts = [r[3] for r in ROWS if r[4] < 100]
    mean = sum(train_amounts) / len(train_amounts)
    _assert_close(out["scaler"]["mean"], mean, "scaler mean")
    expected = _oracle()
    for idx in out["train"].index.union(out["validation"].index):
        actual = _features(out).loc[idx, "amount_z"]
        _assert_close(actual, expected[idx]["amount_z"], f"amount_z[{idx}]")


def test_validation_amounts_do_not_change_training_features():
    base = build_features(_events(), SPLIT, SMOOTHING)
    shifted = _events()
    shifted.loc[shifted["ts"] >= SPLIT, "amount"] *= 1000.0
    out = build_features(shifted, SPLIT, SMOOTHING)
    pd.testing.assert_frame_equal(out["train"], base["train"])
    assert out["scaler"] == base["scaler"]


def test_validation_labels_never_influence_any_feature():
    base = _features(build_features(_events(), SPLIT, SMOOTHING))
    flipped = _events()
    is_valid = flipped["ts"] >= SPLIT
    flipped.loc[is_valid, "label"] = 1 - flipped.loc[is_valid, "label"]
    pd.testing.assert_frame_equal(_features(build_features(flipped, SPLIT, SMOOTHING)), base)


def test_training_row_encoding_never_sees_its_own_label():
    base = _features(build_features(_events(), SPLIT, SMOOTHING))
    for idx in [r[0] for r in ROWS if r[4] < 100]:
        flipped = _events()
        flipped.loc[idx, "label"] = 1 - flipped.loc[idx, "label"]
        out = _features(build_features(flipped, SPLIT, SMOOTHING))
        _assert_close(
            out.loc[idx, "merchant_te"],
            base.loc[idx, "merchant_te"],
            f"merchant_te[{idx}] changed when only its own label flipped",
        )


def test_target_encoding_matches_hand_computed_values():
    out = _features(build_features(_events(), SPLIT, SMOOTHING))
    expected = _oracle()
    for idx in out.index:
        _assert_close(out.loc[idx, "merchant_te"], expected[idx]["merchant_te"], f"te[{idx}]")
    train_prior = sum(r[5] for r in ROWS if r[4] < 100) / sum(1 for r in ROWS if r[4] < 100)
    _assert_close(out.loc[19, "merchant_te"], train_prior, "unseen merchant -> training prior")


def test_recency_uses_previous_transaction_only():
    out = _features(build_features(_events(), SPLIT, SMOOTHING))
    expected = _oracle()
    for idx in out.index:
        _assert_close(
            out.loc[idx, "hours_since_prev_txn"],
            expected[idx]["hours_since_prev_txn"],
            f"hours_since_prev_txn[{idx}]",
        )
    assert out.loc[907, "hours_since_prev_txn"] == -1.0, "u1's first transaction"
    _assert_close(out.loc[301, "hours_since_prev_txn"], 40.0, "u3: hour 100 - hour 60")


def test_future_events_never_change_existing_features():
    base = _features(build_features(_events(), SPLIT, SMOOTHING))
    future = ROWS + [
        (9001, "u1", "a", 77.0, 400, 1),
        (9002, "u2", "c", 5.0, 410, 0),
        (9003, "u3", "b", 123.0, 420, 1),
    ]
    out = _features(build_features(_events(future), SPLIT, SMOOTHING)).drop([9001, 9002, 9003])
    pd.testing.assert_frame_equal(out, base)


def test_input_is_not_mutated():
    events = _events()
    snapshot = events.copy()
    build_features(events, SPLIT, SMOOTHING)
    pd.testing.assert_frame_equal(events, snapshot)
