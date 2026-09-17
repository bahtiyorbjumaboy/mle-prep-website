# 2027 Search + Recommendation Staff-Depth Roadmap — FINAL

**Status:** ACTIVE 2027 SPECIALIZATION ROADMAP  
**Dates:** January 3–December 31, 2027  
**Prerequisite:** Complete the 2026 Generalist MLE readiness gate first.  
**Knowledge:** 112 conversations = 56 Search + 56 Recommendation  
**Coding:** 48 IDs = 24 Search + 24 Recommendation  
**Primary target:** Staff-level technical knowledge and judgment in retrieval, ranking, Search/IR, and Recommendation/Personalization, while professional Staff level still depends on real scope, impact, and experience.

## Design principles

- No LLM/RAG/agent/inference curriculum is scheduled in 2027.
- New syllabus exposure finishes by **Week 36**; Weeks 37–52 are primarily transfer, vertical cases, capstone hardening, research, reliability, teaching, and Staff defense.
- Maintain the 2026 generalist core with one rotating cold block every 1–2 weeks.
- Every normal week should create evidence in four forms: **build, measure, explain, defend**.
- Every week also includes three explicit interview surfaces: **Model Design**, **System Design**, and **Debugging / Incident Diagnosis**. These are required practice, not optional examples.
- Projects use public/synthetic/self-generated data and must not be represented as employer production ownership.

## Core artifacts

- **P1+ Recommendation System** — multi-channel retrieval, ANN, LTR/industrial ranking, constraints, causal/off-policy evaluation, sequential models, serving, monitoring, and vertical cases.
- **P2+ Search Engine** — lexical/neural retrieval, ANN, hybrid fusion, LTR/reranking, query understanding, relevance science, distributed/index lifecycle, serving, and vertical cases.
- **Shared Retrieval/Ranking Lab** — reusable metrics, ANN benchmarks, replay, ranking/evaluation utilities, with domain-specific objectives preserved.
- **Research/Expert Repo** — Search reproduction, Recommendation reproduction, LTR reproduction, original extension, failure atlases, design memos, and oral-board repairs.

# Phase I — Shared Retrieval & Ranking Foundations

## Week 1 — Jan 3–Jan 9, 2027 — Shared retrieval/ranking architecture + lexical index foundations

### Knowledge — first exposure
- **R01 — Two-stage and multi-stage recommender architecture**
- **R02 — Explicit, implicit, and exposure-conditioned feedback**
- **S01 — End-to-end search architecture**
- **S02 — Inverted indexes, postings, and positional information**

### Coding — first exposure
- **SRCH-01 — Inverted Index + BM25 + Positions**

### Detailed weekly tasks
- Build or extend the shared retrieval/ranking lab so Search and Recommendation reuse evaluation/benchmark primitives without sharing objectives blindly.
- Complete the scheduled coding IDs and benchmark at least one quality/resource trade-off.
- Cold-retest one prior D3/coding item and one 2026 generalist-core item when due.
- Write a short mechanism-first design note connecting this week's Search and Recommendation concepts.

### Explicit interview problems
- **Model Design:** Choose a two-stage recommendation architecture and a lexical-search baseline for a new product with little behavioral data. Explain what should remain simple initially.
- **System Design:** You have 120 ms end-to-end for a two-stage recommender. Candidate retrieval is 35 ms, feature hydration 25 ms, and ranker inference 70 ms. Redesign the stage budgets and fallback behavior.
- **Debugging / Incident:** CTR drops after deployment while candidate recall is unchanged. Given score histograms, feature latency, and segment metrics, identify whether the fault is ranker, features, or serving.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 2 — Jan 10–Jan 16, 2027 — Data correctness, metric contracts, BM25/analyzers

### Knowledge — first exposure
- **R03 — Training-set construction and point-in-time correctness**
- **R04 — Recommendation metrics and metric contracts**
- **S03 — BM25, BM25F, exact match, phrase, and proximity**
- **S04 — Analyzers and linguistic normalization**

### Coding — first exposure
- **REC-01 — Ranking Metrics Suite**
- **REC-02 — Point-in-Time Recommendation Dataset**

### Detailed weekly tasks
- Build or extend the shared retrieval/ranking lab so Search and Recommendation reuse evaluation/benchmark primitives without sharing objectives blindly.
- Complete the scheduled coding IDs and benchmark at least one quality/resource trade-off.
- Cold-retest one prior D3/coding item and one 2026 generalist-core item when due.
- Write a short mechanism-first design note connecting this week's Search and Recommendation concepts.

### Explicit interview problems
- **Model Design:** Choose labels/metrics for a recommendation system where impressions, clicks, and purchases have different delays, and define what the first search relevance metric contract should be.
- **System Design:** Design a point-in-time training pipeline that can rebuild yesterday’s model exactly while late events arrive continuously.
- **Debugging / Incident:** Offline metrics improve, but only because future information leaked into training rows. Find the leakage from event timestamps and joins.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 3 — Jan 17–Jan 23, 2027 — Cold start, candidate sources, query intent/execution

### Knowledge — first exposure
- **R05 — Cold start and bootstrap strategies**
- **R06 — Collaborative, content, co-visitation, graph, and hybrid retrieval**
- **S05 — Query intent and query-class routing**
- **S06 — Posting-list algorithms**

### Coding — first exposure
- **SRCH-05 — Spelling + Noisy-Channel Correction**
- **SRCH-06 — Autocomplete / Typeahead**

### Detailed weekly tasks
- Build or extend the shared retrieval/ranking lab so Search and Recommendation reuse evaluation/benchmark primitives without sharing objectives blindly.
- Complete the scheduled coding IDs and benchmark at least one quality/resource trade-off.
- Cold-retest one prior D3/coding item and one 2026 generalist-core item when due.
- Write a short mechanism-first design note connecting this week's Search and Recommendation concepts.

### Explicit interview problems
- **Model Design:** Choose candidate sources for a cold-start-heavy recommender and query-routing rules for exact-ID vs informational search.
- **System Design:** Design candidate/query routing that supports exact-ID search and personalized recommendation with shared infrastructure but different SLOs.
- **Debugging / Incident:** Exact-ID queries begin returning semantic matches above the identifier. Diagnose analyzer/routing regression.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 4 — Jan 24–Jan 30, 2027 — MF/two-tower foundations + WAND/index lifecycle gate

