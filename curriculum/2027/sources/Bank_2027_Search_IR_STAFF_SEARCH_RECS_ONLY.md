# 2027 Bank — Search & Information Retrieval (Search + Recs Staff-Depth)

**Status:** ACTIVE 2027 SPECIALIZATION BANK  
**Count:** 56 conversations  
**Purpose:** Staff-depth ownership of classical IR, neural retrieval, vector search, learning-to-rank, relevance science, vertical search, and production search systems.

## Bank contract

- D2 = strong independent explanation/application.
- D3 = mechanism + quantitative design + implementation/system connection + diagnosis + changed-constraint transfer.
- Search is treated as an end-to-end system: ingestion/index → retrieval → ranking → evaluation → experimentation → serving/operations.
- Explicit vertical-transfer cases are required: e-commerce/product, video/media, local/place, enterprise/document, marketplace, sponsored search, and multimodal retrieval.
- No LLM/RAG curriculum is part of this bank.

### S01 — End-to-end search architecture
**Depth:** D2

**Prompt:** Walk through query intake, analysis, rewrite, routing, candidate retrieval, filtering, ranking, blending, post-processing, rendering, logging, and evaluation with stage objectives and latency budgets.

**Mastery standard:** Can diagnose bad search by stage rather than treating search as one model.

### S02 — Inverted indexes, postings, and positional information
**Depth:** D3

**Prompt:** Explain term dictionaries, postings, TF, positions, fields, doc statistics, compression, and Boolean/phrase/proximity execution.

**Mastery standard:** Can implement a compact inverted index and reason about storage/query cost.

### S03 — BM25, BM25F, exact match, phrase, and proximity
**Depth:** D3

**Prompt:** Derive BM25 intuition; analyze TF saturation, length normalization, IDF variants, field weighting, exact identifiers, phrase/proximity boosts.

**Mastery standard:** Can tune lexical scoring by query class and explain lexical advantages.

### S04 — Analyzers and linguistic normalization
**Depth:** D2

**Prompt:** Compare tokenization, case/Unicode normalization, stemming, lemmatization, stopwords, synonyms, language-specific analysis, and exact-ID/SKU analyzers.

**Mastery standard:** Can design query/index analyzer parity and protect identity queries.

### S05 — Query intent and query-class routing
**Depth:** D3

**Prompt:** Classify navigational, informational, transactional, exact-ID, head/torso/tail, local, media, product, and structured/faceted queries and route them appropriately.

**Mastery standard:** Can define deterministic protections and query-dependent retrieval/ranking.

### S06 — Posting-list algorithms
**Depth:** D3

**Prompt:** Implement/reason about intersection, union, AND-NOT, shortest-first, galloping, skips, DAAT/TAAT intuition, and top-k accumulation under skew.

**Mastery standard:** Can choose an execution strategy from list lengths and query structure.

### S07 — WAND and Block-Max WAND
**Depth:** D3

**Prompt:** Explain upper bounds, pivoting, block maxima, safe pruning, and exact top-k guarantees under valid bounds.

**Mastery standard:** Can quantify work avoided without changing exact results.

### S08 — Index segments, refresh, merges, deletes, compaction
**Depth:** D3

**Prompt:** Explain immutable segments, refresh/commit, tombstones, merge policy, cache invalidation, segment warming, and merge storms.

**Mastery standard:** Can design freshness/throughput strategy and diagnose lifecycle failures.

### S09 — Distributed lexical search
**Depth:** D3

**Prompt:** Design sharding, replication, routing, scatter/gather, shard-local top-k, global merge, timeouts, partial results, and consistency/freshness.

**Mastery standard:** Can reason quantitatively about fan-out and tail amplification.

### S10 — Facets, filters, aggregations, collapse, and canonicalization
**Depth:** D3

**Prompt:** Explain pre/post filtering, bitmaps, facets, variant grouping, deduplication, canonical result identity, and interaction with ranking/ANN.

**Mastery standard:** Can preserve relevance and UI consistency under structured constraints.

### S11 — Dense bi-encoder retrieval
**Depth:** D3

**Prompt:** Explain query/document asymmetry, contrastive objectives, normalization, temperature, negatives, domain adaptation, and ANN serving.

**Mastery standard:** Can train/evaluate a domain bi-encoder and separate representation from index failure.

