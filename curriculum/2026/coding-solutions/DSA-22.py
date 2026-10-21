from collections import deque


def course_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """Return a topological order via Kahn's algorithm, or [] if a cycle exists."""
    dependents: list[list[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses
    for course, prereq in prerequisites:
        dependents[prereq].append(course)
        indegree[course] += 1
    # Seed with every zero-indegree course so disconnected components are included.
    queue = deque(c for c in range(num_courses) if indegree[c] == 0)
    order: list[int] = []
    while queue:
        course = queue.popleft()
        order.append(course)
        for nxt in dependents[course]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    # Courses on or behind a cycle never reach indegree 0.
    return order if len(order) == num_courses else []
