def reverse_list(head):
    """Reverse a singly linked list in place and return the new head."""
    previous = None
    current = head
    while current is not None:
        current.next, previous, current = previous, current, current.next
    return previous


class _Dummy:
    def __init__(self, next_node):
        self.next = next_node


def reverse_between(head, left: int, right: int):
    """Reverse positions left..right (1-indexed, inclusive) in one pass."""
    dummy = _Dummy(head)  # removes the special case for left == 1
    before = dummy
    for _ in range(left - 1):
        before = before.next
    # Head insertion: repeatedly move the node after `tail` to the front of the sublist.
    tail = before.next
    for _ in range(right - left):
        moved = tail.next
        tail.next = moved.next
        moved.next = before.next
        before.next = moved
    return dummy.next
