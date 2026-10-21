def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """Merge overlapping closed intervals with sort + sweep."""
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            # Closed intervals: touching endpoints overlap; keep the farther end.
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
