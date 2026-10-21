import itertools
import random

from solution import three_sum


def _normalize(triplets):
    # Keep multiplicity so duplicate triplets are detected.
    return sorted(tuple(sorted(t)) for t in triplets)


def _brute(nums):
    return sorted({tuple(sorted(c)) for c in itertools.combinations(nums, 3) if sum(c) == 0})


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "three_sum")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert _normalize(three_sum([-1, 0, 1, 2, -1, -4])) == [(-1, -1, 2), (-1, 0, 1)]


def test_too_short_or_no_solution():
    assert three_sum([]) == []
    assert three_sum([0, 0]) == []
    assert three_sum([1, 2, -2, -1]) == []


def test_all_zeros_reported_once():
    assert _normalize(three_sum([0, 0, 0])) == [(0, 0, 0)]
    assert _normalize(three_sum([0, 0, 0, 0, 0])) == [(0, 0, 0)]


def test_duplicate_skipping_on_every_position():
    assert _normalize(three_sum([-2, 0, 0, 2, 2])) == [(-2, 0, 2)]
    assert _normalize(three_sum([-2, -2, -2, 1, 1, 1, 4, 4])) == [(-2, -2, 4), (-2, 1, 1)]


def test_does_not_reuse_a_single_element():
    # 0 appears once, so (0, 0, 0) is not valid; -2 appears once, so (-2, -2, 4) is not valid.
    assert _normalize(three_sum([0, 1, -1, -2, 4])) == [(-1, 0, 1)]


def test_unsorted_input_with_wide_range():
    nums = [3, -5, 1, 2, -3, 0, 4, -1]
    assert _normalize(three_sum(nums)) == _brute(nums)


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(6)
    for _ in range(200):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 14))]
        assert _normalize(three_sum(list(nums))) == _brute(nums), nums
