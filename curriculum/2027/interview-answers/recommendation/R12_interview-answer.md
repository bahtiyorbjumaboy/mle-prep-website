---
type: interview-answer
item: "2027:R12"
title: "Candidate Blending and Adaptive Retrieval Budgets"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - candidate-generation
  - retrieval
  - adaptive-budgets
---

## Canonical Staff-Depth Question

Given multiple candidate sources with different overlap, recall, cost, and segment behavior, design static or adaptive quota allocation and fallbacks.

## Mastery Answer

I would frame candidate blending as a constrained resource-allocation problem, not as “give every retriever the same number of slots.” The retrieval layer has a fixed latency and candidate budget, and each source contributes a different amount of incremental useful recall after accounting for overlap with the candidates already retrieved.

I would start by making each source observable independently. For source $s$, I want its raw candidate count, unique candidates after deduplication, source-attributed recall at relevant cutoffs, marginal recall given the other sources, latency distribution, compute/network cost, coverage, and segment-level behavior. Raw recall alone is insufficient because two strong sources may return mostly the same items. The useful quantity is the extra relevant coverage gained by allocating more budget to that source.

For a static policy, I would estimate marginal utility curves such as

$$
\Delta U_s(k)
=
U(C \cup C_s(k+\Delta k)) - U(C \cup C_s(k)),
$$

where $C$ is the current blended set and $C_s(k)$ is the top $k$ from source $s$. I would compare that gain with marginal cost: additional latency, CPU/GPU work, ANN probes, feature work, or downstream ranker load. The allocation should continue toward sources with the highest incremental value per unit cost, subject to product constraints such as minimum coverage for cold-start or freshness channels. This usually yields unequal quotas.

I would measure the curves by candidate count rather than choosing one operating point blindly. For example, embedding retrieval might have high early marginal recall but saturate quickly; co-visitation may add complementary session-intent items; popularity may be cheap and robust but redundant for head users; content retrieval may be disproportionately valuable for new items. The right static quota is therefore a measured operating point on a quality-cost frontier.

Then I would make the budget adaptive only where heterogeneity justifies the complexity. A lightweight policy can condition on user-history length, session activity, query/context confidence, inventory state, source health, or predicted marginal gain. New users may receive more popularity/content budget; highly active sessions may shift budget toward co-visitation or session embeddings; a sparse or degraded ANN source may surrender capacity to healthy fallbacks. I would keep hard caps and minimums so the policy cannot starve strategically important channels or explode latency.

Fusing candidates requires deterministic deduplication and source attribution. An item retrieved by multiple channels should normally appear once, while retaining all source provenance as features or diagnostic metadata. The downstream ranker should not inherit arbitrary source-order bias from concatenation.

Fallbacks are part of the design, not an afterthought. If one source times out or returns too few valid items, I would have a deadline-aware policy that reallocates unused quota to cheap, healthy sources such as popularity, cached co-visitation, or precomputed content candidates. If the heavy retrieval path exceeds its deadline, return a smaller deterministic candidate set rather than waiting and violating p99.

Finally, I would validate offline and online. Offline I would report union recall, marginal recall by source and candidate count, overlap/Jaccard matrices, segment metrics, and latency/cost curves. Online I would test end metrics plus guardrails such as p99 latency, coverage, diversity, cold-start performance, and fallback rate. The Staff-level principle is: allocate candidate budget from measured marginal utility under constraints, verify it by segment, and preserve graceful degradation when sources or budgets change.

## Learn the Concepts

### Foundation

A recommendation system rarely asks one algorithm for all candidates. Instead, several **candidate sources** each propose a relatively small set of items from a much larger catalog. Examples include popularity, co-visitation, collaborative filtering, content similarity, graph retrieval, and embedding/ANN retrieval.

