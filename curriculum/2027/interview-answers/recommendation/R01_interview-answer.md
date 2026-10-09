---
type: interview-answer
item: "2027:R01"
title: "Two-stage and multi-stage recommender architecture"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - ranking-systems
  - multi-stage-ranking
  - retrieval
  - system-design
---

## Canonical Staff-Depth Question

Explain candidate generation, pre-ranking, ranking, reranking, and post-processing as separate stages. Define each stage's objective, latency budget, recall/quality ceiling, and failure modes.

## Mastery Answer

A large recommender is usually a funnel rather than one model applied to the entire catalog. The reason is computational: an expensive high-capacity ranker may be good enough to compare hundreds of items, but not millions. The architecture therefore reduces the candidate set in stages, with each stage optimizing a different local objective while preserving enough quality for downstream stages.

**Candidate generation** starts from the full eligible corpus and retrieves a relatively small union of plausible items, often from several channels such as collaborative filtering, co-visitation, content similarity, popularity, graph retrieval, or learned embeddings. Its primary objective is **high recall under a tight latency and compute budget**. The key ceiling is structural: if a relevant item is not retrieved, no later ranker can recover it. I therefore measure source-level and union Recall@K, marginal recall by source, coverage, latency, and segment behavior. Typical failures are candidate collapse, over-reliance on popularity, stale indexes or embeddings, source outages, excessive source overlap, and poor cold-start coverage.

**Pre-ranking** is optional. It cheaply reduces perhaps thousands of retrieved items to a few hundred using lightweight features or a smaller model. Its purpose is to preserve almost all useful candidates while cutting feature and heavy-ranker cost. Its main failure mode is premature pruning: if the pre-ranker removes items the heavy ranker would have preferred, the downstream quality ceiling drops. I evaluate preservation of downstream-quality candidates, Recall@K relative to the full ranker, latency saved, and segment-specific pruning errors.

**Ranking** is the main relevance or utility optimization stage. It operates on a tractable candidate set and can use richer user, item, context, and interaction features. The objective may be click, watch time, conversion, expected value, satisfaction, or a multi-task combination. Ranking usually consumes the largest model-inference and feature-hydration budget. Its ceiling is bounded by the candidates it receives. Failures include feature skew, stale features, objective mismatch, calibration errors, distribution shift, and model/feature-version incompatibility.

**Reranking** operates on the top portion of the ranked list and reasons about the slate rather than treating every item independently. It handles diversity, novelty, redundancy, freshness, category or seller caps, exploration, and other soft or hard constraints. It should spend little latency because the list is already small. Its failure modes include excessive relevance loss, unstable constraint interactions, nondeterministic fallbacks, and business rules that dominate user value.

**Post-processing** applies final eligibility, policy, deduplication, availability, suppression, formatting, and deterministic fallback rules before response. Some hard safety or inventory constraints may also be enforced earlier, but the final boundary must guarantee that invalid items cannot escape. Failures here often look like ranking failures even though model scores are correct.

The system should be debugged stage-by-stage. If candidate Recall@K drops, inspect retrieval. If candidate recall is stable but NDCG or conversion drops, inspect feature hydration and ranking. If ranking scores are stable but final-list composition changes, inspect reranking and post-processing. If offline metrics are stable but online outcomes drop, inspect serving, exposure, latency, experimentation, and objective mismatch.

A useful design principle is: **early stages maximize opportunity under cheap computation; later stages spend more computation to improve ordering and enforce slate/product constraints**. Latency and candidate budgets should therefore be allocated according to marginal quality gain, not folklore. The architecture is successful when each stage has an explicit contract, measurable ceiling, versioned inputs/outputs, and a safe fallback.

## Learn the Concepts

### Foundation

A recommender answers a seemingly simple question: **given a user and a context, which items should be shown, and in what order?**

The naive design would score every item in the catalog with the strongest model and sort the results. That works only when the catalog is tiny or the scoring function is extremely cheap. If the catalog contains millions of items and the strongest model needs rich online features, scoring everything per request is prohibitively expensive.

