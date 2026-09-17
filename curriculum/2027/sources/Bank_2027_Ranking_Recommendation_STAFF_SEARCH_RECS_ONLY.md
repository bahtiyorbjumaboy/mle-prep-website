# 2027 Bank — Ranking & Recommendation (Search + Recs Staff-Depth)

**Status:** ACTIVE 2027 SPECIALIZATION BANK  
**Count:** 56 conversations  
**Purpose:** Staff-depth ownership of recommendation, ranking, personalization, and feed/ads/commerce systems.

## Bank contract

- D2 = strong independent explanation/application.
- D3 = mechanism + quantitative trade-off + implementation/system connection + diagnosis + changed-constraint transfer.
- Mastery requires connection to coding, experiments, serving, and failure analysis.
- Explicit vertical-transfer cases are required: video/feed, social/photo/content, e-commerce/items, ads, marketplace, notifications, and multi-surface recommendation.
- This bank targets Staff-level specialization knowledge, not automatic Staff job level.

### R01 — Two-stage and multi-stage recommender architecture
**Depth:** D2

**Prompt:** Explain candidate generation, pre-ranking, ranking, reranking, and post-processing as separate stages. Define each stage's objective, latency budget, recall/quality ceiling, and failure modes.

**Mastery standard:** Can localize a product regression to retrieval, ranking, constraints, data, or serving and propose a measurement plan.

### R02 — Explicit, implicit, and exposure-conditioned feedback
**Depth:** D2

**Prompt:** Compare explicit and implicit feedback. Explain why non-interaction is not a negative and model exposure, examination, missing-not-at-random labels, repeated impressions, and delayed conversion.

**Mastery standard:** Can construct labels that distinguish unexposed, exposed-but-ignored, and true negative outcomes.

### R03 — Training-set construction and point-in-time correctness
**Depth:** D3

**Prompt:** Starting from impression, click, watch, cart, purchase, hide, dwell, and catalog logs, design a reproducible training table with grain, attribution, deduplication, censoring, temporal splits, late events, and leakage tests.

**Mastery standard:** Can defend every row/label as a modeling choice and prove temporal correctness with tests.

### R04 — Recommendation metrics and metric contracts
**Depth:** D3

**Prompt:** Derive/compare Precision@k, Recall@k, HitRate@k, MRR, MAP, DCG/NDCG, AUC/log-loss, calibration, coverage, novelty, diversity, watch-time/completion, conversion/revenue, and long-term metrics.

**Mastery standard:** Can choose stage-appropriate metrics and define edge-case semantics before evaluation.

### R05 — Cold start and bootstrap strategies
**Depth:** D2

**Prompt:** Distinguish new-user, new-item, new-surface, and sparse-history cold start. Explain priors, content features, popularity, exploration, onboarding signals, and evaluation slices.

**Mastery standard:** Can design explicit cold-start behavior rather than hiding it in aggregate metrics.

### R06 — Collaborative, content, co-visitation, graph, and hybrid retrieval
**Depth:** D3

**Prompt:** Compare matrix factorization, item-item/co-visitation, content similarity, graph propagation, popularity/trending, and learned embeddings as candidate sources.

**Mastery standard:** Can design multi-channel fan-out with quotas, deduplication, attribution, and marginal-recall diagnostics.

### R07 — Matrix factorization and implicit objectives
**Depth:** D3

**Prompt:** Derive the geometry of MF and compare explicit squared error, weighted implicit objectives, and pairwise/BPR-style formulations. Cover confidence weights, regularization, and cold-start limits.

**Mastery standard:** Can implement MF as a serious baseline and explain when neural retrieval does not earn complexity.

### R08 — Two-tower retrieval
**Depth:** D3

**Prompt:** Explain user/query and item/content towers, factorization constraints, ANN serving, normalization, temperature, embedding norms, logQ/popularity correction, and tower serving/freshness.

**Mastery standard:** Can design training and serving together, including index versioning and query-embedding freshness.