The retrieval stage exists because the final ranker cannot score the whole catalog. If the catalog has 10 million items but the ranker can afford to score only 1,000, retrieval is responsible for shrinking 10 million items to roughly 1,000 candidates while trying not to discard items that could have been excellent final recommendations.

A **candidate budget** is how many items a source is allowed to contribute or how much compute it may spend. A **quota** is the explicit candidate-count allocation, such as 400 embedding candidates, 250 co-visitation candidates, 200 popularity candidates, and 150 content candidates. These numbers should be treated as system decisions, not constants handed down by tradition.

Four ideas govern the allocation:

1. **Recall.** Did a source retrieve items that matter for the target outcome? Retrieval recall is concerned with whether useful/relevant items survive the candidate stage.
2. **Overlap.** Two sources can each look strong alone while contributing nearly the same items. Their union may therefore be much less valuable than the sum of their standalone recalls suggests.
3. **Cost.** More candidates may require more ANN probes, network calls, filtering, deduplication, feature hydration, and ranker scoring. Candidate count therefore affects both retrieval and downstream cost.
4. **Segment behavior.** A source can be weak on average but essential for a particular cohort. Content retrieval may matter disproportionately for new items; popularity may matter more for anonymous users; session co-visitation may matter more when recent intent is strong.

A candidate source's **standalone recall** asks, “How many relevant items does this source retrieve by itself?” Its **marginal recall** asks, “How many additional relevant items does this source add after the candidates from other sources are already present?” Marginal recall is the more important quantity for blending.

Suppose the relevant set for one user is $\{A,B,C,D\}$. Embedding retrieval returns $\{A,B,X,Y\}$ and co-visitation returns $\{A,B,C,Z\}$. Each source retrieves two or three useful items, but their overlap is large. The embedding source contributes $A,B$; after those are already present, co-visitation's marginal contribution is primarily $C$. A third source returning $\{D,Q,R,S\}$ has lower standalone hit count than co-visitation but greater marginal value because it contributes the missing relevant item $D$.

A simple worked system example makes the trade-off concrete. Assume a ranker can score at most 1,000 unique candidates within budget. At 400 embedding candidates, 250 co-visitation candidates, 200 popularity candidates, and 150 content candidates, deduplication may leave only 760 unique items because the sources overlap. Increasing embedding from 400 to 600 might produce only 25 new unique items and almost no new relevant items, while increasing content from 150 to 250 might add 70 unique items and improve new-item recall. The correct reaction is not “embedding is our best model, so give it more.” It is “the marginal return of embedding has saturated; content has more complementary value at this point.”

Important distinctions:

- **Candidate quota vs final exposure:** a source can contribute many candidates and still receive little final exposure if the ranker rejects them.
- **Standalone recall vs marginal recall:** standalone performance ignores redundancy with other sources.
- **Candidate count vs unique candidate count:** deduplication can make nominal quotas very different from the actual ranker workload.
- **Static quota vs adaptive quota:** static uses the same allocation rule broadly; adaptive changes allocation based on context, segment, source health, or estimated marginal utility.
- **Source failure vs weak source:** a failed source cannot serve its intended candidates; a weak source is healthy but contributes low incremental value.

### Core Interview Reasoning

A strong answer can use the sequence:

**objective and constraints → instrument sources → measure marginal value → choose baseline quotas → adapt selectively → deduplicate/attribute → define fallbacks → validate**

**1. State the retrieval objective and hard constraints.**

The retrieval layer maximizes the quality ceiling available to the downstream ranker under constraints. Those constraints include total candidate count, retrieval latency, downstream ranker capacity, compute/network cost, and product requirements such as cold-start or freshness coverage.

A useful abstraction is:

$$
\max_{k_1,\ldots,k_m} U\!\left(\bigcup_{s=1}^{m} C_s(k_s)\right)
$$

subject to

$$
\sum_s \text{Cost}_s(k_s) \le B,
$$

