def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """Merge all overlapping closed intervals.

    Intervals are closed, so intervals that share an endpoint (e.g. `[1, 4]` and `[4, 5]`)
    overlap and must be merged. Target O(n log n).

    Args:
        intervals: `[start, end]` pairs with `start <= end`, in any order.

    Returns:
        Non-overlapping merged intervals sorted by start.
    """
    raise NotImplementedError("TODO: implement DSA-24")
