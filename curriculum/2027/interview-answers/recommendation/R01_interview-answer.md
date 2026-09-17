---
type: interview-answer
item: "2027:R01"
title: "Two-stage and multi-stage recommender architecture"
created: "2026-09-17"
updated: "2026-09-17"
tags:
  - recommendation
  - ranking
  - retrieval
  - latency
---

## Canonical Staff-Depth Question

Explain candidate generation, pre-ranking, ranking, reranking, and post-processing as separate stages. Define each stage's objective, latency budget, recall/quality ceiling, and failure modes.

## Mastery Answer

Large recommendation systems usually cannot score the entire corpus with their most expensive model. If the catalog contains millions of items, even a modest per-item inference cost becomes too expensive at request time. The system therefore uses a cascade:

$$
\text{millions} \rightarrow \text{thousands} \rightarrow \text{hundreds} \rightarrow \text{tens}
$$

As the candidate set shrinks, the system can afford more expensive computation, richer features, and more sophisticated models per candidate.

**Candidate generation / retrieval** reduces the corpus to a manageable candidate set. Its primary objective is high recall under candidate-count and latency constraints. Ordering within the retrieved set is secondary. Its key quality ceiling is structural: if a relevant item is absent from the candidate set, no downstream stage can recover it. Production systems often fan out across multiple candidate sources such as popularity, co-visitation, collaborative filtering, content similarity, graph retrieval, and learned embedding retrieval.

**Pre-ranking** is optional. It is useful when retrieval still produces too many candidates for the heavy ranker. A lightweight model removes weak candidates while trying to preserve nearly all candidates that the downstream ranker would value. Its central trade-off is compute saved versus downstream quality lost. Over-pruning creates another irrecoverable ceiling.

**Ranking** applies richer user, item, user-item interaction, and context features to the surviving candidates. Its job is precise personalized ordering or utility estimation. Depending on the product, it may predict click probability, conversion probability, watch time, expected value, or another task-specific objective. Once the candidate set is fixed, position-sensitive metrics such as NDCG, MRR, MAP, or task-specific utility are usually more informative than recall alone.

**Reranking** reasons about the final slate rather than only independent item scores. It can trade some pointwise relevance for diversity, novelty, freshness, exploration, category or seller caps, inventory considerations, policy constraints, or other product and ecosystem objectives. Evaluation should measure both relevance retained and whether the intended slate-level objectives or constraints are satisfied.

**Post-processing** applies deterministic validity and policy rules before results are returned, such as availability, deduplication, eligibility, geographic restrictions, policy enforcement, or already-consumed suppression. Some hard filters may happen earlier when carrying invalid items farther through the pipeline would waste compute.

Each stage should have its own latency budget, quality metric, failure handling, and observability. Candidate count is a key resource knob: increasing it may improve recall and ranking opportunity, but it increases feature-hydration and scoring cost.

For diagnosis, identify the **first stage where behavior diverges**:

- retrieval Recall@K drops → candidate-generation or candidate-source problem;
- retrieval is healthy but valuable items disappear before heavy ranking → pre-ranking or pruning problem;
- candidates are healthy but ordering metrics fall → ranker, feature, objective, or model problem;
- main-ranker output is healthy but final slate quality falls → reranking or constraint problem;
- offline quality is healthy but production behavior changes → serving, feature freshness, cache, versioning, or data-skew problem.

A top-line metric such as CTR is useful for product impact, but it is not sufficient for localization. Stage-specific metrics make the system diagnosable.

## Material Follow-ups / Scenario Variants

### Stage-specific metrics

**Candidate generation**
- Recall@K
- source-level recall
- union recall
- marginal recall by candidate source
- candidate count
- retrieval latency

**Pre-ranking**
- candidate reduction ratio
- heavy-ranker compute or latency saved
- preservation of downstream top candidates
- NDCG or task-utility loss caused by pruning

**Ranking**
- NDCG
- MRR
- MAP
- task-specific utility
- calibration / log loss when probability semantics matter
- segment and slice metrics