### S12 — Hard-negative mining for search
**Depth:** D3

**Prompt:** Compare BM25, ANN, teacher-mined, in-batch, cross-batch-memory negatives and false-negative filtering.

**Mastery standard:** Can build iterative hard-negative mining without training collapse.

### S13 — Learned sparse retrieval
**Depth:** D3

**Prompt:** Explain SPLADE-style learned term expansion/weighting, sparsity regularization, indexability, interpretability, storage, and latency.

**Mastery standard:** Can compare learned sparse with BM25/dense on quality and operations.

### S14 — Late-interaction retrieval
**Depth:** D3

**Prompt:** Explain ColBERT-style token embeddings, MaxSim/late interaction, expressivity, storage/compute, indexing, and pruning.

**Mastery standard:** Can identify workloads where late interaction earns its footprint.

### S15 — Cross-encoder reranking
**Depth:** D3

**Prompt:** Explain full interaction, candidate-set ceiling, batching, truncation, distillation, and latency-aware candidate sizing.

**Mastery standard:** Can design retrieval→reranking cascades and measure marginal gain.

### S16 — Retrieval/ranker distillation
**Depth:** D3

**Prompt:** Explain teacher-student training for bi-encoders, sparse retrievers, late-interaction systems, and lightweight rerankers.

**Mastery standard:** Can design distillation without leaking evaluation data.

### S17 — ANN design: HNSW, IVF, PQ/OPQ, partitioned search
**Depth:** D3

**Prompt:** Compare graph, inverted-file, quantized, and partitioned ANN families on recall, memory, build, update/delete, filtering, hardware, and latency.

**Mastery standard:** Can select and benchmark an ANN family for a concrete corpus.

### S18 — Vector compression and quantization
**Depth:** D3

**Prompt:** Explain PQ, OPQ, residuals, scalar/int8 compression, asymmetric distance computation, and recall-memory trade-offs.

**Mastery standard:** Can estimate memory and measure quality degradation.

### S19 — Filtered ANN
**Depth:** D3

**Prompt:** Explain prefilter, postfilter, graph-aware filtering, partitioning, selective-query pathologies, and hybrid approaches.

**Mastery standard:** Can avoid catastrophic recall/latency for highly selective filters.

### S20 — Vector-index lifecycle
**Depth:** D3

**Prompt:** Design embedding generation, bulk build, incremental update, delete, tombstone, re-embedding, shadow index, validation, version skew, rollback.

**Mastery standard:** Can keep vector and lexical state consistent under continuous change.

### S21 — Vector search at scale
**Depth:** D3

**Prompt:** Estimate memory, replication, shard routing, QPS, candidate scans, cache behavior, rebuild time, and disk/compression thresholds.

**Mastery standard:** Can produce a capacity plan and identify dominant bottlenecks.

### S22 — Hybrid lexical+dense retrieval
**Depth:** D3

**Prompt:** Compare RRF, score normalization, calibrated fusion, learned blending, query-dependent routing, and union recall.

**Mastery standard:** Can prove hybrid value by query class rather than aggregate metrics alone.

### S23 — Query rewriting and simplification
**Depth:** D3

**Prompt:** Design guarded rewrites, term removal, synonyms/expansion, normalization, decomposition, and rollback based on retrieval evidence.

**Mastery standard:** Can prevent destructive rewrites and attribute gains/losses.

### S24 — Spelling correction and noisy-channel search
**Depth:** D3

**Prompt:** Frame correction probabilistically and compare edit distance, n-grams, phonetics, candidate retrieval, and neural/non-neural reranking.

**Mastery standard:** Can choose correct/suggest/do-nothing under asymmetric cost.

### S25 — Zero-result and low-quality recovery
**Depth:** D3

**Prompt:** Create a taxonomy and remedy ladder spanning analyzers, spelling, rewrite, fallback, hybrid retrieval, catalog/content quality, and business constraints.

**Mastery standard:** Can monitor actionable zero-result rates and identify upstream causes.

### S26 — Query/document expansion and pseudo-relevance feedback
**Depth:** D3

**Prompt:** Explain synonym expansion, PRF/RM-style thinking, document expansion, generated-query expansion, drift, and precision loss.

**Mastery standard:** Can test expansion against strong baselines and protect exact queries.