### Knowledge — first exposure
- **R07 — Matrix factorization and implicit objectives**
- **R08 — Two-tower retrieval**
- **S07 — WAND and Block-Max WAND**
- **S08 — Index segments, refresh, merges, deletes, compaction**

### Coding — first exposure
- **REC-03 — Implicit Matrix Factorization**
- **REC-05 — Two-Tower Retrieval**
- **SRCH-02 — Posting Execution + WAND/BMW**
- **SRCH-03 — Segmented / Versioned Index Lifecycle**

### Detailed weekly tasks
- Build or extend the shared retrieval/ranking lab so Search and Recommendation reuse evaluation/benchmark primitives without sharing objectives blindly.
- Complete the scheduled coding IDs and benchmark at least one quality/resource trade-off.
- Cold-retest one prior D3/coding item and one 2026 generalist-core item when due.
- Write a short mechanism-first design note connecting this week's Search and Recommendation concepts.

### Explicit interview problems
- **Model Design:** Choose MF vs two-tower retrieval, and decide when WAND-style pruning is worth operational complexity.
- **System Design:** Design ANN/index refresh so a two-tower model can roll forward atomically without mixed embedding/index versions.
- **Debugging / Incident:** ANN recall suddenly drops after model rollout while exact retrieval is fine. Diagnose embedding/index version mismatch.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Shared retrieval/ranking foundations gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

# Phase II — Search / IR Depth

## Week 5 — Jan 31–Feb 6, 2027 — Distributed search + facets + dense retrieval

### Knowledge — first exposure
- **S09 — Distributed lexical search**
- **S10 — Facets, filters, aggregations, collapse, and canonicalization**
- **S11 — Dense bi-encoder retrieval**

### Coding — first exposure
- **SRCH-04 — Distributed Search Coordinator**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose between distributed lexical retrieval, dense retrieval, or hybrid retrieval for a mixed catalog with structured filters.
- **System Design:** Design distributed search for 20k QPS, 12 shards/query, p99 < 150 ms, and partial-shard failure.
- **Debugging / Incident:** p99 doubles although average shard latency is unchanged. Diagnose tail amplification / one hot or slow shard.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 6 — Feb 7–Feb 13, 2027 — Hard negatives + learned sparse retrieval

### Knowledge — first exposure
- **S12 — Hard-negative mining for search**
- **S13 — Learned sparse retrieval**
- **S14 — Late-interaction retrieval**

### Coding — first exposure
- **SRCH-07 — MinHash / LSH Dedup**
- **SRCH-08 — Dense Bi-Encoder Retrieval**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose hard-negative strategy and learned-sparse vs dense retrieval for a domain with many near-duplicate documents.
- **System Design:** Design a negative-mining pipeline that refreshes hard negatives without making training depend on stale model/index versions.
- **Debugging / Incident:** Dense-retrieval training loss improves but retrieval recall worsens. Diagnose false negatives / over-hard negatives / distribution shift.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 7 — Feb 14–Feb 20, 2027 — Late interaction + cross-encoder reranking

### Knowledge — first exposure
- **S15 — Cross-encoder reranking**
- **S16 — Retrieval/ranker distillation**
- **S17 — ANN design: HNSW, IVF, PQ/OPQ, partitioned search**

### Coding — first exposure
- **SRCH-09 — Learned Sparse Retrieval**
- **SRCH-10 — Late-Interaction Retrieval**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose late interaction vs cross-encoder reranking under a strict candidate budget.
- **System Design:** Design a retrieval→reranker cascade where only 40 ms is available for reranking and candidate count is tunable.
- **Debugging / Incident:** Reranker NDCG is strong offline but production latency causes frequent timeout fallbacks. Determine whether to shrink candidates, distill, or remove features.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 8 — Feb 21–Feb 27, 2027 — Distillation + ANN design

### Knowledge — first exposure
- **S18 — Vector compression and quantization**
- **S19 — Filtered ANN**
- **S20 — Vector-index lifecycle**

### Coding — first exposure
- **SRCH-11 — ANN Benchmark**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose ANN family and compression strategy for 100M vectors with memory limits and frequent updates.
- **System Design:** Design a 100M-vector service under a fixed RAM budget; include build time, replicas, update strategy, and rollback.
- **Debugging / Incident:** ANN memory drops after compression, but recall collapses on one segment. Diagnose quantization/filtered-ANN interaction.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Neural retrieval + ANN gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 9 — Feb 28–Mar 6, 2027 — Vector compression + filtered ANN + vector lifecycle

### Knowledge — first exposure
- **S21 — Vector search at scale**
- **S22 — Hybrid lexical+dense retrieval**
- **S23 — Query rewriting and simplification**

### Coding — first exposure
- **SRCH-12 — Hybrid Retrieval Fusion**
- **SRCH-13 — Cross-Encoder / Neural Reranker**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose hybrid-fusion strategy when BM25 and dense retrieval win on different query cohorts.
- **System Design:** Design hybrid lexical+dense serving with separate indexes, score fusion, query routing, and consistent versioning.
- **Debugging / Incident:** Hybrid search aggregate NDCG rises while exact-ID queries regress. Localize fusion/query-routing issue.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 10 — Mar 7–Mar 13, 2027 — Vector scale + hybrid retrieval + query rewriting

### Knowledge — first exposure
- **S24 — Spelling correction and noisy-channel search**
- **S25 — Zero-result and low-quality recovery**
- **S26 — Query/document expansion and pseudo-relevance feedback**

### Coding — first exposure
- **SRCH-14 — Search LTR / LambdaMART**
- **SRCH-15 — Judgment + Click-Bias Lab**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose a rewrite/spelling policy when correction helps tail queries but hurts exact identifiers.
- **System Design:** Design query-rewrite service with confidence thresholds, caching, rollback, and exact-ID protections.
- **Debugging / Incident:** Spell correction improves tail success rate but corrupts SKUs and names. Diagnose confidence/guardrail failure.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 11 — Mar 14–Mar 20, 2027 — Spelling + zero-result recovery + expansion

