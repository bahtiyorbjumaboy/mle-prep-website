---
type: interview-answer
item: "2027:R01"
title: "Two-stage and multi-stage recommender architecture"
created: "2026-09-17"
updated: "2026-09-18"
tags:
  - recommendation
  - ranking
  - retrieval
  - latency
  - system-design
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

## Learn the Concepts

### What R01 is actually testing

R01 is not mainly asking whether you can recite five stage names. It is testing whether you understand the systems principle that makes the stages necessary:

> **Spend cheap computation broadly, then spend expensive computation narrowly, while preserving enough opportunity for downstream stages to succeed.**

A strong answer therefore connects four things for every stage:

1. **objective** — what this stage is trying to optimize;
2. **resource budget** — how much latency/compute/memory it may consume;
3. **quality ceiling** — what damage becomes impossible to repair downstream;
4. **failure evidence** — what metric or telemetry would reveal that this stage is the first place the system went wrong.

That is the durable mental model. Specific models and candidate counts change from product to product.

### Why the architecture is a funnel

Suppose the corpus contains $N$ items and a scoring model costs roughly $c$ milliseconds per item. Exhaustive request-time scoring costs approximately:

$$
T_{\text{score-all}} \approx N \cdot c
$$

Even a small $c$ becomes impossible when $N$ is large. If a model costs $0.08$ ms per item, then scoring one million items serially would represent roughly:

$$
10^6 \times 0.08\text{ ms} = 80{,}000\text{ ms} = 80\text{ s}
$$

Real systems batch, vectorize, parallelize, and use accelerators, so this is not a literal serving estimate. It illustrates the scaling problem: **per-candidate cost multiplies by candidate count**.

A cascade changes the economics:

$$
\text{corpus}
\rightarrow C_{\text{retrieve}}
\rightarrow C_{\text{pre-rank}}
\rightarrow C_{\text{rank}}
\rightarrow C_{\text{slate}}
$$

with candidate sets shrinking approximately as:

$$
\text{millions} \rightarrow \text{thousands} \rightarrow \text{hundreds} \rightarrow \text{tens}
$$

The exact numbers are product-specific. The invariant is that later stages see fewer candidates and can therefore use richer features and more expensive models.

### Candidate generation / retrieval: preserve opportunity

Candidate generation answers:

> **Which items are worth considering at all?**

Its job is not to produce the perfect final ordering. Its job is to cheaply reduce a huge corpus to a set that still contains the items the downstream system may want.

Suppose 20 items are relevant and retrieval returns 1,000 candidates containing 18 of them:

$$
\operatorname{Recall@1000} = \frac{18}{20} = 0.90
$$

That can be strong retrieval even if those 18 relevant items are poorly ordered inside the 1,000. A later ranker exists specifically to reorder them.

The critical failure is **omission**:

> If a useful item never enters the candidate set, no downstream model can recover it.

This is the **candidate-set ceiling**. It is structural, not a claim that a numerical Recall@K value directly upper-bounds a different metric such as NDCG. The point is simply that unavailable candidates cannot receive downstream scores or positions.

#### Why multiple candidate sources help

Different retrievers encode different notions of usefulness and fail in different places. A recommender may fan out to:

- popularity or trending;
- item-item / co-visitation;
- collaborative filtering;
- content similarity;
- two-tower embedding retrieval;
- graph-based retrieval;
- recent-session/history retrieval;
- fresh-item or exploration pools.

If sources overlap heavily, adding another source may cost latency without adding useful candidates. Therefore measure:

- **source recall** — useful items found by each source;
- **union recall** — useful items found by the combined set;
- **marginal recall** — new useful items source $j$ contributes after the other sources are already present;
- candidate count and source latency.

The useful question is not just “is this retriever good?” but “what incremental opportunity does it add to the funnel for its cost?”

### Pre-ranking: buy compute cheaply

Pre-ranking answers:

> **Which candidates are not worth spending expensive downstream compute on?**

It is optional. Add it only when retrieval leaves too many candidates for the expensive ranker or feature path.

Example:

$$
2000 \rightarrow 400
$$

A good pre-ranker should be much cheaper than the main ranker and should preserve nearly all candidates that matter downstream.

