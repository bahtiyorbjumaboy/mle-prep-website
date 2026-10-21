"""DSA-26 dynamic programming drill: solve each part in order in one sitting."""


def max_non_adjacent_sum(nums: list[int]) -> int:
    """Return the maximum sum of elements of `nums` with no two chosen elements adjacent.

    Choosing no elements is allowed (sum 0), so the result is never negative.
    Target O(n) time and O(1) extra space.

    Args:
        nums: Integers; values may be negative or zero.
    """
    raise NotImplementedError("TODO: implement DSA-26 max_non_adjacent_sum")


def unique_paths(rows: int, cols: int) -> int:
    """Return the number of top-left to bottom-right paths in a `rows x cols` grid.

    Each move goes one cell right or one cell down. Target O(rows * cols) time.

    Args:
        rows: Number of rows, at least 1.
        cols: Number of columns, at least 1.
    """
    raise NotImplementedError("TODO: implement DSA-26 unique_paths")


def unique_paths_with_obstacles(grid: list[list[int]]) -> int:
    """Return the number of right/down paths from top-left to bottom-right avoiding obstacles.

    `0` is open and `1` is an obstacle; a blocked start or goal gives 0.
    Target O(rows * cols) time.

    Args:
        grid: Non-empty rectangular grid.
    """
    raise NotImplementedError("TODO: implement DSA-26 unique_paths_with_obstacles")


def min_path_sum(grid: list[list[int]]) -> int:
    """Return the minimum sum of cell values on a right/down path from top-left to bottom-right.

    Both endpoint cells are included in the sum. Target O(rows * cols) time.

    Args:
        grid: Non-empty rectangular grid of nonnegative integers.
    """
    raise NotImplementedError("TODO: implement DSA-26 min_path_sum")


def edit_distance(source: str, target: str) -> int:
    """Return the minimum number of single-character inserts, deletes, and substitutions
    that turn `source` into `target`.

    Target O(len(source) * len(target)) time.
    """
    raise NotImplementedError("TODO: implement DSA-26 edit_distance")
