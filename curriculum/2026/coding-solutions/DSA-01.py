def two_sum(nums: list[int], target: int) -> list[int]:
    """Return the indices of the unique pair whose values sum to target."""
    seen: dict[int, int] = {}
    for index, value in enumerate(nums):
        complement = target - value
        # Check before inserting so an element is never paired with itself.
        if complement in seen:
            return [seen[complement], index]
        seen[value] = index
    raise ValueError("no valid pair")
