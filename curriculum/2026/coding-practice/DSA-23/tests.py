import random
from collections import Counter

from solution import top_k_frequent


def _assert_valid_top_k(nums, k, result):
    counts = Counter(nums)
    result = list(result)
    assert len(result) == k, f"expected {k} values, got {result}"
    assert len(set(result)) == k, f"values must be distinct: {result}"
    assert all(value in counts for value in result), f"unknown value in {result}"
    chosen_min = min(counts[v] for v in result)
    others = [counts[v] for v in counts if v not in set(result)]
    assert not others or chosen_min >= max(others), f"{result} skips a more frequent value: {counts}"


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "top_k_frequent")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]


def test_k_equals_one():
    assert top_k_frequent([4, 1, 4, 2, 4, 1], 1) == [4]
    assert top_k_frequent([7], 1) == [7]


def test_k_equals_number_of_distinct_values():
    assert sorted(top_k_frequent([3, 1, 2, 1, 3, 3], 3)) == [1, 2, 3]


def test_heap_orientation_keeps_most_frequent():
    # A min-heap of size k must evict the least frequent; reversing it keeps the wrong ones.
    nums = [5] * 6 + [6] * 5 + [7] * 4 + [8] * 3 + [9] * 2 + [10]
    assert sorted(top_k_frequent(nums, 3)) == [5, 6, 7]


def test_frequency_not_value_or_first_occurrence():
    nums = [100, 1, 2, 2, 3, 3, 3, 1, 3, 2]
    assert sorted(top_k_frequent(nums, 2)) == [2, 3]


def test_negative_values_and_zero():
    assert sorted(top_k_frequent([-1, -1, 0, 0, 0, 5], 2)) == [-1, 0]


def test_ties_at_cutoff_accept_any_tied_value():
    nums = [1, 1, 1, 2, 2, 3, 3, 4]
    result = top_k_frequent(list(nums), 2)
    _assert_valid_top_k(nums, 2, result)
    assert 1 in result


def test_random_inputs_satisfy_top_k_invariant():
    rng = random.Random(23)
    for _ in range(300):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 40))]
        k = rng.randint(1, len(set(nums)))
        _assert_valid_top_k(nums, k, top_k_frequent(list(nums), k))
