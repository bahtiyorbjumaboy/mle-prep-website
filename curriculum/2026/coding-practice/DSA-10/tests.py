import functools
import random

from solution import split_array


def _brute(nums, k):
    @functools.lru_cache(maxsize=None)
    def best(start, parts):
        if parts == 1:
            return sum(nums[start:])
        return min(
            max(sum(nums[start:end]), best(end, parts - 1))
            for end in range(start + 1, len(nums) - parts + 2)
        )

    return best(0, k)


def _raises_value_error(nums, k):
    try:
        split_array(nums, k)
    except ValueError:
        return True
    return False


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "split_array")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    # [7, 2, 5] | [10, 8] -> max(14, 18) = 18.
    assert split_array([7, 2, 5, 10, 8], 2) == 18
    assert split_array([1, 2, 3, 4, 5], 2) == 9


def test_k_equals_one_and_n():
    nums = [4, 1, 7, 3]
    assert split_array(nums, 1) == 15
    assert split_array(nums, 4) == 7


def test_singleton_and_zeros():
    assert split_array([5], 1) == 5
    assert split_array([0, 0, 0], 3) == 0
    assert split_array([0, 0, 9, 0], 2) == 9


def test_infeasible_k_raises():
    assert _raises_value_error([1, 2, 3], 4)
    assert _raises_value_error([1, 2, 3], 0)
    assert _raises_value_error([], 1)


def test_lower_bound_is_the_largest_element():
    # Starting the search below max(nums) and greedily packing can "fit" a too-large element.
    assert split_array([1, 1, 1, 10, 1, 1], 3) == 10
    assert split_array([10, 1, 1, 1], 4) == 10


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(10)
    for _ in range(200):
        nums = [rng.randint(0, 12) for _ in range(rng.randint(1, 8))]
        k = rng.randint(1, len(nums))
        assert split_array(list(nums), k) == _brute(tuple(nums), k), (nums, k)


def test_answer_is_monotone_in_k():
    rng = random.Random(100)
    nums = [rng.randint(0, 50) for _ in range(12)]
    answers = [split_array(list(nums), k) for k in range(1, len(nums) + 1)]
    assert answers[0] == sum(nums) and answers[-1] == max(nums)
    assert all(a >= b for a, b in zip(answers, answers[1:])), answers


def test_large_values_need_binary_search_not_a_linear_scan():
    nums = [10**12, 3, 10**12 - 1, 10**11, 5, 10**12]
    assert split_array(nums, 3) == _brute(tuple(nums), 3)
