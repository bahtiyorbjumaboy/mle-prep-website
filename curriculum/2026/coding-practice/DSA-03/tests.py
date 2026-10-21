import math
import random

from solution import product_except_self


class NoDivInt(int):
    """Integer that refuses division, so division-based solutions fail loudly."""

    def _refuse(self, *args):
        raise AssertionError("division is not allowed in DSA-03")

    __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = __divmod__ = __rdivmod__ = _refuse
    __mod__ = __rmod__ = _refuse

    def __mul__(self, other):
        return NoDivInt(int(self) * int(other))

    __rmul__ = __mul__


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "product_except_self")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(nums):
    return [math.prod(nums[:i] + nums[i + 1:]) for i in range(len(nums))]


def test_hand_computed_example():
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]


def test_single_zero():
    assert product_except_self([1, 2, 0, 4]) == [0, 0, 8, 0]


def test_multiple_zeros():
    assert product_except_self([0, 4, 0]) == [0, 0, 0]


def test_negatives():
    assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
    assert product_except_self([-2, -3, 4]) == [-12, -8, 6]


def test_boundaries():
    assert product_except_self([5]) == [1]
    assert product_except_self([2, 3]) == [3, 2]


def test_input_is_not_mutated():
    nums = [3, 1, 2]
    product_except_self(nums)
    assert nums == [3, 1, 2]


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(3)
    for _ in range(200):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(1, 10))]
        assert product_except_self(list(nums)) == _brute(nums), nums


def test_does_not_use_division():
    nums = [NoDivInt(x) for x in [2, 3, 5, 7]]
    assert [int(x) for x in product_except_self(nums)] == [105, 70, 42, 30]
