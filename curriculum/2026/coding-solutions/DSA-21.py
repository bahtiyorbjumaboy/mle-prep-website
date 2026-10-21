def count_components(n: int, edges: list[list[int]]) -> int:
    """Count connected components with iterative DFS from every unvisited node."""
    adjacency: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    visited = [False] * n
    components = 0
    for start in range(n):
        if visited[start]:
            continue
        components += 1
        visited[start] = True
        stack = [start]
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
    return components
