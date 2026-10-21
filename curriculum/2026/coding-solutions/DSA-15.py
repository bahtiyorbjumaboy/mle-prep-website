def subsets_with_dup(nums: list[int]) -> list[list[int]]:
    """Return distinct subsets via backtracking over sorted values."""
    values = sorted(nums)
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int) -> None:
        result.append(path.copy())
        for i in range(start, len(values)):
            # At one depth, choosing an equal value twice would repeat a subset.
            if i > start and values[i] == values[i - 1]:
                continue
            path.append(values[i])
            backtrack(i + 1)
            path.pop()

    backtrack(0)
    return result
