def max_container_area(heights: list[int]) -> int:
    """Return the best container area using converging pointers."""
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        left_height, right_height = heights[left], heights[right]
        best = max(best, (right - left) * min(left_height, right_height))
        # The shorter side cannot do better with any narrower partner, so drop it.
        if left_height < right_height:
            left += 1
        else:
            right -= 1
    return best
