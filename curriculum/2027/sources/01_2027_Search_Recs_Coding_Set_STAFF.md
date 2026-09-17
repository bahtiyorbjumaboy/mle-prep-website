# 2027 Search + Recommendation Specialized Coding Set — Staff-Depth

**Status:** ACTIVE 2027 CODING SET  
**Count:** 48 IDs = 24 Recommendation + 24 Search  
**Goal:** Implementation fluency supporting Staff-depth ownership of retrieval, ranking, relevance, personalization, serving, and experimentation.

## Contract

- LIVE problems should normally fit 30–60 minutes.
- EXTENDED_DRILL problems are staged multi-part implementations.
- CAPSTONE problems are multi-session system builds and count against project workload.
- Mastery requires: reason → implement → test → benchmark/validate → explain complexity/resources → handle follow-ups → later cold/transfer attempt.
- Reused primitives should transfer across Search and Recommendation; do not rebuild identical ANN/evaluation infrastructure without a domain-specific reason.
- No LLM/RAG coding IDs are part of 2027.

# Track — Recommendation / Ranking

## REC-01 — Ranking Metrics Suite
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement Precision@k, Recall@k, HitRate@k, MRR, MAP, DCG/IDCG/NDCG with graded relevance and configurable no-relevant-item policy.

**Core concepts:** ranking metrics; evaluator contracts

**Required mastery output/test:** Ideal ranking gives NDCG=1; irrelevant items beyond k do not change @k; edge-case semantics documented.

## REC-02 — Point-in-Time Recommendation Dataset
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build training examples from impressions/click/watch/cart/purchase events with temporal joins, attribution windows, deduplication, exposure-aware negatives, and temporal split.

**Core concepts:** data correctness; leakage; labels

**Required mastery output/test:** Tests fail on future leakage, late events, duplicates, click-without-impression, and window boundaries.

## REC-03 — Implicit Matrix Factorization
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement weighted implicit MF or BPR-style MF and compare to popularity.

**Core concepts:** MF; implicit objectives

**Required mastery output/test:** Synthetic low-rank data improves over popularity; cold-start behavior documented.

## REC-04 — Negative Sampling Lab
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement uniform, popularity, in-batch, hard-negative, and false-negative masking strategies with diagnostics.

**Core concepts:** sampling bias; false negatives

**Required mastery output/test:** Report realized distributions and show one over-hard-negative failure.

## REC-05 — Two-Tower Retrieval
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement user/query and item towers with normalized embeddings, temperature-scaled logits, in-batch negatives, and duplicate-positive masking.

**Core concepts:** two-tower; contrastive retrieval

**Required mastery output/test:** Synthetic pairs learn correct top-k; embedding norms and Recall@k reported.

## REC-06 — ANN Candidate Benchmark
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement exact top-k plus simplified IVF-like and graph/HNSW-like retrieval, then benchmark recall/latency/memory.

**Core concepts:** ANN; retrieval systems

**Required mastery output/test:** Produce recall@k vs p95 latency/memory curves and update/delete notes.

## REC-07 — Multi-Channel Candidate Fan-Out
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Combine popularity, co-visitation, content, graph, and embedding sources with quotas, deduplication, attribution, and fallback.

**Core concepts:** candidate blending

**Required mastery output/test:** Show union and marginal recall; test source failure and quota behavior.

## REC-08 — Pointwise + Pairwise Ranker
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement a calibrated pointwise scorer and pairwise ranker; compare log-loss/AUC/NDCG and score semantics.

**Core concepts:** LTR objectives; calibration

**Required mastery output/test:** Show a case where better log-loss does not imply better NDCG.

## REC-09 — LambdaMART / Tree Ranker
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Train/evaluate a tree-based ranking model with query/user grouping and ranking metrics; compare to pointwise baseline.

**Core concepts:** LambdaMART; GBDT ranking

**Required mastery output/test:** Correct group handling, feature importance caveats, and latency comparison documented.

## REC-10 — Feature-Cross Ranker
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement a compact DCN/DLRM-style ranker with sparse embeddings, dense features, and explicit interactions.

**Core concepts:** feature interaction; sparse+dense

**Required mastery output/test:** Ablate cross component; report parameter count, latency, and segment metrics.

## REC-11 — Multi-Task Ranking with Expert Sharing
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement shared-bottom and simplified MMoE/PLE-style rankers for two or more objectives.

**Core concepts:** multi-task ranking; negative transfer

**Required mastery output/test:** Construct conflicting tasks and show whether expert sharing mitigates negative transfer.

## REC-12 — Diversity + Constraint Reranker
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement MMR plus hard caps, availability, history suppression, freshness minimums, and deterministic fallback.

**Core concepts:** slate reranking; constraints

**Required mastery output/test:** All constraints hold; quantify relevance/diversity trade-off.

## REC-13 — Counterfactual Evaluation
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement IPS, SNIPS, clipping, effective sample size, and a doubly robust-style estimator on synthetic logs.

**Core concepts:** OPE; exposure bias

**Required mastery output/test:** Recover known policy values under good overlap and fail visibly under poor support.

