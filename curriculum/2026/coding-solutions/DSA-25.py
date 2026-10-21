from collections import defaultdict


def subarray_sum_count(nums: list[int], k: int) -> int:
    """Count subarrays summing to k with prefix sums and a frequency map."""
    prefix_counts: defaultdict[int, int] = defaultdict(int)
    prefix_counts[0] = 1  # the empty prefix, so subarrays starting at index 0 count
    prefix = 0
    count = 0
    for value in nums:
        prefix += value
        # Count earlier prefixes before recording this one so empty subarrays never match.
        count += prefix_counts[prefix - k]
        prefix_counts[prefix] += 1
    return count
