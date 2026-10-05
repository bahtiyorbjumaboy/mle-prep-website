---
type: interview-answer
item: "2027:R04"
title: "Recommendation metrics and metric contracts"
created: "2026-09-24"
updated: "2026-10-05"
tags:
  - recommendation
  - ranking-metrics
  - evaluation
  - metric-contracts
  - staff-depth
---

## Canonical Staff-Depth Question

Derive/compare Precision@k, Recall@k, HitRate@k, MRR, MAP, DCG/NDCG, AUC/log-loss, calibration, coverage, novelty, diversity, watch-time/completion, conversion/revenue, and long-term metrics.

## Mastery Answer

I start by defining the **metric contract** before computing anything: the evaluation unit, candidate universe, relevance label, cutoff $k$, treatment of unjudged or unexposed items, aggregation rule, empty-label cases, weighting, and time horizon. Without that contract, two correct implementations can report different numbers.

For top-$k$ retrieval and ranking, the main distinction is what each metric rewards. Precision@$k$ asks what fraction of the shown top $k$ are relevant; Recall@$k$ asks what fraction of all relevant items were recovered. HitRate@$k$ collapses that to whether there was at least one hit. MRR emphasizes the rank of the first relevant result. MAP averages precision at the ranks where relevant items appear, so it rewards retrieving multiple relevant items early. DCG supports graded relevance and discounts lower ranks; NDCG normalizes DCG by the best possible ordering for that query or user so scores are comparable across examples with different relevance sets.

AUC and log-loss answer different questions from top-$k$ ranking metrics. AUC measures pairwise ordering across positives and negatives and is threshold-free, but can look strong while the top few recommendations are poor. Log-loss evaluates probabilistic predictions and heavily penalizes confident mistakes; if scores are used as probabilities, I also check calibration, because good ordering does not imply truthful probabilities.

Then I add product and system metrics that ranking relevance alone misses. Coverage asks how much of the catalog, user base, or eligible inventory receives exposure. Novelty rewards recommending items that are less obvious or less globally popular. Diversity measures non-redundancy within a slate and must specify the similarity function. Watch-time/completion, conversion, and revenue are closer to product value but can be biased by exposure, position, price, session length, and delayed outcomes. Long-term metrics such as retention, repeated satisfaction, creator or seller health, or downstream value are strategically important but have longer feedback loops and harder causal attribution.

The metric should match the stage. Candidate generation is primarily recall-oriented because missed relevant items cannot be recovered downstream. A ranker is usually judged by top-heavy ranking metrics such as NDCG or MAP, often alongside calibration if probabilities feed thresholds or value calculations. Reranking adds diversity, coverage, constraint, and business metrics. Final product decisions require online experiments on user and business outcomes, with guardrails and segment analysis.

At Staff depth, I would not accept a metric name without semantics. I would state, for example, whether Recall@$k$ uses all known positives or only positives eligible at recommendation time; what NDCG does when IDCG is zero; whether MAP ignores users with no positives or assigns zero; whether repeated impressions count; how ties are handled; whether metrics are macro-averaged per user/query or micro-averaged over events; and whether delayed conversions are censored. I would also diagnose regressions stage by stage: unchanged candidate Recall@$K$ with lower NDCG points toward ranking or labeling rather than retrieval, while offline NDCG up but online conversion down suggests objective mismatch, calibration, exposure bias, serving skew, or constraint effects.

## Learn the Concepts

### Foundation

A recommender produces an **ordered list of items**. Evaluation asks whether that list is useful, but “useful” can mean several different things. The core mental model is therefore:

> **A metric is a measuring instrument, and a metric contract defines exactly what the instrument is allowed to measure.**

Before formulas, define the objects being measured:

- A **user/query/context** is the situation for which recommendations are generated.
- A **candidate set** is the set of items the system is allowed to consider.
- A **ranked list** is the ordered output, for example $[i_1,i_2,\ldots,i_k]$.
- A **relevant item** is an item counted as a positive under a specified label rule, such as purchased, clicked, watched past a threshold, or judged relevant.
- The cutoff **@$k$** means only the first $k$ ranked items are evaluated.
- A **binary relevance label** is usually $rel_i\in\{0,1\}$.
- A **graded relevance label** allows levels such as $0,1,2,3$ for increasingly valuable outcomes.
- **Macro-averaging** computes a metric per user/query and averages those values, giving each evaluation unit equal weight.
- **Micro-averaging** pools events or counts first, giving high-activity units more weight.

A metric contract must settle details such as:

- What is one evaluation unit: user, session, query, impression, or request?
- What items count as eligible?
- What event defines relevance?
- What is $k$?
- What happens when fewer than $k$ items are returned?
- What happens when an example has no relevant items?
- Are repeated impressions or duplicate items allowed?
- How are ties handled?
- Is relevance binary or graded?
- Are labels complete, delayed, censored, or exposure-dependent?
- Is aggregation macro, micro, weighted, or segment-specific?

#### Precision@$k$

Precision@$k$ measures the fraction of the first $k$ recommendations that are relevant:

