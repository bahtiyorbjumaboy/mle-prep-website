import random

from solution import subarray_sum_count


class CountingList(list):
    """List that counts element reads so access patterns can be checked structurally."""

    def __init__(self, values):
        super().__init__(values)
        self.reads = 0

    def __getitem__(self, index):
        value = super().__getitem__(index)
        self.reads += len(value) if isinstance(index, slice) else 1
        return value

    def __iter__(self):
        for value in super().__iter__():
            self.reads += 1
            yield value


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "subarray_sum_count")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(nums, k):
    return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) == k)


def test_hand_computed_example():
    assert subarray_sum_count([1, 1, 1], 2) == 2
    assert subarray_sum_count([1, 2, 3], 3) == 2


def test_empty_and_singleton():
    assert subarray_sum_count([], 0) == 0
    assert subarray_sum_count([5], 5) == 1
    assert subarray_sum_count([5], 0) == 0


def test_prefix_from_index_zero_is_counted():
    # Forgetting the {0: 1} seed misses subarrays that start at index 0.
    assert subarray_sum_count([3, 4, 7], 7) == 2


def test_zero_target_counts_before_inserting_current_prefix():
    # Inserting the current prefix before counting would match the empty subarray.
    assert subarray_sum_count([5], 0) == 0
    assert subarray_sum_count([1, -1, 0], 0) == 3


def test_zeros_produce_many_subarrays():
    assert subarray_sum_count([0, 0, 0], 0) == 6


def test_negative_values_break_sliding_window():
    assert subarray_sum_count([1, -1, 1, -1], 0) == 4
    assert subarray_sum_count([3, -2, 2, -3, 3], 3) == 4
    assert subarray_sum_count([-1, -1, 1], -1) == 3


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(25)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 15))]
        k = rng.randint(-4, 4)
        assert subarray_sum_count(list(nums), k) == _brute(nums, k), (nums, k)


def test_linear_number_of_reads():
    nums = CountingList([1, -1] * 1000)
    assert subarray_sum_count(nums, 0) == 1_000_000
    assert nums.reads <= 3 * len(nums), f"read {nums.reads} values for n={len(nums)}; expected O(n)"