The central mental model is therefore a **funnel**:

`all eligible items → plausible candidates → promising candidates → precisely ordered list → constraint-safe final slate`

Each stage narrows the set while spending progressively more computation per surviving item.

Key terminology:

- **Corpus / catalog:** the full set of items that might be recommendable.
- **Candidate:** an item that survives an early retrieval stage and is eligible for further scoring.
- **Candidate generation / retrieval:** cheap selection of a relatively small set from the full corpus.
- **Pre-ranking:** an optional cheap scoring/pruning stage between retrieval and the expensive ranker.
- **Ranking:** detailed scoring and ordering of the surviving items.
- **Reranking:** list-level adjustment after itemwise ranking, often for diversity or constraints.
- **Post-processing:** final deterministic eligibility, policy, formatting, suppression, and fallback logic.
- **Recall:** whether the system preserved items that ought to be considered.
- **Ranking quality:** whether the best surviving items are ordered near the top.
- **Quality ceiling:** the best performance a downstream stage could possibly achieve given what upstream stages passed to it.
- **Latency budget:** the amount of request-path time a stage is allowed to consume.
- **p99 latency:** the latency below which 99% of requests complete; it matters because users experience tail latency, not only the average.

A crucial distinction is **retrieval recall versus ranking quality**. Retrieval is primarily about not losing good options. Ranking is primarily about ordering the available options well. A ranker cannot rescue an item that retrieval never surfaced.

Another distinction is **itemwise scoring versus slate reasoning**. A ranker commonly assigns each item a score independently or mostly independently. A reranker can reason about the set as a whole: five nearly identical shoes may each score well independently, but showing all five can produce a poor slate.

#### Concrete worked example

Assume an e-commerce recommender has 10 million products and a 120 ms server-side p99 budget.

A plausible funnel could be:

- 10,000,000 products
- candidate generation retrieves 2,000 items in 30 ms
- pre-ranking reduces 2,000 to 300 in 15 ms
- feature hydration for 300 items takes 20 ms
- heavy ranking takes 35 ms
- reranking and post-processing take 10 ms
- orchestration/network overhead takes 10 ms

The critical-path total is roughly:

$$
30 + 15 + 20 + 35 + 10 + 10 = 120 \text{ ms}
$$

Candidate generation might combine:

- 800 collaborative-filtering candidates,
- 500 co-visitation candidates,
- 400 content-similarity candidates,
- 200 trending candidates,
- 100 cold-start or business-fallback candidates,

followed by deduplication.

Suppose the true item a user eventually purchases is absent from those 2,000 candidates. The heavy ranker could be perfect and still fail. Retrieval has imposed a zero probability of ranking that item. This is the **retrieval ceiling**.

Suppose instead that the purchased item is present at candidate rank 1,500, but the pre-ranker removes it before the heavy ranker. Then the pre-ranker, not retrieval, created the ceiling.

Suppose candidate recall is unchanged but the top-10 recommendations become poor after deployment. The failure is more likely downstream: features, heavy ranking, reranking, post-processing, serving, or objective mismatch.

Important beginner distinctions:

- Candidate generation is not "a worse ranker"; it solves a different search problem over a much larger space.
- Pre-ranking is not mandatory; it exists only when the heavy ranker cannot economically process the retrieval set.
- Ranking and reranking are not synonyms: ranking estimates item utility/order; reranking modifies the slate under cross-item or policy constraints.
- Post-processing should not silently become a second opaque ranker. Its rules should be explicit and observable.
- High final NDCG cannot prove candidate generation is healthy unless retrieval recall is measured separately.
- High retrieval recall does not prove the final list is good; downstream ordering can still fail.

### Core Interview Reasoning

A compact reasoning sequence for this question is:

**stage → local objective → candidate count → cost/latency → quality ceiling → metric → failure mode**

That structure prevents describing the pipeline as a list of components without explaining why each exists.

