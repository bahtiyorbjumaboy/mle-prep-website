"""Implementation for REC-01."""

from __future__ import annotations

import math
from collections.abc import Hashable, Mapping, Sequence
from typing import Literal, TypeAlias


ItemId: TypeAlias = Hashable
NoRelevantPolicy: TypeAlias = Literal["zero", "skip", "error"]
GainScheme: TypeAlias = Literal["linear", "exponential"]
MetricValue: TypeAlias = float | None


_VALID_POLICIES = ("zero", "skip", "error")
_VALID_GAIN_SCHEMES = ("linear", "exponential")


def _validate_k(k: int) -> None:
    if k <= 0:
        raise ValueError(f"k must be a positive integer, got {k!r}")


def _validate_no_duplicates(ranked_items: Sequence[ItemId]) -> None:
    seen: set[ItemId] = set()
    for item in ranked_items:
        if item in seen:
            raise ValueError(f"Duplicate item id in ranked_items: {item!r}")
        seen.add(item)


def _validate_relevance_map(relevance_by_item: Mapping[ItemId, float]) -> None:
    for item, grade in relevance_by_item.items():
        if not math.isfinite(grade) or grade < 0:
            raise ValueError(
                f"Invalid relevance grade for item {item!r}: {grade!r}. "
                "Grades must be finite and non-negative."
            )


def _validate_no_relevant_policy(policy: NoRelevantPolicy) -> None:
    if policy not in _VALID_POLICIES:
        raise ValueError(f"Unknown no_relevant_policy: {policy!r}")


def _validate_gain_scheme(gain_scheme: GainScheme) -> None:
    if gain_scheme not in _VALID_GAIN_SCHEMES:
        raise ValueError(f"Unknown gain_scheme: {gain_scheme!r}")


def _count_relevant(
    relevance_by_item: Mapping[ItemId, float],
    relevance_threshold: float,
) -> int:
    """Count items in the full relevance map at or above threshold."""
    return sum(1 for v in relevance_by_item.values() if v >= relevance_threshold)


def _resolve_no_relevant(policy: NoRelevantPolicy) -> MetricValue:
    """Apply the no-relevant-items policy when a metric's denominator is zero."""
    if policy == "zero":
        return 0.0
    if policy == "skip":
        return None
    if policy == "error":
        raise ValueError("No relevant items are present for this query.")
    raise ValueError(f"Unknown no_relevant_policy: {policy!r}")


def _gain(relevance: float, gain_scheme: GainScheme) -> float:
    if gain_scheme == "linear":
        return relevance
    if gain_scheme == "exponential":
        return (2.0**relevance) - 1.0
    raise ValueError(f"Unknown gain_scheme: {gain_scheme!r}")


def _validate_aggregate_inputs(
    rankings: Sequence[Sequence[ItemId]],
    relevance_maps: Sequence[Mapping[ItemId, float]],
) -> None:
    if len(rankings) != len(relevance_maps):
        raise ValueError(
            "rankings and relevance_maps must have the same length "
            f"(got {len(rankings)} and {len(relevance_maps)})."
        )
    if len(rankings) == 0:
        raise ValueError("rankings must contain at least one ranking.")


def precision_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> MetricValue:
    """Return Precision@k for one ranking.

    Precision uses exactly ``k`` as its denominator, even when fewer than
    ``k`` items were returned. Unknown item IDs have relevance zero.
    """
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_no_relevant_policy(no_relevant_policy)

    total_relevant = _count_relevant(relevance_by_item, relevance_threshold)
    if total_relevant == 0:
        return _resolve_no_relevant(no_relevant_policy)

    top_k_recs = ranked_items[:k]
    num_relevance = 0
    for item in top_k_recs:
        if item in relevance_by_item and relevance_by_item[item] >= relevance_threshold:
            num_relevance += 1

    return num_relevance / k


def recall_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> MetricValue:
    """Return Recall@k for one ranking."""
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_no_relevant_policy(no_relevant_policy)

    total_relevant = _count_relevant(relevance_by_item, relevance_threshold)
    if total_relevant == 0:
        return _resolve_no_relevant(no_relevant_policy)

    top_k = ranked_items[:k]
    num_relevant_retrieved = sum(
        1 for item in top_k if relevance_by_item.get(item, 0.0) >= relevance_threshold
    )
    return num_relevant_retrieved / total_relevant


def hit_rate_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> MetricValue:
    """Return 1.0 if the top-k prefix contains a relevant item, else 0.0."""
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_no_relevant_policy(no_relevant_policy)

    total_relevant = _count_relevant(relevance_by_item, relevance_threshold)
    if total_relevant == 0:
        return _resolve_no_relevant(no_relevant_policy)

    top_k = ranked_items[:k]
    hit = any(relevance_by_item.get(item, 0.0) >= relevance_threshold for item in top_k)
    return 1.0 if hit else 0.0


