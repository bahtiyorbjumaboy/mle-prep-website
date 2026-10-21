import os
import sys

import numpy as np

from solution import last_n_mean_pool, masked_max_pool, masked_mean_pool, pad_and_pool, pad_sequences


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


def _seqs():
    return [
        np.array([[1.0, -1.0], [2.0, -2.0], [3.0, -3.0], [4.0, -4.0], [5.0, -5.0], [6.0, -6.0], [7.0, -7.0]]),
        np.array([[-5.0, -6.0], [-7.0, -8.0]]),
        np.zeros((0, 2)),
        np.array([[10.0, 20.0]]),
    ]


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("pad_sequences", "masked_mean_pool", "last_n_mean_pool", "masked_max_pool", "pad_and_pool"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_pad_sequences_shapes_values_and_mask():
    padded, mask = pad_sequences(_seqs())
    assert padded.shape == (4, 7, 2) and padded.dtype == np.float64
    assert mask.shape == (4, 7) and mask.dtype == np.bool_
    assert mask.sum(axis=1).tolist() == [7, 2, 0, 1]
    assert np.array_equal(padded[1, :2], _seqs()[1]) and np.all(padded[1, 2:] == 0.0)
    assert np.all(padded[2] == 0.0) and not mask[2].any()
    assert mask[0].all() and mask[3].tolist() == [True] + [False] * 6


def test_pad_sequences_all_empty_and_validation():
    padded, mask = pad_sequences([np.zeros((0, 3)), np.zeros((0, 3))])
    assert padded.shape == (2, 0, 3) and mask.shape == (2, 0)
    assert _raises(ValueError, pad_sequences, [])
    assert _raises(ValueError, pad_sequences, [np.ones((2, 3)), np.ones((1, 2))])
    assert _raises(ValueError, pad_sequences, [np.ones(3)])


def test_masked_mean_ignores_padding_and_empty_rows_are_zero():
    padded, mask = pad_sequences(_seqs())
    out = masked_mean_pool(padded, mask)
    assert out.shape == (4, 2)
    assert np.allclose(out, [[4.0, -4.0], [-6.0, -7.0], [0.0, 0.0], [10.0, 20.0]])
    assert np.all(np.isfinite(out))


def test_last_five_uses_real_positions_not_padded_tail():
    padded, mask = pad_sequences(_seqs())
    out = last_n_mean_pool(padded, mask)
    assert out.shape == (4, 2)
    # Row 0: positions 2..6 -> mean 5; short rows use all of their real positions.
    assert np.allclose(out, [[5.0, -5.0], [-6.0, -7.0], [0.0, 0.0], [10.0, 20.0]])
    assert np.allclose(last_n_mean_pool(padded, mask, n=1), [[7.0, -7.0], [-7.0, -8.0], [0.0, 0.0], [10.0, 20.0]])
    assert np.allclose(last_n_mean_pool(padded, mask, n=50), masked_mean_pool(padded, mask))
    assert _raises(ValueError, last_n_mean_pool, padded, mask, 0)


def test_left_padded_mask():
    # Left padding (common for decoder batches): real tokens at the end of the time axis.
    padded = np.zeros((2, 7, 1))
    padded[0, :, 0] = [0, 0, 1, 2, 3, 4, 5]
    padded[1, :, 0] = [0, 0, 0, 0, 0, 8, 9]
    mask = np.array([[False, False, True, True, True, True, True], [False] * 5 + [True, True]])
    assert np.allclose(masked_mean_pool(padded, mask), [[3.0], [8.5]])
    assert np.allclose(last_n_mean_pool(padded, mask, n=3), [[4.0], [8.5]])
    assert np.allclose(masked_max_pool(padded, mask), [[5.0], [9.0]])


def test_last_n_with_holes_in_mask():
    padded = np.arange(8, dtype=float).reshape(1, 8, 1)
    mask = np.array([[True, False, True, True, False, True, False, False]])
    assert np.allclose(last_n_mean_pool(padded, mask, n=2), [[(3.0 + 5.0) / 2]])
    assert np.allclose(last_n_mean_pool(padded, mask, n=3), [[(2.0 + 3.0 + 5.0) / 3]])


def test_masked_max_padding_never_wins_on_negative_values():
    padded, mask = pad_sequences(_seqs())
    out = masked_max_pool(padded, mask)
    assert out.shape == (4, 2)
    assert np.allclose(out, [[7.0, -1.0], [-5.0, -6.0], [0.0, 0.0], [10.0, 20.0]])
    assert np.all(np.isfinite(out))


def test_padding_values_are_ignored_even_if_garbage():
    padded, mask = pad_sequences(_seqs())
    for garbage in (1e9, np.inf, np.nan):
        dirty = padded.copy()
        dirty[~mask] = garbage  # e.g. NaN rows from softmax over all-masked attention
        for pool in (masked_mean_pool, last_n_mean_pool, masked_max_pool):
            assert np.allclose(pool(dirty, mask), pool(padded, mask)), (pool.__name__, garbage)


def test_pad_and_pool_composes_and_batch_of_one():
    p, m, mean, last = pad_and_pool([np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[5.0, 6.0]])])
    assert p.shape == (2, 2, 2) and m.tolist() == [[True, True], [True, False]]
    assert np.allclose(mean, [[2, 3], [5, 6]]) and np.allclose(last, [[2, 3], [5, 6]])
    p, m, mean, last = pad_and_pool([np.arange(24, dtype=float).reshape(8, 3)])
    assert p.shape == (1, 8, 3) and mean.shape == (1, 3) and last.shape == (1, 3)
    assert np.allclose(last, np.arange(24, dtype=float).reshape(8, 3)[3:].mean(axis=0))


def test_inputs_not_modified():
    seqs = _seqs()
    copies = [s.copy() for s in seqs]
    padded, mask = pad_sequences(seqs)
    p0, m0 = padded.copy(), mask.copy()
    masked_mean_pool(padded, mask), last_n_mean_pool(padded, mask), masked_max_pool(padded, mask)
    assert all(np.array_equal(a, b) for a, b in zip(seqs, copies))
    assert np.array_equal(padded, p0) and np.array_equal(mask, m0)


def test_pooling_is_vectorized():
    rng = np.random.default_rng(0)
    padded = rng.normal(size=(500, 40, 4))
    mask = np.arange(40)[None, :] < rng.integers(0, 41, size=(500, 1))
    for pool in (masked_mean_pool, last_n_mean_pool, masked_max_pool):
        out, lines = _line_events(pool, padded, mask)
        assert out.shape == (500, 4)
        assert lines <= 60, f"{pool.__name__} executed {lines} Python lines; expected no loops over B or T"
    lengths = mask.sum(axis=1)
    out = last_n_mean_pool(padded, mask)
    i = int(np.argmax(lengths >= 7))
    assert np.allclose(out[i], padded[i, lengths[i] - 5:lengths[i]].mean(axis=0))
