def reverse_list(head):
    """Reverse an entire singly linked list iteratively and return the new head.

    Nodes expose `.val` and `.next`. Rewire the existing nodes in place; O(1) extra space.

    Args:
        head: First node, or `None` for an empty list.

    Returns:
        The new head (`None` for an empty list).
    """
    raise NotImplementedError("TODO: implement DSA-14 reverse_list")


def reverse_between(head, left: int, right: int):
    """Reverse only the nodes at 1-indexed positions `left` through `right` inclusive.

    Rewire the existing nodes in place in one pass; O(1) extra space.

    Args:
        head: First node of a non-empty list.
        left: 1-indexed start position, `1 <= left`.
        right: 1-indexed end position, `left <= right <= length`.

    Returns:
        The head of the resulting list (which changes when `left == 1`).
    """
    raise NotImplementedError("TODO: implement DSA-14 reverse_between")
