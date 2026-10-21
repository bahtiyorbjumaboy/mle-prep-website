import queue
import threading
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class TaskResult:
    """Outcome of one task: `value` on success, the raised exception in `error` on failure."""

    task_id: int
    ok: bool
    value: Any = None
    error: BaseException | None = None


_STOP = object()  # sentinel: one per worker tells it to exit after draining


class WorkerPool:
    """Thread pool over a bounded queue with sentinel-based clean shutdown."""

    def __init__(self, workers: int, max_queue: int) -> None:
        if workers < 1 or max_queue < 1:
            raise ValueError("workers and max_queue must be >= 1")
        self._workers = workers
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue)
        self._threads: list[threading.Thread] = []
        self._results: dict[int, TaskResult] = {}
        self._lock = threading.Lock()  # guards ids, state, results, and pending puts
        self._puts_done = threading.Condition(self._lock)
        self._pending_puts = 0
        self._next_id = 0
        self._state = "new"  # new -> running -> closed

    def start(self) -> None:
        with self._lock:
            if self._state != "new":
                raise RuntimeError("pool already started")
            self._state = "running"
        for index in range(self._workers):
            thread = threading.Thread(target=self._work, name=f"worker-{index}", daemon=True)
            thread.start()
            self._threads.append(thread)

    def _work(self) -> None:
        while True:
            item = self._queue.get()
            if item is _STOP:
                return
            task_id, fn, args, kwargs = item
            try:
                result = TaskResult(task_id, True, value=fn(*args, **kwargs))
            except Exception as exc:  # a failing task must not kill the worker
                result = TaskResult(task_id, False, error=exc)
            with self._lock:
                self._results[task_id] = result

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> int:
        with self._lock:
            if self._state != "running":
                raise RuntimeError("pool is not accepting tasks")
            task_id = self._next_id
            self._next_id += 1
            self._pending_puts += 1
        try:
            # Blocking put outside the lock: bounded backpressure without stalling workers.
            self._queue.put((task_id, fn, args, kwargs))
        finally:
            with self._lock:
                self._pending_puts -= 1
                self._puts_done.notify_all()
        return task_id

    def shutdown(self) -> None:
        with self._lock:
            if self._state != "running":
                if self._state == "new":
                    self._state = "closed"
                return
            self._state = "closed"
            # A submit that passed the state check may still be blocked in put();
            # wait for it so no task lands behind a sentinel and is lost.
            while self._pending_puts:
                self._puts_done.wait()
        # Sentinels queue behind every submitted task, so all work drains first.
        for _ in self._threads:
            self._queue.put(_STOP)
        for thread in self._threads:
            thread.join()

    def results(self) -> list[TaskResult]:
        with self._lock:
            return [self._results[k] for k in sorted(self._results)]
