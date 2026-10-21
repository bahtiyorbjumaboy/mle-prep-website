import itertools
import json
import math
import random
import statistics

from solution import RecordError, StreamingStats, batched, parse_jsonl, transform_records


class Tracked:
    """Iterator that records pulls and fails fast if consumed far beyond what is needed."""

    def __init__(self, iterable, limit=10_000):
        self._it = iter(iterable)
        self.pulled = 0
        self.limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        if self.pulled >= self.limit:
            raise AssertionError(f"input consumed eagerly: pulled more than {self.limit} items")
        value = next(self._it)
        self.pulled += 1
        return value


def _expect_record_error(iterator):
    try:
        for _ in iterator:
            pass
    except RecordError as error:
        return error
    raise AssertionError("expected RecordError")


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("parse_jsonl", "transform_records", "batched", "StreamingStats"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_batched_hand_computed():
    assert list(batched(iter(range(5)), 2)) == [[0, 1], [2, 3], [4]]
    assert list(batched(range(6), 3)) == [[0, 1, 2], [3, 4, 5]]


def test_batched_empty_and_batch_size_one():
    assert list(batched([], 3)) == []
    assert list(batched("abc", 1)) == [["a"], ["b"], ["c"]]
    assert list(batched([1, 2], 10)) == [[1, 2]]


def test_batched_rejects_bad_size_at_call_time():
    for size in (0, -1):
        try:
            batched([1, 2, 3], size)
        except ValueError:
            continue
        raise AssertionError(f"batched(..., {size}) must raise ValueError immediately")


def test_batched_is_lazy_on_infinite_input():
    source = Tracked(itertools.count())
    batches = batched(source, 4)
    assert source.pulled == 0, "nothing should be consumed before the first next()"
    assert next(batches) == [0, 1, 2, 3]
    assert source.pulled == 4
    assert next(batches) == [4, 5, 6, 7]


def test_batched_yields_independent_lists():
    out = list(batched(range(4), 2))
    out[0].append(99)
    assert out[1] == [2, 3]


def test_parse_jsonl_hand_computed_and_blank_lines():
    lines = ['{"a": 1}\n', "\n", "   ", '{"b": [1, 2]}']
    assert list(parse_jsonl(lines)) == [{"a": 1}, {"b": [1, 2]}]


def test_parse_jsonl_is_lazy_and_reports_line_number():
    lines = Tracked(['{"ok": 1}', "", "{bad", '{"never": 1}'])
    records = parse_jsonl(lines)
    assert next(records) == {"ok": 1}
    assert lines.pulled == 1
    error = _expect_record_error(records)
    assert error.position == 3
    assert "3" in str(error)
    assert isinstance(error.__cause__, json.JSONDecodeError)
    assert lines.pulled == 3, "must stop at the failing line"


def test_parse_jsonl_rejects_non_objects():
    error = _expect_record_error(parse_jsonl(['{"a": 1}', "[1, 2]"]))
    assert error.position == 2


def test_transform_records_wraps_errors_with_index():
    def to_int(record):
        return int(record["value"])

    stream = transform_records([{"value": "1"}, {"value": "2"}, {"value": "x"}, {"value": "4"}], to_int)
    assert next(stream) == 1 and next(stream) == 2
    error = _expect_record_error(stream)
    assert error.position == 2
    assert "2" in str(error)
    assert isinstance(error.__cause__, ValueError)


def test_transform_records_is_lazy():
    calls = []
    stream = transform_records(Tracked(itertools.count()), lambda x: calls.append(x) or x * 10)
    assert calls == []
    assert list(itertools.islice(stream, 3)) == [0, 10, 20]
    assert calls == [0, 1, 2]


def test_pipeline_composes_lazily():
    lines = Tracked(json.dumps({"v": i}) for i in itertools.count())
    pipeline = batched(transform_records(parse_jsonl(lines), lambda r: r["v"] * 2), 3)
    assert next(pipeline) == [0, 2, 4]
    assert lines.pulled == 3


def test_streaming_stats_hand_computed_and_empty():
    stats = StreamingStats()
    assert stats.count == 0
    assert stats.mean is None and stats.variance is None and stats.minimum is None and stats.maximum is None
    for value in (2, 4, 4, 4, 5, 5, 7, 9):
        stats.update(value)
    assert stats.count == 8
    assert math.isclose(stats.mean, 5.0) and math.isclose(stats.variance, 4.0)
    assert stats.minimum == 2 and stats.maximum == 9


def test_streaming_stats_single_value_and_negatives():
    stats = StreamingStats()
    stats.update(-3.5)
    assert stats.mean == -3.5 and stats.variance == 0.0 and stats.minimum == stats.maximum == -3.5


def test_streaming_stats_matches_statistics_module():
    rng = random.Random(103)
    values = [rng.uniform(-100, 100) for _ in range(500)]
    stats = StreamingStats()
    for value in values:
        stats.update(value)
    assert math.isclose(stats.mean, statistics.fmean(values), rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(stats.variance, statistics.pvariance(values), rel_tol=1e-9)
    assert stats.minimum == min(values) and stats.maximum == max(values)


def test_streaming_stats_is_numerically_stable_with_large_offset():
    # The sum-of-squares formula E[x^2] - E[x]^2 loses every significant digit here.
    values = [1e9 + x for x in (4, 7, 13, 16)]
    stats = StreamingStats()
    for value in values:
        stats.update(value)
    assert math.isclose(stats.variance, 22.5, rel_tol=1e-6), stats.variance


def test_streaming_stats_does_not_store_values():
    stats = StreamingStats()
    for value in range(10_000):
        stats.update(value)
    stored = [v for v in vars(stats).values() if isinstance(v, (list, tuple, dict, set))]
    assert all(len(v) < 100 for v in stored), "aggregates must use O(1) state"