**1. Start with the funnel constraint.**  
The expensive model cannot usually score the entire catalog. Early stages must reduce search space cheaply; later stages can spend more computation per item.

**2. Candidate generation: maximize opportunity.**  
Ask: which items deserve a chance to be considered? Candidate generation should favor recall, coverage, freshness, and channel complementarity. Multiple candidate sources are common because no single retrieval method dominates across all user/item states.

**3. Pre-ranking: preserve quality while removing cost.**  
Ask: can the expensive ranker afford the retrieved set? If not, use a cheap model or feature subset to prune. The governing invariant is that the pre-ranker should remove computation faster than it removes valuable candidates.

**4. Ranking: estimate item-level utility accurately.**  
Ask: among the survivors, which items best satisfy the product objective? This is where richer features, interaction models, and multi-task objectives are usually justified.

**5. Reranking: optimize the slate, not isolated items.**  
Ask: does a list of individually high-scoring items form a good result set? Diversity, redundancy, freshness, exploration, caps, and other list-level concerns belong here.

**6. Post-processing: enforce final correctness.**  
Ask: is every returned item legal, available, non-duplicated, compatible with policy, and representable by the client? Final hard constraints need deterministic behavior and fallbacks.

**7. Debug by locating the first divergence.**  
Measure every stage boundary. If retrieval metrics diverge first, later failures are consequences. If retrieval remains healthy and ranking metrics diverge, inspect ranking inputs/model. If model scores are stable but response composition changes, inspect reranking/post-processing. If all offline stage metrics are stable but business outcomes move, inspect serving/exposure/experiment validity or objective mismatch.

**8. Allocate latency by marginal value.**  
A stage does not deserve latency merely because it exists. Increase candidate count, feature richness, or model complexity only while the marginal quality gain justifies added p99, compute, and operational complexity.

A useful stage contract table is:

| Stage | Primary objective | Typical quality ceiling / risk | Core measurements |
|---|---|---|---|
| Candidate generation | High recall at low cost | Missing item is unrecoverable | Recall@K, union/marginal recall, coverage, latency |
| Pre-ranking | Preserve strong candidates while pruning | Premature pruning lowers downstream ceiling | preservation recall, ranker-agreement, latency saved |
| Ranking | Accurate utility/order | Bounded by upstream candidates | NDCG/MRR/CTR/log-loss/calibration as appropriate |
| Reranking | Slate quality + constraints | Can sacrifice relevance for slate goals | final-list utility, diversity, constraint rate |
| Post-processing | Hard correctness/eligibility | Can silently remove valid high-score items | drop reasons, fallback rate, invalid-item escape rate |

The interview answer becomes strong when it does not merely define the stages, but connects **each stage to a distinct optimization problem and a distinct failure boundary**.

### Deeper Reasoning and Derivations

#### 1. Why staged ranking is computationally necessary

Let:

- $N$ be catalog size,
- $C_r$ be the cost of cheap retrieval per request,
- $k_1$ be retrieved candidate count,
- $C_p$ be pre-rank cost per candidate,
- $k_2$ be survivors after pre-ranking,
- $C_h$ be heavy-ranker cost per candidate.

A simplified request cost is:

$$
C_{\text{total}}
\approx
C_r + k_1 C_p + k_2 C_h.
$$

If the heavy ranker were applied directly to all $N$ items, the cost would scale roughly as:

$$
N C_h,
$$

which becomes infeasible when $N$ is millions and $C_h$ includes feature hydration or deep interaction computation.

The funnel trades some search optimality for computational tractability. The design problem is not to minimize candidates blindly, but to minimize cost **subject to preserving enough downstream quality**.

#### 2. The upstream quality-ceiling principle

Let $G_u$ be the set of items considered relevant or valuable for user/context $u$, and let $C_K(u)$ be the $K$ candidates returned by retrieval.

Candidate recall can be written as:

$$
\operatorname{Recall@K}(u)
=
\frac{|G_u \cap C_K(u)|}{|G_u|}.
$$

