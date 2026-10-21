import random

from solution import course_order


def _assert_valid_order(num_courses, prerequisites, order):
    assert sorted(order) == list(range(num_courses)), f"order must contain every course once: {order}"
    position = {course: i for i, course in enumerate(order)}
    for course, prereq in prerequisites:
        assert position[prereq] < position[course], f"{prereq} must come before {course} in {order}"


def _has_cycle(num_courses, prerequisites):
    graph = {c: [] for c in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    state = [0] * num_courses

    def dfs(node):
        state[node] = 1
        for nxt in graph[node]:
            if state[nxt] == 1 or (state[nxt] == 0 and dfs(nxt)):
                return True
        state[node] = 2
        return False

    return any(state[c] == 0 and dfs(c) for c in range(num_courses))


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "course_order")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert course_order(2, [[1, 0]]) == [0, 1]
    prereqs = [[1, 0], [2, 0], [3, 1], [3, 2]]
    order = course_order(4, prereqs)
    assert order in ([0, 1, 2, 3], [0, 2, 1, 3])


def test_no_courses_and_no_prerequisites():
    assert course_order(0, []) == []
    assert sorted(course_order(3, [])) == [0, 1, 2]


def test_two_course_cycle_is_impossible():
    assert course_order(2, [[1, 0], [0, 1]]) == []


def test_self_prerequisite_is_impossible():
    assert course_order(3, [[1, 1]]) == []


def test_cycle_in_one_component_makes_everything_impossible():
    # Returning the partial order of the acyclic part is wrong.
    assert course_order(6, [[1, 0], [2, 1], [4, 3], [5, 4], [3, 5]]) == []


def test_disconnected_components_and_isolated_courses_are_included():
    prereqs = [[1, 0], [4, 3]]
    _assert_valid_order(6, prereqs, course_order(6, [p[:] for p in prereqs]))


def test_duplicate_prerequisite_pairs():
    prereqs = [[1, 0], [1, 0], [2, 1], [2, 1]]
    assert course_order(3, prereqs) == [0, 1, 2]


def test_long_chain_given_in_reverse():
    n = 3000
    prereqs = [[i, i + 1] for i in range(n - 1)]
    assert course_order(n, prereqs) == list(range(n - 1, -1, -1))


def test_random_dags_produce_valid_orders():
    rng = random.Random(22)
    for _ in range(200):
        n = rng.randint(1, 12)
        rank = list(range(n))
        rng.shuffle(rank)
        prereqs = []
        for _ in range(rng.randint(0, 20)):
            a, b = rng.sample(range(n), 2) if n > 1 else (0, 0)
            if a != b:
                first, second = sorted((a, b), key=rank.__getitem__)
                prereqs.append([second, first])
        _assert_valid_order(n, prereqs, course_order(n, [p[:] for p in prereqs]))


def test_random_graphs_detect_cycles():
    rng = random.Random(222)
    for _ in range(300):
        n = rng.randint(1, 8)
        prereqs = [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(0, 10))]
        order = course_order(n, [p[:] for p in prereqs])
        if _has_cycle(n, prereqs):
            assert order == [], (n, prereqs, order)
        else:
            _assert_valid_order(n, prereqs, order)