$$
\mathrm{Precision@}k = \frac{\#\{\text{relevant items in top }k\}}{k}.
$$

It answers: **Of what was shown near the top, how much was good?**

Precision is useful when recommendation slots are scarce or bad recommendations are costly. It does not care how many relevant items existed outside the top $k$.

#### Recall@$k$

Recall@$k$ measures the fraction of all relevant items that appear in the first $k$:

$$
\mathrm{Recall@}k = \frac{\#\{\text{relevant items in top }k\}}{\#\{\text{relevant items}\}}.
$$

It answers: **How much of the relevant set did the system recover?**

Recall is especially important in candidate generation. If a relevant item is absent from the candidate set, no downstream ranker can recover it.

#### HitRate@$k$

HitRate@$k$ is binary per evaluation unit:

$$
\mathrm{HitRate@}k = \mathbf{1}[\text{at least one relevant item occurs in top }k].
$$

Aggregated HitRate is the fraction of users/queries with at least one hit. It is simple, but it ignores whether there were one or many relevant items and ignores where inside the top $k$ the hit occurred.

#### MRR

**Mean Reciprocal Rank** focuses on the first relevant result. For one example:

$$
RR = \frac{1}{r},
$$

where $r$ is the rank of the first relevant item. If there is no relevant item in the evaluated list, the usual convention is $RR=0$.

Then:

$$
MRR = \frac{1}{N}\sum_{q=1}^{N} RR_q.
$$

A first hit at rank $1$ gives $1$, rank $2$ gives $1/2$, rank $10$ gives $0.1$. MRR is appropriate when the first satisfactory result dominates the experience.

#### Average Precision and MAP

Average Precision rewards retrieving **multiple** relevant items early. For one evaluation unit:

$$
AP = \frac{1}{R}\sum_{r=1}^{L} P@r\cdot rel_r,
$$

where $R$ is the number of relevant items under the chosen contract, $P@r$ is precision at rank $r$, and $rel_r$ is $1$ if the item at rank $r$ is relevant.

Then:

$$
MAP = \frac{1}{N}\sum_{q=1}^{N} AP_q.
$$

A contract must specify what happens when $R=0$ and whether AP is truncated at $k$.

#### DCG and NDCG

DCG handles graded relevance and explicitly values higher positions more. A common form is:

$$
DCG@k = \sum_{r=1}^{k} \frac{2^{rel_r}-1}{\log_2(r+1)}.
$$

The gain term $2^{rel_r}-1$ makes higher relevance grades disproportionately valuable. The logarithmic denominator discounts results farther down the ranking.

The ideal ranking for the same relevance labels has score $IDCG@k$. Then:

$$
NDCG@k = \frac{DCG@k}{IDCG@k}.
$$

NDCG is typically in $[0,1]$ when gains are nonnegative. If $IDCG@k=0$, the implementation must define a policy, for example returning $0$ or excluding that evaluation unit. That choice is part of the metric contract.

#### AUC

For binary labels, ROC-AUC can be interpreted as:

$$
P(s(x^+) > s(x^-)),
$$

with tie handling defined appropriately: the probability that a random positive receives a higher score than a random negative.

AUC is a global pairwise-ordering metric. It is not top-heavy, so a model can have strong AUC and still perform poorly in the top few recommendation slots.

#### Log-loss

For a predicted probability $p$ and binary label $y$:

$$
\ell_{\text{log}} = -\left[y\log p + (1-y)\log(1-p)\right].
$$

Log-loss rewards probabilities that are both directionally correct and numerically honest. Confident wrong predictions receive a large penalty.

#### Calibration

A model is calibrated when events assigned probability near $p$ happen about a fraction $p$ of the time. For example, among recommendations scored near $0.20$ conversion probability, about $20\%$ should convert under the same evaluation conditions.

Calibration matters when probabilities are used for expected value, thresholds, auction logic, capacity allocation, or decision rules. A ranking model may order items correctly while being badly calibrated.

#### Coverage

Coverage measures how broadly the system uses the available space. Common variants include:

- **catalog coverage:** fraction of eligible items ever recommended;
- **user coverage:** fraction of users for whom the system can produce recommendations;
- **supplier/creator coverage:** fraction of providers receiving exposure.

Coverage can reveal popularity collapse even when relevance metrics look strong.

#### Novelty

Novelty rewards recommendations that are less obvious or less globally common. One common information-style score for item $i$ is:

$$
\mathrm{novelty}(i) = -\log P(i),
$$

where $P(i)$ may be based on historical popularity or exposure frequency.

High novelty is not automatically good; obscure but irrelevant items can score as novel. Novelty should be evaluated with relevance and satisfaction.

#### Diversity

Diversity asks whether items in one recommendation slate are meaningfully different. If $sim(i,j)$ is an item-similarity function, one simple intra-list diversity definition is:

$$
ILD = \frac{2}{k(k-1)}\sum_{i<j} (1-sim(i,j)).
$$

The result depends critically on how similarity is defined: category overlap, embedding cosine similarity, creator identity, topic, brand, or another representation. Therefore diversity has no complete meaning without the similarity contract.

#### Watch-time and completion

In media/feed systems, **watch-time** measures consumed duration, while **completion rate** measures the fraction of content consumed or the probability of crossing a completion threshold.

Raw watch-time can favor long content. Completion can favor short content. Either can be gamed by content length, autoplay, weak negatives, or UI policy. Segmenting by content length and conditioning on exposure is often necessary.

#### Conversion and revenue

Conversion can mean purchase, signup, booking, install, or another downstream action. Revenue can be measured as total revenue, revenue per impression, revenue per session, contribution margin, or expected value.

These metrics have delayed labels and can be affected by price, inventory, promotions, position, attribution windows, and repeat exposure. A metric contract must state attribution and censoring rules.

#### Long-term metrics

Long-term metrics include retention, repeated satisfaction, churn reduction, long-run watch quality, creator/seller health, or lifetime value. They matter because optimizing immediate clicks can damage future user experience or ecosystem health.

Their main difficulty is causal attribution: they are slow, noisy, and influenced by many events between recommendation and outcome.

#### Concrete worked example

Suppose a user has four relevant items: $\{A,C,E,G\}$. The system returns the top five:

$$
[A,B,C,D,F].
$$

The binary relevance sequence is:

$$
[1,0,1,0,0].
$$

Then:

$$
Precision@5 = \frac{2}{5}=0.4,
$$

because two of five shown items are relevant.

$$
Recall@5 = \frac{2}{4}=0.5,
$$

because two of the four relevant items were recovered.

$$
HitRate@5 = 1,
$$

because at least one relevant item appears.

The first relevant item is at rank $1$, so:

$$
RR=1.
$$

For Average Precision, relevant items occur at ranks $1$ and $3$. Precision at those ranks is $1/1=1$ and $2/3$. Under the standard AP definition, the denominator is the number of relevant items in the reference set, here $R=4$:

$$
AP@5 = \frac{1 + 2/3}{4} \approx 0.417.
$$

For truncated AP@$k$, the contract must still specify the exact cutoff convention, especially when $R>k$, and must define what happens when $R=0$. The key invariant is that AP normalization is tied to the relevant set rather than arbitrarily to the recommendation-list length.

Now suppose graded relevance is $[3,0,2,0,0]$. DCG gives high gain to rank $1$, smaller gain to rank $3$, and discounts rank $3$ more heavily. NDCG compares that DCG with the best possible ordering of the same gains.

This one example shows the central distinction: **Precision measures purity, Recall measures recovery, HitRate measures existence, MRR measures first-hit position, MAP measures repeated relevant hits with rank sensitivity, and NDCG measures discounted graded ordering quality.**

### Core Interview Reasoning

A compact reasoning structure for R04 is:

1. **Define the metric contract.**
2. **Separate metric families by what they measure.**
3. **Match metrics to the system stage.**
4. **State trade-offs and blind spots.**
5. **Add product, segment, and online metrics.**
6. **Explain edge cases and diagnosis.**

#### 1. Define the metric contract first

A metric contract is the explicit specification needed to make a reported number reproducible and interpretable. At minimum it should define:

- evaluation unit;
- eligibility/candidate universe;
- labels and relevance grades;
- cutoff $k$;
- duplicate/repeat handling;
- empty-label behavior;
- tie handling;
- missing/unjudged treatment;
- temporal attribution/censoring;
- aggregation and weighting;
- slices/segments;
- version of the metric implementation.

This prevents “same metric name, different number” failures between notebooks, dashboards, experiment systems, and production monitoring.

#### 2. Separate metric families

**Set/top-$k$ metrics:** Precision@$k$, Recall@$k$, HitRate@$k$.

**Rank-sensitive metrics:** MRR, MAP, DCG/NDCG.

**Score/probability metrics:** AUC, log-loss, calibration.

**Catalog/slate health metrics:** coverage, novelty, diversity.

**Product/business metrics:** watch-time, completion, conversion, revenue.

**Long-horizon metrics:** retention, satisfaction, ecosystem health, long-term value.

Each family answers a different question. No single offline metric captures the complete product objective.

#### 3. Match metrics to stages

A multi-stage recommender usually has candidate generation, ranking, reranking, and final product evaluation.

- **Candidate generation:** Recall@$K$ is central because retrieval defines the maximum quality downstream stages can achieve. Source-specific and union recall are useful for multi-channel retrieval.
- **Pre-rank/rank:** NDCG@$k$, MAP@$k$, MRR, or task-specific top-$k$ metrics capture ordering quality. AUC may be useful diagnostically but is rarely sufficient by itself for a top-of-list product.
- **Probability-producing ranker:** add log-loss and calibration when score magnitude matters.
- **Reranker/slate:** add diversity, novelty, coverage, constraint satisfaction, redundancy, and provider/category balance.
- **Product launch:** online user/business metrics, guardrails, segment outcomes, latency, and reliability are required.

#### 4. Understand the main trade-offs

**Precision versus Recall:** At fixed model quality, increasing $k$ often increases Recall@$k$ but can reduce Precision@$k$ because more marginal items enter the list.

**Relevance versus Diversity/Novelty:** Aggressive diversification can lower itemwise relevance while improving slate usefulness, discovery, or long-term satisfaction.

**Ordering versus Probability Quality:** AUC/NDCG can improve while calibration worsens. This matters if downstream systems multiply scores by value or apply thresholds.

**Short-term versus Long-term:** Click or watch-time gains can harm retention, satisfaction, provider health, or content quality.

**Aggregate versus Segments:** An aggregate metric can improve while new users, tail items, a region, or a provider segment regresses.

#### 5. Important edge cases

**No relevant items:** Recall and AP may be undefined mathematically. The evaluator must choose to return zero, skip the unit, or use another documented policy.

**Fewer than $k$ returned items:** Precision can divide by $k$ or by returned count depending on the contract. The distinction is material because dividing by returned count can hide retrieval failure.

**Duplicate recommendations:** Duplicates usually should not receive repeated relevance credit and may indicate a serving bug.

**Incomplete labels:** Historical interactions are not a complete relevance set. Unobserved items may be relevant but never exposed.

**Delayed outcomes:** Purchases, subscriptions, or retention require attribution windows and censoring policies.

**Position/exposure bias:** Observed clicks are affected by where and whether an item was shown, so offline metrics on logged behavior can reflect the old policy rather than pure relevance.

**Ties:** AUC and rank metrics need deterministic or explicitly randomized tie handling.

**Popular-item dominance:** Accuracy-style metrics can look good while coverage and novelty collapse.

#### 6. How the pieces connect

Metrics form a chain of evidence rather than one scoreboard:

$$
\text{candidate recall} \rightarrow \text{ranking quality} \rightarrow \text{slate quality} \rightarrow \text{online outcomes} \rightarrow \text{long-term outcomes}.
$$

A regression can be localized by seeing where this chain first degrades. For example:

- candidate Recall@$1000$ down: retrieval/candidate-source problem;
- Recall@$1000$ stable but NDCG@$20$ down: ranking/feature/objective problem;
- offline ranking stable but diversity constraint violations rise: reranking/serving problem;
- offline NDCG up but online conversion down: metric-objective mismatch, exposure bias, calibration, serving skew, latency, or changed user behavior.

### Deeper Reasoning and Derivations

#### Why top-$k$ metrics are not interchangeable

Assume a user has ten relevant items. System A retrieves one relevant item at rank $1$ and no others in the top $10$; System B retrieves six relevant items in the top $10$, with the first at rank $4$.

- MRR can prefer A because the first hit is earlier.
- Recall@$10$ strongly prefers B because more of the relevant set is recovered.
- Precision@$10$ also prefers B if both return ten items.
- NDCG depends on the exact positions and grades of all relevant results.

The correct metric therefore depends on product semantics. A navigational task may care mostly about the first success; a discovery slate may care about multiple good options.

#### Why retrieval Recall@$K$ is a ceiling

Let $C_K(u)$ be the top-$K$ candidate set produced by retrieval for user/context $u$. A downstream ranker can only reorder items inside $C_K(u)$. If a relevant item $i^*$ is not in $C_K(u)$, then no ranker can place $i^*$ in the final top list.

Thus candidate recall constrains achievable final ranking quality. Improving the ranker cannot repair missing candidates; diagnosing final quality without candidate-recall telemetry can misattribute failure.

#### Why AUC can disagree with top-$k$ quality

AUC averages ordering correctness over many positive-negative pairs. In a recommendation problem with thousands or millions of negatives, most pairs involve low-ranked items that users never see. A model can improve those pairwise relationships and raise AUC without improving the top ten positions.

Therefore AUC is useful for global discrimination but weak as the sole selection metric for top-of-list ranking.

#### Why log-loss and calibration are different from ranking quality

Suppose two models preserve identical item ordering:

- Model A predicts $[0.90,0.80,0.70]$.
- Model B predicts $[0.60,0.40,0.20]$.

Ranking metrics are identical if the order is unchanged. But if true event frequencies align with the second set, Model B has better probability semantics. Log-loss and calibration distinguish these models while NDCG or AUC may not.

This matters whenever a downstream system computes quantities such as:

$$
\mathrm{expected\ value} = P(\mathrm{conversion}) \times \mathrm{value}.
$$

#### Why NDCG normalizes

Raw DCG can be higher for examples that simply have more or larger relevance grades. Dividing by IDCG compares the obtained ordering to the best ordering available for that same relevance set. The normalization makes per-query/user values more comparable before macro-averaging.

The normalization does not solve incomplete or biased labels. If the relevance set is wrong, NDCG can be computed perfectly and still measure the wrong thing.

#### MAP denominator semantics

Average Precision is sensitive to truncation conventions. Standard AP normalizes by the number of relevant items $R$. For AP@$k$, some evaluators cap the attainable denominator at $\min(R,k)$, while others retain $R$ and simply truncate the summed precision terms at $k$. Those are different metric contracts and must not be mixed. In every case, the denominator semantics are tied to the relevant set, not chosen arbitrarily from the output-list length.

#### Exposure-dependent labels

Recommendation labels come from a logged policy. A missing interaction does not necessarily mean irrelevance because the item may never have been shown. Observed feedback is generated by both user preference and the exposure/examination process.

A naïve offline metric can therefore reward a model for imitating the historical policy. Counterfactual evaluation, randomized data, propensity methods, careful negative construction, or controlled experiments may be required when policy bias is material.

#### Metric gaming and proxy failure

A metric becomes a target and can cease to represent the original objective. Examples:

- optimizing CTR can encourage clickbait;
- optimizing raw watch-time can overfavor long content;
- optimizing conversion can over-concentrate on head items or high-intent users;
- optimizing revenue can sacrifice user trust or margin;
- optimizing novelty can surface obscure but irrelevant items;
- optimizing catalog coverage can force low-quality exposure.

Robust evaluation uses a primary metric plus guardrails and slices rather than a single unconstrained proxy.

#### Diagnostic logic from metric movements

A useful Staff-level pattern is to examine **joint movement**, not a single number.

- **Recall@$K$ down, NDCG down:** candidate generation may be failing; ranking may be downstream collateral damage.
- **Recall@$K$ stable, NDCG down:** candidate pool is intact; inspect ranker features, labels, objective, model version, or serving.
- **NDCG up, conversion down:** inspect metric alignment, position/exposure bias, calibration, business constraints, latency, and online population shift.
- **NDCG stable, coverage down sharply:** popularity collapse or retrieval-source concentration may be occurring.
- **Offline metrics stable, online outcome down:** inspect training-serving skew, stale features, serving version mismatch, UI changes, latency, or experimentation problems.
- **Aggregate up, key segment down:** inspect weighting, support, cold-start behavior, and exposure distribution by segment.

### Advanced Staff-Depth Considerations

The reusable Staff-level backbone for this item is:

`Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate`

Equivalently:

`Assumption → Mechanism → Evidence → Decision → Trade-off → Validation`

For this question, the baseline is: The baseline is a versioned metric contract: define evaluation unit, eligible universe, labels/gains, cutoff, empty/tie/duplicate semantics, aggregation, time horizon, and stage before interpreting any number. Stage metrics form a chain from candidate opportunity to ranking quality to slate quality to product/long-term outcomes.

The eight subsections below apply that same loop from different angles. Each explanation teaches the mechanism first; the filled template then compresses it into a reusable interview scaffold.

#### 1. Changed Constraints and Transfer Logic

Metrics must change emphasis when the product or system constraint changes, while preserving the underlying decision question. Reducing candidate budget makes retrieval recall more binding; a one-slot surface shifts weight toward Precision@1/HitRate@1; graded utility calls for NDCG/expected value; tighter latency requires a quality-resource frontier rather than maximizing one metric.

A useful reasoning chain is:

`changed assumption → affected mechanism/stage → invariant → broken assumption → consequence → redesign → metric impact → trade-off → validation`

**Filled template for this item**

- **Original assumption:** Retrieval returns about 1000 candidates and downstream ranking has enough opportunity.
- **Changed constraint:** Candidate budget is reduced to 200 to meet latency.
- **Invariant:** Final product utility remains the objective; retrieval still sets the downstream opportunity ceiling.
- **Broken assumption:** Recall@1000 no longer describes the candidate set actually available to ranking.
- **Consequence:** Relevant-item omission can dominate final quality even if conditional ranker NDCG remains strong.
- **Design change:** Evaluate Recall@K and final quality across multiple candidate budgets; improve retrieval efficiency or adaptive budgets if recall collapses.
- **Metric impact:** Report candidate count, Recall@K, final NDCG/product metric, and p95/p99 together.
- **Trade-off:** Lower p99/compute versus lower candidate opportunity.
- **Validation:** Choose the knee of the quality-latency frontier using online outcomes and stage guardrails.

#### 2. Failure Modes and Diagnosis

Metric incidents require checking both semantics and pipeline stage. Two dashboards can disagree because they use different label populations, empty-case rules, post-processing stages, or code versions even when both implementations are internally correct. Find the first contract or stage divergence before calling one number wrong.

**Filled template for this item**

- **Symptom:** Two dashboards report materially different NDCG@20 for the “same” model/week.
- **Stage decomposition:** candidate population → labels/gains → ranked list → post-processing/served list → aggregation/dashboard.
- **Slices:** User/query eligibility, device, segment, label maturity, candidate source, and zero-positive cases.
- **Competing hypotheses:** Different contract semantics; different populations/snapshots; different model/index/feature versions; ranked-versus-served list; implementation bug.
- **Discriminating evidence:** Shared hand-computed fixtures and contract metadata for each result.
- **Offline/online comparison:** Confirm whether dashboards evaluate raw ranker output or actual served/exposed slates.
- **Replay/isolation:** Run both metric implementations on the same frozen fixture and dataset snapshot.
- **First divergence:** First difference in contract, population, stage, or code output.
- **Immediate mitigation:** Stop comparing/launching on unversioned metric names and publish contract metadata.
- **Permanent prevention:** Shared metric library/fixtures, versioned definitions, lineage, and dashboard contract checks.

Memory aid: `Symptom → Slice → Stage → Hypotheses → Evidence → First divergence → Fix`.

#### 3. Latency and Resource Trade-offs

Metrics should be interpreted on a joint quality-resource surface. Increasing candidate count can improve Recall@K but raise hydration/ranking p99; a heavier reranker can improve NDCG while violating the SLO. The decision is usually marginal quality per unit latency/compute, not maximum offline metric.

**Filled template for this item**

- **Budget:** User-facing p95/p99 and serving-cost envelope.
- **Cost decomposition:** Retrieval depth + feature hydration + ranker compute + reranker/slate processing + evaluation/monitoring overhead where relevant.
- **Dominant cost:** Often candidate-driven hydration/ranking or heavy reranking, depending on architecture.
- **Quality driver:** More candidates/richer models improve opportunity and ordering.
- **Cost driver:** They increase memory traffic, inference, network, and tail latency.
- **Optimization knobs:** Candidate K, ANN effort, pre-ranking, feature set, model size, reranker complexity, caching/precompute.
- **Fallback/degradation:** Smaller candidate/ranker path with hard constraints preserved and fallback traffic measured separately.
- **Trade-off curve:** Recall@K, NDCG/product metric, calibration/guardrails versus p95/p99 and cost.
- **Decision:** Select the operating point meeting the SLO without crossing an accepted quality/business-loss envelope.

Memory aid: `Budget → Breakdown → Bottleneck → Knobs → Quality loss → Fallback`.

#### 4. Scale and Capacity

Evaluation itself becomes a system at large scale. Top-k computation, distributed aggregation, high-cardinality slices, deterministic dedup/ties, label snapshots, and uncertainty estimation must scale without changing metric semantics. Approximation is acceptable only when versioned and quantified.

**Filled template for this item**

- **Scaling dimension:** Users/items/evaluation events and slice cardinality grow by orders of magnitude.
- **Baseline scale assumption:** Exact per-unit metric computation and centralized aggregation are cheap.
- **First bottleneck:** Full sorting, memory, distributed aggregation, and high-cardinality slicing become expensive.
- **Second-order effects:** Double counting, nondeterministic ties, inconsistent snapshots, and unstable small-slice estimates.
- **Architectural response:** Top-k algorithms, distributed keyed aggregation, versioned label/candidate snapshots, and approximate methods with error bounds when needed.
- **Partitioning/replication/caching/batching:** Partition by evaluation unit/time, combine associative statistics carefully, cache immutable fixtures/contracts.
- **Consistency/freshness consequence:** Different partitions or dashboards can compute on mismatched label/model versions.
- **Operational failure mode:** “Same” metric drifts because semantics/population changed under scale optimizations.
- **Validation:** Golden fixtures, exact-vs-approx comparisons, deterministic reruns, confidence intervals, and cross-system parity tests.

Memory aid: `What grows? → What stops fitting? → What bottlenecks? → How do we partition? → What new failure appears?`.

#### 5. Freshness, State, and Versioning

Offline metrics are only as realistic as the state they evaluate. Stale eligibility, user history, embeddings, indexes, prices, or labels can make offline quality optimistic relative to serving. Preserve point-in-time state and version identifiers so quality can be sliced by state age and reproduction is possible.

**Filled template for this item**

- **State that becomes stale:** Labels, candidate universe, user/item state, embeddings/indexes, model/features, eligibility, and metric code.
- **Why freshness matters:** Evaluation may score items/features that would not exist or be valid at serving time.
- **Required freshness:** Match serving-time eligibility and relevant state lag for the decision being evaluated.
- **Refresh cost:** Snapshot generation, re-embedding/indexing, label maturation, and recomputation of large metric suites.
- **Update architecture:** Versioned periodic snapshots plus targeted faster refresh for highly dynamic state.
- **Version consistency:** Metric result must bind dataset/labels, candidate universe, model/index/features, and code/contract versions.
- **Failure from version skew:** Offline gains can reflect newer labels/state than production actually used.
- **Fallback:** Freeze a known-consistent evaluation snapshot rather than mix partially refreshed components.
- **Measurement:** State age/version, label maturity, eligibility age, and quality by freshness bucket.
- **Decision:** Refresh the state that materially changes measured decision quality, while preserving reproducibility.

Memory aid: `What goes stale? → How fast does it matter? → What does refresh cost? → How do versions stay consistent?`.

#### 6. Implementation, Serving, and Observability

Treat every production metric as a versioned artifact. A trustworthy number should be reproducible from the metric contract, code version, label/data snapshot, evaluation population, candidate universe, model/index/feature versions, cutoff/gain rules, aggregation, and experiment assignment. Shared hand-computed fixtures are the interface tests between notebooks, batch jobs, dashboards, and online monitoring.

**Filled template for this item**

- **Conceptual object:** A metric contract plus a deterministic computation over a defined population/stage.
- **Training/data implementation:** Build point-in-time labels/candidate sets and compute per-unit metrics under versioned semantics.
- **Stored artifact/state:** Contract version, code hash, dataset/label snapshot, population definition, model/index/feature versions, results and uncertainty.
- **Serving path:** Log retrieved → ranked → post-processed → served → exposed identities and versions so offline/online stages can be compared.
- **Component contract:** All evaluators must agree on labels, eligibility, cutoff, gains/discounts, empty/tie/duplicate rules, and aggregation.
- **Logging:** Request/unit IDs, candidate/served lists, scores, constraints, exposure, outcomes, versions, experiment assignment.
- **Versioning:** Metric contract and code are versioned just like models.
- **Failure mode:** Two correct systems report different values because their contracts/populations differ.
- **Observability:** Metric deltas by stage/slice with uncertainty and contract/version metadata.
- **Rollback:** Restore the prior contract/code/data snapshot when a metric implementation changes unexpectedly.
- **Testing/replay:** Hand-computed fixtures and identical-request replay across offline/dashboard/experiment implementations.

Memory aid: `Train → Store → Serve → Version → Log → Monitor → Roll back`.

#### 7. Vertical Transfer

The mechanism should transfer; the assumptions must be re-derived. Use the checklist:

`labels → candidate sources → objectives → features → constraints → evaluation → experiments → serving/freshness → ecosystem effects`

Representative verticals:

- **Short-video feed:** **Invariant:** Metric-contract discipline transfers. **Different assumption:** Utility shifts from purchase to watch/completion/skip/session satisfaction; content length biases raw metrics. **Technical consequence:** Redefine gains, add fatigue/diversity/creator-health guardrails, and validate long-term retention.
- **E-commerce:** **Invariant:** Stage metrics and contracts transfer. **Different assumption:** Conversion, revenue/margin, stock, price, delayed purchase, and seller exposure matter. **Technical consequence:** Use retrieval/ranking metrics for development plus conversion/value and inventory-aware online guardrails.
- **Ads:** **Invariant:** Ranking/evaluation framework transfers. **Different assumption:** Calibrated probabilities, expected value, auctions, budgets, pacing, and advertiser/user constraints dominate. **Technical consequence:** Pair ordering metrics with calibration and auction/business outcomes.
- **Marketplace:** **Invariant:** Metric portfolio transfers. **Different assumption:** Consumer utility and provider-side exposure/supply health are jointly important. **Technical consequence:** Measure concentration/coverage on both sides and guard against ecosystem harm.
- **Notifications:** **Invariant:** Offline/online contract discipline transfers. **Different assumption:** Open/click is balanced against fatigue, opt-out, disablement, and send/no-send decisions. **Technical consequence:** Use conservative success metrics plus negative long-term guardrails.

**Filled transfer template — Short-video feed**

- **Invariant:** Metric-contract discipline transfers.
- **Different data-generating process:** Utility shifts from purchase to watch/completion/skip/session satisfaction; content length biases raw metrics.
- **Different objective:** Re-derive the primary product utility for this vertical rather than copying the base objective.
- **Different candidates/features:** Candidate sources and features should reflect the vertical-specific context and available signals.
- **Different constraints:** Utility shifts from purchase to watch/completion/skip/session satisfaction; content length biases raw metrics.
- **Metric change:** Retain transferable stage metrics, then add vertical-specific outcomes and guardrails.
- **Serving change:** Redefine gains, add fatigue/diversity/creator-health guardrails, and validate long-term retention.
- **Ecosystem effect:** Check creator/provider/seller/advertiser or user-side concentration where relevant.
- **Validation:** Evaluate both transferable retrieval/ranking quality and the vertical-specific product outcome.

Memory aid: `Keep the mechanism; re-derive the assumptions.`

#### 8. Objective and Metric Mismatch

Objective mismatch is central to R04. An offline metric can improve because the system optimized exactly what it rewards while the product outcome worsens because the metric omits calibration, causal exposure effects, value, UX, segments, or long-term utility. First rule out execution mismatch; then interrogate the proxy.

**Filled template for this item**

- **Offline/model metric:** NDCG@20 improves.
- **Online/product outcome:** Conversion, retention, or another business/user metric declines.
- **Execution verification:** Verify candidates, features, versions, ranker scores, reranking, latency/fallback, and served/exposed list.
- **Metric semantics:** NDCG rewards discounted ordering under its relevance labels/gains.
- **Blind spots:** Probability calibration, price/value, position/exposure bias, segment weighting, inventory, UX friction, and long-term effects.
- **Missing product factor:** The relevance label/gain mapping may not encode actual conversion/value/satisfaction.
- **Repair:** Revise labels/gains or objective portfolio; add calibration, business/long-term guardrails, and slice-specific metrics.
- **Trade-off:** Better alignment often increases label delay/noise and creates multi-objective tension.
- **Online validation:** Randomized experiment measuring primary product outcome, relevance metrics, calibration/constraints, latency, and segment guardrails.

Memory aid: `Did we execute the objective incorrectly, or correctly optimize the wrong objective?`

## Material Follow-ups / Scenario Variants

### Staff Variant — Candidate budget shrinks from 1000 to 200

Suppose the original system retrieves $1000$ candidates with:

$$
Recall@1000 = 0.96, \qquad NDCG@20 = 0.45,
$$

and after a latency-driven change it retrieves only $200$ candidates with:

$$
Recall@200 = 0.74, \qquad NDCG@20 = 0.46,
$$

while p99 latency improves from $160\text{ ms}$ to $85\text{ ms}$.

The first conclusion is that the ranker is not obviously worse. Conditional on the smaller candidate set, NDCG@20 is slightly higher. The important regression is upstream: retrieval is preserving a much smaller fraction of the relevant set. Because downstream rankers can only reorder items they receive, the candidate-stage quality ceiling has fallen.

The correct interpretation is therefore not "NDCG improved, so the system improved." It is:

- retrieval quality decreased materially;
- ranking quality conditional on retrieval remained roughly intact;
- latency improved substantially;
- the product decision is now a quality-versus-latency trade-off.

The next step is to build a candidate-count frontier, for example at $K\in\{100,200,300,500,800,1000\}$, and measure at each point:

- Recall@$K$;
- final NDCG@$20$ or the main product metric;
- feature-hydration cost;
- ranker compute;
- p95/p99 latency;
- memory or serving cost where material.

The decision should be based on **marginal quality gained per additional candidate under the latency budget**, not on maximizing Recall@$K$ or minimizing latency in isolation. If Recall collapses rapidly as $K$ shrinks, the retrieval system may need better candidate sources, more efficient ANN parameters, better pre-ranking, or selective/adaptive candidate budgets rather than a globally fixed smaller $K$.

### Staff Variant — Offline NDCG improves but mobile conversion drops

Suppose a new ranker changes offline NDCG@20 from $0.41$ to $0.46$, online conversion falls by $8\%$, Recall@1000 is unchanged, and the regression is concentrated on mobile while desktop is neutral.

The diagnosis should proceed in order.

**1. Localize by stage.** Unchanged Recall@1000 weakens the hypothesis that retrieval lost relevant candidates. The likely fault boundary is downstream: ranker features, ranking objective, calibration, reranking, serving, or product/UI behavior.

**2. Slice the offline metric.** Recompute NDCG@20 by device. If mobile NDCG regressed offline while aggregate NDCG improved, the aggregate hid a segment regression. That is primarily an evaluation/weighting problem rather than an online-only failure.

**3. Compare offline and online inputs for mobile.** If mobile NDCG also improved offline, compare mobile production with the offline evaluator on:

- candidate IDs and candidate ordering;
- feature values, missingness, preprocessing, and freshness;
- model, index, and feature versions;
- score distributions;
- reranking/constraint outcomes;
- timeout, cache, and fallback behavior.

This tests for training-serving skew or a mobile-specific serving path problem.

**4. Replay identical mobile requests.** Run the same logged requests through the old and new pipelines and compare:

$$
\text{candidates}
\rightarrow
\text{features}
\rightarrow
\text{scores}
\rightarrow
\text{reranked slate}
\rightarrow
\text{served/exposed slate}.
$$

The first divergence is the strongest lead for root cause.

**5. If replay is equivalent, strengthen the objective-mismatch hypothesis.** If the mobile production pipeline uses the same candidates, features, model version, scores, and ranking logic as offline evaluation, then the system is faithfully executing the offline winner. The remaining question is whether NDCG's relevance labels adequately represent conversion for mobile users.

Investigate whether mobile conversion depends on factors not captured in the offline relevance definition, such as price, inventory, shipping friction, screen real estate, UI position effects, purchase intent, or calibration. At that point the issue is not that production failed to execute the model; it is that the offline metric or label contract was an incomplete proxy for the business outcome.

### Staff Variant — Two dashboards disagree on NDCG@20

Suppose Dashboard A reports:

$$
NDCG@20 = 0.47,
$$

while Dashboard B reports:

$$
NDCG@20 = 0.42,
$$

for what is believed to be the same model and evaluation week.

Do not start by assuming one dashboard has a coding bug. First verify that the two systems are computing the same mathematical object.

**1. Compare the metric contract.** Check:

- cutoff $k$;
- relevance grades and gain function;
- discount convention;
- duplicate handling;
- zero-positive / zero-IDCG policy;
- tie handling;
- truncation semantics;
- macro versus micro averaging;
- weighting by user/query/session.

**2. Compare the evaluation population and labels.** Verify:

- dataset snapshot;
- evaluation time window;
- user/query eligibility;
- candidate universe;
- delayed-label attribution window;
- censoring policy;
- filtering of invalid or unavailable items.

**3. Compare model and pipeline versions.** Confirm the same model, index, feature versions, post-processing rules, and candidate-generation outputs were evaluated.

**4. Compare ranked versus served/exposed slates.** One dashboard may evaluate the raw ranked list while another evaluates the post-processed or actually exposed list after availability filters, policy constraints, sponsored insertion, history suppression, timeouts, or fallbacks.

**5. Reproduce both computations on a shared fixture.** Use a small hand-computed set of users/queries with known relevance grades and expected NDCG. If the contract, data, population, and versions all match but the numbers still differ, then an implementation bug becomes the leading hypothesis.

The systems lesson is that a metric name is not an interface contract. A trustworthy metric result should be traceable to its metric-contract version, label/data snapshot, model/index/feature versions, evaluation population, and code version.

### Staff Variant — Vertical transfer from e-commerce to short-video feed

The mechanics of the evaluation framework remain invariant: define a metric contract, use stage-appropriate retrieval/ranking metrics, retain rank-aware evaluation, measure actual product outcomes, and add guardrails. What changes is the meaning of relevance and utility.

For a short-video feed:

- **Retrieval:** Recall@$K$ can remain useful, but the positive/relevant set should be based on feed-appropriate outcomes rather than purchase/cart labels.
- **Ranking:** NDCG remains useful if graded relevance is redefined, for example with gains based on satisfied watch, completion, positive feedback, or skip/hide behavior. The gain mapping should reflect product utility rather than mechanically copying e-commerce grades.
- **Immediate product metrics:** add watch-time, completion, skip rate, session continuation, hides/reports, and possibly qualified engagement rather than conversion/revenue as the primary outcomes.
- **Slate metrics:** diversity, redundancy, freshness, creator concentration, and topical repetition become more important because sequential consumption amplifies slate composition effects.
- **Long-term metrics:** retention, repeated-session satisfaction, creator ecosystem health, and fatigue become more central.
- **Guardrails:** raw watch-time can favor long videos; completion can favor short videos; click/open metrics can reward sensational content; diversity can reduce immediate relevance if pushed too hard.

Thus the invariant is the evaluation architecture, while the labels, gains, time horizon, product outcomes, and guardrails must change with the vertical.
