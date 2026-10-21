import math
import pickle

import pytest

from solution import RankingEvaluator

# ---------------------------------------------------------------------------------------
# A. Existing regression suite: must stay unchanged and passing.
# ---------------------------------------------------------------------------------------

LOG2_3 = math.log2(3)
NDCG_Q1 = (1 / LOG2_3) / (1 + 1 / LOG2_3)  # relevant {b, d}; only b (rank 2) is in the top 3


def _two_queries(evaluator):
    evaluator.add_query(["a", "b", "c", "d"], {"b", "d"})
    evaluator.add_query(["x", "y", "z"], {"x"})


def _assert_metrics(actual, expected):
    assert set(actual) == set(expected), (sorted(actual), sorted(expected))
    for key, value in expected.items():
        assert math.isclose(actual[key], value, rel_tol=1e-12), (key, actual[key], value)


def test_existing_hand_computed_metrics():
    ev = RankingEvaluator(k=3)
    _two_queries(ev)
    _assert_metrics(
        ev.compute(),
        {"num_queries": 2, "mrr": 0.75, "precision@3": 1 / 3, "ndcg@3": (NDCG_Q1 + 1) / 2},
    )


def test_existing_relevant_items_beyond_k_or_unranked():
    ev = RankingEvaluator(k=2)
    ev.add_query(["a", "b", "c", "d"], {"d", "zz"})  # hit at rank 4; "zz" never ranked
    _assert_metrics(ev.compute(), {"num_queries": 1, "mrr": 0.25, "precision@2": 0.0, "ndcg@2": 0.0})


def test_existing_compute_is_repeatable_and_reset_clears():
    ev = RankingEvaluator(k=3)
    _two_queries(ev)
    assert ev.compute() == ev.compute()
    ev.reset()
    with pytest.raises(ValueError):
        ev.compute()
    ev.add_query(["x", "y", "z"], {"x"})
    assert ev.compute()["num_queries"] == 1


def test_existing_input_validation():
    with pytest.raises(ValueError):
        RankingEvaluator(k=0)
    ev = RankingEvaluator()
    with pytest.raises(ValueError):
        ev.add_query(["a", "b"], set())
    with pytest.raises(ValueError):
        ev.add_query(["a", "a"], {"a"})
    with pytest.raises(ValueError):
        ev.compute()


def test_existing_accepts_any_iterables():
    ev = RankingEvaluator(k=3)
    ev.add_query((item for item in ["a", "b", "c", "d"]), ["b", "d"])
    ev.add_query(iter(["x", "y", "z"]), ("x",))
    assert math.isclose(ev.compute()["mrr"], 0.75)


# ---------------------------------------------------------------------------------------
# B. Extension spec: recall@k, per-segment metrics, streaming accumulation.
# ---------------------------------------------------------------------------------------

LEGACY_KEYS = {"num_queries", "mrr", "precision@3", "ndcg@3"}


def test_default_output_is_unchanged_when_new_features_are_unused():
    ev = RankingEvaluator(k=3)
    ev.add_query(["a", "b", "c", "d"], {"b", "d"}, segment="web")
    ev.add_query(["x", "y", "z"], {"x"})
    assert set(ev.compute()) == LEGACY_KEYS
    assert set(ev.compute_segments()["web"]) == LEGACY_KEYS


def test_recall_at_arbitrary_cutoffs():
    ev = RankingEvaluator(k=3, recall_ks=(1, 2, 50))
    ev.add_query(["a", "b", "c", "d"], {"b", "d", "zz"})  # hits at ranks 2 and 4 of 3 relevant
    ev.add_query(["x", "y", "z"], {"x", "z"})  # hits at ranks 1 and 3 of 2 relevant
    out = ev.compute()
    assert set(out) == LEGACY_KEYS | {"recall@1", "recall@2", "recall@50"}
    assert math.isclose(out["recall@1"], (0 + 1 / 2) / 2)
    assert math.isclose(out["recall@2"], (1 / 3 + 1 / 2) / 2)
    assert math.isclose(out["recall@50"], (2 / 3 + 1) / 2)
    assert math.isclose(out["mrr"], (1 / 2 + 1) / 2), "existing metrics unaffected by recall_ks"