Its central trade-off is:

$$
\text{compute saved} \leftrightarrow \text{downstream quality lost}
$$

Useful diagnostics include:

- candidate reduction ratio;
- heavy-ranker latency or FLOPs saved;
- fraction of the heavy ranker's eventual top-$M$ candidates preserved;
- change in downstream NDCG or task utility;
- slice-level preservation for cold-start, long-tail, fresh, or other important segments.

If pruning 80% of candidates cuts ranking cost dramatically while barely moving downstream quality, the pre-ranker is doing useful work. If it removes high-value candidates or saves little compute, it is not.

Because pre-ranking is another irreversible pruning step, it creates another quality ceiling.

### Ranking: spend capacity on precise ordering

Ranking answers:

> **Among the surviving candidates, which are best for this user in this context?**

At this point the candidate set is small enough to hydrate richer features and evaluate a more expressive model. Features can include:

- user history and preferences;
- item attributes and learned representations;
- user-item crosses or interaction features;
- session and request context;
- fresh online signals;
- business or marketplace features when appropriate.

The ranker's output may be a calibrated probability such as:

$$
P(\text{click}\mid u,i,c)
$$

or

$$
P(\text{purchase}\mid u,i,c)
$$

or it may be an ordering score with no probability semantics.

That distinction matters. If downstream logic multiplies a score by price, thresholds it, feeds it to an auction, or interprets it as risk, calibration and score semantics become important. If the score is used only for ordering, ranking quality may matter more than probability calibration.

At this stage, metrics such as NDCG, MRR, MAP, or task-specific utility are often more diagnostic than candidate recall because the main problem is **ordering within the available set**.

### Reranking: optimize the slate, not isolated items

Ranking commonly scores candidates independently or approximately independently. That can produce a bad page even if every individual score is reasonable.

For example, the top ten items may all be near-duplicates, all come from one creator, or violate an inventory/exposure objective when considered together.

Reranking answers:

> **Does the whole output slate make sense?**

It may optimize or constrain:

- diversity and redundancy;
- novelty;
- freshness;
- exploration;
- category balance;
- seller / creator exposure;
- inventory or supply considerations;
- product policy;
- page-level compatibility or spacing rules.

The conceptual distinction is:

**Ranking:** How good is this candidate?

**Reranking:** How good is this candidate in the context of the already-constructed or intended slate?

Reranking therefore needs both **relevance-retention metrics** and metrics for the slate-level objective it was introduced to control.

### Post-processing: enforce hard validity

Post-processing answers:

> **Is every returned result valid and allowed to show?**

Some properties should not depend on a model learning to behave correctly. Examples include:

- item availability;
- geographic or contractual eligibility;
- hard policy restrictions;
- deduplication;
- already-consumed suppression;
- mandatory exclusions.

These rules are often deterministic.

“Post-processing” describes the logical role, not a requirement that every hard filter run at the very last microsecond. If an item is definitely invalid and carrying it through expensive feature hydration/ranking wastes resources, apply the filter earlier. The important design question is whether the rule is a **hard validity constraint** or a **soft learned preference**.

### How quality ceilings propagate

A useful set view is:

$$
C_{\text{rank}} \subseteq C_{\text{pre-rank}} \subseteq C_{\text{retrieve}} \subseteq \mathcal{I}
$$

where $\mathcal{I}$ is the full item universe.

Every pruning stage can only remove items unless another candidate source is explicitly introduced later. Therefore:

- retrieval can lose opportunity before ranking begins;
- pre-ranking can lose opportunity before the heavy model begins;
- ranking can misorder available candidates but usually cannot recover removed ones;
- reranking can improve the slate only from what survived earlier stages;
- post-processing can make results valid, but if it removes many items late it may leave a thin or low-quality slate unless refill/fallback logic exists.

This is why early-stage recall/preservation is treated differently from late-stage ordering quality.

### Metrics should follow stage objectives

One top-line metric is not sufficient for a multi-stage system.

Use the mapping:

$$
\text{stage objective} \rightarrow \text{stage metric}
$$

