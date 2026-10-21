def tree_depth_and_balanced(root) -> tuple[int, bool]:
    """Return (max depth, is height-balanced) in one post-order traversal."""

    def visit(node) -> tuple[int, bool]:
        if node is None:
            return 0, True
        left_depth, left_ok = visit(node.left)
        right_depth, right_ok = visit(node.right)
        balanced = left_ok and right_ok and abs(left_depth - right_depth) <= 1
        return 1 + max(left_depth, right_depth), balanced

    return visit(root)
