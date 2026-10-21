"""Lazy record utilities: parse, transform, batch, and aggregate streams."""
import json
from typing import Any, Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class RecordError(Exception):
    """A record could not be read or transformed at `position`."""

    def __init__(self, message: str, position: int) -> None:
        super().__init__(message)
        self.position = position


def parse_jsonl(lines: Iterable[str]) -> Iterator[dict[str, Any]]:
    """Lazily parse JSON-object lines, skipping blank lines."""
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RecordError(f"line {line_number}: invalid JSON: {exc.msg}", line_number) from exc
        if not isinstance(record, dict):
            cause = TypeError(f"expected a JSON object, got {type(record).__name__}")
            raise RecordError(f"line {line_number}: {cause}", line_number) from cause
        yield record


def transform_records(records: Iterable[T], fn: Callable[[T], U]) -> Iterator[U]:
    """Lazily apply fn, wrapping failures with the record index."""
    for index, record in enumerate(records):
        try:
            result = fn(record)
        except Exception as exc:
            raise RecordError(f"record {index}: {type(exc).__name__}: {exc}", index) from exc
        yield result


def batched(records: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    """Group records into lists of batch_size; validates eagerly, iterates lazily."""
    # Validation lives outside the generator so a bad size fails at call time.
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    return _batches(iter(records), batch_size)


def _batches(iterator: Iterator[T], batch_size: int) -> Iterator[list[T]]:
    batch: list[T] = []
    for record in iterator:
        batch.append(record)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


class StreamingStats:
    """Welford running statistics with O(1) state."""

    def __init__(self) -> None:
        self._count = 0
        self._mean = 0.0
        self._m2 = 0.0  # sum of squared deviations from the running mean
        self._min: float | None = None
        self._max: float | None = None

    def update(self, value: float) -> None:
        self._count += 1
        delta = value - self._mean
        self._mean += delta / self._count
        self._m2 += delta * (value - self._mean)
        self._min = value if self._min is None else min(self._min, value)
        self._max = value if self._max is None else max(self._max, value)

    @property
    def count(self) -> int:
        return self._count

    @property
    def mean(self) -> float | None:
        return self._mean if self._count else None

    @property
    def variance(self) -> float | None:
        return self._m2 / self._count if self._count else None

    @property
    def minimum(self) -> float | None:
        return self._min

    @property
    def maximum(self) -> float | None:
        return self._max
