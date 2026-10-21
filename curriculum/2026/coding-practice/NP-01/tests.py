import os
import sys

import numpy as np

from solution import array_operations


def _line_events(fn, *args, **kwargs):
    """Count Python line events executed inside solution.py (timing-free loop detector)."""
    count = 0

    def local(frame, event, arg):
        nonlocal count
        if event == "line":
            count += 1
        return local

    def global_trace(frame, event, arg):
        return local if os.path.basename(frame.f_code.co_filename) == "solution.py" else None

    previous = sys.gettrace()
    sys.settrace(global_trace)
    try:
        result = fn(*args, **kwargs)
    finally:
        sys.settrace(previous)
    return result, count


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "array_operations")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_non_square_example():
    x = np.array([[3.0, 4.0, 0.0], [1.0, 2.0, 3.0]])
    out = array_operations(x, weights=np.array([1.0, 0.0, 3.0]), mask=np.array([[True, False, True], [False, True, True]]))
    assert np.allclose(out["row_normalized"], [[0.6, 0.8, 0.0], np.array([1, 2, 3]) / np.sqrt(14)])
    assert np.allclose(out["col_standardized"], [[1.0, 1.0, -1.0], [-1.0, -1.0, 1.0]])
    assert np.allclose(out["masked_mean"], [1.5, 2.5])
    assert np.allclose(out["weighted_row_mean"], [0.75, 2.5])


def test_output_shapes_dtypes_and_batch_of_one():
    for b, d in [(1, 4), (4, 1), (3, 5), (5, 3)]:
        x = np.arange(b * d, dtype=float).reshape(b, d) + 1
        out = array_operations(x)
        assert set(out) == {"row_normalized", "col_standardized", "masked_mean", "weighted_row_mean"}
        assert out["row_normalized"].shape == (b, d) and out["col_standardized"].shape == (b, d)
        assert out["masked_mean"].shape == (b,) and out["weighted_row_mean"].shape == (b,)
        for value in out.values():
            assert isinstance(value, np.ndarray) and value.dtype == np.float64


def test_row_normalization_axis_and_zero_rows():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(3, 5))
    x[1] = 0.0
    out = array_operations(x)["row_normalized"]
    assert np.all(np.isfinite(out))
    assert np.allclose(out[1], 0.0)
    norms = np.linalg.norm(out, axis=1)
    assert np.allclose(norms[[0, 2]], 1.0)
    assert np.allclose(out[[0, 2]], x[[0, 2]] / np.linalg.norm(x[[0, 2]], axis=1, keepdims=True))


def test_row_normalization_extreme_magnitudes():
    x = np.array([[1e-150, 2e-150], [3e150, -4e150]])
    out = array_operations(x)["row_normalized"]
    assert np.allclose(out, [[1 / np.sqrt(5), 2 / np.sqrt(5)], [0.6, -0.8]])


def test_column_standardization_population_std_and_axis():
    rng = np.random.default_rng(1)
    x = rng.normal(loc=5.0, scale=3.0, size=(6, 4))
    out = array_operations(x)["col_standardized"]
    assert np.allclose(out.mean(axis=0), 0.0)
    assert np.allclose(out.std(axis=0), 1.0)  # ddof=0, not ddof=1
    assert np.allclose(out, (x - x.mean(axis=0)) / x.std(axis=0))


def test_constant_columns_use_exact_equality_not_tiny_std():
    # std of [0.1, 0.1, 0.1] is ~1e-17, not 0: guarding with `std > 0` yields -1s.
    x = np.array([[0.1, 12345.678, 1.0, 2.0], [0.1, 12345.678, 1.0 + 1e-9, 4.0], [0.1, 12345.678, 1.0, 6.0]])
    out = array_operations(x)["col_standardized"]
    assert np.all(np.isfinite(out))
    assert np.allclose(out[:, 0], 0.0) and np.allclose(out[:, 1], 0.0)
    # A nearly-constant but genuinely varying column is still standardized.
    assert np.allclose(out[:, 2], (x[:, 2] - x[:, 2].mean()) / x[:, 2].std())
    single = array_operations(np.array([[1.0, -2.0, 3.0]]))["col_standardized"]
    assert np.array_equal(single, np.zeros((1, 3)))


