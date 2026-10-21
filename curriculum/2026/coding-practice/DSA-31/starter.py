def assign_workers(jobs: list[tuple[int, int]]) -> tuple[int, list[int]]:
    """Compute the minimum number of workers for `jobs` and a deterministic assignment.

    Each job occupies its worker for the half-open interval `[start, end)`, so a worker
    whose job ends at time `t` can take a job starting at `t`. Target O(n log n).

    Deterministic assignment rule:
        * Process jobs in order of `(start, end, input index)`.
        * Before assigning a job, free every worker whose current job ends at or before
          the job's start.
        * Give the job the free worker with the smallest id; if none is free, create a
          new worker whose id is the number of workers created so far (0, 1, 2, ...).

    Args:
        jobs: `(start, end)` pairs with `start < end`, in any order.

    Returns:
        `(worker_count, assignment)` where `assignment[i]` is the worker id for `jobs[i]`.
    """
    raise NotImplementedError("TODO: implement DSA-31")