If a relevant item is outside $C_K(u)$, a downstream ranker cannot place it in the final list. Therefore, downstream quality is conditioned on the candidate set.

This yields a useful debugging rule:

**stable candidate recall + degraded final ranking quality means retrieval is less likely to be the first failure boundary.**

It does not prove retrieval is perfect—distributional composition may still change—but it narrows the search.

#### 3. Candidate-source complementarity and marginal recall

Suppose source A retrieves 1,000 items with 80% recall and source B retrieves 1,000 items with 70% recall. Their union does not automatically have 150% recall, because the sources overlap.

What matters operationally is **marginal recall**:

$$
\Delta R_B
=
R(A \cup B) - R(A).
$$

A source with lower standalone recall may still be valuable if it retrieves items that stronger sources systematically miss, especially for cold-start users, new items, niche interests, or long-tail content.

Therefore source quotas should be informed by:

- union recall,
- marginal recall,
- overlap,
- cost,
- segment-specific recall,
- freshness,
- failure independence.

#### 4. Why pre-ranking can help and hurt

Pre-ranking is beneficial when:

$$
\text{quality lost by pruning}
<
\text{quality gained by allowing a stronger downstream ranker within budget}.
$$

For example, if a heavy ranker can process only 300 items within the p99 budget, but retrieval returns 2,000, a pre-ranker may be necessary. A good pre-ranker is not judged only by its own NDCG. It is judged by how much final-system quality it preserves per unit of cost removed.

A subtle failure occurs when the pre-ranker is trained on a target or feature set too similar to the heavy ranker but with insufficient capacity. It may systematically remove unusual items the heavy model could have correctly recovered.

#### 5. Why reranking exists after ranking

Independent item scores assume that the utility of item $i$ can be evaluated without fully modeling what else appears in the slate. But user value can be non-additive:

- redundant items compete for the same attention,
- categories may need diversity,
- marketplace exposure may have concentration limits,
- one item may complement another,
- freshness and exploration may be list-level requirements.

Thus the optimal slate can differ from the top items under independent scores.

A simple diversity-aware reranking objective might trade relevance against redundancy:

$$
\text{slate score}
=
\sum_i \text{relevance}(i)
-
\lambda
\sum_{i<j} \text{similarity}(i,j).
$$

The point is not the exact formula; it is that the reranker has access to **relationships among selected items**, which the base ranker may not.

#### 6. Latency is a critical-path property

A naive latency sum is useful, but real systems include parallel work. If candidate sources execute in parallel, total retrieval latency is closer to the slowest required source plus orchestration, not the sum of all source latencies.

Similarly, some features may be fetched concurrently. Therefore the architecture should distinguish:

- total compute,
- wall-clock critical path,
- fan-out tail amplification,
- timeout policy,
- optional versus mandatory sources.

This matters because adding one 20 ms candidate source may cost almost nothing at the median if parallelized, yet still worsen p99 if it becomes the slowest dependency.

#### 7. Metrics must align with stage responsibility

A common architectural mistake is evaluating every stage with the final product metric.

Candidate generation should not be primarily optimized for final top-10 NDCG because it does not control final ordering. A ranker should not be blamed for relevant items absent from the candidate set. A reranker should not be evaluated only by base-model score retention if its purpose is diversity or constraint satisfaction.

Stage-specific metrics create causal observability.

### Advanced Staff-Depth Considerations

The universal reasoning loop for this architecture is:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate**

Compressed:

**Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**

For R01, the baseline is a measurable funnel with explicit candidate counts, stage objectives, latency budgets, version contracts, and stage-boundary metrics. The most important mechanisms are candidate-set ceilings, pruning, feature/model scoring, slate interaction, and final eligibility. The observables are candidate recall, marginal source recall, per-stage latency, score distributions, pruning rates, constraint-drop reasons, segment metrics, and online product outcomes. Decisions include candidate budgets, source quotas, pre-rank aggressiveness, model complexity, reranking strength, and fallback behavior. Validation requires offline replay plus staged online rollout because a locally improved stage can still degrade the whole system.