### Knowledge — first exposure
- **S27 — Autocomplete and typeahead**
- **S28 — Search learning-to-rank**
- **S29 — Search feature architecture**

### Coding — first exposure
- **SRCH-16 — Query Rewrite Guardrails**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose zero-result recovery and query/document expansion policies while controlling query drift.
- **System Design:** Design zero-result recovery so fallback expansion cannot create unbounded latency or irrelevant broadening.
- **Debugging / Incident:** Zero-result rate falls but abandonment rises. Determine whether fallback expansion is returning low-quality results.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 12 — Mar 21–Mar 27, 2027 — Autocomplete + Search LTR + feature architecture

### Knowledge — first exposure
- **S30 — Judgment collection and pooling**
- **S31 — Click models and behavior bias**
- **S32 — Counterfactual and unbiased learning-to-rank for search**

### Coding — first exposure
- **SRCH-17 — Search Evaluation + Replay Harness**
- **SRCH-18 — Product / E-Commerce Search Case**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose LambdaMART vs neural reranking for a search surface with strong tabular features and tight latency.
- **System Design:** Design search LTR serving where feature hydration dominates latency; decide precompute vs online features and candidate counts.
- **Debugging / Incident:** Search LTR scores look healthy but one feature is silently stale online. Detect offline/online skew.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Search ranking/relevance gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 13 — Mar 28–Apr 3, 2027 — Judgments + click models + counterfactual LTR

### Knowledge — first exposure
- **S33 — Search evaluation science**
- **S34 — Commercial objectives and personalization**
- **S35 — Multilingual and cross-lingual search**

### Coding — first exposure
- **SRCH-19 — Video / Media Search Case**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose click-debiasing method and whether behavior logs are suitable for training or only evaluation.
- **System Design:** Design judgment/click pipelines with label versioning, propensity logging, and reproducible offline evaluation.
- **Debugging / Incident:** Click-trained model gains offline but loses online. Diagnose position/examination bias or logging-policy mismatch.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 14 — Apr 4–Apr 10, 2027 — Search evaluation + personalization + multilingual IR

### Knowledge — first exposure
- **S36 — Federated and blended search**
- **S37 — E-commerce/product search**
- **S38 — Video/media/content search**

### Coding — first exposure
- **SRCH-20 — Local / Geo Search Case**
- **SRCH-21 — Enterprise / ACL Search Case**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose personalization depth for search when aggregate relevance improves but long-tail users regress.
- **System Design:** Design personalized search while preserving cacheability and p99 under a shared cluster.
- **Debugging / Incident:** Personalization improves average metrics but hurts new users. Diagnose cold-start/segment evaluation gap.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 15 — Apr 11–Apr 17, 2027 — Federated search + product/media vertical search

### Knowledge — first exposure
- **S39 — Local/place search**
- **S40 — Enterprise/document search**
- **S41 — Marketplace search**

### Coding — first exposure
- **SRCH-22 — Search Serving + Cache Simulator**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Cold-retain prior ANN/LTR/relevance-science material rather than broad rereading.

### Explicit interview problems
- **Model Design:** Choose ranking/blending across federated verticals with incompatible score distributions.
- **System Design:** Design federated search across three verticals with separate backends and a 180 ms total latency budget.
- **Debugging / Incident:** One federated vertical dominates results after a scoring change. Diagnose score-scale/calibration/blending failure.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 16 — Apr 18–Apr 24, 2027 — Local/enterprise/marketplace/sponsored/multimodal search capstone

### Knowledge — first exposure
- **S42 — Ads/sponsored search ranking**
- **S43 — Multimodal search without generative models**
- **S44 — Search latency engineering**

### Coding — first exposure
- **SRCH-23 — Search Incident Lab**
- **SRCH-24 — End-to-End Search Capstone**

### Detailed weekly tasks
- Extend P2+ Search with this week's retrieval/index/ranking capabilities; preserve reproducible baselines and per-query-class slices.
- Complete scheduled Search coding and report relevance plus latency/memory/indexing cost where applicable.
- Inject at least one failure or adversarial query and diagnose it from logs/result diffs.
- Complete SRCH-24 and run a 120-minute Search architecture defense covering indexing, retrieval, LTR, vertical behavior, serving, experiments, and rollback.

### Explicit interview problems
- **Model Design:** Choose a vertical-specific ranking stack for product/media/local/enterprise/sponsored search and justify what differs.
- **System Design:** Design P2+ to survive index rebuilds, reranker outages, and partial shard failures under production-like SLOs.
- **Debugging / Incident:** Search relevance drops after merge/index rollout. Use version metadata, replay, and result diffs to isolate the change.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Search Capstone / Search Gate I
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

# Phase III — Recommendation / Ranking Depth

## Week 17 — Apr 25–May 1, 2027 — Negative sampling + ANN candidates + embedding systems

### Knowledge — first exposure
- **R09 — Negative sampling and false negatives**
- **R10 — ANN for recommendation**
- **R11 — Large embedding-table systems**

### Coding — first exposure
- **REC-04 — Negative Sampling Lab**
- **REC-06 — ANN Candidate Benchmark**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose negative-sampling strategy and ANN candidate method for a recommender with extreme popularity skew.
- **System Design:** Design recommendation retrieval with three candidate sources, 50 ms retrieval budget, and 5M-item catalog.
- **Debugging / Incident:** Recommendation recall falls only for tail items. Diagnose popularity-biased negatives or ANN/index partitioning.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 18 — May 2–May 8, 2027 — Candidate blending + core LTR + LambdaMART

### Knowledge — first exposure
- **R12 — Candidate blending and adaptive retrieval budgets**
- **R13 — Pointwise, pairwise, and listwise learning to rank**
- **R14 — Gradient-boosted trees and LambdaMART for ranking**

