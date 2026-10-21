def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """Return unique combinations (with reuse) summing to target."""
    values = sorted(candidates)
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path.copy())
            return
        # Only consider indices >= start so each multiset is built in one order.
        for i in range(start, len(values)):
            if values[i] > remaining:
                break  # sorted, so every later candidate is too large as well
            path.append(values[i])
            backtrack(i, remaining - values[i])  # i, not i + 1: reuse is allowed
            path.pop()

    backtrack(0, target)
    return result
