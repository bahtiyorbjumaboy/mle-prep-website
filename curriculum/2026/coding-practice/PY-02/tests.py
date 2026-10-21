import copy
import math
import random

from solution import FeatureTransformer

ROWS = [
    {"age": 10, "income": 1.0, "country": "us", "device": "ios"},
    {"age": None, "income": 3.0, "country": "ca", "device": "web"},
    {"age": 30, "income": float("nan"), "country": "us"},
    {"income": 5.0, "country": None, "device": "ios", "extra": "ignored"},
]


def _close(actual, expected):
    assert len(actual) == len(expected), (actual, expected)
    for a_row, e_row in zip(actual, expected):
        assert len(a_row) == len(e_row), (a_row, e_row)
        for a, e in zip(a_row, e_row):
            assert math.isclose(a, e, rel_tol=1e-9, abs_tol=1e-9), (a_row, e_row)


def _raises(exc_type, fn):
    try:
        fn()
    except exc_type:
        return True
    return False


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.FeatureTransformer)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_feature_names_layout():
    t = FeatureTransformer(numeric=["age", "income"], categorical=["country", "device"]).fit(ROWS)
    assert t.feature_names_ == [
        "age", "age__missing", "income", "income__missing",
        "country=ca", "country=us", "country=__unknown__",
        "device=ios", "device=web", "device=__unknown__",
    ]


def test_hand_computed_fit_transform():
    t = FeatureTransformer(numeric=["age", "income"], categorical=["country", "device"])
    out = t.fit_transform(ROWS)
    # age: values [10, 30] -> mean 20, std 10.  income: [1, 3, 5] -> mean 3, std sqrt(8/3).
    s = math.sqrt(8 / 3)
    _close(out, [
        [-1.0, 0.0, -2 / s, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 1.0, 2 / s, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
    ])


def test_transform_uses_training_statistics_and_unknown_bucket():
    t = FeatureTransformer(numeric=["age"], categorical=["country"]).fit(ROWS)
    out = t.transform([{"age": 40, "country": "xx"}, {"country": "us"}])
    _close(out, [[2.0, 0.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0, 0.0]])


def test_single_row_transform_does_not_refit():
    # Refitting on one row would give std 0 / mean 40 and a different schema.
    t = FeatureTransformer(numeric=["age"], categorical=["country"]).fit(ROWS)
    names = list(t.feature_names_)
    _close(t.transform([{"age": 40, "country": "ca"}]), [[2.0, 0.0, 1.0, 0.0, 0.0]])
    assert t.feature_names_ == names


def test_constant_and_all_missing_numeric_columns():
    rows = [{"a": 5, "b": None}, {"a": 5}]
    t = FeatureTransformer(numeric=["a", "b"]).fit(rows)
    _close(t.transform([{"a": 5, "b": None}, {"a": 7, "b": 2}]), [[0.0, 0.0, 0.0, 1.0], [2.0, 0.0, 2.0, 0.0]])


def test_output_is_finite():
    t = FeatureTransformer(numeric=["age", "income"], categorical=["country"]).fit(ROWS)
    out = t.transform([{"age": float("nan"), "income": None, "country": "zz"}])
    assert all(math.isfinite(x) for x in out[0])


def test_second_fit_resets_state():
    t = FeatureTransformer(numeric=["x"], categorical=["c"])
    t.fit([{"x": 100, "c": "old"}, {"x": 200, "c": "older"}])
    t.fit([{"x": 1, "c": "new"}, {"x": 3, "c": "new"}])
    assert t.feature_names_ == ["x", "x__missing", "c=new", "c=__unknown__"]
    _close(t.transform([{"x": 3, "c": "old"}]), [[1.0, 0.0, 0.0, 1.0]])


def test_schema_is_stable_under_row_order():
    rng = random.Random(102)
    rows = [{"n": rng.randint(0, 9), "c": rng.choice("dcba")} for _ in range(30)]
    base = FeatureTransformer(numeric=["n"], categorical=["c"]).fit(rows)
    probe = [{"n": 4, "c": "b"}, {"n": None, "c": "q"}]
    for _ in range(3):
        rng.shuffle(rows)
        other = FeatureTransformer(numeric=["n"], categorical=["c"]).fit(rows)
        assert other.feature_names_ == base.feature_names_
        _close(other.transform(probe), base.transform(probe))


def test_fit_transform_equals_fit_then_transform_and_rows_are_not_mutated():
    rows = copy.deepcopy(ROWS)
    a = FeatureTransformer(numeric=["age", "income"], categorical=["country"]).fit_transform(rows)
    b = FeatureTransformer(numeric=["age", "income"], categorical=["country"]).fit(rows).transform(rows)
    _close(a, b)
    assert repr(rows) == repr(ROWS)


def test_fit_returns_self_and_handles_empty_transform():
    t = FeatureTransformer(numeric=["age"])
    assert t.fit(ROWS) is t
    assert t.transform([]) == []


def test_error_contract():
    assert _raises(RuntimeError, lambda: FeatureTransformer(numeric=["a"]).transform([{"a": 1}]))
    assert _raises(ValueError, lambda: FeatureTransformer(numeric=["a"]).fit([]))
    assert _raises(ValueError, lambda: FeatureTransformer(numeric=["a"]).fit([{"a": "abc"}]))
    assert _raises(ValueError, lambda: FeatureTransformer(numeric=["a"]).fit([{"a": True}]))
    t = FeatureTransformer(numeric=["a"]).fit([{"a": 1}])
    assert _raises(ValueError, lambda: t.transform([{"a": "1"}]))
