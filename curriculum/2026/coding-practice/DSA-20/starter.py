def grid_shortest_path(grid: list[list[int]]) -> int:
    """Return the fewest 4-directional moves from the top-left to the bottom-right cell.

    `0` is open, `1` is an obstacle. Moves go up/down/left/right through open cells only.
    Target O(rows * cols).

    Args:
        grid: Non-empty rectangular grid (need not be square).

    Returns:
        The number of moves on a shortest path (0 when start is the goal), or -1 if the
        goal is unreachable or either endpoint is blocked.
    """
    raise NotImplementedError("TODO: implement DSA-20")
