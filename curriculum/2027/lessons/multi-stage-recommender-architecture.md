---
type: lesson
id: "multi-stage-recommender-architecture"
title: "Multi-stage recommender architecture"
items:
  - "2027:R01"
created: "2026-09-17"
updated: "2026-09-17"
tags:
  - recommendation
  - retrieval
  - ranking
  - system-design
---

## The core problem: expensive scoring over a huge corpus

A recommender may have millions of possible items but only enough request-time budget to return a few dozen results.

The naive approach is:

1. score every item with the strongest model;
2. sort all scores;
3. return the top results.

This fails operationally because per-item cost multiplies by corpus size. A model that seems inexpensive for one candidate can be impossibly expensive over millions of candidates.

The standard response is a funnel:

$$
\text{millions} \rightarrow \text{thousands} \rightarrow \text{hundreds} \rightarrow \text{tens}
$$

The candidate set gets smaller while allowable compute per candidate gets larger.

That one idea explains most of the architecture.

## Retrieval: preserve opportunity

Candidate generation is a retrieval problem, not final ranking.

Suppose there are 20 relevant items and retrieval returns 1,000 candidates containing 18 of them:

$$
\mathrm{Recall@1000} = \frac{18}{20} = 0.90
$$

That can be strong retrieval even if those 18 relevant items are not near the top of the 1,000, because a later ranker will reorder the set.

The essential failure mode is omission:

> If a useful item never enters the candidate set, no later model can recover it.

This is the candidate-set ceiling.

Do not confuse this with saying a numerical Recall@K value directly caps a later metric such as NDCG. The ceiling is structural: unavailable candidates cannot be ranked.

### Why multiple retrieval sources help

Different retrievers encode different notions of relevance and have different failure modes.

A system might retrieve from:
- popularity or trending;
- item-item / co-visitation;
- collaborative filtering;
- content similarity;
- two-tower embeddings;
- graph-based sources;
- recent-history or session sources;
- fresh-item pools.

The important measurements are not only per-source recall, but also **union recall** and **marginal recall**: how many useful candidates does a source add after accounting for overlap with the others?

## Pre-ranking: buy compute cheaply

Pre-ranking is optional.

Use it when the retrieved set is still too large for the expensive ranker.

Example:

$$
2000 \rightarrow 400
$$

The pre-ranker should be much cheaper than the heavy ranker and should preserve the candidates that matter downstream.

A useful mental model is:

$$
\text{compute saved} \leftrightarrow \text{quality lost}
$$

If pruning 80% of the candidates cuts ranking cost dramatically while barely changing downstream NDCG, the pre-ranker is doing useful work.

If it saves little latency or removes high-value candidates, it is not.

## Ranking: spend model capacity where it matters

Once the candidate set is small, richer scoring becomes feasible.

A heavy ranker can use:
- user features;
- item features;
- user-item crosses;
- session/context features;
- fresh online features;
- richer neural or tree interactions.

Its output might represent:

$$
P(\text{click} \mid u,i,c)
$$

or

$$
P(\text{purchase} \mid u,i,c)
$$

or some other utility.

At this stage, the task is primarily **ordering**. That is why position-sensitive ranking metrics such as NDCG, MRR, or MAP are usually more useful than recall alone.

## Reranking: optimize the slate, not just items

A pointwise ranker can produce a list of individually strong items that is poor as a page or feed.

For example, the top positions may all contain near-duplicates.

Reranking can account for:
- diversity;
- novelty;
- freshness;
- exploration;
- category balance;
- seller / creator exposure;
- inventory;
- policy or product constraints.

The distinction is:

**Ranking:** How good is this candidate?

**Reranking:** How good is this whole slate?

Reranking therefore needs metrics for both relevance retention and its intended slate-level effect.

## Post-processing: hard validity

Some requirements should not depend on a learned model choosing to behave correctly.

Examples:
- item availability;
- geographic eligibility;
- policy restrictions;
- deduplication;
- already-consumed suppression.

These can be applied in post-processing or earlier if carrying invalid candidates downstream wastes resources.

## Metrics should follow stage objectives

One top-line metric is not enough.

Use the mapping:

$$
\text{stage objective} \rightarrow \text{stage metric}
$$

Typical examples:

| Stage | What it is trying to do | Useful measurements |
|---|---|---|
| Retrieval | Preserve relevant candidates cheaply | Recall@K, union recall, marginal recall, latency |
| Pre-rank | Prune while preserving downstream quality | candidate reduction, top-candidate preservation, quality loss, latency saved |
| Rank | Order candidates correctly | NDCG, MRR, MAP, task utility, calibration where relevant |
| Rerank | Build a good constrained slate | relevance retained, diversity, novelty, constraint satisfaction |
| Serve | Execute the intended pipeline reliably | p50/p95/p99, timeouts, fallback rate, freshness, versions |

CTR is an outcome metric. It can tell you that product behavior changed, but not where the pipeline first went wrong.

## Latency is a budget, not a vague requirement

For a service with p99 < 120 ms, assign explicit budgets to stages.

