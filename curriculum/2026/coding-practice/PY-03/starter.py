"""PY-03: reusable lazy iterator utilities.

Every function must be lazy: consume input only as output is requested, and never load
the whole input into memory. Memory should stay O(batch_size + aggregate state).
"""
from typing import Any, Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class RecordError(Exception):
    """A record could not be read or transformed.

    Attributes:
        position: For `parse_jsonl`, the 1-based line number (blank lines count); for
            `transform_records`, the 0-based index of the record in its input.

    The original exception must be chained as `__cause__`, and `str(error)` must mention
    the position.
    """

    def __init__(self, message: str, position: int) -> None:
        super().__init__(message)
        self.position = position


def parse_jsonl(lines: Iterable[str]) -> Iterator[dict[str, Any]]:
    """Lazily parse JSON-object lines, skipping blank/whitespace-only lines.

    Raises:
        RecordError: When a non-blank line is not valid JSON or not a JSON object, raised
            when that line is reached (records before it are still yielded).
    """
    raise NotImplementedError("TODO: implement PY-03 parse_jsonl")


def transform_records(records: Iterable[T], fn: Callable[[T], U]) -> Iterator[U]:
    """Lazily yield `fn(record)` for each record.

    Raises:
        RecordError: Wrapping any exception raised by `fn`, with the record's index.
    """
    raise NotImplementedError("TODO: implement PY-03 transform_records")


def batched(records: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    """Lazily group `records` into lists of `batch_size`; the final batch may be shorter.

    Never yields an empty batch, and pulls at most `batch_size` records from the input
    before yielding each batch.

    Raises:
        ValueError: Immediately at call time (not on first iteration) if `batch_size < 1`.
    """
    raise NotImplementedError("TODO: implement PY-03 batched")


class StreamingStats:
    """Running count/mean/min/max/variance in O(1) memory.

    Must stay numerically stable when values share a huge offset (e.g. 1e9 + small).
    `mean`, `variance` (population, ddof=0), `minimum`, and `maximum` are None while
    `count == 0`.
    """

    def __init__(self) -> None:
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")

    def update(self, value: float) -> None:
        """Incorporate one value."""
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")

    @property
    def count(self) -> int:
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")

    @property
    def mean(self) -> float | None:
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")

    @property
    def variance(self) -> float | None:
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")

    @property
    def minimum(self) -> float | None:
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")

    @property
    def maximum(self) -> float | None:
        raise NotImplementedError("TODO: implement PY-03 StreamingStats")
