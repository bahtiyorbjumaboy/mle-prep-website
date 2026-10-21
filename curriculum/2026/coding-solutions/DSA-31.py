import heapq


def assign_workers(jobs: list[tuple[int, int]]) -> tuple[int, list[int]]:
    """Return the minimum worker count and a deterministic job-to-worker assignment."""
    order = sorted(range(len(jobs)), key=lambda i: (jobs[i][0], jobs[i][1], i))
    busy: list[tuple[int, int]] = []  # (end, worker) for workers currently on a job
    free: list[int] = []  # ids of idle workers, smallest first
    assignment = [0] * len(jobs)
    workers = 0
    for i in order:
        start, end = jobs[i]
        # Half-open intervals: a job ending exactly at `start` releases its worker.
        while busy and busy[0][0] <= start:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            worker = heapq.heappop(free)
        else:
            worker = workers
            workers += 1
        assignment[i] = worker
        heapq.heappush(busy, (end, worker))
    return workers, assignment