### Coding — first exposure
- **REC-07 — Multi-Channel Candidate Fan-Out**
- **REC-08 — Pointwise + Pairwise Ranker**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose pointwise, pairwise, or LambdaMART ranking for a recommendation surface with calibrated probabilities used downstream.
- **System Design:** Design a two-stage recommender with pre-rank + heavy ranker where p99 is capped at 100 ms; allocate candidate counts and compute budgets.
- **Debugging / Incident:** New ranker improves NDCG offline but conversion falls online. Diagnose metric/objective mismatch or calibration issue.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 19 — May 9–May 15, 2027 — Deep ranking interactions + DCN + multi-task ranking

### Knowledge — first exposure
- **R15 — Wide & Deep, FM/DeepFM, DLRM, and feature interactions**
- **R16 — DCN / explicit feature crossing**
- **R17 — Multi-task ranking: shared-bottom, MMoE, PLE-style**

### Coding — first exposure
- **REC-09 — LambdaMART / Tree Ranker**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose DCN/DLRM-style interactions vs a simpler MLP/tree ranker under sparse+dense features.
- **System Design:** Design sparse+dense feature serving for DLRM/DCN-style ranking without blowing network or feature-store latency.
- **Debugging / Incident:** Multi-task ranker improves click task but harms conversion. Diagnose negative transfer / loss weighting / shared representation.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 20 — May 16–May 22, 2027 — Calibration + feature systems + diversity

### Knowledge — first exposure
- **R18 — Calibration, uncertainty, and score semantics**
- **R19 — Feature architecture and leakage**
- **R20 — Diversity, novelty, redundancy, and MMR**

### Coding — first exposure
- **REC-10 — Feature-Cross Ranker**
- **REC-11 — Multi-Task Ranking with Expert Sharing**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose calibration and diversity strategy when the ranker is accurate but over-concentrates exposure.
- **System Design:** Design calibration + diversity reranking that fits inside a 15 ms post-rank budget.
- **Debugging / Incident:** Diversity improves but overall satisfaction drops. Diagnose over-aggressive reranking or bad similarity definition.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Industrial recommendation ranking gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 21 — May 23–May 29, 2027 — Constraints + multi-objective + slate optimization

### Knowledge — first exposure
- **R21 — Hard constraints and slate construction**
- **R22 — Multi-objective ranking and Pareto trade-offs**
- **R23 — Slate-level interactions and page/feed optimization**

### Coding — first exposure
- **REC-12 — Diversity + Constraint Reranker**
- **REC-13 — Counterfactual Evaluation**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose hard constraints vs learned multi-objective optimization for a feed with creator and category limits.
- **System Design:** Design a constraint layer that guarantees policy/category caps even when the main ranker or feature service fails.
- **Debugging / Incident:** Policy constraints are occasionally violated under timeout. Diagnose whether constraints are applied before/after fallback.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 22 — May 30–Jun 5, 2027 — Marketplace effects + exposure bias + counterfactual evaluation

### Knowledge — first exposure
- **R24 — Marketplace and provider-side recommendation**
- **R25 — Exposure, position, and selection bias**
- **R26 — IPS, SNIPS, doubly robust estimation, and overlap**

### Coding — first exposure
- **REC-14 — Bandit Simulator**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose counterfactual estimator when propensity overlap is weak and logged policy is partially deterministic.
- **System Design:** Design logging for IPS/SNIPS/DR and future policy evaluation before launching a new recommendation policy.
- **Debugging / Incident:** IPS estimate swings wildly across runs. Diagnose poor overlap, extreme weights, or propensity estimation errors.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 23 — Jun 6–Jun 12, 2027 — Counterfactual training + experiments + exploration

### Knowledge — first exposure
- **R27 — Counterfactual learning-to-rank**
- **R28 — A/B tests, interleaving, switchbacks, and interference**
- **R29 — Exploration: epsilon-greedy, UCB, Thompson, contextual bandits**

### Coding — first exposure
- **REC-15 — SASRec-Style Sequential Recommendation**
- **REC-16 — Masked Sequential Recommendation**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose exploration policy and experiment design for a recommendation system with delayed rewards.
- **System Design:** Design an online experimentation platform supporting A/B, switchback, and bandit exploration with delayed rewards.
- **Debugging / Incident:** Bandit exploration appears to improve reward but logging is incomplete. Determine whether OPE is invalid.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 24 — Jun 13–Jun 19, 2027 — OPE + long-horizon reward + session recommendation

### Knowledge — first exposure
- **R30 — Off-policy evaluation for new policies**
- **R31 — Long-horizon objectives and delayed reward**
- **R32 — Session-based recommendation fundamentals**

### Coding — first exposure
- **REC-17 — Graph Recommendation Baseline**
- **REC-18 — Video / Feed Recommendation Case**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose SASRec-style sequential modeling vs simpler session/co-visitation baselines.
- **System Design:** Design session-state serving for sequential recommendation under high QPS and bounded per-user state.
- **Debugging / Incident:** Sequential model beats baseline only under sampled negatives, not full-catalog eval. Diagnose evaluation pathology.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Counterfactual/online-learning gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 25 — Jun 20–Jun 26, 2027 — SASRec + BERT4Rec + graph recommendation

### Knowledge — first exposure
- **R33 — SASRec-style autoregressive sequential recommendation**
- **R34 — BERT4Rec-style masked sequential recommendation**
- **R35 — Graph recommendation**

### Coding — first exposure
- **REC-19 — E-Commerce / Item Recommendation Case**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose autoregressive vs masked sequential modeling and whether graph recommendation adds meaningful signal.
- **System Design:** Design sequence/graph recommendation serving with embedding/index freshness and online state consistency.
- **Debugging / Incident:** Graph model degrades after adding more propagation layers. Diagnose oversmoothing / stale graph / leakage.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 26 — Jun 27–Jul 3, 2027 — Video/feed + social/photo + e-commerce recommendation

### Knowledge — first exposure
- **R36 — Feed and video recommendation**
- **R37 — Social/photo/content recommendation**
- **R38 — E-commerce and item recommendation**