| Stage | Primary objective | Useful measurements |
|---|---|---|
| Retrieval | Preserve useful opportunity cheaply | Recall@K, source recall, union recall, marginal recall, candidate count, latency |
| Pre-rank | Remove expensive-to-score weak candidates with bounded quality loss | reduction ratio, top-candidate preservation, downstream quality loss, compute/latency saved |
| Rank | Order surviving candidates accurately | NDCG, MRR, MAP, task utility, log loss/calibration when probability semantics matter, slice metrics |
| Rerank | Produce a good slate under multiple objectives/constraints | relevance retained, diversity, novelty, coverage, freshness, exposure, constraint satisfaction |
| Post-process | Guarantee validity | invalid-result rate, dedup correctness, eligibility violations, refill/fallback behavior |
| Serve | Execute the intended pipeline reliably | p50/p95/p99, timeout rate, fallback rate, freshness, cache hit rate, version consistency, error rate |

CTR, conversion, watch time, or revenue are important product outcomes. They tell you **whether the product changed**. They usually do not tell you **where the pipeline first went wrong**.

### Latency is a budget, not a vague requirement

For a service with p99 below 120 ms, do not say every component “needs to be fast.” Assign stage budgets.

A request-time decomposition might be:

$$
T_{\text{request}}
\approx
T_{\text{retrieval}}
+T_{\text{feature}}
+T_{\text{pre-rank}}
+T_{\text{rank}}
+T_{\text{rerank}}
+T_{\text{overhead}}
$$

The sum is only a first-order model because independent work can run in parallel and tail latency depends on dependency fan-out, queuing, batching, hardware, and network behavior. But the decomposition forces explicit ownership of the budget.

Candidate count is one of the strongest control knobs. If heavy scoring costs approximately $0.08$ ms per candidate:

$$
300 \times 0.08 \approx 24\text{ ms}
$$

while

$$
1000 \times 0.08 \approx 80\text{ ms}
$$

More candidates may improve recall and ranking opportunity, but they also increase:

- feature lookups;
- memory traffic;
- ranker inference work;
- batching pressure;
- downstream reranking work;
- tail-latency exposure.

The Staff-level habit is to state **the quality or reliability cost of every latency optimization**.

### Latency/resource levers and their costs

#### Reduce candidate count

**Why it helps:** fewer candidates require feature hydration and scoring.

**Cost:** relevant candidates may be excluded, lowering the upstream ceiling.

#### Add or strengthen pre-ranking

**Why it helps:** the expensive ranker sees fewer candidates.

**Cost:** a weak or biased pre-ranker can over-prune important slices and create another irrecoverable ceiling.

#### Precompute or cache features

**Why it helps:** less request-time computation and fewer remote lookups.

**Cost:** staleness, storage, invalidation complexity, cache misses, and possible training/serving mismatch.

#### Use a smaller or distilled ranker

**Why it helps:** fewer operations and usually a smaller memory footprint.

**Cost:** reduced capacity or imperfect teacher fidelity.

#### Quantize the ranker

**Why it helps:** reduced precision such as FP32 → FP16/BF16 or INT8 can reduce memory bandwidth and accelerate supported kernels.

**Cost:** numerical approximation can change score quality or ordering and must be measured on the actual hardware/runtime.

#### Tune ANN retrieval

**Why it helps:** fewer probes, smaller search effort, or more compression can reduce latency/memory.

**Cost:** approximate retrieval recall can fall.

#### Parallelize independent work

**Why it helps:** wall-clock latency can approach the slowest parallel branch rather than the sum of branch latencies.

**Cost:** more resource pressure and greater exposure to stragglers/fan-out tail effects.

#### Batch/vectorize inference

**Why it helps:** better accelerator utilization and lower per-candidate overhead.

**Cost:** batching windows can add queueing latency; large batches can hurt tail latency or memory pressure.

### Fallbacks are part of the architecture

A production design is incomplete if it describes only the happy path.

Define deterministic degradation behavior for stage deadlines and failures. For example:

- retrieval timeout → cached/popularity candidates or another healthy retrieval source;
- feature timeout → stale-but-safe/default features or a simpler scoring path;
- heavy-ranker timeout → pre-ranker/lightweight-ranker order;
- reranker failure → main-ranker order plus mandatory hard filters;
- insufficient valid results after filtering → controlled refill from a safe fallback pool.

