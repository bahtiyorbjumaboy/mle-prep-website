import random

from solution import merge_intervals


def _brute(intervals):
    points = sorted({x for s, e in intervals for x in range(2 * s, 2 * e + 1)})
    merged = []
    for p in points:
        if merged and p == merged[-1][1] + 1:
            merged[-1][1] = p
        else:
            merged.append([p, p])
    return [[s // 2, e // 2] for s, e in merged]


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "merge_intervals")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _merge(intervals):
    return [list(x) for x in merge_intervals([list(x) for x in intervals])]


def test_hand_computed_example():
    assert _merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_empty_and_single():
    assert _merge([]) == []
    assert _merge([[4, 7]]) == [[4, 7]]


def test_touching_endpoints_merge():
    assert _merge([[1, 4], [4, 5]]) == [[1, 5]]


def test_gaps_do_not_merge():
    assert _merge([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]


def test_nested_interval_keeps_larger_end():
    # Overwriting the end with the later interval's end shrinks [1, 10] to [1, 3].
    assert _merge([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]


def test_unsorted_input():
    assert _merge([[8, 10], [1, 3], [2, 6]]) == [[1, 6], [8, 10]]


def test_chain_of_overlaps_and_duplicates():
    assert _merge([[1, 2], [2, 3], [3, 4], [1, 2]]) == [[1, 4]]


def test_zero_length_and_negative_intervals():
    assert _merge([[5, 5], [-3, -1], [-1, 0], [5, 6]]) == [[-3, 0], [5, 6]]


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(24)
    for _ in range(300):
        intervals = []
        for _ in range(rng.randint(0, 10)):
            start = rng.randint(-10, 10)
            intervals.append([start, start + rng.randint(0, 5)])
        assert _merge(intervals) == _brute(intervals), intervals
