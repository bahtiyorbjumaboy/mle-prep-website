import random

from solution import tree_depth_and_balanced


class Node:
    """Binary tree node that counts child-pointer reads."""

    reads = 0

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self._left = left
        self._right = right

    @property
    def left(self):
        Node.reads += 1
        return self._left

    @property
    def right(self):
        Node.reads += 1
        return self._right


def _chain(n, side):
    root = None
    for i in range(n):
        root = Node(i, root, None) if side == "left" else Node(i, None, root)
    return root


def _perfect(depth):
    return None if depth == 0 else Node(depth, _perfect(depth - 1), _perfect(depth - 1))


def _random_tree(rng, n):
    if n == 0:
        return None
    left = rng.randint(0, n - 1)
    return Node(n, _random_tree(rng, left), _random_tree(rng, n - 1 - left))


def _brute(node):
    if node is None:
        return 0, True
    (dl, bl), (dr, br) = _brute(node._left), _brute(node._right)
    return 1 + max(dl, dr), bl and br and abs(dl - dr) <= 1


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "tree_depth_and_balanced")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_empty_and_single_node():
    assert tuple(tree_depth_and_balanced(None)) == (0, True)
    assert tuple(tree_depth_and_balanced(Node(1))) == (1, True)


def test_hand_computed_example():
    #     3
    #    / \
    #   9  20
    #      / \
    #     15  7
    root = Node(3, Node(9), Node(20, Node(15), Node(7)))
    assert tuple(tree_depth_and_balanced(root)) == (3, True)


def test_skewed_trees():
    assert tuple(tree_depth_and_balanced(_chain(2, "left"))) == (2, True)
    assert tuple(tree_depth_and_balanced(_chain(3, "left"))) == (3, False)
    assert tuple(tree_depth_and_balanced(_chain(400, "right"))) == (400, False)


def test_balanced_at_root_but_not_below():
    # Root subtrees both have depth 3, but each child is itself unbalanced (2 vs 0).
    left = Node(2, Node(4, Node(8)), None)
    right = Node(3, None, Node(5, None, Node(9)))
    assert tuple(tree_depth_and_balanced(Node(1, left, right))) == (4, False)


def test_depth_difference_of_exactly_one_is_balanced():
    root = Node(1, Node(2, Node(4), Node(5, Node(6))), Node(3, Node(7)))
    assert tuple(tree_depth_and_balanced(root)) == (4, True)


def test_matches_brute_force_on_random_trees():
    rng = random.Random(17)
    for _ in range(300):
        root = _random_tree(rng, rng.randint(0, 25))
        assert tuple(tree_depth_and_balanced(root)) == _brute(root)


def test_linear_number_of_node_visits():
    # Recomputing subtree heights at every node is O(n log n) here and O(n^2) in general.
    root = _perfect(12)
    n = 2**12 - 1
    Node.reads = 0
    assert tuple(tree_depth_and_balanced(root)) == (12, True)
    assert Node.reads <= 8 * n, f"{Node.reads} child reads for n={n}; expected O(n)"