### R09 — Negative sampling and false negatives
**Depth:** D3

**Prompt:** Compare uniform, popularity-weighted, in-batch, hard, semi-hard, exposure-aware, and teacher-mined negatives. Explain sampling bias, accidental positives, false negatives, and correction.

**Mastery standard:** Can choose and validate a sampler against the deployment distribution.

### R10 — ANN for recommendation
**Depth:** D3

**Prompt:** Compare exact retrieval with HNSW, IVF, PQ/OPQ, partitioned/ScaNN-style, filtered ANN, and disk-aware strategies on recall, RAM, build/update/delete, and p99 latency.

**Mastery standard:** Can select an ANN family from catalog size, update rate, memory, and tail-latency constraints.

### R11 — Large embedding-table systems
**Depth:** D3

**Prompt:** Explain sharding, hashing, hot/cold parameters, quantization, cache tiers, embedding freshness, synchronization, parameter-server/all-to-all patterns, and failure modes.

**Mastery standard:** Can reason about memory/network/consistency bottlenecks in large sparse recommenders.

### R12 — Candidate blending and adaptive retrieval budgets
**Depth:** D3

**Prompt:** Given multiple candidate sources with different overlap, recall, cost, and segment behavior, design static or adaptive quota allocation and fallbacks.

**Mastery standard:** Can justify candidate budgets from marginal recall and cost rather than fixed folklore.

### R13 — Pointwise, pairwise, and listwise learning to rank
**Depth:** D3

**Prompt:** Compare statistical targets, losses, pair construction, listwise normalization, LambdaMART-style lambdas, and metric alignment. Explain when calibrated pointwise modeling is preferable.

**Mastery standard:** Can connect training objective, evaluation metric, and serving semantics.

### R14 — Gradient-boosted trees and LambdaMART for ranking
**Depth:** D3

**Prompt:** Explain why tree ensembles remain strong for ranking, how LambdaMART optimizes ranking metrics indirectly, feature interactions, monotonic constraints, missing values, and serving trade-offs.

**Mastery standard:** Can choose a tree ranker when it is the right inductive bias rather than defaulting to deep models.

### R15 — Wide & Deep, FM/DeepFM, DLRM, and feature interactions
**Depth:** D3

**Prompt:** Compare memorization/cross features, factorization-style interactions, DLRM sparse+dense interactions, and deep ranking networks.

**Mastery standard:** Can select an architecture based on feature regime, sparsity, scale, and latency.

### R16 — DCN / explicit feature crossing
**Depth:** D3

**Prompt:** Explain polynomial cross layers and why explicit learned crosses can outperform unconstrained MLP interaction learning in sparse ranking problems.

**Mastery standard:** Can reason about interaction order, parameter efficiency, inductive bias, and deployment cost.

### R17 — Multi-task ranking: shared-bottom, MMoE, PLE-style
**Depth:** D3

**Prompt:** Design a ranker for click, watch, completion, conversion, value, hide/report, or retention. Explain negative transfer, routing, label sparsity, loss weighting, and cascaded objectives.

**Mastery standard:** Can diagnose task conflict and propose architectural or optimization remedies.

### R18 — Calibration, uncertainty, and score semantics
**Depth:** D3

**Prompt:** Distinguish ordering scores from probabilities. Cover Platt/isotonic-style calibration, segment drift, uncertainty, selective prediction, and downstream use in thresholds/auctions/expected value.

**Mastery standard:** Can prevent arbitrary ranking scores from being misused as probabilities.

### R19 — Feature architecture and leakage
**Depth:** D3

**Prompt:** Design user, item, context, cross, freshness, history, behavioral, social, content, and business features with point-in-time generation, online/offline parity, missingness, and leakage controls.

**Mastery standard:** Can audit a ranking feature set for correctness and serving feasibility.

### R20 — Diversity, novelty, redundancy, and MMR
**Depth:** D3

