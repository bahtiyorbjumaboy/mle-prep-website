import random

from solution import longest_consecutive


class CountingInt(int):
    """Integer that counts hash computations, i.e. set/dict lookups and inserts."""

    hashes = 0

    def __hash__(self):
        CountingInt.hashes += 1
        return int.__hash__(self)

    def __add__(self, other):
        return CountingInt(int(self) + int(other))

    __radd__ = __add__

    def __sub__(self, other):
        return CountingInt(int(self) - int(other))

    def __rsub__(self, other):
        return CountingInt(int(other) - int(self))


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "longest_consecutive")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(nums):
    values = set(nums)
    best = 0
    for value in values:
        length = 0
        while value + length in values:
            length += 1
        best = max(best, length)
    return best


def test_hand_computed_example():
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4


def test_empty_and_singleton():
    assert longest_consecutive([]) == 0
    assert longest_consecutive([7]) == 1


def test_duplicates_do_not_break_or_extend_runs():
    assert longest_consecutive([1, 2, 2, 3]) == 3
    assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longest_consecutive([5, 5, 5]) == 1


def test_negative_values_and_crossing_zero():
    assert longest_consecutive([-1, 1, 0, -2, 5]) == 4


def test_separated_runs_choose_the_longest():
    assert longest_consecutive([10, 11, 12, 1, 2, 30, 31, 32, 33]) == 4


def test_input_is_not_mutated():
    nums = [3, 1, 2]
    longest_consecutive(nums)
    assert nums == [3, 1, 2]


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(4)
    for _ in range(200):
        nums = [rng.randint(-15, 15) for _ in range(rng.randint(0, 25))]
        assert longest_consecutive(list(nums)) == _brute(nums), nums


def test_linear_number_of_set_lookups():
    # Expanding a run from every value instead of only from run heads is O(n^2).
    n = 2000
    nums = [CountingInt(x) for x in range(n, 0, -1)]
    CountingInt.hashes = 0
    assert longest_consecutive(nums) == n
    assert CountingInt.hashes <= 8 * n, f"{CountingInt.hashes} hash lookups for n={n}; expected O(n)"