def test_masked_mean_rows_and_empty_row_is_nan():
    x = np.array([[1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0], [5.0, 5.0, 5.0, 5.0]])
    mask = np.array([[True, True, False, False], [False, False, False, False], [False, False, False, True]])
    out = array_operations(x, mask=mask)["masked_mean"]
    assert out.shape == (3,)
    assert np.allclose(out[[0, 2]], [1.5, 5.0])
    assert np.isnan(out[1])


def test_integer_mask_is_boolean_not_fancy_index():
    x = np.array([[1.0, 2.0, 3.0], [4.0, 6.0, 8.0]])
    bool_mask = np.array([[True, False, True], [False, True, True]])
    by_bool = array_operations(x, mask=bool_mask)["masked_mean"]
    by_int = array_operations(x, mask=bool_mask.astype(int))["masked_mean"]
    assert np.allclose(by_bool, [2.0, 7.0]) and np.allclose(by_int, by_bool)


def test_mask_none_is_plain_row_mean():
    x = np.array([[1.0, 2.0, 6.0], [0.0, -3.0, 3.0]])
    assert np.allclose(array_operations(x)["masked_mean"], [3.0, 0.0])


def test_weighted_row_mean_uses_column_weights_on_non_square_input():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(5, 3))
    w = np.array([0.5, 2.0, 1.5])
    out = array_operations(x, weights=w)["weighted_row_mean"]
    assert out.shape == (5,)
    assert np.allclose(out, (x * w).sum(axis=1) / w.sum())
    assert np.allclose(array_operations(x)["weighted_row_mean"], x.mean(axis=1))


def test_integer_input_is_promoted_to_float():
    x = np.array([[1, 2], [3, 4], [0, 0]])
    out = array_operations(x, weights=np.array([1, 3]))
    assert np.allclose(out["row_normalized"][0], np.array([1, 2]) / np.sqrt(5))
    assert np.allclose(out["weighted_row_mean"], [1.75, 3.75, 0.0])


def test_inputs_are_not_modified():
    x = np.array([[3.0, 4.0], [1.0, 1.0], [0.0, 2.0]])
    w = np.array([1.0, 2.0])
    mask = np.array([[True, False], [True, True], [False, False]])
    copies = (x.copy(), w.copy(), mask.copy())
    out = array_operations(x, weights=w, mask=mask)
    out["row_normalized"][:] = -1
    assert np.array_equal(x, copies[0]) and np.array_equal(w, copies[1]) and np.array_equal(mask, copies[2])


def test_invalid_inputs_raise_value_error():
    x = np.ones((3, 2))
    assert _raises(ValueError, array_operations, np.ones(4))
    assert _raises(ValueError, array_operations, x, weights=np.ones(3))
    assert _raises(ValueError, array_operations, x, weights=np.ones((2, 1)))
    assert _raises(ValueError, array_operations, x, weights=np.array([1.0, -1.0]))
    assert _raises(ValueError, array_operations, x, weights=np.zeros(2))
    assert _raises(ValueError, array_operations, x, mask=np.ones((3, 1), dtype=bool))
    assert _raises(ValueError, array_operations, x, mask=np.ones((2, 3), dtype=bool))


def test_vectorized_no_python_loops_over_batch_or_features():
    rng = np.random.default_rng(3)
    x = rng.normal(size=(400, 300))
    mask = rng.random(size=x.shape) < 0.5
    w = rng.random(300)
    out, lines = _line_events(array_operations, x, weights=w, mask=mask)
    assert lines <= 150, f"executed {lines} Python lines; expected a loop-free O(BD) implementation"
    assert np.allclose(out["masked_mean"], np.where(mask, x, 0).sum(axis=1) / mask.sum(axis=1))
