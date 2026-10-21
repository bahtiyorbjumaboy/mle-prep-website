import random

from solution import level_order


class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def _random_tree(rng, n, counter):
    if n == 0:
        return None
    counter[0] += 1
    value = counter[0]
    left = rng.randint(0, n - 1)
    return Node(value, _random_tree(rng, left, counter), _random_tree(rng, n - 1 - left, counter))


def _by_depth(root):
    levels = []

    def dfs(node, depth):
        if node is None:
            return
        if depth == len(levels):
            levels.append([])
        levels[depth].append(node.val)
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return levels


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "level_order")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    root = Node(3, Node(9), Node(20, Node(15), Node(7)))
    assert level_order(root) == [[3], [9, 20], [15, 7]]


def test_empty_and_single_node():
    assert level_order(None) == []
    assert level_order(Node(1)) == [[1]]


def test_skewed_tree_has_one_value_per_level():
    root = Node(1, None, Node(2, Node(3, None, Node(4))))
    assert level_order(root) == [[1], [2], [3], [4]]


def test_level_boundaries_with_missing_children():
    # Cousins at the same depth stay in one level even when their parents differ in shape.
    root = Node(1, Node(2, None, Node(4)), Node(3, Node(5, Node(7)), Node(6)))
    assert level_order(root) == [[1], [2, 3], [4, 5, 6], [7]]


def test_left_to_right_order_and_repeated_values():
    root = Node(0, Node(1, Node(1), Node(2)), Node(1, Node(2), Node(1)))
    assert level_order(root) == [[0], [1, 1], [1, 2, 2, 1]]


def test_matches_depth_grouping_on_random_trees():
    rng = random.Random(18)
    for _ in range(300):
        root = _random_tree(rng, rng.randint(0, 30), [0])
        assert level_order(root) == _by_depth(root)


def test_wide_tree():
    nodes = [Node(i) for i in range(1, 2**11)]
    for i, node in enumerate(nodes):
        if 2 * i + 1 < len(nodes):
            node.left, node.right = nodes[2 * i + 1], nodes[2 * i + 2]
    levels = level_order(nodes[0])
    assert [len(level) for level in levels] == [2**d for d in range(11)]
    assert levels[-1][0] == 2**10 and levels[-1][-1] == 2**11 - 1
