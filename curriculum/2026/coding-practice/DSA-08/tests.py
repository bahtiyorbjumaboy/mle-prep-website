import random

from solution import min_subarray_len


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
    target = getattr(solution, "min_subarray_len")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(target, nums):
    best = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total >= target:
                best = j - i + 1 if best == 0 else min(best, j - i + 1)
                break
    return best


def test_hand_computed_example():
    assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2


def test_no_subarray_reaches_target():
    assert min_subarray_len(100, [1, 2]) == 0
    assert min_subarray_len(5, []) == 0


def test_single_element_is_enough():
    assert min_subarray_len(4, [1, 4, 4]) == 1
    assert min_subarray_len(3, [3]) == 1


def test_threshold_is_inclusive():
    assert min_subarray_len(7, [3, 4]) == 2


def test_whole_array_needed():
    assert min_subarray_len(11, [1, 2, 3, 4, 1]) == 5


def test_window_must_shrink_repeatedly():
    # After adding 7 the window has to drop four elements, not just one.
    assert min_subarray_len(7, [1, 1, 1, 1, 7]) == 1
    assert min_subarray_len(15, [5, 1, 3, 5, 10, 7, 4, 9, 2, 8]) == 2


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(8)
    for _ in range(300):
        nums = [rng.randint(1, 9) for _ in range(rng.randint(0, 15))]
        target = rng.randint(1, 40)
        assert min_subarray_len(target, list(nums)) == _brute(target, nums), (target, nums)


def test_linear_number_of_reads():
    nums = CountingList([1] * 799 + [1000])
    assert min_subarray_len(1000, nums) == 1
    assert nums.reads <= 4 * len(nums), f"read {nums.reads} values for n={len(nums)}; expected O(n)"
