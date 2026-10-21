import random

from solution import two_sum


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


def _check(nums, target, expected):
    result = two_sum(list(nums), target)
    assert len(result) == 2, f"expected two indices, got {result!r}"
    assert sorted(result) == sorted(expected), f"two_sum({nums}, {target}) -> {result!r}, expected {expected}"


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "two_sum")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    _check([2, 7, 11, 15], 9, [0, 1])


def test_duplicate_values_form_the_pair():
    _check([3, 3], 6, [0, 1])
    _check([1, 5, 2, 5], 10, [1, 3])


def test_does_not_reuse_the_same_index():
    # Insert-before-check would return [0, 0] here (3 + 3 == 6 using one element).
    _check([3, 2, 4], 6, [1, 2])
    _check([5, 1, 8, 5], 10, [0, 3])


def test_negatives_and_zeros():
    _check([-3, 4, 3, 90], 0, [0, 2])
    _check([0, 4, 3, 0], 0, [0, 3])
    _check([-1, -2, -3, -4, -5], -8, [2, 4])


def test_pair_at_the_end_of_the_array():
    nums = list(range(10, 1000, 7)) + [1, 2]
    _check(nums, 3, [len(nums) - 2, len(nums) - 1])


def test_result_is_valid_on_random_inputs():
    rng = random.Random(1)
    for _ in range(200):
        nums = [rng.randint(-50, 50) for _ in range(rng.randint(2, 30))]
        i, j = rng.sample(range(len(nums)), 2)
        target = nums[i] + nums[j]
        a, b = two_sum(list(nums), target)
        assert a != b and nums[a] + nums[b] == target, (nums, target, (a, b))


def test_one_pass_stops_once_pair_is_seen():
    # The pair is the first two elements; a single pass with check-before-insert needs
    # only a handful of reads, while building a full lookup table first reads everything.
    nums = CountingList([5, 10] + list(range(1000, 3000)))
    assert sorted(two_sum(nums, 15)) == [0, 1]
    assert nums.reads <= 10, f"read {nums.reads} elements; expected a single early-exit pass"


def test_linear_number_of_reads():
    n = 2000
    nums = CountingList(list(range(10, 10 + n - 2)) + [-1, -2])
    assert sorted(two_sum(nums, -3)) == [n - 2, n - 1]
    assert nums.reads <= 3 * n, f"read {nums.reads} elements for n={n}; nested scans are O(n^2)"