The goal is not merely availability. It is:

> **deterministic, observable degradation**

Monitor fallback rate and the quality of fallback traffic. A service can have a good availability number while silently serving a degraded path to a meaningful fraction of users.

Versioning belongs here too. A model, feature definition, feature snapshot, embedding generator, and ANN index may need compatible versions. “All components are up” does not mean the intended system is being served if those versions are skewed.

### Debugging by first divergence

When a product metric changes, do not immediately blame “the model.” Walk the funnel and locate the first place where evidence diverges from baseline.

- **Recall@K drops** → investigate retrieval, source health, ANN/index state, filtering, or candidate quotas.
- **Retrieval is stable but good candidates disappear before heavy ranking** → investigate pre-ranking/pruning.
- **Candidate pool is stable but NDCG/task utility falls** → investigate ranker objective, features, labels, model, or calibration/score semantics.
- **Main-ranker output is stable but final slate changes** → investigate reranking, caps, constraints, policy, or inventory logic.
- **Offline quality is stable but production outcomes change** → investigate serving, feature freshness/skew, caches, model/index/feature versions, latency, fallbacks, and presentation changes.

This is the **first-divergence principle**: the earliest stage whose inputs/outputs/telemetry depart from the healthy reference is usually a more useful localization point than the final business metric.

### Debugging with ranked hypotheses

A Staff-quality incident answer should not stop at a list of possible causes. Rank the hypotheses and name a discriminating check for each.

Consider this incident:

- offline NDCG improves;
- retrieval recall is unchanged;
- pre-rank preservation is unchanged;
- CTR is flat;
- conversion drops;
- the drop is concentrated on mobile;
- the new model uses three real-time features;
- p99 rises but remains just below the server-side SLO.

A reasonable hypothesis order is:

#### Hypothesis 1: mobile-specific feature / serving skew

Why plausible:
- the regression is segmented to mobile;
- new real-time features were introduced.

Discriminating checks:
- feature freshness by device;
- missing/default rate by device;
- online-vs-offline feature distributions;
- timestamp alignment;
- training/serving transformation parity.

Supporting evidence would be substantially higher stale/missing/default feature rates on mobile.

#### Hypothesis 2: objective mismatch

Why plausible:
- CTR is flat;
- conversion falls.

The model may still rank clickable items well while worsening downstream purchase propensity.

Checks:
- purchase-oriented offline metrics;
- conversion by score bucket;
- score semantics/calibration for purchase;
- mobile vs desktop purchase slices.

#### Hypothesis 3: mobile-sensitive latency regression

Why plausible:
- p99 increased materially;
- mobile user experience may be more sensitive to end-to-end latency than server-only SLOs reveal.

Checks:
- conversion by latency bucket;
- client-side/mobile end-to-end latency;
- request abandonment or rendering delay;
- tail latency beyond the server boundary.

Important lesson: **one healthy metric rarely rules out an entire failure class**. Unchanged fallback rate does not rule out feature skew. Being under an SLO does not prove latency is harmless. Higher offline NDCG does not prove the online objective improved.

### Safe mitigation before perfect root-cause certainty

Incident response and root-cause analysis are related but not identical.

If one segment is clearly harmed and the system supports safe segmented rollback, mitigate the harm first while preserving evidence for diagnosis. Examples include:

- roll back mobile while leaving healthy desktop traffic unchanged;
- disable a new real-time feature and use the previous safe feature path;
- shrink candidate count temporarily if latency is causing severe degradation;
- route to the last known-good model/index pair.

A root cause becomes much stronger when **evidence and intervention agree**: the suspected mechanism is observed, changing it removes the regression, and a regression test can reproduce/prevent the failure.

### Changed-constraint transfer

The same funnel principle survives very different products, but stage choices change with constraints.

#### Smaller catalog, cheap model

If the catalog is only tens of thousands of items and the ranker is cheap, you may not need a distinct pre-ranker. Simpler architecture can be better.

#### Huge catalog, expensive features

For tens or hundreds of millions of items, retrieval quality, ANN design, candidate quotas, and pre-ranking become much more important because exhaustive feature hydration is impossible.

