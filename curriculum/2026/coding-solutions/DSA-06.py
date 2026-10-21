def three_sum(nums: list[int]) -> list[list[int]]:
    """Return unique zero-sum triplets using sort + two pointers."""
    values = sorted(nums)
    result: list[list[int]] = []
    for i in range(len(values) - 2):
        if i > 0 and values[i] == values[i - 1]:
            continue
        if values[i] > 0:
            break
        left, right = i + 1, len(values) - 1
        while left < right:
            total = values[i] + values[left] + values[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([values[i], values[left], values[right]])
                left += 1
                right -= 1
                # Skip equal values so each triplet is emitted once.
                while left < right and values[left] == values[left - 1]:
                    left += 1
    return result
