def split_array(nums: list[int], k: int) -> int:
    """Return the minimized largest part sum via binary search on the answer."""
    if k < 1 or k > len(nums):
        raise ValueError(f"cannot split {len(nums)} values into {k} nonempty parts")

    def parts_needed(cap: int) -> int:
        # Greedy packing gives the fewest parts with every part sum <= cap.
        parts, current = 1, 0
        for value in nums:
            if current + value > cap:
                parts += 1
                current = 0
            current += value
        return parts

    # Feasibility (parts_needed(cap) <= k) is monotone in cap; find the smallest feasible cap.
    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if parts_needed(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