#### High freshness requirement

If new items or interactions must appear within seconds/minutes, the design must account for incremental candidate sources, feature freshness, and index update semantics rather than assuming everything can be precomputed daily.

#### Strict policy/availability constraints

If many retrieved items are ineligible, apply cheap hard filtering earlier to avoid wasting downstream compute, but preserve deterministic final validation before response.

#### Tight latency, high QPS

Candidate counts, cache strategy, batching, model size, parallel fan-out, and fallback behavior become resource-allocation decisions, not merely modeling choices.

The correct architecture is therefore not “always five stages.” The correct architecture is the **simplest cascade that meets quality, latency, freshness, reliability, and product constraints**.

### Common precision mistakes

Avoid these in interviews and design reviews:

- **Calling retrieval “sampling” by default.** Retrieval is usually deterministic or approximate search/routing, not statistical sampling.
- **Treating pre-ranking as mandatory.** It exists only when it earns its complexity by saving meaningful downstream compute.
- **Saying Recall@K numerically caps NDCG.** The real ceiling is structural: missing candidates cannot be ranked.
- **Treating reranking as only diversity.** It can encode slate interactions, exposure, freshness, inventory, business rules, and ecosystem objectives.
- **Putting every hard filter at the very end.** Logical post-processing rules can execute earlier if that saves compute, as long as correctness is preserved.
- **Using one metric for every stage.** Different stages have different objectives and therefore different diagnostics.
- **Assuming “below SLO” means latency is harmless.** Product sensitivity can exist inside the formal budget, especially across segments or client conditions.
- **Assuming offline ranking gains guarantee online gains.** Objective mismatch, serving skew, feedback effects, latency, or presentation can reverse the result.
- **Listing hypotheses without discriminating tests.** Good debugging pairs each hypothesis with the observation that would support or weaken it.

### What to study here versus in later questions

R01 should give you architectural ownership of the funnel. It should not become a substitute for the deeper specialized questions that follow.

Use later items for deeper treatment of:

- **R04 — Recommendation metrics and metric contracts:** exact definitions, derivations, edge-case semantics, and metric selection;
- **R06 — Collaborative, content, co-visitation, graph, and hybrid retrieval:** candidate-source mechanisms and blending;
- **R08 — Two-tower retrieval:** contrastive training, serving, normalization, ANN coupling, and freshness;
- **R10 — ANN for recommendation:** recall/latency/memory/update trade-offs among ANN families;
- **R12 — Candidate blending and adaptive retrieval budgets:** quotas, overlap, marginal recall, and adaptive allocation;
- **R13/R14 — learning-to-rank and LambdaMART:** ranking objectives and ranker mechanics;
- **R20/R21 — diversity and hard constraints:** reranking/slate construction in depth;
- **R43 — recommendation serving architecture:** deadlines, features, caches, versioning, rollback, and serving topology;
- **R45/R46 — monitoring/failure diagnosis and capacity/cost/scaling:** production localization and quantitative resource planning.

R01 is the conceptual skeleton those later questions attach to.

### Self-test prompts for concept ownership

Without looking at notes, you should be able to reason through these:

1. Why can a retrieval system have strong Recall@1000 even if its internal ordering is poor?
2. Why is a pre-ranker optional, and what evidence would justify adding one?
3. What exactly is meant by an upstream “quality ceiling”?
4. Why might increasing retrieval from 300 to 1,000 candidates improve quality but break p99?
5. Why is NDCG a better rank-stage diagnostic than CTR?
6. Give two reranking objectives that cannot be represented well by independent item scoring alone.
7. Which hard constraints would you move earlier in the pipeline, and why?
8. Design one deterministic fallback for each major stage.
9. If candidate recall is unchanged but conversion drops after a ranker rollout, what do you check next and in what order?
10. Under what constraints would you deliberately remove the pre-rank stage?

If you can answer those from first principles, you understand the architecture rather than only the memorized wording.

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

Suppose total server-side latency is constrained to p99 < 120 ms. Decompose the request into retrieval, feature hydration, pre-ranking, heavy ranking, reranking, and overhead. Assign explicit budgets rather than saying every stage should simply be “fast.”

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
