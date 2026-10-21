def min_subarray_len(target: int, nums: list[int]) -> int:
    """Return the shortest window with sum >= target (positive inputs only)."""
    best = 0
    left = 0
    window = 0
    for right, value in enumerate(nums):
        window += value
        # Positivity makes shrinking monotone: removing from the left only lowers the sum.
        while window >= target:
            length = right - left + 1
            best = length if best == 0 else min(best, length)
            window -= nums[left]
            left += 1
    return best