plus candidate-count, latency, and coverage constraints. Here, $k_s$ is the budget for source $s$, $C_s(k_s)$ is its top-$k_s$ candidate set, $U$ is retrieval utility, and $B$ is the available resource budget.

This formulation matters because the utility is a function of the **union**, not the sum of individual source scores.

**2. Instrument every source independently.**

For each source, log at least:

- requested and returned count;
- valid count after policy/availability filters;
- unique contribution after deduplication;
- standalone recall/HitRate where labels allow it;
- marginal recall conditional on the other sources;
- source overlap matrix;
- p50/p95/p99 latency;
- timeout/error/empty-result rate;
- cost proxies such as ANN probes, RPCs, CPU/GPU time, or bytes transferred;
- segment slices such as new user, sparse user, active session, new item, geography, device, or catalog category.

Without provenance and source-level telemetry, quota tuning becomes guesswork.

**3. Measure marginal utility curves.**

For each source, sweep candidate counts and measure the gain from additional candidates. If $U(k)$ is union retrieval utility at a particular allocation, the finite-difference marginal gain for source $s$ is approximately

$$
\frac{\Delta U_s}{\Delta k_s}.
$$

For cost-aware allocation, compare

$$
\frac{\Delta U_s}{\Delta \text{Cost}_s}.
$$

The curves often show diminishing returns: the first 50 or 100 candidates can add much more value than candidates 900–1000. This is why fixed equal quotas are rarely principled.

**4. Choose a static baseline before building adaptation.**

A static policy is easier to debug, replay, capacity-plan, and A/B test. A strong first design allocates quotas using measured marginal value while preserving minimum floors for strategically important channels. For example, a content channel may deserve a floor for new-item coverage even if its aggregate marginal recall is lower.

The static policy should include per-source caps, total-unique-candidate targets, and explicit overfetch assumptions when deduplication or filtering is high.

**5. Add adaptation only for stable, explainable heterogeneity.**

Adaptive budgeting is useful when the marginal-value curves differ materially by context. Possible signals include:

- user-history length;
- session recency/activity;
- confidence in a user or session embedding;
- cold-start status;
- query/context class;
- catalog availability;
- source latency/health;
- predicted source yield or unique-candidate rate.

The policy can begin rule-based. A later version may use a learned gating/budget model, but that model must be constrained because mistakes occur upstream of ranking: starving a source removes candidates that the ranker can never recover.

**6. Deduplicate while preserving provenance.**

The same item should normally be scored once downstream. Deduplication therefore forms a union of candidate identities. However, the system should keep provenance such as `retrieved_by_embedding`, `retrieved_by_covisit`, source ranks, and source scores. Those signals are useful for analysis and can be useful ranker features if generated consistently.

**7. Design fallback and deadline behavior.**

Each source should have a deadline and a defined response when it is late, empty, corrupt, or unavailable. Safe fallbacks are usually cheap and deterministic. Unused capacity can be reallocated to a healthy source if there is enough time, but fallback logic must not itself create unbounded fan-out or duplicate work.

**8. Validate the policy as a system.**

Offline validation should include union recall, source marginal recall, unique-yield curves, overlap, segment metrics, and cost/latency. Online experiments should test product outcomes with retrieval health and latency as guardrails. A policy that improves aggregate Recall@K while harming new-user coverage or p99 is not automatically better.

### Deeper Reasoning and Derivations

The central mathematical reason candidate blending is different from independent source tuning is **substitution through overlap**. If two sources retrieve the same items, one source's value depends on what the other source already returned.

Let $G(u)$ be the set of relevant items for user/context $u$, and let the blended candidate set be

$$
C(u;\mathbf{k}) = \bigcup_{s=1}^{m} C_s(u;k_s),
$$

where $\mathbf{k}=(k_1,\ldots,k_m)$ is the quota vector. A simple retrieval utility is

$$
R(u;\mathbf{k})
=
\frac{|G(u)\cap C(u;\mathbf{k})|}{|G(u)|}.
$$