A possible design might reserve time for:
- retrieval;
- feature hydration;
- pre-ranking;
- heavy ranking;
- reranking;
- serialization/network overhead.

The exact numbers depend on the system. The important part is making the allocation explicit.

Candidate count is one of the strongest control knobs.

If heavy ranking costs about $0.08$ ms per candidate:

$$
300 \times 0.08 \approx 24 \text{ ms}
$$

while:

$$
1000 \times 0.08 \approx 80 \text{ ms}
$$

More candidates may improve ranking opportunity, but they also consume latency and feature-serving capacity.

## Latency levers and their costs

### Reduce candidate count
**Why it helps:** fewer candidates need feature hydration and ranking.

**Possible cost:** useful candidates may be excluded.

### Strengthen pre-ranking
**Why it helps:** the expensive ranker sees fewer candidates.

**Possible cost:** pre-ranking can over-prune and create an upstream ceiling.

### Precompute or cache features
**Why it helps:** less online feature computation.

**Possible cost:** stale features, larger storage, cache invalidation complexity.

### Use a smaller / distilled / quantized ranker
**Why it helps:** faster inference and often better hardware efficiency.

**Possible cost:** approximation error or reduced model capacity.

### Tune ANN retrieval
**Why it helps:** fewer probes or less search work.

**Possible cost:** lower retrieval recall.

### Parallelize independent work
**Why it helps:** wall-clock latency approaches the slowest parallel branch rather than the sum.

**Possible cost:** higher resource pressure and more tail-latency sensitivity to slow dependencies.

## Fallbacks are part of the architecture

A production recommender should define what happens when a stage misses its deadline.

Examples:
- retrieval timeout → cached/popularity candidates;
- feature timeout → stale-but-safe features;
- ranker timeout → lightweight or pre-ranker ordering;
- reranker failure → main-ranker order plus mandatory hard filters.

The goal is not merely availability.

The goal is **deterministic, observable degradation**.

Monitor fallback rate because a service may be technically healthy while silently serving degraded recommendations.

## Debugging by first divergence

When a product metric changes, do not immediately blame "the model."

Find the first stage where the evidence changes.

- Recall@K drops → investigate retrieval.
- Retrieval is stable but candidates disappear before ranking → investigate pre-ranking.
- Candidate pool is stable but NDCG falls → investigate ranking/features/objective.
- Ranker output is stable but final slate changes → investigate reranking/constraints.
- Offline quality is stable but production changes → investigate serving, freshness, caches, and version coupling.

This stage-localization habit is the durable skill behind the architecture.


## Reconstruction 1 extension: explain the whole funnel from first principles

A good reconstruction should answer two questions:

1. Why is one heavy ranker over the whole corpus impractical?
2. What distinct job does each stage perform?

The strongest reasoning sequence is:

- the corpus is too large for exhaustive expensive scoring;
- therefore the system progressively shrinks the candidate set;
- early stages optimize breadth and recall;
- later stages optimize precise ordering and slate quality;
- every irreversible pruning step creates a quality ceiling.

A clean mental model is:

**retrieval = preserve opportunity**  
**pre-rank = save compute**  
**rank = order precisely**  
**rerank = optimize the slate**  
**post-process = enforce hard validity**

Common precision mistakes to avoid:
- do not call retrieval statistical “sampling” unless it actually is sampling;
- do not imply that pre-ranking is mandatory;
- do not claim one stage's Recall@K numerically caps a different downstream metric such as NDCG;
- do not reduce reranking to only diversity—reranking can encode broader slate, business, exposure, and ecosystem objectives.

The durable idea is that **missing candidates cannot be recovered downstream**.

---

## Reconstruction 2 extension: choose metrics by stage objective

A multi-stage system should not be evaluated with one metric everywhere.

Use this rule:

**stage objective → stage metric**

### Retrieval

Retrieval is primarily about coverage.

Useful metrics:
- Recall@K;
- source-level recall;
- union recall;
- marginal recall by source;
- candidate count;
- latency.

If retrieval recall falls, downstream ranking may be perfect and the system can still fail because good items never enter the funnel.

### Pre-ranking

Pre-ranking is about compute savings under bounded quality loss.

Useful measurements:
- candidate reduction ratio;
- downstream top-candidate preservation;
- latency saved;
- heavy-ranker compute saved;
- NDCG / utility loss caused by pruning.

The correct question is not:

> Did pruning reduce latency?

It is:

> How much downstream quality did I lose for the compute I saved?

### Ranking

Once the candidate set is fixed, ordering becomes central.

Useful metrics:
- NDCG;
- MRR;
- MAP;
- task-specific utility;
- calibration / log loss when score semantics matter;
- per-segment metrics.

Recall can still be useful in some analyses, but it is usually less diagnostic of ordering quality at this stage.

### Reranking

Reranking usually trades multiple objectives.

Useful metrics:
- relevance retained;
- diversity;
- novelty;
- freshness;
- coverage;
- constraint-satisfaction rate;
- seller / creator / category exposure.

### Serving

A model can be good offline and still fail in production.