### Coding — first exposure
- **REC-20 — Ads Ranking Case**
- **REC-21 — Recommendation Evaluation + Slice Harness**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose objective/architecture differences for video/feed vs social/photo vs e-commerce recommendation.
- **System Design:** Design a feed/video serving stack with strict freshness and 80 ms ranking budget.
- **Debugging / Incident:** Feed engagement rises while hides/reports and creator concentration worsen. Diagnose objective imbalance.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 27 — Jul 4–Jul 10, 2027 — Ads + notification + multi-surface recommendation

### Knowledge — first exposure
- **R39 — Ads recommendation and ranking**
- **R40 — Notification and push recommendation**
- **R41 — Homepage/module and multi-surface recommendation**

### Coding — first exposure
- **REC-22 — Recommendation Serving Simulator**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Cold-retain Search and 2026 generalist fundamentals through mixed review.

### Explicit interview problems
- **Model Design:** Choose ads ranking objective when CTR, CVR, bid/value, pacing, and frequency caps conflict.
- **System Design:** Design ads ranking with eligibility, pCTR/pCVR inference, pacing, auction, and frequency caps under 50–100 ms.
- **Debugging / Incident:** Ads CTR rises but advertiser ROI and user satisfaction fall. Diagnose value/calibration/pacing/frequency issues.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 28 — Jul 11–Jul 17, 2027 — Multimodal rec + serving/freshness capstone

### Knowledge — first exposure
- **R42 — Multimodal recommendation without generative models**
- **R43 — Recommendation serving architecture**
- **R44 — Model/index/feature consistency and freshness**

### Coding — first exposure
- **REC-23 — Recommendation Incident Lab**
- **REC-24 — End-to-End Recommendation Capstone**

### Detailed weekly tasks
- Extend P1+ Recommendation with this week's retrieval/ranking/causal/sequential capabilities and maintain temporal correctness.
- Complete scheduled Recommendation coding and report segment-level quality plus serving/resource implications.
- Run at least one objective-conflict, bias, or failure-mode experiment rather than only a clean benchmark.
- Complete REC-24 and run a 120-minute Recommendation architecture defense spanning data, retrieval, LTR, objectives, experiments, serving, and rollback.

### Explicit interview problems
- **Model Design:** Choose serving cascade and freshness strategy for a multimodal recommendation stack.
- **System Design:** Design P1+ serving with fan-out, hydration, ranking, reranking, caches, timeouts, fallbacks, and version contracts.
- **Debugging / Incident:** Recommendation p99 spikes after increasing candidate count. Use per-stage latency to identify the bottleneck and redesign.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Recommendation Capstone / Recommendation Gate I
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

# Phase IV — Advanced Search Operations & Staff Cases

## Week 29 — Jul 18–Jul 24, 2027 — Search caching + observability + adversarial retrieval

### Knowledge — first exposure
- **S45 — Caching and query-result reuse**
- **S46 — Observability, replay, and relevance incidents**
- **S47 — Security, spam, and adversarial retrieval**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P2+ for caching, freshness, observability, adversarial behavior, cost, and incident response.
- Run a realistic relevance/latency failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x scale change.
- Use Staff architecture cases to force changed-constraint redesign rather than memorized diagrams.

### Explicit interview problems
- **Model Design:** Choose cache layers for search without violating freshness/personalization requirements.
- **System Design:** Design multi-layer caching for Search and quantify the freshness/latency trade-off.
- **Debugging / Incident:** Cache hit rate falls after personalization launch and p99 jumps. Diagnose keying/invalidation/personalization interaction.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 30 — Jul 25–Jul 31, 2027 — Freshness/incremental indexing + experimentation + capacity

### Knowledge — first exposure
- **S48 — Freshness and incremental indexing**
- **S49 — Search experimentation under interference**
- **S50 — Capacity, cost, and scaling**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P2+ for caching, freshness, observability, adversarial behavior, cost, and incident response.
- Run a realistic relevance/latency failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x scale change.
- Use Staff architecture cases to force changed-constraint redesign rather than memorized diagrams.

### Explicit interview problems
- **Model Design:** Choose incremental indexing architecture and experiment unit under rapidly changing content.
- **System Design:** Design near-real-time indexing with delta segments, merge policy, backfill, and rollback.
- **Debugging / Incident:** Fresh content is missing from search while old content remains correct. Diagnose indexing/refresh/merge path.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 31 — Aug 1–Aug 7, 2027 — Search evaluation pathologies + incident response + e-commerce Staff case

### Knowledge — first exposure
- **S51 — Offline evaluation pathologies**
- **S52 — Search incident response and rollback**
- **S53 — E-commerce Staff architecture case**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P2+ for caching, freshness, observability, adversarial behavior, cost, and incident response.
- Run a realistic relevance/latency failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x scale change.
- Use Staff architecture cases to force changed-constraint redesign rather than memorized diagrams.

### Explicit interview problems
- **Model Design:** Choose which offline metrics and slices should block launch despite aggregate improvement.
- **System Design:** Design launch gates and replay infrastructure that can prevent a bad relevance rollout.
- **Debugging / Incident:** Offline relevance improves because judged pool coverage changed. Diagnose evaluation-set contamination/bias.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 32 — Aug 8–Aug 14, 2027 — Media/enterprise/local/general Search Staff defenses

### Knowledge — first exposure
- **S54 — Media/social Staff architecture case**
- **S55 — Enterprise/local Staff architecture case**
- **S56 — General Staff-level search architecture case**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P2+ for caching, freshness, observability, adversarial behavior, cost, and incident response.
- Run a realistic relevance/latency failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x scale change.
- Use Staff architecture cases to force changed-constraint redesign rather than memorized diagrams.

### Explicit interview problems
- **Model Design:** Choose final Staff-level search architecture for one of: media, enterprise, local, or general web/product search.
- **System Design:** Design a full Search system for 10× traffic and explain shard count, replicas, index memory, reranker capacity, and failover.
- **Debugging / Incident:** Search p99 is fine, but relevance fails only after partial shard timeouts. Diagnose merge/fallback behavior.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Search final Staff-depth gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

# Phase V — Advanced Recommendation Operations & Staff Cases

## Week 33 — Aug 15–Aug 21, 2027 — Recommendation monitoring + capacity + privacy/safety