### S27 — Autocomplete and typeahead
**Depth:** D3

**Prompt:** Design prefix indexes, popularity/freshness, personalization, typo tolerance, abuse filtering, caching, online updates, and distinct metrics.

**Mastery standard:** Can explain why autocomplete is its own ranking system.

### S28 — Search learning-to-rank
**Depth:** D3

**Prompt:** Compare pointwise, pairwise, listwise, LambdaMART, neural reranking, feature crosses, and calibrated vs ordering-only scores.

**Mastery standard:** Can align ranking objective, query-level metrics, and serving semantics.

### S29 — Search feature architecture
**Depth:** D3

**Prompt:** Design lexical, semantic, query, document, behavioral, freshness, popularity, personalization, business, and interaction features with point-in-time correctness.

**Mastery standard:** Can distinguish robust relevance signals from leakage/proxy traps.

### S30 — Judgment collection and pooling
**Depth:** D3

**Prompt:** Design relevance guidelines, graded scales, assessor training, adjudication, inter-rater agreement, pooling, active sampling, and tail coverage.

**Mastery standard:** Can quantify label noise and judged-pool bias.

### S31 — Click models and behavior bias
**Depth:** D3

**Prompt:** Explain examination/position/trust bias, cascade/position-based click-model intuition, propensity estimation, and when clicks cease to represent relevance.

**Mastery standard:** Can use behavior labels without confusing UI policy with relevance.

### S32 — Counterfactual and unbiased learning-to-rank for search
**Depth:** D3

**Prompt:** Explain propensity-weighted evaluation/training, click debiasing, support/overlap, clipping, and variance control.

**Mastery standard:** Can determine when counterfactual LTR is valid and when it is not.

### S33 — Search evaluation science
**Depth:** D3

**Prompt:** Combine recall, MRR/MAP/NDCG, success/zero-result/session metrics, segment analysis, online tests, calibration/commerce metrics, and uncertainty.

**Mastery standard:** Can decide when an offline gain should be rejected.

### S34 — Commercial objectives and personalization
**Depth:** D3

**Prompt:** Analyze relevance vs revenue/business boosts, personalization, user intent, privacy, query classes, and guardrail accounting.

**Mastery standard:** Can deploy personalization/boosting without hiding relevance cost.

### S35 — Multilingual and cross-lingual search
**Depth:** D3

**Prompt:** Compare language-specific analyzers, multilingual embeddings, translation-based retrieval, transliteration, locale features, and per-language evaluation.

**Mastery standard:** Can design fallbacks for low-resource languages and code-switching.

### S36 — Federated and blended search
**Depth:** D3

**Prompt:** Design search across heterogeneous verticals/corpora with different rankers and score distributions. Cover routing, fusion, quotas, and calibration.

**Mastery standard:** Can prevent one vertical from dominating due to score-scale artifacts.

### S37 — E-commerce/product search
**Depth:** D3

**Prompt:** Design product search with exact identifiers, attributes, variants, availability, price, personalization, revenue, seller constraints, and catalog churn.

**Mastery standard:** Can adapt retrieval/ranking/evaluation to commerce semantics.

### S38 — Video/media/content search
**Depth:** D3

**Prompt:** Design search over video/photo/media with metadata, transcripts/tags, visual/audio embeddings, freshness, creator/content policy, and relevance judgments.

**Mastery standard:** Can reason about multimodal retrieval without relying on generative systems.

### S39 — Local/place search
**Depth:** D3

**Prompt:** Design local search using text relevance, geo distance, availability/open-now, popularity, quality, personalization, and query intent.

**Mastery standard:** Can reason about geographic indexing, blended objectives, and evaluation.

### S40 — Enterprise/document search
**Depth:** D3

**Prompt:** Design enterprise search across documents, ACLs, freshness, metadata, structured filters, dedup/canonicalization, and heterogeneous corpora.

**Mastery standard:** Can preserve permissions and relevance under complex access constraints.

### S41 — Marketplace search
**Depth:** D3

**Prompt:** Design marketplace search where buyer relevance, seller exposure, inventory, price, promotions, and marketplace health interact.

**Mastery standard:** Can define multi-stakeholder metrics and constraints.

### S42 — Ads/sponsored search ranking
**Depth:** D3