**Reranking**
- relevance retained
- diversity / novelty / coverage
- constraint-satisfaction rate
- seller / creator / category exposure
- freshness
- product-specific guardrails

**Serving**
- p50 / p95 / p99 latency
- timeout rate
- fallback rate
- feature freshness
- cache hit rate
- model / index / feature version consistency
- error rate

### Latency-budget variant

Suppose total server-side latency is constrained to p99 < 120 ms. Decompose the request into retrieval, feature hydration, pre-ranking, heavy ranking, reranking, and overhead. Assign explicit budgets rather than saying every stage should simply be "fast."

Candidate count directly affects heavy-ranking cost. If scoring costs approximately $0.08$ ms per candidate:

$$
300 \times 0.08 \approx 24 \text{ ms}
$$

while

$$
1000 \times 0.08 \approx 80 \text{ ms}
$$

Possible latency levers include:
- reduce candidate count;
- add or strengthen pre-ranking;
- precompute or cache features;
- batch/vectorize scoring;
- distill or quantize the ranker;
- tune ANN retrieval;
- parallelize independent candidate sources.

For every optimization, state the possible quality or reliability cost.

### Failure-handling variant

Define deterministic degradation paths:
- retrieval timeout → cached, popularity, or another healthy candidate source;
- feature-service timeout → stale-but-safe features or a simpler ranker;
- heavy-ranker timeout → pre-ranker or lightweight-ranker ordering;
- reranker failure → main-ranker order plus required hard filtering.

Monitor fallback rate. A service can remain technically available while silently serving degraded recommendations.

### Offline / online mismatch variant

If offline NDCG improves while online conversion falls, do not assume the ranker itself is the cause. Check:
- objective mismatch;
- calibration or score-semantic changes;
- feature skew or staleness;
- timeout/fallback behavior;
- model/index/feature version mismatch;
- segment regressions;
- business-rule or presentation changes.

## Plain-English Model

Think of the recommender as a sequence of increasingly expensive filters.

Retrieval asks: **Which items are worth considering at all?**

Pre-ranking asks: **Which candidates are not worth spending expensive compute on?**

Ranking asks: **Among the survivors, which items are best for this user in this context?**

Reranking asks: **Does the whole list make sense as a slate rather than as independent items?**

Post-processing asks: **Is every result valid and allowed to show?**

The system spends cheap computation broadly and expensive computation narrowly.

## Reasoning Chain

1. The corpus is too large for exhaustive heavy-model scoring.
2. Therefore reduce the search space in stages.
3. Retrieval prioritizes recall because missed candidates are unrecoverable downstream.
4. Optional pre-ranking buys compute savings by pruning before expensive scoring.
5. Ranking spends richer features and model capacity on a much smaller set.
6. Reranking handles slate-level interactions and constraints that itemwise scoring misses.
7. Post-processing enforces deterministic validity.
8. Because each stage has a different objective, each needs stage-specific metrics.
9. Candidate count, feature cost, and model complexity jointly determine latency.
10. Production systems require deterministic fallbacks when stages miss deadlines.
11. Debugging should localize the first stage where quality, latency, freshness, or version state diverges.
12. Top-line CTR measures outcome; stage metrics localize the cause.

## Staff Compression

A production recommender is usually a cascade because the full corpus is too large for exhaustive heavy ranking. Retrieval maximizes recall cheaply over the corpus; optional pre-ranking removes candidates that are not worth expensive scoring; the main ranker performs precise personalized ordering; reranking optimizes the slate under diversity, business, and ecosystem constraints; and post-processing enforces hard validity.

The key systems principle is that early-stage misses create downstream quality ceilings, while later stages can spend progressively more compute on progressively fewer items. I would give every stage explicit quality and p99 budgets, treat candidate count as a resource knob, define deterministic timeout fallbacks, and instrument the funnel so that a regression can be localized to retrieval, pruning, ranking, constraints, data, or serving rather than diagnosed from CTR alone.