def reciprocal_rank_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> MetricValue:
    """Return reciprocal rank of the first relevant item through rank k."""
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_no_relevant_policy(no_relevant_policy)

    total_relevant = _count_relevant(relevance_by_item, relevance_threshold)
    if total_relevant == 0:
        return _resolve_no_relevant(no_relevant_policy)

    top_k = ranked_items[:k]
    for rank, item in enumerate(top_k, start=1):
        if relevance_by_item.get(item, 0.0) >= relevance_threshold:
            return 1.0 / rank
    return 0.0


def average_precision_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> MetricValue:
    """Return AP@k using ``min(total_relevant, k)`` as denominator."""
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_no_relevant_policy(no_relevant_policy)

    total_relevant = _count_relevant(relevance_by_item, relevance_threshold)
    if total_relevant == 0:
        return _resolve_no_relevant(no_relevant_policy)

    top_k = ranked_items[:k]
    denominator = min(total_relevant, k)
    num_relevant_so_far = 0
    precision_sum = 0.0
    for rank, item in enumerate(top_k, start=1):
        if relevance_by_item.get(item, 0.0) >= relevance_threshold:
            num_relevant_so_far += 1
            precision_sum += num_relevant_so_far / rank
    return precision_sum / denominator


def mean_reciprocal_rank_at_k(
    rankings: Sequence[Sequence[ItemId]],
    relevance_maps: Sequence[Mapping[ItemId, float]],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> float:
    """Return the macro mean of per-ranking reciprocal ranks."""
    _validate_aggregate_inputs(rankings, relevance_maps)
    _validate_k(k)
    _validate_no_relevant_policy(no_relevant_policy)

    values: list[float] = []
    for ranked_items, relevance_by_item in zip(rankings, relevance_maps):
        rr = reciprocal_rank_at_k(
            ranked_items,
            relevance_by_item,
            k,
            relevance_threshold=relevance_threshold,
            no_relevant_policy=no_relevant_policy,
        )
        if rr is not None:
            values.append(rr)

    if not values:
        raise ValueError(
            "All queries were skipped under no_relevant_policy='skip'; "
            "nothing to aggregate."
        )
    return sum(values) / len(values)


def mean_average_precision_at_k(
    rankings: Sequence[Sequence[ItemId]],
    relevance_maps: Sequence[Mapping[ItemId, float]],
    k: int,
    *,
    relevance_threshold: float = 1.0,
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> float:
    """Return the macro mean of per-ranking AP@k values."""
    _validate_aggregate_inputs(rankings, relevance_maps)
    _validate_k(k)
    _validate_no_relevant_policy(no_relevant_policy)

    values: list[float] = []
    for ranked_items, relevance_by_item in zip(rankings, relevance_maps):
        ap = average_precision_at_k(
            ranked_items,
            relevance_by_item,
            k,
            relevance_threshold=relevance_threshold,
            no_relevant_policy=no_relevant_policy,
        )
        if ap is not None:
            values.append(ap)

    if not values:
        raise ValueError(
            "All queries were skipped under no_relevant_policy='skip'; "
            "nothing to aggregate."
        )
    return sum(values) / len(values)


def dcg_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    gain_scheme: GainScheme = "exponential",
) -> float:
    """Return DCG@k using discounts ``log2(rank + 1)``."""
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_gain_scheme(gain_scheme)

    top_k = ranked_items[:k]
    total = 0.0
    for rank, item in enumerate(top_k, start=1):
        relevance = relevance_by_item.get(item, 0.0)
        total += _gain(relevance, gain_scheme) / math.log2(rank + 1)
    return total


def idcg_at_k(
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    gain_scheme: GainScheme = "exponential",
) -> float:
    """Return ideal DCG@k over the complete relevance map."""
    _validate_k(k)
    _validate_relevance_map(relevance_by_item)
    _validate_gain_scheme(gain_scheme)

    sorted_relevances = sorted(relevance_by_item.values(), reverse=True)
    top_k = sorted_relevances[:k]
    total = 0.0
    for rank, relevance in enumerate(top_k, start=1):
        total += _gain(relevance, gain_scheme) / math.log2(rank + 1)
    return total


def ndcg_at_k(
    ranked_items: Sequence[ItemId],
    relevance_by_item: Mapping[ItemId, float],
    k: int,
    *,
    gain_scheme: GainScheme = "exponential",
    no_relevant_policy: NoRelevantPolicy = "zero",
) -> MetricValue:
    """Return normalized DCG@k, applying policy when IDCG is zero."""
    _validate_k(k)
    _validate_no_duplicates(ranked_items)
    _validate_relevance_map(relevance_by_item)
    _validate_gain_scheme(gain_scheme)
    _validate_no_relevant_policy(no_relevant_policy)

    ideal = idcg_at_k(relevance_by_item, k, gain_scheme=gain_scheme)
    if ideal == 0.0:
        return _resolve_no_relevant(no_relevant_policy)

    actual = dcg_at_k(ranked_items, relevance_by_item, k, gain_scheme=gain_scheme)
    return actual / ideal