import math
from collections.abc import Hashable, Iterable

# Context: `RankingEvaluator` is used by three offline-eval jobs and its regression suite
# (the "existing behaviour" tests) must keep passing unchanged. Product now wants metrics
# per traffic segment, recall at several cut-offs, and evaluation over hundreds of millions
# of queries, which the current implementation cannot hold in memory.
#
# Canonical prompt: given a tested ranking evaluator with `add_query`, `compute`, and
# `reset`, add per-segment metrics, arbitrary `recall@k`, and streaming accumulation where
# mathematically possible without breaking existing tests.
# Follow-up: which ranking metrics require global state?
#
# Extension spec:
# - `RankingEvaluator(k=10, recall_ks=())`: for every `r` in `recall_ks` (positive ints,
#   otherwise `ValueError`), `compute()` additionally reports `recall@{r}`, the mean over
#   queries of |relevant in top r| / |relevant|. With no `recall_ks`, `compute()` returns
#   exactly the keys it returns today.
# - `add_query(ranked_ids, relevant_ids, segment=None)`: a query with a non-None `segment`
#   also counts toward that segment. `compute_segments()` returns
#   `{segment: metrics}` with the same keys and semantics as `compute()`, for every segment
#   seen since the last `reset()`. The overall `compute()` still averages over all queries.
# - Streaming: evaluator state must not grow with the number of queries (it may grow with
#   the number of segments). `compute()` may be called at any time while queries stream in.


def reciprocal_rank(ranked: list, relevant: set) -> float:
    for position, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1.0 / position
    return 0.0


def precision_at(ranked: list, relevant: set, k: int) -> float:
    return sum(item in relevant for item in ranked[:k]) / k


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
    """

    def __init__(self, k: int = 10):
        if not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive int")
        self.k = k
        self.reset()

    def reset(self) -> None:
        self._rankings: list[list] = []
        self._relevant: list[set] = []

    def add_query(self, ranked_ids: Iterable[Hashable], relevant_ids: Iterable[Hashable]) -> None:
        ranked, relevant = list(ranked_ids), set(relevant_ids)
        if not relevant:
            raise ValueError("relevant_ids must be non-empty")
        if len(set(ranked)) != len(ranked):
            raise ValueError("ranked_ids must be unique")
        self._rankings.append(ranked)
        self._relevant.append(relevant)

    def compute(self) -> dict[str, float]:
        if not self._rankings:
            raise ValueError("no queries added")
        mrr = precision = ndcg = 0.0
        for ranked, relevant in zip(self._rankings, self._relevant):
            mrr += reciprocal_rank(ranked, relevant)
            precision += precision_at(ranked, relevant, self.k)
            ndcg += ndcg_at(ranked, relevant, self.k)
        n = len(self._rankings)
        return {
            "num_queries": n,
            "mrr": mrr / n,
            f"precision@{self.k}": precision / n,
            f"ndcg@{self.k}": ndcg / n,
        }