**Prompt:** Design sponsored-search candidate generation/ranking with keyword/semantic matching, quality, pCTR/pCVR, bids, auctions, budgets/pacing, policy, and user experience.

**Mastery standard:** Can distinguish organic relevance from sponsored ranking while reasoning about shared signals.

### S43 — Multimodal search without generative models
**Depth:** D3

**Prompt:** Use image/text/audio/video embeddings, cross-modal alignment, late fusion, modality missingness, and modality-specific evaluation.

**Mastery standard:** Can design non-generative multimodal retrieval with explicit trade-offs.

### S44 — Search latency engineering
**Depth:** D3

**Prompt:** Break down p50/p95/p99 across analysis, fan-out, retrieval, reranking, fetch, and rendering. Cover caches, early termination, shedding, timeouts, and fallbacks.

**Mastery standard:** Can explain mechanisms for meeting an SLO and degradation behavior.

### S45 — Caching and query-result reuse
**Depth:** D3

**Prompt:** Compare term/posting caches, query-result caches, feature caches, embedding caches, invalidation, personalization interactions, and freshness trade-offs.

**Mastery standard:** Can identify where caching helps or causes stale/wrong results.

### S46 — Observability, replay, and relevance incidents
**Depth:** D3

**Prompt:** Design logs, traces, index/version metadata, query cohorts, result diffs, recall proxies, latency metrics, and replay tools.

**Mastery standard:** Can localize relevance regressions quickly from production evidence.

### S47 — Security, spam, and adversarial retrieval
**Depth:** D3

**Prompt:** Analyze spam, keyword stuffing, cloaking, embedding poisoning, abuse of ranking signals, malicious documents, and ingestion controls.

**Mastery standard:** Can define controls at ingestion, retrieval, ranking, and serving.

### S48 — Freshness and incremental indexing
**Depth:** D3

**Prompt:** Design near-real-time ingestion, delta indexes, merge policies, deletion/update semantics, versioning, backfills, and freshness metrics.

**Mastery standard:** Can choose freshness architecture from update rate and query SLOs.

### S49 — Search experimentation under interference
**Depth:** D3

**Prompt:** Compare A/B, interleaving, query-level randomization, switchbacks, repeated-session effects, novelty, and carryover.

**Mastery standard:** Can choose experiment unit from product and interference structure.

### S50 — Capacity, cost, and scaling
**Depth:** D3

**Prompt:** Size corpus, index memory, replicas, QPS, fan-out, reranker compute, update throughput, cache layers, and storage.

**Mastery standard:** Can identify cost centers and justify simplifications.

### S51 — Offline evaluation pathologies
**Depth:** D3

**Prompt:** Analyze judged-pool bias, head-query dominance, metric saturation, candidate-set leakage, click contamination, stale labels, and benchmark overfitting.

**Mastery standard:** Can audit search evaluation before trusting a gain.

### S52 — Search incident response and rollback
**Depth:** D3

**Prompt:** Given a relevance collapse, bad analyzer rollout, shard skew, stale index, or neural reranker regression, design triage, replay, rollback, and postmortem.

**Mastery standard:** Can debug from evidence and restore safe service quickly.

### S53 — E-commerce Staff architecture case
**Depth:** D3

**Prompt:** Design a large commercial search engine with identifiers, attributes, hybrid retrieval, LTR, personalization, filters, freshness, and strict p99 latency.

**Mastery standard:** Can lead an adversarial architecture review with business and relevance constraints.

### S54 — Media/social Staff architecture case
**Depth:** D3

**Prompt:** Design search for a large media/social corpus with multimodal content, freshness, creators, policy constraints, and personalized ranking.

**Mastery standard:** Can adapt retrieval and relevance science to media semantics.

### S55 — Enterprise/local Staff architecture case
**Depth:** D3

**Prompt:** Design either enterprise or local search under ACL/geo/freshness constraints, heterogeneous corpora, and reliability requirements.

**Mastery standard:** Can change architecture when the operational constraint changes.

### S56 — General Staff-level search architecture case
**Depth:** D3

**Prompt:** Design a large-scale search system from query understanding through indexing, retrieval, ranking, experimentation, serving, and incident handling.

**Mastery standard:** Can lead a multi-hour architecture defense and quantify major trade-offs.