## REC-14 — Bandit Simulator
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement epsilon-greedy, UCB, Thompson sampling, and a simple contextual bandit under non-stationarity.

**Core concepts:** exploration; regret

**Required mastery output/test:** Plot/measure regret and adaptation; log propensities for OPE.

## REC-15 — SASRec-Style Sequential Recommendation
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement a simplified causal self-attention next-item recommender.

**Core concepts:** sequential recommendation

**Required mastery output/test:** Compare against popularity/co-visitation/static embedding baselines with temporal splits.

## REC-16 — Masked Sequential Recommendation
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement BERT4Rec-style masked-item training and compare with autoregressive training.

**Core concepts:** sequence objectives

**Required mastery output/test:** Document masking/inference mismatch and avoid invalid sampled-negative evaluation.

## REC-17 — Graph Recommendation Baseline
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement a small graph collaborative-filtering/message-passing recommender and compare to co-visitation/MF.

**Core concepts:** graph recommendation

**Required mastery output/test:** Measure quality vs cost; document sampling/oversmoothing limitations.

## REC-18 — Video / Feed Recommendation Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build a small feed ranking pipeline with watch/completion/skip labels, session features, freshness, diversity, and long-horizon proxy metrics.

**Core concepts:** video/feed ranking

**Required mastery output/test:** Demonstrate objective conflicts and sequence/freshness effects.

## REC-19 — E-Commerce / Item Recommendation Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build a product recommender with conversion/value, availability, inventory, substitutes/complements, cold start, and seller constraints.

**Core concepts:** commerce recommendation

**Required mastery output/test:** Verify unavailable items never surface; measure relevance vs value/inventory effects.

## REC-20 — Ads Ranking Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build a simplified ad ranking stack with pCTR/pCVR/value, calibration, budget/pacing, frequency caps, and auction-like ordering.

**Core concepts:** ads ranking; calibration

**Required mastery output/test:** Show calibration/value interactions and budget/frequency behavior.

## REC-21 — Recommendation Evaluation + Slice Harness
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Create reusable offline evaluation with temporal slices, cold-start slices, calibration, coverage/diversity, bootstrap uncertainty, and candidate-source diagnostics.

**Core concepts:** evaluation science

**Required mastery output/test:** Detect deliberately injected aggregate-metric and sampling pathologies.

## REC-22 — Recommendation Serving Simulator
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Simulate candidate fan-out, feature hydration, rank/rerank, cache, timeout, fallback, and version contracts under a latency budget.

**Core concepts:** serving; reliability

**Required mastery output/test:** Measure p50/p95/p99 and verify deterministic degradation on partial failure.

## REC-23 — Recommendation Incident Lab
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Inject stale embeddings, feature outage, candidate collapse, score drift, and mixed versions; diagnose from telemetry and replay.

**Core concepts:** observability; incident response

**Required mastery output/test:** Root cause must be localized without privileged knowledge; rollback restores safe state.

## REC-24 — End-to-End Recommendation Capstone
**Level:** L3  
**Format:** CAPSTONE

**Implementation prompt:** Build a production-shaped recommendation system spanning logged data, multi-channel retrieval, ANN, ranking/LTR, constraints, evaluation, experimentation plan, serving, monitoring, and one vertical specialization.

**Core concepts:** integration

**Required mastery output/test:** Reproducible repo, benchmark tables, failure tests, architecture memo, and Staff-level defense.

# Track — Search / IR

## SRCH-01 — Inverted Index + BM25 + Positions
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement a field-aware inverted index with positions and BM25/BM25F-style scoring.

**Core concepts:** lexical retrieval

**Required mastery output/test:** Hand-computed fixtures verify TF/IDF/length/phrase behavior.

## SRCH-02 — Posting Execution + WAND/BMW
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement posting intersection/union and a simplified WAND/Block-Max WAND execution path.

**Core concepts:** query execution

**Required mastery output/test:** Exact top-k matches exhaustive scoring while reducing scored documents.

## SRCH-03 — Segmented / Versioned Index Lifecycle
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement or simulate immutable segments, refresh, deletes, merges, shadow versions, and atomic switch.

**Core concepts:** index lifecycle

**Required mastery output/test:** Version skew and delete/merge cases are tested.

## SRCH-04 — Distributed Search Coordinator
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement a toy scatter/gather coordinator with sharding, replicas, shard-local top-k, global merge, timeout, and partial-result policy.

**Core concepts:** distributed search

**Required mastery output/test:** Inject slow/failed shards and measure tail amplification.

## SRCH-05 — Spelling + Noisy-Channel Correction
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement edit/n-gram candidate generation plus probabilistic scoring and protect exact identifiers.

**Core concepts:** query understanding

**Required mastery output/test:** Adversarial SKU/name cases avoid destructive correction.

## SRCH-06 — Autocomplete / Typeahead
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement trie/prefix retrieval with popularity/freshness scoring and typo-tolerant candidates.

**Core concepts:** autocomplete

**Required mastery output/test:** Separate autocomplete metrics and latency from normal search.