#### 1. Changed Constraints and Transfer Logic

The architecture should preserve its core invariant under changed constraints: **expensive computation is spent only on a progressively smaller set while upstream stages preserve downstream opportunity**. What changes is the appropriate number of stages, candidate counts, model complexity, and freshness strategy.

If latency tightens, the first question is not simply "which model do we remove?" It is which stage consumes critical-path time and which quality curve is flattest. Retrieval may be parallelized or approximated; pre-ranking may become more aggressive; features may be precomputed; the heavy ranker may be distilled or quantized; reranking may use simpler constraints. But eliminating candidate diversity to save a few milliseconds can create a permanent retrieval ceiling.

Representative template:

- Original assumption: 120 ms p99 allows retrieval, pre-rank, feature hydration, heavy rank, and rerank.
- Changed constraint: p99 target drops to 70 ms.
- Invariant: high-value candidates must survive until the strongest affordable scoring stage.
- Broken assumption: current heavy-ranker and feature path fit the request budget.
- Consequence: timeout risk or forced truncation increases, especially at tail latency.
- Design change: parallelize retrieval sources, precompute slow features, reduce candidates before heavy rank, and use a distilled ranker with deterministic fallback.
- Metric impact: candidate recall should remain near baseline; final NDCG/CTR may fall slightly if ranker capacity is reduced.
- Trade-off: lower p99 and higher reliability for some loss in ranking expressiveness.
- Validation: replay with recorded requests, compare stage recall/quality and p99, then canary online with fallback and segment guardrails.

#### 2. Failure Modes and Diagnosis

Failure localization should follow the actual data path:

**candidate sources → union/dedup → pre-rank → feature hydration → ranker scores → rerank/constraints → post-processing → exposure → product outcome**

The key is to identify the **first divergence** from a healthy baseline.

Examples:

- candidate recall drops while downstream score behavior is unchanged: inspect source freshness, ANN/index/model versions, quotas, filters, and source outages;
- candidate recall is stable but NDCG drops: inspect pre-rank pruning, feature skew, ranker model/config, missing features, or distribution shift;
- ranker metrics and score distributions are stable but final category mix changes: inspect reranking and post-processing;
- offline stages are stable but CTR/conversion drops: inspect latency, timeouts, exposure logging, experiment assignment, UI changes, or objective mismatch.

Filled template:

- Symptom: online conversion drops 8% after deployment while aggregate candidate Recall@1000 is unchanged.
- Stage decomposition: retrieval → pre-rank → features → ranker → rerank → post-process → exposure.
- Slices: new users, returning users, device, region, category, candidate source, latency bucket.
- Competing hypotheses: feature skew, ranker version issue, reranker constraint change, timeout fallback, objective mismatch.
- Discriminating evidence: compare feature distributions, score histograms, final-slate diffs, timeout/fallback rate, and source contribution against control.
- Offline/online comparison: replay identical logged requests through old and new stacks and compare boundary outputs.
- Replay/isolation: freeze candidate set, then compare rankers; freeze ranker scores, then compare rerank/post-process.
- First divergence: e.g. feature hydration returns stale inventory for one region before ranker scoring.
- Immediate mitigation: rollback or switch to previous feature snapshot/model bundle.
- Permanent prevention: version-coupled feature/model contracts, freshness SLOs, replay tests, and regional slice alerts.

#### 3. Latency and Resource Trade-offs

End-to-end latency is governed by the critical path:

$$
L_{\text{total}}
\approx
L_{\text{retrieval}}
+
L_{\text{pre-rank}}
+
L_{\text{features}}
+
L_{\text{ranking}}
+
L_{\text{reranking}}
+
L_{\text{overhead}},
$$

with the caveat that parallel work contributes through the slowest dependent branch rather than a simple sum.

