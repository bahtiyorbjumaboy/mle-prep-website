import random

from solution import num_islands


def _grid(*rows):
    return [list(row) for row in rows]


def _brute(grid):
    cells = {(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == "1"}
    parent = {cell: cell for cell in cells}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for r, c in cells:
        for nb in ((r + 1, c), (r, c + 1)):
            if nb in cells:
                parent[find((r, c))] = find(nb)
    return len({find(cell) for cell in cells})


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "num_islands")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    grid = _grid("11000", "11000", "00100", "00011")
    assert num_islands(grid) == 3


def test_empty_grids():
    assert num_islands([]) == 0
    assert num_islands([[]]) == 0


def test_single_cell():
    assert num_islands([["1"]]) == 1
    assert num_islands([["0"]]) == 0


def test_diagonal_cells_are_separate_islands():
    assert num_islands(_grid("101", "010", "101")) == 5


def test_u_shaped_island_is_one_component():
    # A row-by-row scan that only looks up/left counts the two arms separately.
    assert num_islands(_grid("10101", "10101", "11111")) == 1
    assert num_islands(_grid("11111", "00001", "11101", "10001", "11111")) == 1


def test_non_square_grids_respect_bounds():
    assert num_islands([list("1011011")]) == 3
    assert num_islands([["1"], ["1"], ["0"], ["1"]]) == 2
    assert num_islands(_grid("110", "001", "011", "100", "101")) == 4


def test_all_land_and_all_water():
    assert num_islands([["1"] * 20 for _ in range(20)]) == 1
    assert num_islands([["0"] * 20 for _ in range(20)]) == 0


def test_matches_union_find_on_random_grids():
    rng = random.Random(19)
    for _ in range(200):
        rows, cols = rng.randint(1, 8), rng.randint(1, 8)
        grid = [[rng.choice("01") for _ in range(cols)] for _ in range(rows)]
        expected = _brute(grid)
        assert num_islands([row[:] for row in grid]) == expected, grid