### Knowledge — first exposure
- **R45 — Monitoring and failure diagnosis**
- **R46 — Capacity, cost, and scaling**
- **R47 — Privacy, safety, and policy constraints in recommendation**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P1+ for monitoring, capacity, privacy/safety, fairness/exposure, causal reasoning, and incident response.
- Run a realistic ranking/candidate/feature failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x traffic/catalog change.
- Use vertical Staff cases to force objective and architecture changes across feed, commerce, and ads.

### Explicit interview problems
- **Model Design:** Choose monitoring signals and capacity controls for a recommender before a 10× traffic event.
- **System Design:** Design recommendation monitoring and autoscaling for 10× traffic without violating candidate/ranker SLOs.
- **Debugging / Incident:** Recommendation score distributions shift without model change. Diagnose upstream feature/data version drift.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 34 — Aug 22–Aug 28, 2027 — Exposure fairness + causal/uplift + distillation

### Knowledge — first exposure
- **R48 — Fairness, exposure, and creator/seller health**
- **R49 — Causal recommendation and uplift thinking**
- **R50 — Retriever-ranker distillation and compression**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P1+ for monitoring, capacity, privacy/safety, fairness/exposure, causal reasoning, and incident response.
- Run a realistic ranking/candidate/feature failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x traffic/catalog change.
- Use vertical Staff cases to force objective and architecture changes across feed, commerce, and ads.

### Explicit interview problems
- **Model Design:** Choose fairness/exposure interventions and causal/uplift framing for a marketplace recommender.
- **System Design:** Design a marketplace recommendation service with exposure constraints, privacy controls, and causal measurement hooks.
- **Debugging / Incident:** Provider exposure becomes concentrated despite stable user metrics. Diagnose ecosystem metric blind spot.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 35 — Aug 29–Sep 4, 2027 — Offline evaluation pathology + incident response + video Staff case

### Knowledge — first exposure
- **R51 — Offline evaluation pathologies**
- **R52 — Incident response and rollback for ranking systems**
- **R53 — Video/feed Staff architecture case**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P1+ for monitoring, capacity, privacy/safety, fairness/exposure, causal reasoning, and incident response.
- Run a realistic ranking/candidate/feature failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x traffic/catalog change.
- Use vertical Staff cases to force objective and architecture changes across feed, commerce, and ads.

### Explicit interview problems
- **Model Design:** Choose evaluation protocol robust to sampled-negative and temporal leakage pathologies.
- **System Design:** Design a safe model/index rollout path that prevents offline-evaluation pathologies from becoming online incidents.
- **Debugging / Incident:** Offline gains disappear under full-catalog temporal evaluation. Diagnose sampled-negative or leakage artifact.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

---

## Week 36 — Sep 5–Sep 11, 2027 — Commerce/ads/general Recommendation Staff defenses

### Knowledge — first exposure
- **R54 — E-commerce/marketplace Staff architecture case**
- **R55 — Ads Staff architecture case**
- **R56 — General Staff-level recommendation architecture case**

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Harden P1+ for monitoring, capacity, privacy/safety, fairness/exposure, causal reasoning, and incident response.
- Run a realistic ranking/candidate/feature failure drill and produce replay evidence plus rollback decision.
- Perform capacity arithmetic under at least one 10x traffic/catalog change.
- Use vertical Staff cases to force objective and architecture changes across feed, commerce, and ads.

### Explicit interview problems
- **Model Design:** Choose final Staff-level recommendation architecture for commerce, ads, feed, or general personalization.
- **System Design:** Design a complete Staff-level recommender with capacity, freshness, versioning, experimentation, and rollback.
- **Debugging / Incident:** After model rollout, only one device/region regresses. Diagnose feature availability, cache, or serving-version skew.

### Mastery / review
- Complete due D3/coding re-attempts before optional reading.
- Include one mixed-context cold item from the other specialization and one 2026 generalist item when due.

### Milestone — Recommendation final Staff-depth gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

# Phase VI — Vertical Transfer, Research, Reliability & Final Validation

## Week 37 — Sep 12–Sep 18, 2027 — Vertical transfer lab — video/feed

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Use one common data/serving skeleton to compare short-video/feed objectives, sequence state, freshness, diversity, creator effects, and long-horizon metrics.
- Run an ablation showing how optimizing clicks alone differs from watch/completion/satisfaction.
- Defend candidate generation and ranking under a strict feed latency budget.
- Produce a vertical-transfer memo: what changed from generic recommendation and why.

### Explicit interview problems
- **Model Design:** Choose model/objective changes required to adapt a generic recommender into a video/feed system.
- **System Design:** Design a short-video feed where retrieval, pre-rank, heavy-rank, and slate rerank must fit within a fixed latency envelope.
- **Debugging / Incident:** Feed latency stays within budget but watch-time falls after reducing candidates. Diagnose retrieval ceiling vs ranker quality.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 38 — Sep 19–Sep 25, 2027 — Vertical transfer lab — e-commerce/items

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Build/extend a commerce item-recommendation case with inventory, price, conversion/value, substitutes/complements, seller exposure, and promotions.
- Run counterfactual/experiment thought exercises for changing ranking objectives.
- Stress catalog churn and cold-start behavior.
- Defend the system as both a user-ranking and marketplace system.

### Explicit interview problems
- **Model Design:** Choose ranking and candidate architecture for commerce when inventory and conversion value change rapidly.
- **System Design:** Design commerce recommendation where inventory invalidation can happen faster than full index rebuilds.
- **Debugging / Incident:** Commerce recommender surfaces unavailable products. Diagnose freshness/availability constraint placement.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 39 — Sep 26–Oct 2, 2027 — Vertical transfer lab — social/photo/content

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Build/extend a social/photo/content case using graph affinity, freshness, creator signals, saves/shares, hides/reports, and diversity.
- Compare graph/co-visitation/content-embedding candidate sources.
- Test repeated-exposure and creator concentration failures.
- Explain when social graph should dominate or defer to content relevance.