The expected objective across requests is $\mathbb{E}_u[R(u;\mathbf{k})]$, perhaps weighted by segment importance or replaced with another stage-appropriate utility.

The marginal value of adding $\Delta k$ candidates to source $s$ is

$$
\Delta_s U
=
U(k_1,\ldots,k_s+\Delta k,\ldots,k_m)
-
U(k_1,\ldots,k_s,\ldots,k_m).
$$

If this marginal value is small, then the additional candidates are either irrelevant, redundant, filtered, or too deep in the source ranking to matter. Each case suggests a different intervention.

A cost-aware greedy approximation allocates the next small budget increment to the source with the largest ratio

$$
\rho_s
=
\frac{\Delta_s U}{\Delta_s C},
$$

where $\Delta_s C$ is the marginal resource cost. This is not a universal proof of global optimality because utility and cost can interact across sources, latency may be parallel rather than additive, and downstream ranking quality can be non-linear. But it is a powerful diagnostic and baseline allocation rule.

**Overlap changes the economics.** Consider two sources $A$ and $B$. If their useful result sets are nearly identical, then

$$
|G\cap (A\cup B)|
\approx
\max(|G\cap A|, |G\cap B|),
$$

not their sum. High standalone recall from both does not imply high union gain. Pairwise Jaccard overlap is useful diagnostically,

$$
J(A,B)=\frac{|A\cap B|}{|A\cup B|},
$$

but candidate overlap alone is not sufficient: overlap among relevant candidates matters more than overlap among irrelevant ones.

**Deduplication creates a hidden budget problem.** Suppose the ranker target is 1,000 unique candidates and the average duplication rate is 30%. Requesting exactly 1,000 candidates across sources may yield only about 700 unique items. A production blender may therefore overfetch and stop once a unique target is reached, but overfetch must be bounded because it raises source and downstream cost.

**Segment averaging can conceal a necessary source.** Let the population contain head users $H$ and cold users $C$. An aggregate utility

$$
U = p_H U_H + p_C U_C
$$

can make a cold-start source look unattractive when $p_C$ is small. If product requirements demand a minimum cold-user quality, the optimization should include a constraint such as

$$
U_C(\mathbf{k}) \ge \tau_C
$$

rather than expecting one global average to protect the segment.

**Adaptive allocation is a contextual decision problem.** Let $x$ describe the request: user-history length, session signals, source-health state, device, region, or candidate-yield predictions. Then the policy chooses

$$
\mathbf{k}(x) = \pi(x),
$$

subject to per-request resource constraints. The benefit of adaptation is the gap between the best one-size-fits-all allocation and the expected utility of a context-sensitive policy. The policy is justified only if this gain exceeds added operational complexity, estimation error, instability, and observability burden.

**Latency is not necessarily additive.** If sources run in parallel, total retrieval latency is closer to the maximum critical-path source latency plus orchestration than to the sum of source latencies. However, adding a slow source can still dominate p99, increase timeout frequency, consume shared pools, or expand the ranker workload. Therefore candidate allocation must consider both source-level cost and end-to-end critical-path cost.

**The retrieval ceiling matters.** A ranker cannot surface an item that retrieval discarded. This makes false negatives in candidate generation qualitatively different from ranker score errors. Aggressive budget optimization can reduce cost while silently lowering the maximum achievable ranking quality. Candidate policies must therefore be judged on both efficiency and the quality ceiling they preserve.

### Advanced Staff-Depth Considerations

The universal Staff reasoning loop for this item is:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate.**

For candidate blending, the baseline is the current set of sources, quotas, latency budget, unique-candidate target, and segment requirements. A change might be a larger catalog, a new cold-start cohort, a slow ANN service, or a source whose marginal recall has saturated. The mechanism is how that change alters overlap, candidate yield, recall, cost, or the downstream ranking ceiling. Evidence comes from source-attributed recall, marginal-recall curves, overlap, segment slices, latency, timeout rates, and replay. The decision is a quota/fallback/policy change, and validation requires offline replay plus online experimentation under latency and segment guardrails.