## SRCH-07 — MinHash / LSH Dedup
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement shingles, MinHash, and LSH for near-duplicate detection/canonicalization.

**Core concepts:** dedup; hashing

**Required mastery output/test:** Recall/precision trade-off against exact Jaccard documented.

## SRCH-08 — Dense Bi-Encoder Retrieval
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Train a small contrastive query-document retriever with hard negatives.

**Core concepts:** dense retrieval

**Required mastery output/test:** Separate representation Recall@k from ANN effects.

## SRCH-09 — Learned Sparse Retrieval
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement a simplified learned-sparse/term-expansion retrieval model or faithful miniature.

**Core concepts:** learned sparse

**Required mastery output/test:** Compare quality, sparsity, storage, and latency to BM25.

## SRCH-10 — Late-Interaction Retrieval
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement a ColBERT-style token-level MaxSim retriever on a small corpus.

**Core concepts:** late interaction

**Required mastery output/test:** Compare quality/storage/latency against single-vector retrieval.

## SRCH-11 — ANN Benchmark
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Benchmark exact vs IVF-like vs HNSW-like retrieval and at least one compression setting.

**Core concepts:** ANN systems

**Required mastery output/test:** Produce recall/latency/memory/build-time curves.

## SRCH-12 — Hybrid Retrieval Fusion
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement RRF, normalized-score fusion, and query-dependent blending.

**Core concepts:** hybrid retrieval

**Required mastery output/test:** Show query classes where each method wins/loses.

## SRCH-13 — Cross-Encoder / Neural Reranker
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Train or implement a compact reranker and evaluate candidate-set ceiling vs latency.

**Core concepts:** reranking

**Required mastery output/test:** Measure marginal gain as candidate count increases.

## SRCH-14 — Search LTR / LambdaMART
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Train/evaluate a search ranker using lexical/semantic/behavioral features with proper query grouping.

**Core concepts:** learning to rank

**Required mastery output/test:** Compare pointwise, tree-LTR, and reranker behavior.

## SRCH-15 — Judgment + Click-Bias Lab
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Create graded judgments and synthetic biased clicks; estimate position effects and compare raw vs debiased signals.

**Core concepts:** relevance science

**Required mastery output/test:** Demonstrate how UI policy contaminates clicks.

## SRCH-16 — Query Rewrite Guardrails
**Level:** L3  
**Format:** LIVE

**Implementation prompt:** Implement guarded term removal/synonym/expansion logic with evidence-based rollback.

**Core concepts:** query rewriting

**Required mastery output/test:** Exact-ID and destructive-rewrite adversarial tests pass.

## SRCH-17 — Search Evaluation + Replay Harness
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement recall/MRR/MAP/NDCG, slices, result diffs, bootstrap uncertainty, and replay over versioned runs.

**Core concepts:** evaluation science

**Required mastery output/test:** Detect regressions hidden by aggregate metrics.

## SRCH-18 — Product / E-Commerce Search Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build a small product-search stack with identifiers, attributes, filters, availability, hybrid retrieval, LTR, and revenue guardrails.

**Core concepts:** vertical search

**Required mastery output/test:** Verify exact-ID, facet, inventory, and relevance behavior.

## SRCH-19 — Video / Media Search Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build a media search prototype using metadata plus visual/audio/text embeddings or precomputed multimodal features.

**Core concepts:** media search

**Required mastery output/test:** Evaluate lexical vs semantic vs multimodal retrieval by query class.

## SRCH-20 — Local / Geo Search Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Implement text + geo scoring, radius/viewport filtering, availability, popularity, and ranking.

**Core concepts:** local search

**Required mastery output/test:** Test geographic edge cases and relevance-distance trade-offs.

## SRCH-21 — Enterprise / ACL Search Case
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Build a small document search system with ACL filtering, metadata, freshness, dedup, and hybrid retrieval.

**Core concepts:** enterprise search

**Required mastery output/test:** Prove unauthorized documents never surface and measure filter cost.

## SRCH-22 — Search Serving + Cache Simulator
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Simulate query analysis, shard fan-out, caches, retrieval, reranking, fetch, timeouts, and fallbacks.

**Core concepts:** serving; latency

**Required mastery output/test:** Measure p50/p95/p99 and cache/freshness trade-offs.

## SRCH-23 — Search Incident Lab
**Level:** L3  
**Format:** EXTENDED_DRILL

**Implementation prompt:** Inject bad analyzer rollout, stale shard, merge storm, hot shard, reranker regression, and vector-version mismatch; diagnose via replay.

**Core concepts:** observability; reliability

**Required mastery output/test:** Root cause must be localized and rollback path demonstrated.

## SRCH-24 — End-to-End Search Capstone
**Level:** L3  
**Format:** CAPSTONE

**Implementation prompt:** Build a production-shaped search engine spanning ingestion/indexing, lexical+dense retrieval, ANN, hybrid fusion, LTR/reranking, evaluation, vertical behavior, serving, monitoring, and experiments.

**Core concepts:** integration

**Required mastery output/test:** Reproducible repo, benchmark tables, failure tests, architecture memo, and Staff-level defense.
