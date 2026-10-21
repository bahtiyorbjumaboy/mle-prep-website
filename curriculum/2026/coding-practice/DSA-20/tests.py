import random

from solution import grid_shortest_path


def _parse(*rows):
    return [[1 if ch == "#" else 0 for ch in row] for row in rows]


def _bellman(grid):
    rows, cols = len(grid), len(grid[0])
    if grid[0][0] or grid[-1][-1]:
        return -1
    inf = float("inf")
    dist = [[inf] * cols for _ in range(rows)]
    dist[0][0] = 0
    changed = True
    while changed:
        changed = False
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] or dist[r][c] == inf:
                    continue
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and not grid[nr][nc] and dist[r][c] + 1 < dist[nr][nc]:
                        dist[nr][nc] = dist[r][c] + 1
                        changed = True
    return -1 if dist[-1][-1] == inf else dist[-1][-1]


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "grid_shortest_path")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert grid_shortest_path([[0, 0], [1, 0]]) == 2
    assert grid_shortest_path(_parse("...", "##.", "...")) == 4


def test_single_cell():
    assert grid_shortest_path([[0]]) == 0
    assert grid_shortest_path([[1]]) == -1


def test_blocked_endpoints():
    assert grid_shortest_path(_parse("#.", "..")) == -1
    assert grid_shortest_path(_parse("..", ".#")) == -1


def test_unreachable_goal():
    assert grid_shortest_path(_parse("..#", ".#.", "#..")) == -1


def test_diagonal_moves_are_not_allowed():
    assert grid_shortest_path(_parse(".#", "#.")) == -1


def test_detour_around_walls():
    grid = _parse(
        ".#...",
        ".#.#.",
        ".#.#.",
        "...#.",
    )
    assert grid_shortest_path(grid) == 13


def test_shortest_not_first_found_path():
    # Depth-first search tends to wander along the long corridor first.
    grid = _parse(
        "......",
        ".####.",
        "......",
    )
    assert grid_shortest_path(grid) == 7


def test_non_square_grids():
    assert grid_shortest_path([[0, 0, 0, 0, 0]]) == 4
    assert grid_shortest_path([[0], [0], [0]]) == 2


def test_open_grid():
    assert grid_shortest_path([[0] * 40 for _ in range(30)]) == 68


def test_matches_relaxation_on_random_grids():
    rng = random.Random(20)
    for _ in range(200):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        grid = [[1 if rng.random() < 0.3 else 0 for _ in range(cols)] for _ in range(rows)]
        assert grid_shortest_path([row[:] for row in grid]) == _bellman(grid), grid