The compressed form is **Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**. For R12 specifically, the invariant is that candidate budgets should buy complementary useful coverage within system constraints; the quotas themselves are not invariants.

#### 1. Changed Constraints and Transfer Logic

A static blend implicitly assumes that the relative value and cost of sources are stable enough across traffic. That assumption breaks when user state, catalog state, traffic mix, or source health changes. The redesign should follow the mechanism of the change rather than merely retuning all quotas.

For example, if traffic shifts toward anonymous/new users, collaborative sources can lose yield because they lack personalized history, while popularity and content sources retain signal. The invariant is still to preserve a strong candidate-quality ceiling within the retrieval budget. The broken assumption is that historical-user marginal-recall curves represent the new traffic mix. The response is to condition allocation on cold-start state or establish a cold-user policy tier, then validate both aggregate and cold-user recall/online outcomes.

Filled template:

- Original assumption: most requests have enough behavioral history for personalized retrievers to dominate early marginal recall.
- Changed constraint: anonymous/new-user traffic doubles.
- Invariant: maximize complementary useful candidate coverage within the same latency and downstream candidate budget.
- Broken assumption: the old per-source marginal-recall curves remain representative.
- Consequence: personalized quotas waste budget on low-yield candidates and cold-user recall falls.
- Design change: reduce history-dependent quotas for cold users and raise content/popularity/trending allocation with explicit floors.
- Metric impact: expect improved cold-user Recall@K/coverage; aggregate metrics may move only modestly.
- Trade-off: less personalization for cold users in exchange for higher usable candidate yield and robustness.
- Validation: offline cold-user replay followed by an online cold-user slice experiment with p99 and diversity guardrails.

#### 2. Failure Modes and Diagnosis

Candidate blending can fail through at least five distinct mechanisms: a source returns too few candidates; a source returns many candidates but mostly duplicates; a source's quality distribution drifts; the blender misallocates quota; or downstream filtering/deduplication destroys the intended mix. The same aggregate symptom—lower final conversion—can originate at any of these boundaries.

Localization should follow the candidate path: request context → per-source retrieval → filtering → deduplication/blending → unique candidate set → ranker → exposure. Compare requested count, returned count, valid count, unique contribution, source-attributed relevant hits, and latency at each boundary. If standalone source recall is stable but marginal recall falls, overlap likely increased. If source recall is stable but blended recall falls, blending/filtering/deduplication is suspect. If blended recall is stable and online outcomes fall, the primary fault is probably downstream of retrieval.

Filled template:

- Symptom: aggregate Recall@1000 drops after a quota-policy rollout.
- Stage decomposition: source request → source return → policy filtering → deduplication → union → ranker input.
- Slices: new vs established users, head vs tail items, region/device, policy version, source-health state.
- Competing hypotheses: ANN quality regression; excessive overlap; quota starvation; availability filtering; dedup bug.
- Discriminating evidence: per-source standalone recall, unique contribution, overlap matrix, requested/returned counts, filter-drop rates.
- Offline/online comparison: replay old and new policies on the same logged request set and compare candidate unions before ranking.
- Replay/isolation: force fixed quotas and individually disable sources to locate the first changed boundary.
- First divergence: new policy cuts content-source unique contribution for tail items despite stable source health.
- Immediate mitigation: revert to the prior static quota table or enforce a content-source floor.
- Permanent prevention: policy guardrails plus pre-deploy replay tests on segment-level marginal recall and minimum source contribution.

#### 3. Latency and Resource Trade-offs

Candidate count is not free. A larger source budget can increase ANN work, network payload, filter work, deduplication, feature hydration, and the number of candidates scored downstream. The dominant cost must be identified empirically because different architectures place the bottleneck in different stages.