### Explicit interview problems
- **Model Design:** Choose graph/content/freshness weighting for a social/photo feed.
- **System Design:** Design a social feed with freshness tiers, graph features, content embeddings, and creator-diversity constraints.
- **Debugging / Incident:** Social feed repeats the same creators despite diversity target. Diagnose candidate-source concentration or reranker configuration.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 40 — Oct 3–Oct 9, 2027 — Vertical transfer lab — ads and sponsored ranking

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Compare organic recommendation, ad recommendation, and sponsored search using the same ranking vocabulary but different economics/constraints.
- Work through pCTR/pCVR calibration, value ranking, budget/pacing, auction/frequency-cap behavior, and delayed conversions.
- Run an ads incident/measurement case.
- Produce an 'organic vs ads' ranking decision memo.

### Explicit interview problems
- **Model Design:** Choose organic vs sponsored ranking boundaries and what should be jointly modeled vs separated.
- **System Design:** Design sponsored ranking with organic/sponsored blending, budget/pacing, and strict user-experience guardrails.
- **Debugging / Incident:** Sponsored ranking consumes budget too early in the day. Diagnose pacing/value/calibration interaction.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 41 — Oct 10–Oct 16, 2027 — Vertical transfer lab — product and marketplace search

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Build/extend product and marketplace search with IDs, attributes, facets, availability, personalization, seller constraints, and revenue guardrails.
- Compare organic product search to item recommendation on the same catalog.
- Run search+recommendation cannibalization/consistency cases.
- Defend vertical metrics and experiment design.

### Explicit interview problems
- **Model Design:** Choose product-search vs product-recommendation architecture for the same commerce catalog.
- **System Design:** Design shared infra for product search and recommendation without coupling their release cadence or evaluation.
- **Debugging / Incident:** Product search and recommendation disagree badly on item availability. Diagnose shared-catalog/version inconsistency.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 42 — Oct 17–Oct 23, 2027 — Vertical transfer lab — media, local, and enterprise search

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Compare media search, local/place search, and enterprise/document search under multimodal, geo, ACL, and freshness constraints.
- For each vertical, identify which generic search assumptions break.
- Run one serving/filtering failure case per vertical.
- Produce a compact architecture-delta matrix.

### Explicit interview problems
- **Model Design:** Choose architecture differences across media, local, and enterprise search.
- **System Design:** Design separate media/local/enterprise search backends behind one federated gateway with independent SLOs.
- **Debugging / Incident:** Enterprise search leaks an unauthorized document in a cache hit. Diagnose ACL-filter/caching order.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 43 — Oct 24–Oct 30, 2027 — Unified Learning-to-Rank deep dive

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Deep-dive pointwise/pairwise/listwise objectives, LambdaMART, neural rankers, feature interactions, calibration, debiasing, reranking, and multi-task ranking across both domains.
- Reimplement or transfer one ranking primitive between Search and Recommendation and explain what must change.
- Run three changed-objective ranking cases.
- Gate: defend LTR choices from labels/objective/metric/serving constraints.

### Explicit interview problems
- **Model Design:** Choose the ranking objective/model family for three contrasting LTR scenarios and justify each choice.
- **System Design:** Design a common LTR platform serving tree and neural rankers with consistent feature/version contracts.
- **Debugging / Incident:** LambdaMART offline NDCG improves but online ranking is worse. Diagnose grouping/features/metric mismatch or stale features.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

### Milestone — Unified LTR gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 44 — Oct 31–Nov 6, 2027 — Counterfactual evaluation + experimentation gauntlet

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Run IPS/SNIPS/DR and click/exposure-bias exercises across both Search and Recommendation.
- Design A/B, interleaving, switchback, or cluster experiments for at least four interference structures.
- Construct one poor-overlap case where no offline estimator is trustworthy.
- Defend logging requirements before deployment.

### Explicit interview problems
- **Model Design:** Choose offline vs online/counterfactual evaluation strategy under several logging and interference regimes.
- **System Design:** Design a logging/experiment platform so counterfactual estimators remain valid months later.
- **Debugging / Incident:** Counterfactual estimate says policy B is better, A/B says worse. Diagnose overlap, propensities, interference, or logging drift.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 45 — Nov 7–Nov 13, 2027 — Scale, serving, freshness, and reliability gauntlet

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Run a unified failure gauntlet: stale index, mixed model/version, feature outage, hot shard, candidate collapse, latency spike, and bad analyzer/constraint rollout.
- Perform memory/QPS/p95-p99/cost arithmetic for both P1+ and P2+.
- Demonstrate fallback/degradation and rollback.
- Produce incident postmortems with preventive controls.

### Explicit interview problems
- **Model Design:** Choose which quality optimization to sacrifice first when scale/reliability constraints tighten.
- **System Design:** Design graceful degradation for Search and Recommendation when one dependency doubles latency or fails.
- **Debugging / Incident:** After 10× traffic, quality drops although models are unchanged. Diagnose load shedding, smaller candidate sets, stale caches, or feature timeouts.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

### Milestone — Reliability/scale gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 46 — Nov 14–Nov 20, 2027 — Search research reproduction

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Reproduce one important Search/IR result at feasible scale with strong baseline, ablation, negative finding, and operational implication.
- State corpus/query/judgment protocol precisely.
- Explain discrepancies from the reported result.
- Present a 30-minute Search research seminar.

### Explicit interview problems
- **Model Design:** Choose the strongest baseline and ablation plan for the Search reproduction.
- **System Design:** Design a reproducible Search research harness that can rerun old index/model versions.
- **Debugging / Incident:** Reproduced Search result fails on one query slice. Determine whether paper protocol hides the failure.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 47 — Nov 21–Nov 27, 2027 — Recommendation research reproduction

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Reproduce one important Recommendation/Ranking result at feasible scale with temporal/evaluation audit.
- Include a baseline and one non-default ablation.
- Check sampled-negative/exposure/leakage assumptions explicitly.
- Present a 30-minute Recommendation research seminar.