def test_recall_cutoffs_are_validated():
    for bad in [(0,), (-1,), (2.5,), (3, 0)]:
        with pytest.raises(ValueError):
            RankingEvaluator(k=3, recall_ks=bad)


def test_segment_metrics_match_per_segment_evaluation():
    queries = [
        (["a", "b", "c", "d"], {"b", "d"}, "web"),
        (["x", "y", "z"], {"x"}, "app"),
        (["p", "q", "r"], {"r"}, "web"),
        (["m", "n", "o"], {"o", "n"}, None),  # counts overall only
    ]
    ev = RankingEvaluator(k=3, recall_ks=(2,))
    for ranked, relevant, segment in queries:
        ev.add_query(ranked, relevant, segment=segment)
    by_segment = ev.compute_segments()
    assert set(by_segment) == {"web", "app"}
    for name in ("web", "app"):
        fresh = RankingEvaluator(k=3, recall_ks=(2,))
        for ranked, relevant, segment in queries:
            if segment == name:
                fresh.add_query(ranked, relevant)
        _assert_metrics(by_segment[name], fresh.compute())
    assert by_segment["web"]["num_queries"] == 2 and by_segment["app"]["num_queries"] == 1
    assert math.isclose(by_segment["web"]["mrr"], (1 / 2 + 1 / 3) / 2)
    assert math.isclose(by_segment["app"]["recall@2"], 1.0)


def test_overall_metrics_average_all_queries_not_segments():
    plain, segmented = RankingEvaluator(k=3), RankingEvaluator(k=3)
    rows = [(["a", "b", "c"], {"a"}, "big"), (["a", "b", "c"], {"b"}, "big"),
            (["a", "b", "c"], {"c"}, "big"), (["a", "b", "c"], {"zz"}, "small")]
    for ranked, relevant, segment in rows:
        plain.add_query(ranked, relevant)
        segmented.add_query(ranked, relevant, segment=segment)
    assert segmented.compute() == plain.compute()
    assert math.isclose(segmented.compute()["mrr"], (1 + 1 / 2 + 1 / 3 + 0) / 4)


def test_reset_clears_segments_too():
    ev = RankingEvaluator(k=3)
    ev.add_query(["a", "b"], {"a"}, segment="web")
    ev.reset()
    assert ev.compute_segments() == {}
    ev.add_query(["a", "b"], {"b"}, segment="app")
    assert set(ev.compute_segments()) == {"app"}


def _stream(n):
    for i in range(n):
        ranked = [f"item{(i * 7 + j) % 50}" for j in range(20)]
        yield ranked, {f"item{(i * 3) % 50}", f"item{(i * 11) % 50}"}


def test_partial_results_while_streaming_match_batch_results():
    streaming = RankingEvaluator(k=5, recall_ks=(1, 10))
    for i, (ranked, relevant) in enumerate(_stream(300), start=1):
        streaming.add_query(ranked, relevant, segment=i % 3)
        if i in (1, 150, 300):
            batch = RankingEvaluator(k=5, recall_ks=(1, 10))
            for prefix_ranked, prefix_relevant in _stream(i):
                batch.add_query(prefix_ranked, prefix_relevant)
            _assert_metrics(streaming.compute(), batch.compute())


def test_state_does_not_grow_with_the_number_of_queries():
    small, large = RankingEvaluator(k=5), RankingEvaluator(k=5)
    for ranked, relevant in _stream(200):
        small.add_query(ranked, relevant)
    for ranked, relevant in _stream(5000):
        large.add_query(ranked, relevant)
    growth = len(pickle.dumps(large)) - len(pickle.dumps(small))
    assert growth < 64, f"state grew by {growth} bytes for 4800 extra queries"


def test_segmented_state_grows_with_segments_not_queries():
    small, large = RankingEvaluator(k=5, recall_ks=(1, 10)), RankingEvaluator(k=5, recall_ks=(1, 10))
    for i, (ranked, relevant) in enumerate(_stream(200)):
        small.add_query(ranked, relevant, segment=f"s{i % 4}")
    for i, (ranked, relevant) in enumerate(_stream(5000)):
        large.add_query(ranked, relevant, segment=f"s{i % 4}")
    growth = len(pickle.dumps(large)) - len(pickle.dumps(small))
    assert growth < 64, f"state grew by {growth} bytes for 4800 extra queries"