If sources run in parallel, the slowest healthy source can dominate retrieval p99. A small quality gain from a slow source may therefore be more expensive than a larger gain from a cheap source. Conversely, if downstream ranker inference dominates, the key optimization may be reducing the final unique union rather than reducing retrieval RPC count.

Safe optimization knobs include reducing deep low-yield retrieval, changing ANN search effort, caching/precomputing stable channels, filtering earlier, using cheaper sources as fallbacks, parallelizing independent channels, and setting source deadlines. Any optimization should state the quality ceiling it sacrifices.

Filled template:

- Budget: 40 ms retrieval p99 and at most 1,000 unique candidates entering pre-rank.
- Cost decomposition: parallel source RPCs + ANN work + filtering/dedup + network transfer + downstream candidate scoring.
- Dominant cost: embedding ANN source determines retrieval p99 and large unions dominate pre-rank compute.
- Quality driver: complementary relevant items surviving into the union.
- Cost driver: deep ANN probing and total unique candidate count.
- Optimization knobs: trim saturated ANN depth, raise cheap complementary source quota, bound overfetch, cache popularity/co-visitation, set per-source deadlines.
- Fallback/degradation: on ANN timeout, fill from cached co-visitation/popularity/content up to a smaller safe unique target.
- Trade-off curve: marginal Recall@K versus p99 and candidates scored.
- Decision: operate at the knee of the marginal-recall/cost curve rather than the highest reachable recall point.

#### 4. Scale and Capacity

As catalog size, QPS, or number of candidate sources grows, the first broken assumption is often not ranking accuracy but operational affordability. Larger catalogs can increase ANN memory/probe cost and make simple popularity/co-visitation tables larger; more sources increase fan-out and coordination; higher QPS raises shared-pool contention; more candidates raise downstream feature and ranking cost.

The architectural response depends on which dimension grows. Catalog growth may require partitioned ANN, tiered retrieval, or compressed indexes. QPS growth may require caching, request coalescing, source-specific capacity pools, or tighter budgets. Source-count growth may require hierarchical gating so every request does not fan out to every retriever.

Filled template:

- Scaling dimension: candidate sources increase from 4 to 12 while QPS triples.
- Baseline scale assumption: all sources can be queried in parallel on every request without saturating shared resources.
- First bottleneck: RPC fan-out and connection/thread-pool contention raise p99 before model compute is exhausted.
- Second-order effects: more duplicate candidates, larger payloads, noisier attribution, and higher fallback frequency.
- Architectural response: lightweight source gating plus per-source capacity pools and a bounded union target.
- Partitioning/replication/caching/batching: replicate hot cheap sources, cache stable channels, batch compatible ANN queries where supported.
- Consistency/freshness consequence: cached and precomputed channels may lag fast-changing catalog/user state.
- Operational failure mode: one slow source consumes shared resources and causes correlated latency across otherwise healthy sources.
- Validation: load test with realistic overlap, timeouts, and partial failures while measuring p99, unique yield, and retrieval quality.

#### 5. Freshness, State, and Versioning

Quota decisions depend on state that changes: user/session history, catalog availability, source indexes, learned embeddings, source-quality statistics, and the budget policy itself. Stale state can misallocate budget even if each retriever is individually correct.

For example, a content index may contain newly launched items while an embedding index lags by several hours. A policy trained on old source-yield statistics may continue giving the stale embedding source too much quota. Source metadata therefore needs freshness/version information, and replay must log the policy version plus source/index versions used for a request.

Filled template:

- State that becomes stale: per-segment source-yield statistics and embedding-index/catalog versions.
- Why freshness matters: adaptive policy decisions are only as good as the source capability and availability state they assume.
- Required freshness: session/user state may need seconds-to-minutes; catalog availability may need near-real-time; quota statistics can often update more slowly.
- Refresh cost: streaming/session updates and index refreshes consume compute and can destabilize serving if unbounded.
- Update architecture: hybrid streaming for fast-changing user/catalog signals plus periodic recomputation of robust marginal-recall statistics.
- Version consistency: log blender-policy version and every source/index version in the request trace.
- Failure from version skew: policy allocates heavily to a source whose index lacks the newest valid items.
- Fallback: enforce freshness/health eligibility; reallocate to healthy sources when a source is stale beyond threshold.
- Measurement: source freshness age, index lag, candidate-yield drift, marginal-recall drift, version-mismatch rate.
- Decision: treat source freshness as an input/eligibility constraint, not only as a monitoring dashboard metric.

#### 6. Implementation, Serving, and Observability

Production candidate blending needs more than a quota vector. It needs a source registry, a request-time budget policy, deadlines, source adapters, filtering/deduplication, provenance retention, deterministic ordering semantics, health state, logging, and replay.

The source contract should specify request context, requested count/search effort, timeout, response candidates, source-local score/rank, index/model version, freshness metadata, and error status. The blender should construct a canonical candidate identity, deduplicate deterministically, retain all source provenance, enforce global and per-source constraints, and emit a bounded candidate set.

Observability must permit replaying “why was this item present or absent?” and “why did this source get this quota?” That requires logging policy inputs and outputs, not only final candidates.

Filled template:

- Conceptual object: per-request allocation of retrieval capacity across candidate sources.
- Training/data implementation: offline logs join source candidates/provenance with later relevance or outcome labels to estimate marginal utility by segment and depth.
- Stored artifact/state: quota tables or gating-policy parameters, source-health state, marginal-yield statistics, and version metadata.
- Serving path: request context → budget policy → parallel source calls → filters → dedup/provenance merge → bounded union → ranker.
- Component contract: every source returns canonical item IDs, source rank/score, version/freshness, and explicit partial/error status.
- Logging: requested/returned/valid/unique counts, latency, timeout, overlap, policy inputs, quota decision, fallback decision.
- Versioning: pin/log blender-policy and source/index versions per request.
- Failure mode: source adapter silently truncates results, causing the policy to believe the source has low marginal yield.
- Observability: dashboards and traces for source yield, marginal contribution, p99, fallback rate, and segment coverage.
- Rollback: versioned quota policy with immediate switch to a known static baseline.
- Testing/replay: deterministic request replay, source-timeout injection, duplicate-heavy fixtures, cold-start slices, and minimum-contribution assertions.

#### 7. Vertical Transfer

The transferable mechanism is always the same: use limited retrieval capacity to construct a complementary candidate union that preserves downstream opportunity. What changes across verticals is the data-generating process, candidate universe, latency/freshness regime, and the cost of missing particular source types.

**E-commerce/items.** Availability and catalog cold start make content, category, substitute/complement, and business-rule-aware sources important. Inventory invalidation can make stale candidates worthless, so valid-yield rather than raw-yield matters.

**Video/feed.** Session intent can shift quickly, so recent co-engagement and sequential/session retrievers may deserve dynamic budget even if long-term user embeddings remain strong overall. Freshness can be a first-class source.

**Ads.** Candidate eligibility includes policy, targeting, budget, pacing, and auction constraints. A source with high relevance but low eligible yield may waste budget; calibration/value semantics matter downstream.

**Marketplace.** Provider/seller coverage may require floors or constraints so purely user-utility-driven marginal recall does not collapse supply diversity or marketplace health.

**Notifications.** Because false-positive interruption cost is high, the candidate set itself may need to remain deliberately small; adaptive budgets should emphasize confidence and suppression rather than maximizing union size.

Filled transfer template for e-commerce:

- Invariant: buy complementary useful coverage under a bounded retrieval/ranker budget.
- Different data-generating process: clicks and purchases depend on inventory, price, promotions, and prior exposure.
- Different objective: relevance plus conversion/value with hard availability requirements.
- Different candidates/features: content/category/substitute/complement and new-item channels gain importance.
- Different constraints: unavailable or policy-ineligible items must not consume effective budget.
- Metric change: valid Recall@K, conversion/value, new-item coverage, and availability violation rate.
- Serving change: fast inventory filtering/reallocation and freshness-aware source eligibility.
- Ecosystem effect: seller exposure and concentration can be affected by source quotas.
- Validation: replay inventory changes and run segment-level online experiments with seller/user guardrails.

#### 8. Objective and Metric Mismatch

Candidate blending can execute perfectly while optimizing the wrong retrieval proxy. For example, maximizing offline union Recall@1000 may favor highly popular candidates that make historical held-out interactions easy to retrieve, while reducing novelty, new-item coverage, or long-term discovery. That is an objective mismatch, not necessarily a serving bug.

The first diagnostic question is whether the intended candidate policy was served correctly. If quotas, versions, source outputs, and union construction match the experiment design, then a drop in product outcomes despite better retrieval metrics shifts attention toward metric semantics and logging bias rather than execution.

Filled template:

- Offline/model metric: historical union Recall@1000 improves by 4%.
- Online/product outcome: conversion is flat and new-item exposure falls sharply.
- Execution verification: quotas, source versions, deduplication, ranker input counts, and latency match the intended rollout.
- Metric semantics: offline recall rewards recovering historically interacted items from logged exposure.
- Blind spots: novelty, catalog cold start, exposure bias, seller/item coverage, and incremental business value.
- Missing product factor: discovery of relevant new inventory.
- Repair: add segment/coverage objectives or constraints and measure marginal contribution on unbiased or better-designed evaluation slices.
- Trade-off: a small loss in historical Recall@K may buy better discovery and catalog health.
- Online validation: A/B test with conversion plus new-item exposure, coverage, repeat rate, and latency guardrails.

## Material Follow-ups / Scenario Variants

### Two individually strong sources overlap heavily. How should the quotas change?

Do not compare their standalone recall in isolation. Measure the union and each source's marginal contribution conditional on the other. If the second source adds little unique relevant coverage beyond the first, reduce its deep quota until its marginal utility per unit cost becomes competitive with other sources. Preserve a floor only if it protects a required segment, freshness path, or failure fallback. Validate that the reduced quota does not create segment-specific recall loss hidden by aggregate metrics.

### A source is expensive but uniquely strong for a small segment. Keep it or remove it?

Treat the segment as a constraint-aware optimization problem. If that segment is product-critical, maintain a segment-conditioned route or minimum allocation rather than making the decision from global averages. If the segment is small and the source's per-request cost is high, gate the source so only requests likely to benefit invoke it. Measure both segment utility and system-wide cost; the design goal is targeted expenditure rather than universal fan-out.

### How would you move from hand-tuned quotas to a learned adaptive policy?

Begin with reliable logged features and a stable static baseline. Define the policy output as bounded quotas or source-enable decisions, not unrestricted candidate generation. Train or estimate expected marginal utility/cost by context, enforce floors/caps and source-health constraints, and replay against historical traffic before online testing. Be careful about policy-induced logging bias: once the gating policy stops calling a source, future logs no longer reveal what that source would have returned. Preserve exploration or shadow retrieval where the value of counterfactual source outcomes justifies the cost.

### One source times out at p99 but has high average quality. What is the fallback policy?

Give the source a deadline consistent with the end-to-end critical path. If it misses the deadline, do not stall the request indefinitely; reallocate to healthy low-latency sources or return a smaller deterministic set. Track whether timeout cases differ systematically by segment or load, because timeout-induced candidate changes can create product bias. Long term, either reduce that source's search effort, isolate its capacity, cache/precompute where possible, or gate it to high-value requests. Validate quality specifically on fallback traffic as well as normal traffic.
