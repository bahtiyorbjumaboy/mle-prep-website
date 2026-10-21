def longest_consecutive(nums: list[int]) -> int:
    """Return the longest run of consecutive values in O(n) expected time."""
    values = set(nums)
    best = 0
    for value in values:
        # Only expand from run heads so every run is walked once.
        if value - 1 in values:
            continue
        length = 1
        while value + length in values:
            length += 1
        best = max(best, length)
    return best
