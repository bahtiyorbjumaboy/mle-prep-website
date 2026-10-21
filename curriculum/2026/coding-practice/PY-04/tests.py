import threading

from solution import TaskResult, WorkerPool

TIMEOUT = 5.0


def _raises(exc_type, fn):
    try:
        fn()
    except exc_type:
        return True
    return False


def _run_in_thread(fn):
    """Run fn in a daemon thread; return (thread, done_event, box) so callers can wait."""
    done, box = threading.Event(), {}

    def target():
        try:
            box["value"] = fn()
        except BaseException as exc:  # surfaced to the test via box
            box["error"] = exc
        finally:
            done.set()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread, done, box


def _shutdown(pool):
    """Shut down with a deadline so a deadlocked pool fails instead of hanging the suite."""
    _, finished, box = _run_in_thread(pool.shutdown)
    assert finished.wait(TIMEOUT), "shutdown did not finish (deadlock or lost worker?)"
    if "error" in box:
        raise box["error"]


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.WorkerPool)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_success_failure_and_shutdown():
    pool = WorkerPool(workers=2, max_queue=2)
    pool.start()
    ids = [pool.submit(lambda x: x * 2, i) for i in range(3)]
    _shutdown(pool)
    results = pool.results()
    assert ids == [0, 1, 2]
    assert [r.task_id for r in results] == ids
    assert [r.value for r in results] == [0, 2, 4] and all(r.ok and r.error is None for r in results)


def test_failures_are_captured_and_workers_survive():
    pool = WorkerPool(workers=1, max_queue=4)
    pool.start()

    def maybe_fail(i):
        if i % 2:
            raise ValueError(f"bad {i}")
        return i

    for i in range(6):
        pool.submit(maybe_fail, i)
    _shutdown(pool)
    results = pool.results()
    assert [r.ok for r in results] == [True, False] * 3
    failure = results[1]
    assert isinstance(failure.error, ValueError) and str(failure.error) == "bad 1" and failure.value is None
    assert [r.value for r in results if r.ok] == [0, 2, 4]


def test_kwargs_are_forwarded():
    pool = WorkerPool(workers=1, max_queue=1)
    pool.start()
    pool.submit(lambda a, b=0: a - b, 10, b=3)
    _shutdown(pool)
    assert pool.results() == [TaskResult(task_id=0, ok=True, value=7)]


def test_no_task_is_lost_with_many_tasks_and_concurrent_submitters():
    pool = WorkerPool(workers=4, max_queue=3)
    pool.start()
    ids, lock = [], threading.Lock()

    def submitter(offset):
        for i in range(250):
            task_id = pool.submit(lambda x: x + 1, offset + i)
            with lock:
                ids.append(task_id)

    threads = [threading.Thread(target=submitter, args=(k * 1000,)) for k in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(TIMEOUT)
    _shutdown(pool)
    results = pool.results()
    assert sorted(ids) == list(range(1000)), "task ids must be unique and sequential"
    assert [r.task_id for r in results] == list(range(1000))
    assert sorted(r.value for r in results) == sorted(k * 1000 + i + 1 for k in range(4) for i in range(250))


def test_workers_run_concurrently():
    workers = 3
    barrier = threading.Barrier(workers, timeout=TIMEOUT)
    pool = WorkerPool(workers=workers, max_queue=workers)
    pool.start()
    for _ in range(workers):
        pool.submit(barrier.wait)
    _shutdown(pool)
    assert all(r.ok for r in pool.results()), "tasks must run on separate worker threads at the same time"


def test_submit_blocks_when_queue_is_full():
    gate, started = threading.Event(), threading.Event()
    pool = WorkerPool(workers=1, max_queue=1)
    pool.start()

    def blocked():
        started.set()
        assert gate.wait(TIMEOUT)
        return "done"

    pool.submit(blocked)  # taken by the only worker
    assert started.wait(TIMEOUT)
    pool.submit(lambda: 1)  # fills the queue
    _, submitted, box = _run_in_thread(lambda: pool.submit(lambda: 2))
    assert not submitted.wait(0.2), "submit must block while the queue is full"
    gate.set()
    assert submitted.wait(TIMEOUT) and box.get("value") == 2
    _shutdown(pool)
    assert [r.value for r in pool.results()] == ["done", 1, 2]


def test_shutdown_drains_queued_tasks_and_joins_threads():
    baseline = threading.active_count()
    gate = threading.Event()
    pool = WorkerPool(workers=2, max_queue=10)
    pool.start()
    assert threading.active_count() == baseline + 2
    for i in range(8):
        pool.submit(lambda i=i: gate.wait(TIMEOUT) and i)
    shutdown_thread, finished, _ = _run_in_thread(pool.shutdown)
    assert not finished.wait(0.2), "shutdown must wait for submitted tasks"
    gate.set()
    assert finished.wait(TIMEOUT)
    shutdown_thread.join(TIMEOUT)
    assert [r.value for r in pool.results()] == list(range(8))
    assert threading.active_count() == baseline, "worker threads must be joined"


def test_shutdown_while_a_submit_is_blocked_keeps_the_task():
    gate, started = threading.Event(), threading.Event()
    pool = WorkerPool(workers=1, max_queue=1)
    pool.start()

    def blocked():
        started.set()
        return gate.wait(TIMEOUT)

    pool.submit(blocked)
    assert started.wait(TIMEOUT)
    pool.submit(lambda: "queued")
    _, submitted, box = _run_in_thread(lambda: pool.submit(lambda: "late"))
    assert not submitted.wait(0.2)
    _, finished, _ = _run_in_thread(pool.shutdown)
    gate.set()
    assert submitted.wait(TIMEOUT) and finished.wait(TIMEOUT), "shutdown and submit must not deadlock"
    assert box.get("value") == 2
    assert [r.value for r in pool.results()] == [True, "queued", "late"]


def test_lifecycle_errors():
    assert _raises(ValueError, lambda: WorkerPool(workers=0, max_queue=1))
    assert _raises(ValueError, lambda: WorkerPool(workers=1, max_queue=0))
    pool = WorkerPool(workers=1, max_queue=1)
    assert _raises(RuntimeError, lambda: pool.submit(print))
    pool.start()
    assert _raises(RuntimeError, pool.start)
    _shutdown(pool)
    _shutdown(pool)  # idempotent
    assert _raises(RuntimeError, lambda: pool.submit(print))


def test_shutdown_with_no_tasks():
    pool = WorkerPool(workers=3, max_queue=1)
    pool.start()
    _shutdown(pool)
    assert pool.results() == []
