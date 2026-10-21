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


class WorkerPool:
    """Fixed set of worker threads consuming tasks from a bounded queue.

    Lifecycle: `WorkerPool(...)` -> `start()` -> any number of `submit(...)` ->
    `shutdown()` -> `results()`.

    Contract:
        * `submit` blocks while `max_queue` tasks are waiting (bounded in-flight work).
        * A task that raises is recorded as a failure; the worker keeps processing.
        * `shutdown` stops accepting tasks, lets workers finish every task already
          submitted, then joins all worker threads. Calling it again is a no-op.
        * After `shutdown`, every submitted task has exactly one `TaskResult`; no task is
          lost silently.
        * Must be safe when `submit` is called from several threads at once.
        * No arbitrary sleeps: coordinate with queues/locks/events.
    """

    def __init__(self, workers: int, max_queue: int) -> None:
        """Configure the pool.

        Raises:
            ValueError: If `workers < 1` or `max_queue < 1`.
        """
        raise NotImplementedError("TODO: implement PY-04")

    def start(self) -> None:
        """Start the worker threads.

        Raises:
            RuntimeError: If the pool was already started.
        """
        raise NotImplementedError("TODO: implement PY-04")

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> int:
        """Enqueue `fn(*args, **kwargs)` and return its task id (0, 1, 2, ... in submit order).

        Raises:
            RuntimeError: If the pool is not started or is shutting down / shut down.
        """
        raise NotImplementedError("TODO: implement PY-04")

    def shutdown(self) -> None:
        """Drain submitted tasks, stop and join the workers."""
        raise NotImplementedError("TODO: implement PY-04")

    def results(self) -> list[TaskResult]:
        """Return results of completed tasks sorted by `task_id`."""
        raise NotImplementedError("TODO: implement PY-04")