Candidate count is a major multiplier. Increasing retrieval from 1,000 to 5,000 may improve recall but can multiply feature-fetch volume and ranking work. Therefore every extra candidate should justify its downstream cost.

Optimization knobs include:

- source-specific candidate quotas;
- ANN search effort;
- source parallelism and timeouts;
- precomputed or cached features;
- cheaper pre-rankers;
- candidate pruning;
- model distillation/quantization;
- batching/vectorization;
- reduced cross features;
- deterministic fallback rankers;
- skipping optional reranking under deadline pressure.

Filled template:

- Budget: 100 ms p99 server-side.
- Cost decomposition: 30 ms retrieval, 15 ms pre-rank, 20 ms features, 30 ms heavy rank, 5 ms rerank/overhead.
- Dominant cost: heavy ranking plus feature hydration.
- Quality driver: candidate breadth and interaction-rich ranking.
- Cost driver: candidates reaching online feature hydration and heavy inference.
- Optimization knobs: prune from 2,000 to 400 earlier, precompute item features, batch scoring, distill heavy ranker.
- Fallback/degradation: if feature/ranker deadline is exceeded, use cached/light ranker on retrieved candidates and still enforce hard constraints.
- Trade-off curve: p99 decreases as candidate count/model complexity falls, but NDCG and long-tail recall eventually degrade.
- Decision: choose the knee of the measured quality-latency curve, not a fixed candidate count by convention.

#### 4. Scale and Capacity

The first scaling assumption to break is often not the ranker itself but the amount of state and fan-out surrounding it.

As catalog size grows:

- brute-force retrieval stops fitting latency;
- ANN/index memory and rebuild time rise;
- candidate-source computation becomes more expensive;
- feature storage grows.

As QPS grows:

- online feature stores become bottlenecks;
- network fan-out amplifies tails;
- GPU batching and utilization become important;
- cache hit rate and hotspot behavior matter.

As event volume grows:

- freshness pipelines, deduplication, and feature updates become operational bottlenecks.

Filled template:

- Scaling dimension: catalog grows from 10M to 500M items while QPS grows 10×.
- Baseline scale assumption: current ANN index fits comfortably in RAM and can be rebuilt quickly.
- First bottleneck: index memory and refresh/rebuild time.
- Second-order effects: more shards increase fan-out and tail latency; replication increases memory cost.
- Architectural response: shard/partition retrieval, compress embeddings, route queries, maintain incremental updates plus periodic rebuild.
- Partitioning/replication/caching/batching: partition by stable routing key where possible, replicate hot shards, cache head-query or user retrieval outputs carefully, batch embedding inference.
- Consistency/freshness consequence: model and index versions must remain coupled across partitions.
- Operational failure mode: partial rollout yields mixed embedding spaces and recall collapse.
- Validation: exact-vs-ANN recall benchmarks per shard, shadow index comparison, p99 under production-like fan-out, rollback rehearsal.

#### 5. Freshness, State, and Versioning

Different stages own different state:

- user/session features may need seconds-to-minutes freshness;
- item availability may need near-real-time freshness;
- co-visitation statistics may refresh hourly;
- embeddings may refresh daily or incrementally;
- model parameters may deploy less frequently;
- ANN indexes may lag embedding generation;
- business rules and experiment configs may change independently.

The danger is **version skew**. A query embedding generated by model version B against an item index built with model version A may produce meaningless nearest neighbors even though both components are individually healthy.

Filled template:

- State that becomes stale: user/session features and item embeddings/index.
- Why freshness matters: stale user state misses recent intent; stale item state misses new or changed inventory.
- Required freshness: session features within seconds/minutes; item index according to catalog churn and product need.
- Refresh cost: streaming feature updates are cheap per event but operationally complex; embedding/index refresh can be expensive.
- Update architecture: streaming user features plus incremental item updates and periodic full index rebuild.
- Version consistency: package query encoder, item-embedding schema, index version, and feature schema under compatible release identifiers.
- Failure from version skew: candidate relevance collapses while ranker itself appears healthy.
- Fallback: route to prior compatible model/index bundle or lexical/popularity fallback.
- Measurement: index age, embedding age, version-mismatch counters, Recall@K shadow probes.
- Decision: spend freshness where behavior changes quickly; avoid real-time machinery for state whose value decays slowly.

