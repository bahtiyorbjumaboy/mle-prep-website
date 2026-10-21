import random

from solution import max_container_area


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
    target = getattr(solution, "max_container_area")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(heights):
    return max((j - i) * min(heights[i], heights[j]) for i in range(len(heights)) for j in range(i + 1, len(heights)))


def test_hand_computed_example():
    assert max_container_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49


def test_two_lines():
    assert max_container_area([1, 1]) == 1
    assert max_container_area([0, 5]) == 0


def test_area_uses_the_shorter_line():
    assert max_container_area([1, 100]) == 1


def test_moving_the_taller_line_misses_the_optimum():
    # Optimal pair is (1, 3) with area 4; moving the taller side first skips it.
    assert max_container_area([1, 2, 4, 3]) == 4
    assert max_container_area([2, 3, 10, 5, 7, 8, 9]) == 36


def test_equal_heights_and_plateaus():
    assert max_container_area([4, 4, 4, 4]) == 12
    assert max_container_area([1, 3, 2, 5, 25, 24, 5]) == 24


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(5)
    for _ in range(200):
        heights = [rng.randint(0, 12) for _ in range(rng.randint(2, 15))]
        assert max_container_area(list(heights)) == _brute(heights), heights


def test_linear_number_of_reads():
    rng = random.Random(55)
    heights = CountingList([rng.randint(0, 1000) for _ in range(600)])
    assert max_container_area(heights) == _brute(list(heights))
    heights.reads = 0
    max_container_area(heights)
    assert heights.reads <= 6 * len(heights), f"read {heights.reads} values for n={len(heights)}; expected O(n)"
