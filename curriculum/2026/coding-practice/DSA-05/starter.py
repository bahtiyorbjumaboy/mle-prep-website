def max_container_area(heights: list[int]) -> int:
    """Return the maximum area of water held between two of the given vertical lines.

    The area for indices `i < j` is `(j - i) * min(heights[i], heights[j])`.
    Target O(n) time and O(1) extra space.

    Args:
        heights: Non-negative line heights; at least two lines.

    Returns:
        The maximum area over all pairs of indices.
    """
    raise NotImplementedError("TODO: implement DSA-05")