#### 6. Implementation, Serving, and Observability

A conceptual multi-stage architecture is production-ready only if stage contracts are explicit.

Candidate generation needs source APIs/indexes, per-source quotas, deduplication, source attribution, timeouts, and fallback. Pre-ranking needs a defined feature subset and reproducible pruning policy. Ranking needs point-in-time-safe feature generation, feature/version contracts, model registry, calibrated or ordering score semantics, and efficient batch inference. Reranking needs deterministic constraint ordering or a well-defined optimization policy. Post-processing needs auditable drop reasons and hard guarantees.

Every request should produce enough telemetry to reconstruct the funnel:

- request/context ID;
- experiment assignment;
- candidate source and source rank;
- candidate counts before/after dedup and each pruning step;
- feature versions and missingness;
- model and index versions;
- scores;
- reranker actions;
- post-processing drop reasons;
- stage latencies;
- timeout/fallback path;
- final exposures.

Filled template:

- Conceptual object: staged recommendation funnel.
- Training/data implementation: point-in-time examples tied to impressions/outcomes and stage-specific labels where needed.
- Stored artifact/state: retrieval indexes, feature tables, model artifacts, rerank configs, policy rules.
- Serving path: request → parallel retrieval → union/dedup → optional pre-rank → feature hydration → heavy rank → rerank → hard post-process.
- Component contract: each stage specifies input schema, candidate count, score semantics, version, deadline, and fallback.
- Logging: source attribution, scores, pruning/drop reasons, exposures, outcomes, latency.
- Versioning: atomically compatible model/index/feature/config bundles.
- Failure mode: mixed versions or silent fallback changes final distribution.
- Observability: stage metrics, per-segment quality, latency, fallbacks, candidate-source health.
- Rollback: revert to prior compatible bundle, not just prior model weights.
- Testing/replay: deterministic request replay plus stage-boundary diff tests.

#### 7. Vertical Transfer

The multi-stage mechanism transfers widely: cheap broad filtering first, expensive precise decision-making later. What must be re-derived are labels, candidate sources, constraints, freshness, and product metrics.

**E-commerce/items.**  
Invariant: retrieve broadly, rank precisely, enforce final constraints.  
Changed assumptions: inventory and price change quickly; purchase labels are sparse and delayed.  
Consequence: availability must be hard-enforced, candidates need content/co-visitation/popularity/collaborative sources, and ranking often values conversion or expected value rather than pure engagement.

**Video/feed.**  
Invariant: staged retrieval and ranking remain useful.  
Changed assumptions: session intent changes quickly and consumption creates immediate feedback.  
Consequence: session-state freshness, watch/completion/skip signals, diversity, novelty, and long-horizon satisfaction become more central.

**Ads.**  
Invariant: a large eligible set is narrowed before expensive scoring.  
Changed assumptions: auction economics, budgets, pacing, calibration, and legal/business constraints are first-class.  
Consequence: ranking scores may need probability calibration and expected-value semantics; post-processing must respect budget/frequency constraints.

**Marketplace.**  
Invariant: user relevance still matters.  
Changed assumptions: provider exposure and supply health affect long-run value.  
Consequence: reranking may include provider caps/fairness and concentration controls; metrics need both consumer and provider sides.

Filled template for e-commerce:

- Invariant: broad candidate recall upstream, precise utility ranking downstream.
- Different data-generating process: impressions, clicks, carts, and purchases with delayed conversion.
- Different objective: relevance plus conversion/value and customer satisfaction.
- Different candidates/features: co-visitation, substitutes/complements, product content, price, inventory, seller.
- Different constraints: availability, policy, seller/category caps, duplicate variants.
- Metric change: Recall@K for retrieval; NDCG/CTR/CVR/revenue plus coverage and slice metrics downstream.
- Serving change: inventory/price freshness and deterministic suppression are stricter.
- Ecosystem effect: over-concentrating exposure can harm seller health and long-run assortment.
- Validation: offline stage metrics plus controlled online experiment with inventory and seller-segment guardrails.

