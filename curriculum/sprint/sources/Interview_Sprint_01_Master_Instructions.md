# Search + Ranking + Recommendation Interview Sprint — Master Instructions

**Status:** TEMPORARY INTERVIEW OVERLAY  
**Default duration:** 3 weeks  
**Allowed duration:** 2–4 weeks depending on interview date  
**Purpose:** maximize readiness for an imminent Search / Ranking / Recommendation MLE interview without starting the full 2027 specialization roadmap early.

---

# 0. Governance

This sprint is an **overlay**, not a replacement roadmap.

Long-term authority remains with the 2026 Generalist MLE files and the latest 2027 Search+Recs specialization files. This sprint may borrow selected 2027 IDs early.

After the interview:
1. stop the sprint;
2. resume the 2026 roadmap immediately;
3. keep borrowed 2027 items in spaced review;
4. when a borrowed item appears in 2027, convert that slot into cold retest, harder variant, transfer, or system-depth work rather than repeating first exposure.

Do not mark interview cramming as mastery. A serious early attempt usually produces **Learned** or **Independent**, not **Mastered**.

# 1. Interview signal being optimized for

Known interview surfaces:
- end-to-end ML ownership;
- Search / Ranking / Recommendation system design;
- limited-latency multi-stage ranking;
- ML/ranking-oriented coding;
- model/system debugging.

Priority order:

`ranking coding → multi-stage system design → end-to-end ownership → Search/Recs fundamentals → debugging → advanced extras`

# 2. Three required interview problem types

## A. Model Design
Examples: two-tower vs MF/co-visitation, pointwise vs pairwise/listwise/LambdaMART, lexical vs dense vs hybrid, calibrated probability vs ordering score, negative sampling, candidate count vs ranker capacity.

## B. System Design
Examples: two-stage ranking under 80–120 ms, candidate retrieval + feature hydration + pre-rank + heavy rank + rerank, ANN memory/freshness, feature precompute vs online hydration, timeout/fallback, model/index/feature versioning, p95/p99/QPS reasoning.

## C. Debugging / Incident Diagnosis
Examples: NDCG up but online metric down, p99 spike after candidate-count increase, stale features, embedding/index mismatch, exact-ID regression after semantic rollout, cache collapse, slice regression, constraints violated on timeout.

# 3. Borrowed-ID accounting

For every borrowed 2027 item record:
- early exposure date;
- sprint result: Red / Yellow / Green;
- mastery state: Unseen / Learned / Independent / Mastered;
- next cold review date;
- 2027 scheduled treatment.

Interpretation:
- serious attempt + repair = **Learned**;
- independent cold answer/implementation = **Independent**;
- later spaced cold performance with variants/transfer = **Mastered**.

# 4. End-to-end ownership answer contract

Prepare at least two concrete stories using:

`problem → objective → data/logging → labels → leakage/point-in-time correctness → baseline → model choice → offline metrics → experiment → serving → latency/resources → monitoring → failure/incident → iteration`

For each story be ready to answer:
- What did you personally own?
- What did adjacent teams own?
- Why this metric/model?
- What could leak?
- What failed?
- How was it monitored?
- What happened online?
- What would you redesign now?

Never overclaim ownership.

# 5. Limited-latency ranking framework

For any latency-constrained design:
1. clarify server-side vs end-to-end latency;
2. establish QPS, corpus/catalog, freshness, p99 target;
3. decompose stages;
4. assign stage budgets;
5. identify what can be precomputed;
6. choose candidate counts per stage;
7. parallelize independent work;
8. choose model complexity under budget;
9. define timeout/degradation/fallback;
10. define observability/versioning/rollback;
11. state quality lost for each latency optimization.

Canonical decomposition:

`request/context → retrieval → feature hydration → pre-rank → heavy rank → rerank/constraints → response`

Be able to discuss candidate pruning, pre-ranking, batching/vectorization, caching/precompute, distillation, quantization, ANN tuning, smaller interaction models, deadlines, and fallback rankers.

# 6. Coding mode

Default: **INTERVIEW**.

For each problem:
1. clarify input/output and metric semantics;
2. give baseline;
3. state invariant/objective;
4. implement;
5. test edge cases;
6. explain complexity/resources;
7. handle ranking/system follow-ups.

Prioritize ranking metrics, temporal training data, two-tower retrieval, exact/ANN retrieval, pointwise/pairwise/tree LTR, reranking, and evaluation/replay.

# 7. Success criteria

Before interview day, be able to:
- explain two-stage Search/Recs architecture cold;
- choose stage-specific metrics;
- reason about retrieval ceiling and Recall@k vs NDCG;
- explain pointwise/pairwise/listwise and LambdaMART;
- explain two-tower retrieval and negative sampling;
- compare lexical/dense/hybrid retrieval;
- reason about ANN recall-latency-memory;
- design a 2–3 stage ranking service under a fixed p99 budget;
- diagnose at least five model/system incidents;
- implement ranking-oriented problems under time pressure;
- give two end-to-end ownership stories with precise ownership boundaries.

# 8. Post-interview rule

Resume 2026 immediately. Do not keep expanding specialization because the sprint created momentum. Preserve only the borrowed-ID ledger and a light cold-review queue until the full 2027 specialization begins.
