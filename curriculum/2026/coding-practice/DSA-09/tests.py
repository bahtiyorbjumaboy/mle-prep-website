import random

from solution import search_range


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
    target = getattr(solution, "search_range")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(nums, target):
    hits = [i for i, x in enumerate(nums) if x == target]
    return [hits[0], hits[-1]] if hits else [-1, -1]


def test_hand_computed_example():
    assert search_range([5, 7, 7, 8, 8, 10], 8) == [3, 4]


def test_missing_target_inside_and_outside_range():
    assert search_range([5, 7, 7, 8, 8, 10], 6) == [-1, -1]
    assert search_range([5, 7, 7, 8, 8, 10], 4) == [-1, -1]
    assert search_range([5, 7, 7, 8, 8, 10], 11) == [-1, -1]


def test_empty_and_singleton():
    assert search_range([], 1) == [-1, -1]
    assert search_range([1], 1) == [0, 0]
    assert search_range([1], 2) == [-1, -1]


def test_all_equal():
    assert search_range([2, 2, 2, 2, 2], 2) == [0, 4]


def test_target_at_both_boundaries():
    assert search_range([1, 1, 2, 3, 3], 1) == [0, 1]
    assert search_range([1, 1, 2, 3, 3], 3) == [3, 4]
    assert search_range([-3, -3, 0, 5], -3) == [0, 1]


def test_matches_linear_scan_on_random_inputs():
    rng = random.Random(9)
    for _ in range(300):
        nums = sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 20)))
        target = rng.randint(-6, 6)
        assert search_range(list(nums), target) == _brute(nums, target), (nums, target)


def test_logarithmic_reads_on_long_run_of_duplicates():
    # Finding one match and then walking outwards is O(n) on a long run.
    n = 100_000
    nums = CountingList([0] * 10 + [7] * (n - 20) + [9] * 10)
    assert search_range(nums, 7) == [10, n - 11]
    assert nums.reads <= 120, f"read {nums.reads} elements for n={n}; expected O(log n)"


def test_does_not_use_bisect():
    import inspect
    import solution
    source = inspect.getsource(solution)
    assert "import bisect" not in source and "from bisect" not in source, "implement the bounds yourself"