Useful serving metrics:
- p50 / p95 / p99 latency;
- timeout rate;
- fallback rate;
- feature freshness;
- cache hit rate;
- model / index / feature version consistency;
- error rate.

### Why CTR alone is insufficient

CTR is an **outcome metric**, not a **localization metric**.

A CTR drop could come from:
- retrieval degradation;
- pre-rank over-pruning;
- ranker objective or feature issues;
- reranking constraints;
- feature skew;
- latency;
- fallbacks;
- presentation changes.

Stage metrics let you find the first divergence.

---

## Reconstruction 3 extension: latency-budget reasoning

When the heavy ranker gets slower, do not jump to one optimization. Think in terms of **resource levers and quality costs**.

A good answer includes at least four levers.

### Lever 1: reduce retrieval candidate count

Why latency improves:
- fewer candidates need feature hydration;
- fewer candidates reach downstream scoring.

Possible cost:
- lower recall;
- useful candidates may be excluded before the heavy ranker sees them.

### Lever 2: strengthen pre-ranking

Why latency improves:
- the heavy ranker scores fewer candidates.

Possible cost:
- over-pruning;
- another upstream quality ceiling.

### Lever 3: precompute or cache features

Why latency improves:
- less request-time feature computation;
- fewer remote lookups may be required.

Possible cost:
- stale features;
- cache invalidation complexity;
- storage cost;
- cache misses or dependency failures.

### Lever 4: use a smaller, distilled, or quantized ranker

These are related but distinct ideas.

**Distillation**:
- train a smaller student model to approximate a larger teacher;
- usually reduces model size and compute;
- possible cost: reduced model capacity or fidelity.

**Quantization**:
- reduce numeric precision, such as FP32 → FP16/BF16 or INT8/INT4;
- can reduce memory bandwidth and speed up supported hardware kernels;
- possible cost: numerical approximation error and possible ranking-quality degradation.

Do not describe quantization as “0.64 to 0.32.” Name the numeric formats explicitly.

### Other useful levers

- batch/vectorize inference;
- tune ANN retrieval;
- parallelize independent candidate sources;
- reduce online feature count;
- move expensive features offline;
- use per-stage deadlines and graceful fallbacks.

The interview-quality habit is:

**latency optimization + explicit quality/reliability cost**

---

## Reconstruction 4 extension: debugging with ranked hypotheses

A strong debugging answer is not:

> I think feature freshness is the problem.

A strong debugging answer is:

1. rank plausible hypotheses;
2. name a discriminating check for each;
3. observe which hypothesis the evidence supports;
4. localize the first failing stage;
5. mitigate safely;
6. add a regression test.

For the example incident:

- offline NDCG improves;
- retrieval recall is unchanged;
- pre-rank preservation is unchanged;
- CTR is flat;
- conversion drops;
- the drop is concentrated on mobile;
- the new model uses three real-time features;
- p99 rises but remains just below the server-side SLO.

A reasonable ranked hypothesis set is:

### Hypothesis 1: mobile-specific feature / serving skew

Why plausible:
- regression is concentrated on mobile;
- new real-time features were introduced.

Checks:
- feature freshness by device;
- missingness / default-value rate by device;
- online-vs-offline feature distributions;
- train-serving parity;
- timestamp alignment.

Supporting evidence:
- mobile has substantially more stale, missing, defaulted, or shifted feature values than desktop.

### Hypothesis 2: objective mismatch

Why plausible:
- CTR is flat;
- conversion drops.

Interpretation:
- the model may still rank clickable items well;
- but it may rank items with worse downstream purchase propensity.

Checks:
- purchase-oriented metrics;
- conversion-conditioned score distributions;
- mobile-vs-desktop purchase slices;
- model-score calibration against conversion labels.

Supporting evidence:
- click-oriented behavior stays stable while purchase-oriented quality degrades.

### Hypothesis 3: mobile-sensitive latency regression

Why plausible:
- p99 increased materially;
- mobile may be more sensitive to end-to-end latency than desktop;
- being below a formal SLO does not prove zero product impact.

Checks:
- conversion by latency bucket;
- mobile end-to-end latency;
- client-side timing;
- tail latency beyond server-only measurement.

Supporting evidence:
- conversion degrades systematically as latency increases, especially on mobile.

### Important debugging principles

**Do not over-rule hypotheses from one healthy metric.**

Examples:
- unchanged fallback rate does not rule out serving skew;
- latency below SLO does not prove latency is harmless;
- higher offline NDCG does not prove the online objective improved.

**Immediate mitigation should be safe and narrow.**

If desktop is healthy but mobile is degraded:
- roll back mobile first;
- preserve healthy desktop traffic if operationally safe;
- continue investigation with the segment isolated.

**Root cause is localized when evidence and intervention agree.**

Examples:
- mobile feature missingness is high, fixing it restores conversion;
- purchase-oriented quality is worse despite flat CTR, and reverting the objective restores conversion;
- high-latency mobile buckets show the conversion drop, and latency reduction removes it.

This hypothesis → check → evidence → localization structure is reusable across ranking incidents.
