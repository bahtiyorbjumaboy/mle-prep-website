def tree_depth_and_balanced(root) -> tuple[int, bool]:
    """Return a binary tree's maximum depth and whether it is height-balanced.

    Nodes expose `.val`, `.left`, and `.right`. Depth counts nodes on the longest
    root-to-leaf path (empty tree: 0). A tree is height-balanced when, at every node, the
    depths of the two subtrees differ by at most 1. Target O(n) time.

    Args:
        root: Root node, or `None` for an empty tree.

    Returns:
        `(max_depth, is_balanced)`.
    """
    raise NotImplementedError("TODO: implement DSA-17")
