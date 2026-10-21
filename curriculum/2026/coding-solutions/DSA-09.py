def _lower_bound(nums: list[int], target: int) -> int:
    """Return the first index whose value is >= target (half-open search on [lo, hi))."""
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def search_range(nums: list[int], target: int) -> list[int]:
    """Return [first, last] index of target in sorted nums, or [-1, -1]."""
    first = _lower_bound(nums, target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    # The last match sits just before the first value > target.
    return [first, _lower_bound(nums, target + 1) - 1]
