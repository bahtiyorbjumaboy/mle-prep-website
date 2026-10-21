from collections import deque


def level_order(root) -> list[list]:
    """Return values grouped by depth using BFS with explicit level boundaries."""
    if root is None:
        return []
    levels: list[list] = []
    queue = deque([root])
    while queue:
        level = []
        # The queue holds exactly one level at the top of each iteration.
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        levels.append(level)
    return levels