### Explicit interview problems
- **Model Design:** Choose the strongest baseline and evaluation protocol for the Recommendation reproduction.
- **System Design:** Design a reproducible Recommendation research harness with temporal snapshots and candidate reconstruction.
- **Debugging / Incident:** Reproduced Recommendation result disappears with strict temporal split. Diagnose protocol leakage/sampling assumptions.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 48 — Nov 28–Dec 4, 2027 — Ranking/LTR research reproduction

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Reproduce one ranking/LTR result applicable to Search or Recommendation.
- Compare at least two objective families or model families.
- Measure both ranking quality and serving/resource behavior.
- Explain whether the result transfers across both domains.

### Explicit interview problems
- **Model Design:** Choose a ranking/LTR reproduction whose result meaningfully transfers across Search and Recommendation.
- **System Design:** Design a ranking benchmark platform that compares quality and serving cost across model families.
- **Debugging / Incident:** LTR reproduction gains vanish after adding latency constraints. Diagnose whether quality result is operationally irrelevant.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 49 — Dec 5–Dec 11, 2027 — Original cross-domain retrieval/ranking experiment

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Preregister one cross-domain retrieval/ranking hypothesis with success/failure criteria.
- Run an original experiment with sensitivity analysis and negative results retained.
- Connect the finding to architecture or evaluation policy.
- Gate: defend experimental validity, not novelty theater.

### Explicit interview problems
- **Model Design:** Choose one falsifiable cross-domain retrieval/ranking hypothesis and a minimal decisive experiment.
- **System Design:** Design the original experiment so data, model, and serving versions are fully pinned and replayable.
- **Debugging / Incident:** Original experiment gives inconsistent results across seeds/slices. Diagnose underpowered design or hidden confounder.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

### Milestone — Research/originality gate
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

## Week 50 — Dec 12–Dec 18, 2027 — Teaching + incident-response boards

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Teach one advanced Search topic and one advanced Recommendation topic to a strong audience or recorded mock.
- Run two incident-response boards from telemetry only.
- Create a targeted repair queue from failures.
- Update failure atlases and design memos.

### Explicit interview problems
- **Model Design:** Choose two advanced topics to teach and defend from first principles without notes.
- **System Design:** Design observability needed for incident-style oral boards from telemetry only.
- **Debugging / Incident:** Given only traces and dashboards, diagnose one Search incident and one Recommendation incident end to end.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 51 — Dec 19–Dec 25, 2027 — Staff oral boards — Search and Recommendation

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Run one 120-minute Staff Search board and one 120-minute Staff Recommendation board.
- Require derivations/code sketches/capacity math/incident diagnosis/changed constraints.
- Repair only observed weaknesses.
- Do not add new syllabus topics.

### Explicit interview problems
- **Model Design:** Choose architecture alternatives under adversarial Staff-board constraints rather than defending one memorized stack.
- **System Design:** Design one architecture under normal load, then redesign after 10× QPS and half the latency budget.
- **Debugging / Incident:** During Staff board, a dependency failure invalidates your original design. Re-plan degradation/rollback live.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

---

## Week 52 — Dec 26–Dec 31, 2027 — Final integrated retrieval/ranking defense + 2028 depth plan

### Knowledge — first exposure
- No new bank conversations; mastery/transfer/research only.

### Coding — first exposure
- No new coding ID; use capacity for integration, cold mastery, research, or incident drills.

### Detailed weekly tasks
- Run one unified retrieval/ranking architecture defense spanning search query/user/session context, candidate retrieval, ANN/indexes, LTR, constraints, experiments, feedback, and operations.
- Score Search and Recommendation separately; a top score requires artifact + cold-defense evidence.
- Write remaining-unknowns memo and select one narrower 2028 Principal-depth direction.
- Final acceptance is evidence-based; calendar completion alone does not pass.

### Explicit interview problems
- **Model Design:** Choose a final integrated retrieval/ranking design under changed latency, freshness, scale, and business objectives.
- **System Design:** Design a unified retrieval/ranking platform while preserving independent Search and Recommendation objectives, versions, and rollback.
- **Debugging / Incident:** Final gauntlet: one latent data bug, one model regression, and one serving failure occur simultaneously; prioritize diagnosis and mitigation.

### Mastery / review
- Use evidence-backed targeted repair only; avoid broad rereading.
- Vertical/research/oral-board work must expose weak assumptions, not just produce polished artifacts.

### Milestone — Final Staff-depth acceptance
- Pass only with independent artifact/code + measurement + cold technical defense; completion alone does not pass.

---

# Coverage audit

- Search knowledge: **56/56** scheduled exactly once.
- Recommendation knowledge: **56/56** scheduled exactly once.
- Total knowledge: **112/112**.
- Search coding: **24/24** scheduled exactly once.
- Recommendation coding: **24/24** scheduled exactly once.
- Total coding: **48/48**.
- All new syllabus exposure ends by Week 36.

# Final acceptance criteria

- [ ] P1+ and P2+ are reproducible, benchmarked, tested, documented, failure-tested, and defensible.
- [ ] Can reason from first principles about lexical/neural retrieval, ANN, candidate generation, LTR, industrial ranking, relevance/evaluation, causal bias, experiments, and serving.
- [ ] Can transfer the ranking stack across video/feed, social/photo/content, e-commerce/items, ads/sponsored ranking, marketplace, local, enterprise, and media search.
- [ ] Can perform capacity, memory, QPS, latency, freshness, and cost arithmetic across Search and Recommendation.
- [ ] Can solve recurring **Model Design** cases by choosing objectives/architectures from evidence and constraints.
- [ ] Can solve recurring **System Design** cases with explicit latency/QPS/memory/freshness budgets, including multi-stage ranking under constrained latency.
- [ ] Can diagnose deliberately induced **Model/System Debugging** incidents involving relevance/ranking/index/feature/serving failures from evidence.
- [ ] Can reproduce and critique research, including negative findings and protocol weaknesses.
- [ ] Can teach and defend both specialties under adversarial Staff-level questioning.
- [ ] Remaining unknowns are explicitly documented; calendar completion alone does not imply mastery.

# Scope note

This roadmap targets **Staff-level technical knowledge and judgment in Search/IR and Recommendation/Ranking**. It deliberately does not maintain LLM specialization literacy in 2027. Professional Staff leveling still requires real production ownership, organizational scope, and impact.