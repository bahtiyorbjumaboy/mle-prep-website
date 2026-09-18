"""Implementation for REC-02."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, TypeAlias


EventType: TypeAlias = Literal["impression", "click", "watch", "cart", "purchase"]
OutcomeType: TypeAlias = Literal["click", "watch", "cart", "purchase"]
Split: TypeAlias = Literal["train", "validation", "test"]

EVENT_TYPES = frozenset({"impression", "click", "watch", "cart", "purchase"})
OUTCOME_TYPES = frozenset({"click", "watch", "cart", "purchase"})


@dataclass(frozen=True)
class Event:
    """One immutable behavioral event.

    Impression events use their own ``event_id`` as the impression identity
    and must have ``impression_id=None``. Outcome events must reference an
    impression through ``impression_id``. ``value`` stores watch seconds or
    purchase value when applicable.
    """

    event_id: str
    event_type: EventType
    user_id: str
    item_id: str
    event_time: datetime
    ingestion_time: datetime
    impression_id: str | None = None
    value: float | None = None


@dataclass(frozen=True)
class CatalogRecord:
    """A versioned item record used for point-in-time feature lookup."""

    item_id: str
    effective_time: datetime
    ingestion_time: datetime
    category: str
    price: float
    available: bool


@dataclass(frozen=True)
class DatasetConfig:
    """Attribution, observation, and half-open temporal-split boundaries."""

    attribution_windows: Mapping[OutcomeType, timedelta]
    label_cutoff: datetime
    train_end: datetime
    validation_end: datetime
    test_end: datetime


@dataclass(frozen=True)
class TrainingExample:
    """One training row at impression grain."""

    impression_id: str
    user_id: str
    item_id: str
    impression_time: datetime
    category_at_impression: str | None
    price_at_impression: float | None
    available_at_impression: bool | None
    clicked: int
    watch_seconds: float
    carted: int
    purchased: int
    purchase_value: float
    is_negative: bool
    split: Split


@dataclass(frozen=True)
class BuildDiagnostics:
    """Counts for events or impressions that require operational visibility."""

    duplicate_events_removed: int = 0
    orphan_outcome_events: int = 0
    mismatched_outcome_events: int = 0
    out_of_window_events: int = 0
    late_events_excluded: int = 0
    censored_impressions: int = 0
    missing_catalog_snapshots: int = 0


@dataclass(frozen=True)
class BuildResult:
    examples: tuple[TrainingExample, ...]
    diagnostics: BuildDiagnostics


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def _validate_event(event: Event) -> None:
    if not event.event_id or not event.user_id or not event.item_id:
        raise ValueError("event_id, user_id, and item_id must be non-empty")
    if event.event_type not in EVENT_TYPES:
        raise ValueError(f"unsupported event type: {event.event_type!r}")

    _require_aware(event.event_time, "event_time")
    _require_aware(event.ingestion_time, "ingestion_time")

    if event.event_type == "impression":
        if event.impression_id is not None:
            raise ValueError("impression events must have impression_id=None")
    elif not event.impression_id:
        raise ValueError("outcome events must reference an impression_id")

    if event.value is not None and (
        not math.isfinite(event.value) or event.value < 0
    ):
        raise ValueError("event values must be finite and nonnegative")


def _validate_catalog_record(record: CatalogRecord) -> None:
    if not record.item_id:
        raise ValueError("catalog item_id must be non-empty")
    _require_aware(record.effective_time, "catalog effective_time")
    _require_aware(record.ingestion_time, "catalog ingestion_time")
    if not math.isfinite(record.price) or record.price < 0:
        raise ValueError("catalog price must be finite and nonnegative")


def _validate_config(config: DatasetConfig, build_as_of: datetime | None = None) -> None:
    required_windows = OUTCOME_TYPES
    if set(config.attribution_windows) != required_windows:
        raise ValueError(
            "attribution_windows must contain exactly click, watch, cart, and purchase"
        )

    for event_type, window in config.attribution_windows.items():
        if not isinstance(window, timedelta) or window < timedelta(0):
            raise ValueError(f"{event_type} attribution window must be nonnegative")

    for name in ("label_cutoff", "train_end", "validation_end", "test_end"):
        _require_aware(getattr(config, name), name)

    if not config.train_end < config.validation_end < config.test_end:
        raise ValueError("split boundaries must be strictly increasing")

    if build_as_of is not None:
        _require_aware(build_as_of, "build_as_of")
        if build_as_of < config.label_cutoff:
            raise ValueError("build_as_of cannot precede label_cutoff")


def _event_content(event: Event) -> tuple[object, ...]:
    """Return identity-bearing event fields, excluding arrival time."""
    return (
        event.event_id,
        event.event_type,
        event.user_id,
        event.item_id,
        event.event_time,
        event.impression_id,
        event.value,
    )


def deduplicate_events(events: Sequence[Event]) -> tuple[tuple[Event, ...], int]:
    """Deduplicate by event ID and return ``(events, duplicates_removed)``.

    Duplicates with equivalent behavioral content (all fields except
    ``ingestion_time``) retain the earliest-ingested copy. Reusing an event ID
    for conflicting behavioral content raises ``ValueError``.
    Returned events are ordered by ``(event_time, event_id)``.
    """
    by_id: dict[str, Event] = {}
    duplicates_removed = 0

    for event in events:
        _validate_event(event)
        existing = by_id.get(event.event_id)
        if existing is None:
            by_id[event.event_id] = event
            continue

        if _event_content(existing) != _event_content(event):
            raise ValueError(f"conflicting content for event_id {event.event_id!r}")

        duplicates_removed += 1
        if event.ingestion_time < existing.ingestion_time:
            by_id[event.event_id] = event

    ordered = tuple(sorted(by_id.values(), key=lambda event: (event.event_time, event.event_id)))
    return ordered, duplicates_removed


def catalog_record_as_of(
    catalog_history: Sequence[CatalogRecord],
    item_id: str,
    feature_time: datetime,
    build_as_of: datetime,
) -> CatalogRecord | None:
    """Return the latest catalog record knowable at ``feature_time``.

    A candidate record must satisfy ``effective_time <= feature_time`` and
    ``ingestion_time <= min(feature_time, build_as_of)``. The ingestion check
    prevents a later backfill from leaking into an older feature row. Return
    ``None`` when no record qualifies.
    """
    _require_aware(feature_time, "feature_time")
    _require_aware(build_as_of, "build_as_of")

    candidates: list[CatalogRecord] = []
    for record in catalog_history:
        _validate_catalog_record(record)
        if (
            record.item_id == item_id
            and record.effective_time <= feature_time
            and record.ingestion_time <= min(feature_time, build_as_of)
        ):
            candidates.append(record)

    if not candidates:
        return None

    latest_key = max((record.effective_time, record.ingestion_time) for record in candidates)
    latest = [
        record
        for record in candidates
        if (record.effective_time, record.ingestion_time) == latest_key
    ]
    if len(latest) > 1 and any(record != latest[0] for record in latest[1:]):
        raise ValueError("conflicting catalog records at the same point-in-time version")
    return latest[0]


def assign_temporal_split(impression_time: datetime, config: DatasetConfig) -> Split:
    """Assign a split using half-open event-time intervals.

    Times before ``train_end`` are train; ``[train_end, validation_end)`` is
    validation; ``[validation_end, test_end)`` is test. Times at or beyond
    ``test_end`` are outside the evaluation interval and raise ``ValueError``.
    """
    _validate_config(config)
    _require_aware(impression_time, "impression_time")

    if impression_time < config.train_end:
        return "train"
    if impression_time < config.validation_end:
        return "validation"
    if impression_time < config.test_end:
        return "test"
    raise ValueError("impression_time is at or beyond test_end")


def build_training_examples(
    events: Sequence[Event],
    catalog_history: Sequence[CatalogRecord],
    config: DatasetConfig,
    *,
    build_as_of: datetime,
) -> BuildResult:
    """Build deterministic, point-in-time-correct rows at impression grain."""
    _validate_config(config, build_as_of)

    for event in events:
        _validate_event(event)
    for record in catalog_history:
        _validate_catalog_record(record)

    available_events = [event for event in events if event.ingestion_time <= build_as_of]
    late_events_excluded = len(events) - len(available_events)
    deduplicated, duplicates_removed = deduplicate_events(available_events)

    impressions: dict[str, Event] = {
        event.event_id: event
        for event in deduplicated
        if event.event_type == "impression"
    }

    outcomes_by_impression: dict[str, list[Event]] = {
        impression_id: [] for impression_id in impressions
    }
    orphan_outcome_events = 0
    mismatched_outcome_events = 0
    out_of_window_events = 0

    for event in deduplicated:
        if event.event_type == "impression":
            continue

        assert event.impression_id is not None
        parent = impressions.get(event.impression_id)
        if parent is None:
            orphan_outcome_events += 1
            continue
        if event.user_id != parent.user_id or event.item_id != parent.item_id:
            mismatched_outcome_events += 1
            continue

        window = config.attribution_windows[event.event_type]
        if not parent.event_time <= event.event_time <= parent.event_time + window:
            out_of_window_events += 1
            continue

        outcomes_by_impression[parent.event_id].append(event)

    max_window = max(config.attribution_windows.values())
    examples: list[TrainingExample] = []
    censored_impressions = 0
    missing_catalog_snapshots = 0

    for parent in sorted(
        impressions.values(), key=lambda event: (event.event_time, event.event_id)
    ):
        if parent.event_time + max_window > config.label_cutoff:
            censored_impressions += 1
            continue

        split = assign_temporal_split(parent.event_time, config)
        snapshot = catalog_record_as_of(
            catalog_history,
            parent.item_id,
            parent.event_time,
            build_as_of,
        )
        if snapshot is None:
            missing_catalog_snapshots += 1

        attributed = outcomes_by_impression[parent.event_id]
        clicked = int(any(event.event_type == "click" for event in attributed))
        carted = int(any(event.event_type == "cart" for event in attributed))
        purchased = int(any(event.event_type == "purchase" for event in attributed))
        watch_seconds = sum(
            event.value or 0.0 for event in attributed if event.event_type == "watch"
        )
        purchase_value = sum(
            event.value or 0.0
            for event in attributed
            if event.event_type == "purchase"
        )

        examples.append(
            TrainingExample(
                impression_id=parent.event_id,
                user_id=parent.user_id,
                item_id=parent.item_id,
                impression_time=parent.event_time,
                category_at_impression=snapshot.category if snapshot else None,
                price_at_impression=snapshot.price if snapshot else None,
                available_at_impression=snapshot.available if snapshot else None,
                clicked=clicked,
                watch_seconds=watch_seconds,
                carted=carted,
                purchased=purchased,
                purchase_value=purchase_value,
                is_negative=not (clicked or watch_seconds > 0 or carted or purchased),
                split=split,
            )
        )

    diagnostics = BuildDiagnostics(
        duplicate_events_removed=duplicates_removed,
        orphan_outcome_events=orphan_outcome_events,
        mismatched_outcome_events=mismatched_outcome_events,
        out_of_window_events=out_of_window_events,
        late_events_excluded=late_events_excluded,
        censored_impressions=censored_impressions,
        missing_catalog_snapshots=missing_catalog_snapshots,
    )
    return BuildResult(examples=tuple(examples), diagnostics=diagnostics)