**Prompt:** Explain MMR and alternative diversity-aware reranking. Define item similarity carefully and analyze relevance loss, novelty, creator/category diversity, and segment effects.

**Mastery standard:** Can tune diversity from product objectives and measured trade-offs.

### R21 — Hard constraints and slate construction
**Depth:** D3

**Prompt:** Design reranking with availability, policy, history suppression, seller/creator/category caps, minimum guarantees, incompatibilities, and deterministic fallbacks.

**Mastery standard:** Can guarantee constraint behavior and quantify relevance/business cost.

### R22 — Multi-objective ranking and Pareto trade-offs
**Depth:** D3

**Prompt:** Analyze weighted blends of CTR, completion, conversion, revenue, freshness, diversity, creator health, satisfaction, and retention. Cover proxy gaming and constraint formulations.

**Mastery standard:** Can set/learn trade-offs using experiments and constraints rather than arbitrary weights.

### R23 — Slate-level interactions and page/feed optimization
**Depth:** D3

**Prompt:** Explain why independent item scoring fails under redundancy, complementarity, position interactions, and limited attention. Discuss slate-level objectives and tractable approximations.

**Mastery standard:** Can identify when itemwise scoring is structurally insufficient.

### R24 — Marketplace and provider-side recommendation
**Depth:** D3

**Prompt:** Reason about consumer utility, provider exposure, supply health, fairness, concentration, inventory, and long-term ecosystem effects in two-sided marketplaces.

**Mastery standard:** Can define multi-stakeholder metrics and detect when user-only optimization harms the marketplace.

### R25 — Exposure, position, and selection bias
**Depth:** D3

**Prompt:** Draw the logged-data generating process. Distinguish exposure, position/examination, trust, selection, survivorship, and policy bias; explain why adding position as a feature does not debias training.

**Mastery standard:** Can identify which biases affect training versus evaluation.

### R26 — IPS, SNIPS, doubly robust estimation, and overlap
**Depth:** D3

**Prompt:** Derive intuition for IPS, clipping, self-normalization, effective sample size, doubly robust estimation, propensity estimation, and overlap/support.

**Mastery standard:** Can decide whether an offline policy comparison is identifiable and trustworthy.

### R27 — Counterfactual learning-to-rank
**Depth:** D3

**Prompt:** Explain how inverse-propensity or related corrections enter ranking training, required assumptions, and how propensity noise/clipping trade off bias and variance.

**Mastery standard:** Can separate counterfactual evaluation from counterfactual training.

### R28 — A/B tests, interleaving, switchbacks, and interference
**Depth:** D3

**Prompt:** Compare user-level A/B tests, interleaving, cluster randomization, and switchbacks. Cover novelty, carryover, network/marketplace interference, guardrails, and sequential peeking.

**Mastery standard:** Can choose an experimental design from the interference structure.

### R29 — Exploration: epsilon-greedy, UCB, Thompson, contextual bandits
**Depth:** D3

**Prompt:** Compare exploration strategies, uncertainty assumptions, regret, delayed/sparse rewards, non-stationarity, contexts, safety constraints, and logging requirements.

**Mastery standard:** Can implement/simulate alternatives and defend exploration budget.

### R30 — Off-policy evaluation for new policies
**Depth:** D3

**Prompt:** Connect bandit logging to future policy evaluation. Analyze support, deterministic policies, clipping, model-based baselines, confidence intervals, and policy drift.

**Mastery standard:** Can construct logs so future policy evaluation remains possible.

### R31 — Long-horizon objectives and delayed reward
**Depth:** D3

**Prompt:** Model immediate engagement versus purchase, satisfaction, and retention. Cover delayed labels, censoring, attribution windows, repeated exposure, reward shaping, and proxy gaming.

**Mastery standard:** Can design evaluation/experimentation for long-term outcomes.

### R32 — Session-based recommendation fundamentals
**Depth:** D3

