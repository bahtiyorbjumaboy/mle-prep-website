from solution import detect_cycle


class Node:
    __slots__ = ("val", "next")

    def __init__(self, val):
        self.val = val
        self.next = None


class UnhashableNode(Node):
    """Node that cannot be stored in a set or dict, enforcing O(1) extra space."""

    __slots__ = ()
    __hash__ = None


def _build(values, cycle_at=None, node_type=Node):
    nodes = [node_type(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if cycle_at is not None:
        nodes[-1].next = nodes[cycle_at]
    return (nodes[0] if nodes else None), nodes


def _snapshot(nodes):
    return [(n.val, n.next) for n in nodes]


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "detect_cycle")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_cycle_entry():
    head, nodes = _build([3, 2, 0, -4], cycle_at=1)
    assert detect_cycle(head) is nodes[1]


def test_empty_and_single_node():
    assert detect_cycle(None) is None
    head, _ = _build([1])
    assert detect_cycle(head) is None


def test_single_node_self_loop():
    head, nodes = _build([1], cycle_at=0)
    assert detect_cycle(head) is nodes[0]


def test_two_node_cycles():
    head, nodes = _build([1, 2], cycle_at=0)
    assert detect_cycle(head) is nodes[0]
    head, nodes = _build([1, 2], cycle_at=1)
    assert detect_cycle(head) is nodes[1]


def test_acyclic_lists_of_various_lengths():
    for n in range(2, 8):
        head, _ = _build(list(range(n)))
        assert detect_cycle(head) is None, n


def test_entry_is_identified_by_identity_not_value():
    # Duplicate values: returning the first node with a matching value is wrong.
    head, nodes = _build([7, 7, 7, 7, 7], cycle_at=3)
    assert detect_cycle(head) is nodes[3]


def test_every_entry_position_and_tail_length():
    for n in range(1, 12):
        for entry in range(n):
            head, nodes = _build(list(range(n)), cycle_at=entry)
            assert detect_cycle(head) is nodes[entry], (n, entry)


def test_list_is_not_modified():
    head, nodes = _build(list(range(9)), cycle_at=4)
    before = _snapshot(nodes)
    detect_cycle(head)
    assert _snapshot(nodes) == before


def test_constant_extra_space():
    head, nodes = _build(list(range(50)), cycle_at=17, node_type=UnhashableNode)
    assert detect_cycle(head) is nodes[17]
    head, _ = _build(list(range(50)), node_type=UnhashableNode)
    assert detect_cycle(head) is None
