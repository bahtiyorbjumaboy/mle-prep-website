def max_non_adjacent_sum(nums: list[int]) -> int:
    """Return the best sum of non-adjacent elements (empty choice allowed)."""
    take, skip = 0, 0  # best sums ending with the current element taken / not taken
    for value in nums:
        take, skip = skip + value, max(take, skip)
    return max(take, skip)


def unique_paths(rows: int, cols: int) -> int:
    """Count right/down paths with a rolling row."""
    row = [1] * cols
    for _ in range(1, rows):
        for c in range(1, cols):
            row[c] += row[c - 1]
    return row[-1]


def unique_paths_with_obstacles(grid: list[list[int]]) -> int:
    """Count right/down paths avoiding obstacles with a rolling row."""
    cols = len(grid[0])
    row = [0] * cols
    row[0] = 1
    for cells in grid:
        for c in range(cols):
            if cells[c] == 1:
                row[c] = 0
            elif c > 0:
                row[c] += row[c - 1]
    return row[-1]


def min_path_sum(grid: list[list[int]]) -> int:
    """Return the minimum right/down path sum with a rolling row."""
    inf = float("inf")
    row = [inf] * len(grid[0])
    row[0] = 0
    for cells in grid:
        for c, value in enumerate(cells):
            best_prev = row[c] if c == 0 else min(row[c], row[c - 1])
            row[c] = best_prev + value
    return row[-1]


def edit_distance(source: str, target: str) -> int:
    """Return Levenshtein distance using two rolling rows."""
    previous = list(range(len(target) + 1))  # distance from "" to each target prefix
    for i, s_char in enumerate(source, start=1):
        current = [i] + [0] * len(target)
        for j, t_char in enumerate(target, start=1):
            if s_char == t_char:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(previous[j], current[j - 1], previous[j - 1])
        previous = current
    return previous[-1]
