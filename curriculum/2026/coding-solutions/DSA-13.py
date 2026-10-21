def detect_cycle(head):
    """Return the cycle entry node using Floyd's tortoise and hare, or None."""
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            # Head and meeting point are equally far from the entry (mod cycle length).
            finder = head
            while finder is not slow:
                finder = finder.next
                slow = slow.next
            return finder
    return None
