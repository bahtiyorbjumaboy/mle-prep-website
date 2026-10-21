import random

from solution import reverse_between, reverse_list


class Node:
    __slots__ = ("val", "next")

    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def _build(values):
    head = None
    for value in reversed(values):
        head = Node(value, head)
    return head


def _nodes(head, limit=10_000):
    out = []
    while head is not None:
        out.append(head)
        assert len(out) <= limit, "result contains a cycle"
        head = head.next
    return out


def _values(head):
    return [node.val for node in _nodes(head)]


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("reverse_list", "reverse_between"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name



def test_reverse_list_hand_computed():
    assert _values(reverse_list(_build([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]


def test_reverse_list_empty_single_and_pair():
    assert reverse_list(None) is None
    assert _values(reverse_list(_build([1]))) == [1]
    assert _values(reverse_list(_build([1, 2]))) == [2, 1]


def test_reverse_list_rewires_existing_nodes():
    head = _build(list(range(6)))
    original = _nodes(head)
    result = _nodes(reverse_list(head))
    assert [id(n) for n in result] == [id(n) for n in reversed(original)]
    assert original[0].next is None, "the old head must become the tail"


def test_reverse_list_long_list_is_iterative():
    # A recursive reversal overflows the default recursion limit here.
    assert _values(reverse_list(_build(list(range(5000)))))[:3] == [4999, 4998, 4997]


def test_reverse_between_hand_computed():
    assert _values(reverse_between(_build([1, 2, 3, 4, 5]), 2, 4)) == [1, 4, 3, 2, 5]


def test_reverse_between_single_node_and_noop_range():
    assert _values(reverse_between(_build([5]), 1, 1)) == [5]
    assert _values(reverse_between(_build([1, 2, 3]), 2, 2)) == [1, 2, 3]


def test_reverse_between_from_head_changes_head():
    assert _values(reverse_between(_build([1, 2, 3, 4]), 1, 3)) == [3, 2, 1, 4]
    assert _values(reverse_between(_build([1, 2]), 1, 2)) == [2, 1]


def test_reverse_between_through_tail():
    assert _values(reverse_between(_build([1, 2, 3, 4]), 3, 4)) == [1, 2, 4, 3]
    assert _values(reverse_between(_build([1, 2, 3, 4]), 1, 4)) == [4, 3, 2, 1]


def test_reverse_between_rewires_existing_nodes():
    head = _build(list(range(8)))
    original = _nodes(head)
    result = _nodes(reverse_between(head, 3, 6))
    expected = original[:2] + original[2:6][::-1] + original[6:]
    assert [id(n) for n in result] == [id(n) for n in expected]


def test_reverse_between_matches_slicing_on_random_ranges():
    rng = random.Random(14)
    for _ in range(300):
        values = [rng.randint(0, 9) for _ in range(rng.randint(1, 12))]
        left = rng.randint(1, len(values))
        right = rng.randint(left, len(values))
        expected = values[:left - 1] + values[left - 1:right][::-1] + values[right:]
        assert _values(reverse_between(_build(values), left, right)) == expected, (values, left, right)
