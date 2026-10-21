import random

from solution import daily_temperatures


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
    target = getattr(solution, "daily_temperatures")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def _brute(temps):
    out = []
    for i, t in enumerate(temps):
        out.append(next((j - i for j in range(i + 1, len(temps)) if temps[j] > t), 0))
    return out


def test_hand_computed_example():
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]


def test_empty_and_singleton():
    assert daily_temperatures([]) == []
    assert daily_temperatures([50]) == [0]


def test_equal_temperatures_are_not_warmer():
    assert daily_temperatures([70, 70, 70]) == [0, 0, 0]
    assert daily_temperatures([70, 70, 71]) == [2, 1, 0]


def test_monotone_sequences():
    assert daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
    assert daily_temperatures([60, 50, 40, 30]) == [0, 0, 0, 0]


def test_answer_is_distance_not_index_or_value():
    assert daily_temperatures([55, 38, 53, 81, 61, 93, 97]) == [3, 1, 1, 2, 1, 1, 0]


def test_negative_temperatures():
    assert daily_temperatures([-5, -10, -3, -3, 0]) == [2, 1, 2, 1, 0]


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(12)
    for _ in range(300):
        temps = [rng.randint(-3, 3) for _ in range(rng.randint(0, 15))]
        assert daily_temperatures(list(temps)) == _brute(temps), temps


def test_linear_number_of_reads():
    n = 1000
    temps = CountingList(list(range(n, 0, -1)) + [n + 1])
    assert daily_temperatures(temps) == [n - i for i in range(n)] + [0]
    assert temps.reads <= 6 * len(temps), f"read {temps.reads} values for n={len(temps)}; expected O(n)"