#### 8. Objective and Metric Mismatch

A production regression can come from two fundamentally different causes.

**Execution failure:** the system is not correctly implementing the intended objective. Examples include stale features, wrong index version, serialization bugs, timeout fallback, or incorrect constraints.

**Objective mismatch:** the system is correctly optimizing a metric that does not adequately represent product value. For example, a ranker may improve predicted click probability while increasing clickbait, reducing conversion, or concentrating exposure too aggressively.

For R01, this distinction matters because each stage has local metrics. A team can improve candidate Recall@1000, pre-ranker agreement, or offline NDCG independently while degrading the end product. Local optimization is necessary for observability but insufficient for product success.

Filled template:

- Offline/model metric: NDCG@20 improves 4% with candidate Recall@1000 unchanged.
- Online/product outcome: conversion drops 6%.
- Execution verification: replay old/new stacks with identical candidates/features; verify model/index/feature versions, latency, fallback, and rerank configs.
- Metric semantics: NDCG rewards ordering according to the offline relevance label used.
- Blind spots: purchase value, satisfaction, diversity, delayed conversion, or exposure effects may be absent.
- Missing product factor: model over-optimizes click-heavy but low-conversion items.
- Repair: revise labels/objective or use multi-task/expected-value ranking with product guardrails.
- Trade-off: some offline NDCG may be sacrificed for better business/user utility.
- Online validation: staged experiment with CTR, CVR, value, satisfaction, latency, and segment guardrails.

## Material Follow-ups / Scenario Variants

### Candidate recall is unchanged, but online conversion drops after a ranker deployment. Where do you look?

Treat stable candidate recall as evidence that the retrieval ceiling is probably unchanged, then localize downstream. First verify pre-rank preservation, feature freshness and schema/version parity, ranker score distributions, calibration if scores feed thresholds or expected value, reranking/constraint diffs, timeout/fallback rates, and post-processing drop reasons. Replay the same requests through old and new stacks while freezing upstream candidates to isolate the first divergence. If execution is correct, test objective mismatch: the new ranker may improve its offline target while worsening conversion or another product metric. Mitigate with rollback if user impact is material; permanently fix the first divergent component or the objective/metric contract.

### A heavier ranker improves offline NDCG but pushes p99 over budget. How should the architecture change?

Measure the quality-latency curve rather than debating model complexity abstractly. Determine whether the dominant cost is inference, feature hydration, candidate count, or orchestration. Preserve candidate recall, then try earlier pruning, feature precomputation, batching/vectorization, distillation, quantization, or smaller interaction layers. If quality gains concentrate in the highest-confidence candidates, reduce the number sent to the heavy model. Define a deadline-aware fallback. Ship only if the online gain justifies added p99 and cost; otherwise keep the simpler ranker.

### One candidate source is slow and overlaps heavily with other sources. Should it be removed?

Evaluate its **marginal** contribution, not standalone recall. Measure union recall with and without the source, especially on slices where other sources are weak, then compare marginal recall against p99, compute, freshness, and operational risk. A highly overlapping source may still be useful as a failure-independent fallback; alternatively it may add little value and worsen tail latency. Removal should be validated by offline replay and an online experiment or shadow analysis on affected segments.

### When is pre-ranking unnecessary?

If candidate generation already returns a set small enough for the heavy ranker to process within p99 and cost limits, pre-ranking adds complexity without economic value. It creates another model, another version boundary, another source of pruning error, and another monitoring surface. The correct architecture is the simplest funnel that satisfies quality and resource constraints. Pre-ranking becomes justified only when its cost savings enable a stronger downstream stage or higher candidate recall than the system could otherwise afford.
