import random

from solution import assign_workers


def _max_overlap(jobs):
    events = sorted([(s, 1) for s, _ in jobs] + [(e, -1) for _, e in jobs], key=lambda x: (x[0], x[1]))
    best = current = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best


def _model(jobs):
    order = sorted(range(len(jobs)), key=lambda i: (jobs[i][0], jobs[i][1], i))
    busy_until, assignment = [], [None] * len(jobs)
    for i in order:
        start, end = jobs[i]
        free = [w for w, until in enumerate(busy_until) if until <= start]
        worker = min(free) if free else len(busy_until)
        if worker == len(busy_until):
            busy_until.append(end)
        else:
            busy_until[worker] = end
        assignment[i] = worker
    return len(busy_until), assignment


def _assert_no_conflicts(jobs, assignment):
    for i in range(len(jobs)):
        for j in range(i + 1, len(jobs)):
            if assignment[i] == assignment[j]:
                (s1, e1), (s2, e2) = jobs[i], jobs[j]
                assert e1 <= s2 or e2 <= s1, f"jobs {jobs[i]} and {jobs[j]} share worker {assignment[i]}"


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.assign_workers)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    count, assignment = assign_workers([(0, 10), (10, 20), (5, 15)])
    assert count == 2
    assert list(assignment) == [0, 0, 1]


def test_empty_and_single_job():
    count, assignment = assign_workers([])
    assert count == 0 and list(assignment) == []
    count, assignment = assign_workers([(3, 4)])
    assert count == 1 and list(assignment) == [0]


def test_touching_endpoints_reuse_a_worker():
    count, assignment = assign_workers([(0, 5), (5, 10), (10, 15)])
    assert count == 1 and list(assignment) == [0, 0, 0]


def test_all_overlapping_jobs_need_separate_workers():
    count, assignment = assign_workers([(0, 10), (1, 9), (2, 8), (3, 7)])
    assert count == 4 and list(assignment) == [0, 1, 2, 3]


def test_assignment_is_reported_in_input_order():
    count, assignment = assign_workers([(10, 20), (0, 5), (5, 15)])
    assert count == 2
    assert list(assignment) == [1, 0, 0]


def test_smallest_free_worker_id_not_earliest_finisher():
    # Workers 0 and 1 are both free at time 6; worker 1 finished earlier, but 0 must be used.
    count, assignment = assign_workers([(0, 5), (1, 3), (6, 7)])
    assert count == 2 and list(assignment) == [0, 1, 0]


def test_jobs_with_equal_starts_are_ordered_by_end_then_index():
    count, assignment = assign_workers([(0, 9), (0, 4), (0, 4), (4, 6)])
    assert count == 3
    assert list(assignment) == [2, 0, 1, 0]


def test_invariants_on_random_jobs():
    rng = random.Random(31)
    for _ in range(300):
        jobs = []
        for _ in range(rng.randint(0, 12)):
            start = rng.randint(0, 20)
            jobs.append((start, start + rng.randint(1, 6)))
        count, assignment = assign_workers(list(jobs))
        assignment = list(assignment)
        assert count == _max_overlap(jobs), jobs
        assert len(assignment) == len(jobs) and set(assignment) == set(range(count))
        _assert_no_conflicts(jobs, assignment)
        assert (count, assignment) == _model(jobs), jobs


def test_input_is_not_mutated():
    jobs = [(5, 6), (0, 2), (1, 3)]
    assign_workers(jobs)
    assert jobs == [(5, 6), (0, 2), (1, 3)]
