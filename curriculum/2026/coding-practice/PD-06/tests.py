from solution import reshape_and_reconcile
import math
import numpy as np
import pandas as pd

LABELS = ["apparel", "auto", "books", "crafts", "unassigned", "unknown"]


def _frame():
    return pd.DataFrame({
        "entity_id": [2, 1, 1, 2, 3, 3],
        "region": ["us", "us", "eu", "eu", "us", "us"],
        "codes": [[], ["a", "b"], ["a"], ["c", "c", "z"], None, ["b"]],
        "value": [6.0, 10.0, 4.0, 9.0, 2.0, 1.0],
    })


def _dimension():
    return pd.DataFrame({"region": ["us", "us", "eu", "eu"], "code": ["a", "b", "a", "c"], "label": ["apparel", "books", "auto", "crafts"]})


def _entity(wide, entity_id):
    rows = wide[wide["entity_id"] == entity_id]
    assert len(rows) == 1, f"expected one row for entity {entity_id}, found {len(rows)}"
    return rows.iloc[0]


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "reshape_and_reconcile"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_entity_grain_and_columns():
    wide, _ = reshape_and_reconcile(_frame(), _dimension())
    assert wide["entity_id"].tolist() == [1, 2, 3] and list(wide.index) == [0, 1, 2]
    assert list(wide.columns) == ["entity_id", *LABELS, "total", "n_codes"]


def test_multi_key_merge_maps_code_by_region():
    wide, _ = reshape_and_reconcile(_frame(), _dimension())
    e1 = _entity(wide, 1)
    assert (e1["apparel"], e1["auto"], e1["books"]) == (5.0, 4.0, 5.0)


def test_value_is_split_across_codes_with_duplicate_entries():
    wide, _ = reshape_and_reconcile(_frame(), _dimension())
    e2 = _entity(wide, 2)
    assert math.isclose(e2["crafts"], 6.0) and math.isclose(e2["unknown"], 3.0)


def test_empty_and_missing_lists_go_to_unassigned():
    wide, _ = reshape_and_reconcile(_frame(), _dimension())
    assert _entity(wide, 2)["unassigned"] == 6.0 and _entity(wide, 3)["unassigned"] == 2.0
    assert _entity(wide, 1)["unassigned"] == 0.0


def test_totals_and_code_counts():
    wide, _ = reshape_and_reconcile(_frame(), _dimension())
    assert wide["total"].tolist() == [14.0, 15.0, 3.0] and wide["n_codes"].tolist() == [3, 3, 1]
    assert not wide[LABELS].isna().any().any()


def test_reconciliation_is_balanced():
    _, rec = reshape_and_reconcile(_frame(), _dimension())
    assert math.isclose(rec["before"], 32.0) and math.isclose(rec["after"], 32.0)
    assert abs(rec["difference"]) <= 1e-9 and bool(rec["balanced"]) is True


def test_conservation_on_random_frames():
    rng = np.random.default_rng(9)
    codes = ["a", "b", "c", "z"]
    frame = pd.DataFrame({
        "entity_id": rng.integers(0, 10, 200),
        "region": rng.choice(["us", "eu"], 200),
        "codes": [list(rng.choice(codes, rng.integers(0, 4))) for _ in range(200)],
        "value": rng.random(200) * 100,
    })
    wide, rec = reshape_and_reconcile(frame, _dimension())
    assert math.isclose(wide["total"].sum(), frame["value"].sum()) and bool(rec["balanced"]) is True
    label_columns = [c for c in wide.columns if c not in ("entity_id", "total", "n_codes")]
    assert math.isclose(rec["after"], wide[label_columns].to_numpy().sum()) and math.isclose(rec["before"], frame["value"].sum())
    expected = frame.groupby("entity_id")["value"].sum()
    assert np.allclose(wide.set_index("entity_id")["total"].reindex(expected.index).to_numpy(), expected.to_numpy())


def test_duplicate_dimension_keys_raise():
    dim = pd.concat([_dimension(), pd.DataFrame({"region": ["us"], "code": ["a"], "label": ["accessories"]})], ignore_index=True)
    try:
        reshape_and_reconcile(_frame(), dim)
    except ValueError:
        return
    raise AssertionError("duplicate (region, code) in dimension must raise ValueError")


def test_inputs_are_not_mutated():
    frame, dim = _frame(), _dimension()
    before = (frame.copy(deep=True), dim.copy(deep=True))
    reshape_and_reconcile(frame, dim)
    pd.testing.assert_frame_equal(frame, before[0])
    pd.testing.assert_frame_equal(dim, before[1])