**Prompt:** Explain when short-term session intent dominates long-term preference. Compare co-visitation, RNN/session encoders, attention, and transformer-based approaches.

**Mastery standard:** Can define state/session boundaries and strong baselines before choosing a sequence model.

### R33 — SASRec-style autoregressive sequential recommendation
**Depth:** D3

**Prompt:** Explain causal self-attention for next-item prediction, positional encoding, truncation, negative sampling, online state, and deployment.

**Mastery standard:** Can implement a simplified SASRec-like model and compare against static baselines.

### R34 — BERT4Rec-style masked sequential recommendation
**Depth:** D3

**Prompt:** Compare masked-item bidirectional training with autoregressive next-item training. Cover masking strategy, train/inference mismatch, and evaluation pitfalls.

**Mastery standard:** Can compare sequence objectives empirically without invalid sampled-negative evaluation.

### R35 — Graph recommendation
**Depth:** D3

**Prompt:** Explain user-item/content graph propagation, graph collaborative filtering, oversmoothing, sampling, temporal updates, and scalability.

**Mastery standard:** Can identify when graph structure adds information beyond co-visitation/two-towers.

### R36 — Feed and video recommendation
**Depth:** D3

**Prompt:** Design ranking for video/feed surfaces using watch time, completion, skips, repeats, freshness, session intent, creator diversity, satisfaction, and long-term engagement.

**Mastery standard:** Can explain how feed/video objectives change labels, candidate sources, sequence modeling, metrics, and serving.

### R37 — Social/photo/content recommendation
**Depth:** D3

**Prompt:** Design social or photo/content ranking using follows, graph proximity, freshness, creator affinity, reshares/saves, hides/reports, diversity, and repeated exposure.

**Mastery standard:** Can separate social-graph priors from content relevance and reason about ecosystem/creator effects.

### R38 — E-commerce and item recommendation
**Depth:** D3

**Prompt:** Design recommendation for products/items with conversion, revenue, inventory, availability, price, substitution/complementarity, seasonality, catalog cold start, and seller constraints.

**Mastery standard:** Can adapt retrieval/ranking/evaluation to commerce semantics rather than copying a feed objective.

### R39 — Ads recommendation and ranking
**Depth:** D3

**Prompt:** Design ad candidate retrieval/ranking around CTR/CVR/value, calibration, auctions/bids, budgets/pacing, frequency caps, delayed conversions, position bias, advertiser constraints, and user experience.

**Mastery standard:** Can distinguish relevance ranking from value/auction ranking and reason about calibration and ecosystem trade-offs.

### R40 — Notification and push recommendation
**Depth:** D3

**Prompt:** Model sparse interruption opportunities, send-time choice, fatigue, frequency caps, delayed conversions, opt-outs, and long-term user value.

**Mastery standard:** Can design conservative policies and evaluation where false positives are expensive.

### R41 — Homepage/module and multi-surface recommendation
**Depth:** D3

**Prompt:** Design multiple recommendation modules on one page/product where modules compete for attention and share candidate sources.

**Mastery standard:** Can reason about cross-module cannibalization, global diversity, and page-level optimization.

### R42 — Multimodal recommendation without generative models
**Depth:** D3

**Prompt:** Use text/image/audio/video embeddings or metadata for retrieval/ranking. Explain modality alignment, missing modalities, cold start, representation drift, and serving costs.

**Mastery standard:** Can integrate multimodal features without treating them as magic.

### R43 — Recommendation serving architecture
**Depth:** D3

**Prompt:** Design online fan-out, feature hydration, pre-rank/rank/rerank cascade, caches, timeouts, degradation, routing, and result assembly under a latency SLO.

**Mastery standard:** Can allocate latency by stage and specify fallbacks for partial failure.

### R44 — Model/index/feature consistency and freshness
**Depth:** D3

**Prompt:** Explain staleness in features, embeddings, ANN indexes, catalog/content state, and business rules. Design version contracts, streaming updates, backfills, shadow validation, and rollback.

