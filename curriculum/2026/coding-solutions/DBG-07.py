import math
from collections.abc import Hashable, Iterable

# Extension of the DBG-07 evaluator. Every metric here (MRR, precision@k, nDCG@k,
# recall@r) is a mean of independent per-query scores, so the evaluator keeps running sums
# instead of the queries themselves: O(1) state per segment, mergeable, and identical to
# the old results because the sums are accumulated in the same order. Metrics that compare
# items or queries against each other (median rank, global AUC over all pairs, percentile
# cut-offs) are not decomposable this way and would still need global state or sketches.
#
# Public API kept: `k`, `add_query(ranked, relevant)`, `compute()`, `reset()`, the error
# cases, and the exact `compute()` keys when `recall_ks` is not used.


def reciprocal_rank(ranked: list, relevant: set) -> float:
    for position, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1.0 / position
    return 0.0


def precision_at(ranked: list, relevant: set, k: int) -> float:
    return sum(item in relevant for item in ranked[:k]) / k


def recall_at(ranked: list, relevant: set, k: int) -> float:
    return sum(item in relevant for item in ranked[:k]) / len(relevant)


def ndcg_at(ranked: list, relevant: set, k: int) -> float:
    dcg = sum(1.0 / math.log2(i + 2) for i, item in enumerate(ranked[:k]) if item in relevant)
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / ideal


class RankingEvaluator:
    """Mean binary-relevance ranking metrics over queries.

    - `add_query(ranked_ids, relevant_ids)`: `ranked_ids` are unique item ids, best first;
      `relevant_ids` is a non-empty collection. Violations raise `ValueError`.
    - `compute()` returns `{"num_queries", "mrr", "precision@k", "ndcg@k"}` and raises
      `ValueError` when no query has been added. It does not change state.
    - `reset()` forgets every query.
    - `recall_ks` adds `recall@r` for each cut-off; `segment` and `compute_segments()` give
      the same metrics per segment. State does not grow with the number of queries.
    """

    def __init__(self, k: int = 10, recall_ks: Iterable[int] = ()):
        if not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive int")
        recall_ks = tuple(recall_ks)
        if any(isinstance(r, bool) or not isinstance(r, int) or r < 1 for r in recall_ks):
            raise ValueError("recall_ks must be positive ints")
        self.k = k
        self.recall_ks = tuple(sorted(set(recall_ks)))
        self.reset()

    def reset(self) -> None:
        self._totals = self._empty_totals()
        self._segments: dict[Hashable, dict[str, float]] = {}

    def _empty_totals(self) -> dict[str, float]:
        totals = {"num_queries": 0, "mrr": 0.0, f"precision@{self.k}": 0.0, f"ndcg@{self.k}": 0.0}
        totals.update({f"recall@{r}": 0.0 for r in self.recall_ks})
        return totals

    def add_query(
        self,
        ranked_ids: Iterable[Hashable],
        relevant_ids: Iterable[Hashable],
        segment: Hashable | None = None,
    ) -> None:
        ranked, relevant = list(ranked_ids), set(relevant_ids)
        if not relevant:
            raise ValueError("relevant_ids must be non-empty")
        if len(set(ranked)) != len(ranked):
            raise ValueError("ranked_ids must be unique")
        scores = {
            "mrr": reciprocal_rank(ranked, relevant),
            f"precision@{self.k}": precision_at(ranked, relevant, self.k),
            f"ndcg@{self.k}": ndcg_at(ranked, relevant, self.k),
        }
        scores.update({f"recall@{r}": recall_at(ranked, relevant, r) for r in self.recall_ks})
        self._accumulate(self._totals, scores)
        if segment is not None:
            self._accumulate(self._segments.setdefault(segment, self._empty_totals()), scores)

    def compute(self) -> dict[str, float]:
        if not self._totals["num_queries"]:
            raise ValueError("no queries added")
        return self._means(self._totals)

    def compute_segments(self) -> dict[Hashable, dict[str, float]]:
        return {segment: self._means(totals) for segment, totals in self._segments.items()}

    @staticmethod
    def _accumulate(totals: dict[str, float], scores: dict[str, float]) -> None:
        totals["num_queries"] += 1
        for key, value in scores.items():
            totals[key] += value

    @staticmethod
    def _means(totals: dict[str, float]) -> dict[str, float]:
        n = totals["num_queries"]
        return {key: n if key == "num_queries" else value / n for key, value in totals.items()}
