import itertools
import random

from solution import subsets_with_dup


def _normalize(subsets):
    # Keep multiplicity so duplicate subsets are detected.
    return sorted(tuple(sorted(s)) for s in subsets)


def _brute(nums):
    return sorted({tuple(sorted(c)) for r in range(len(nums) + 1) for c in itertools.combinations(nums, r)})


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "subsets_with_dup")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert _normalize(subsets_with_dup([1, 2, 2])) == [(), (1,), (1, 2), (1, 2, 2), (2,), (2, 2)]


def test_empty_and_singleton():
    assert _normalize(subsets_with_dup([])) == [()]
    assert _normalize(subsets_with_dup([0])) == [(), (0,)]


def test_distinct_values_give_all_two_to_the_n_subsets():
    result = _normalize(subsets_with_dup([3, 1, 2]))
    assert len(result) == 8 and result == _brute([1, 2, 3])


def test_all_equal_values():
    assert _normalize(subsets_with_dup([4, 4, 4])) == [(), (4,), (4, 4), (4, 4, 4)]


def test_unsorted_input_with_separated_duplicates():
    # Duplicate skipping that assumes sorted input misses that the 2s are equal here.
    assert _normalize(subsets_with_dup([2, 1, 2])) == [(), (1,), (1, 2), (1, 2, 2), (2,), (2, 2)]


def test_negative_values():
    assert _normalize(subsets_with_dup([-1, 0, -1])) == _brute([-1, 0, -1])


def test_returned_subsets_are_independent_lists():
    # Appending the shared path list instead of a copy makes every subset alias one list.
    result = subsets_with_dup([1, 2, 3])
    assert len({id(s) for s in result}) == len(result)
    assert _normalize(result) == _brute([1, 2, 3])


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(15)
    for _ in range(150):
        nums = [rng.randint(-2, 2) for _ in range(rng.randint(0, 8))]
        assert _normalize(subsets_with_dup(list(nums))) == _brute(nums), nums
