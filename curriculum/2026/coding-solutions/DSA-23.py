import heapq
from collections import Counter


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """Return k most frequent values using a size-k min-heap keyed by frequency."""
    heap: list[tuple[int, int]] = []
    for value, count in Counter(nums).items():
        if len(heap) < k:
            heapq.heappush(heap, (count, value))
        elif count > heap[0][0]:
            # The heap root is the least frequent of the current top k.
            heapq.heapreplace(heap, (count, value))
    return [value for _, value in heap]