**Mastery standard:** Can prevent mixed-version serving and reason about bounded staleness.

### R45 — Monitoring and failure diagnosis
**Depth:** D3

**Prompt:** Design monitoring for candidate recall proxies, score/calibration distributions, segment metrics, coverage, concentration, freshness, feature health, latency, and downstream outcomes.

**Mastery standard:** Can localize retrieval, ranking, data, experiment, or serving regressions.

### R46 — Capacity, cost, and scaling
**Depth:** D3

**Prompt:** Estimate QPS, candidate volume, feature reads, ranker FLOPs, embedding/index memory, cache hit rates, network traffic, and p99 budgets.

**Mastery standard:** Can perform back-of-the-envelope sizing and identify dominant bottlenecks.

### R47 — Privacy, safety, and policy constraints in recommendation
**Depth:** D3

**Prompt:** Analyze sensitive features, data minimization, consent, age/safety constraints, inappropriate content, policy enforcement, and auditability.

**Mastery standard:** Can design hard controls outside the model and define safe fallbacks.

### R48 — Fairness, exposure, and creator/seller health
**Depth:** D3

**Prompt:** Define individual/group exposure, provider concentration, opportunity metrics, and trade-offs with user utility. Cover measurement and intervention pitfalls.

**Mastery standard:** Can reason about exposure fairness without collapsing it into one scalar metric.

### R49 — Causal recommendation and uplift thinking
**Depth:** D3

**Prompt:** Distinguish predicting engagement from estimating incremental effect. Explain uplift, heterogeneous treatment effects, interference, and when causal targeting changes ranking.

**Mastery standard:** Can identify when prediction is not the right objective.

### R50 — Retriever-ranker distillation and compression
**Depth:** D3

**Prompt:** Explain teacher-student distillation across retrieval/ranking stages, soft labels, ranking distillation, quantization/pruning, and deployment objectives.

**Mastery standard:** Can reduce cost while preserving the relevant ranking behavior.

### R51 — Offline evaluation pathologies
**Depth:** D3

**Prompt:** Analyze sampled negatives, popularity leakage, temporal leakage, candidate-set mismatch, invalid leave-one-out protocols, and metric saturation.

**Mastery standard:** Can audit a recommender evaluation protocol and reject misleading gains.

### R52 — Incident response and rollback for ranking systems
**Depth:** D3

**Prompt:** Given score shifts, feature outages, candidate collapse, or index skew, design triage, replay, rollback, and postmortem methodology.

**Mastery standard:** Can debug a recommendation incident from telemetry rather than intuition.

### R53 — Video/feed Staff architecture case
**Depth:** D3

**Prompt:** Design a large-scale personalized video/feed recommender with fresh content, sequential intent, creator ecosystem constraints, multi-objective ranking, and strict latency.

**Mastery standard:** Can lead a multi-hour architecture review and adapt when product assumptions change.

### R54 — E-commerce/marketplace Staff architecture case
**Depth:** D3

**Prompt:** Design a product/item recommender for a two-sided marketplace with inventory churn, price, conversion/revenue, seller exposure, cold start, and promotions.

**Mastery standard:** Can connect ranking, marketplace economics, experimentation, and serving.

### R55 — Ads Staff architecture case
**Depth:** D3

**Prompt:** Design an ad recommendation/ranking stack with eligibility, retrieval, pCTR/pCVR/value models, calibration, budget/pacing, auctions, frequency caps, and online experimentation.

**Mastery standard:** Can defend where relevance, economics, and policy constraints enter the stack.

### R56 — General Staff-level recommendation architecture case
**Depth:** D3

**Prompt:** Given a product surface with sparse implicit feedback, rapidly changing inventory/content, multiple objectives, strict latency, and heterogeneous users, design the end-to-end recommender.

**Mastery standard:** Can challenge assumptions, quantify trade-offs, and identify what must be measured before committing.
