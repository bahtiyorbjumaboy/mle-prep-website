import functools
import itertools
import math
import random

from solution import edit_distance, max_non_adjacent_sum, min_path_sum, unique_paths, unique_paths_with_obstacles

FUNCTIONS = ("max_non_adjacent_sum", "unique_paths", "unique_paths_with_obstacles", "min_path_sum", "edit_distance")


def _brute_non_adjacent(nums):
    best = 0
    for mask in range(1 << len(nums)):
        if mask & (mask >> 1) == 0:
            best = max(best, sum(x for i, x in enumerate(nums) if mask >> i & 1))
    return best


def _paths(grid, obstacles=True):
    rows, cols = len(grid), len(grid[0])
    out = []

    def walk(r, c, path):
        if r >= rows or c >= cols or (obstacles and grid[r][c] == 1):
            return
        path = path + [grid[r][c]]
        if (r, c) == (rows - 1, cols - 1):
            out.append(path)
            return
        walk(r + 1, c, path)
        walk(r, c + 1, path)

    walk(0, 0, [])
    return out


def _brute_edit(a, b):
    @functools.lru_cache(maxsize=None)
    def go(i, j):
        if i == len(a) or j == len(b):
            return len(a) - i + len(b) - j
        if a[i] == b[j]:
            return go(i + 1, j + 1)
        return 1 + min(go(i + 1, j), go(i, j + 1), go(i + 1, j + 1))

    return go(0, 0)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in FUNCTIONS:
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_non_adjacent_hand_computed():
    assert max_non_adjacent_sum([2, 7, 9, 3, 1]) == 12
    assert max_non_adjacent_sum([5, 1, 1, 5]) == 10


def test_non_adjacent_base_cases():
    assert max_non_adjacent_sum([]) == 0
    assert max_non_adjacent_sum([4]) == 4
    # dp[1] must be max(nums[0], nums[1]), not nums[1].
    assert max_non_adjacent_sum([9, 2]) == 9


def test_non_adjacent_negatives_and_zeros():
    assert max_non_adjacent_sum([-1, -2, -3]) == 0
    assert max_non_adjacent_sum([-5, 4, -1, 0, 6]) == 10


def test_non_adjacent_matches_brute_force():
    rng = random.Random(26)
    for _ in range(300):
        nums = [rng.randint(-5, 9) for _ in range(rng.randint(0, 12))]
        assert max_non_adjacent_sum(list(nums)) == _brute_non_adjacent(nums), nums


def test_unique_paths():
    assert unique_paths(3, 7) == 28
    assert unique_paths(1, 1) == 1
    assert unique_paths(1, 9) == 1 and unique_paths(9, 1) == 1
    assert unique_paths(3, 2) == 3
    for rows, cols in itertools.product(range(1, 9), repeat=2):
        assert unique_paths(rows, cols) == math.comb(rows + cols - 2, rows - 1), (rows, cols)


def test_obstacles_hand_computed():
    assert unique_paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2


def test_obstacles_block_the_rest_of_first_row_and_column():
    # Initializing the whole first row/column to 1 ignores obstacles on it.
    assert unique_paths_with_obstacles([[0, 1, 0], [0, 0, 0]]) == 1
    assert unique_paths_with_obstacles([[0, 0], [1, 0], [0, 0]]) == 1
    assert unique_paths_with_obstacles([[0, 1, 0, 0]]) == 0


def test_obstacles_on_endpoints():
    assert unique_paths_with_obstacles([[1]]) == 0
    assert unique_paths_with_obstacles([[0]]) == 1
    assert unique_paths_with_obstacles([[1, 0], [0, 0]]) == 0
    assert unique_paths_with_obstacles([[0, 0], [0, 1]]) == 0


def test_obstacles_match_enumeration():
    rng = random.Random(260)
    for _ in range(200):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[1 if rng.random() < 0.25 else 0 for _ in range(cols)] for _ in range(rows)]
        assert unique_paths_with_obstacles([r[:] for r in grid]) == len(_paths(grid)), grid


def test_min_path_sum():
    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert min_path_sum([[5]]) == 5
    assert min_path_sum([[1, 2, 3]]) == 6
    assert min_path_sum([[1], [2], [3]]) == 6
    assert min_path_sum([[0, 0], [0, 0]]) == 0


def test_min_path_sum_matches_enumeration():
    rng = random.Random(261)
    for _ in range(200):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[rng.randint(0, 9) for _ in range(cols)] for _ in range(rows)]
        assert min_path_sum([r[:] for r in grid]) == min(sum(p) for p in _paths(grid, obstacles=False)), grid


def test_edit_distance_hand_computed():
    assert edit_distance("horse", "ros") == 3
    assert edit_distance("intention", "execution") == 5


def test_edit_distance_base_cases():
    assert edit_distance("", "") == 0
    assert edit_distance("", "abc") == 3
    assert edit_distance("abc", "") == 3
    assert edit_distance("same", "same") == 0


def test_edit_distance_is_symmetric_and_matches_recursion():
    rng = random.Random(262)
    for _ in range(200):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        expected = _brute_edit(a, b)
        assert edit_distance(a, b) == expected == edit_distance(b, a), (a, b)


def test_larger_inputs_are_polynomial():
    assert max_non_adjacent_sum([1] * 5000) == 2500
    assert unique_paths(17, 17) == math.comb(32, 16)
    assert min_path_sum([[1] * 200 for _ in range(200)]) == 399
    assert edit_distance("a" * 300, "b" * 300) == 300
