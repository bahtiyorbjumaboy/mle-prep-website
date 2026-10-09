---
type: interview-answer
item: "2027:R04"
title: "Recommendation Metrics and Metric Contracts"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - ranking-metrics
  - evaluation
  - metric-contracts
---

## Canonical Staff-Depth Question

Derive/compare Precision@k, Recall@k, HitRate@k, MRR, MAP, DCG/NDCG, AUC/log-loss, calibration, coverage, novelty, diversity, watch-time/completion, conversion/revenue, and long-term metrics.

## Mastery Answer

I would start by separating **what stage I am evaluating** from **what user or business outcome I ultimately care about**. A recommender usually has at least retrieval, ranking, reranking/constraints, and product-outcome layers, so no single metric is sufficient. The metric contract must define the evaluation unit, relevance labels, cutoff $k$, candidate universe, aggregation rule, treatment of users with no positives, duplicate items, ties, and whether negatives are the full catalog or sampled. Without that contract, even a familiar metric can be misleading.

For **retrieval**, the main question is whether relevant items survive candidate generation. Recall@k is usually the primary ceiling metric: among all relevant items for a user, what fraction appear in the top $k$ retrieved candidates? Precision@k asks what fraction of the retrieved $k$ are relevant, but retrieval often intentionally returns a large candidate set, so precision may be less important there. HitRate@k collapses the question to whether at least one relevant item appears. It is intuitive but ignores whether a user had one relevant item or twenty.

For **ranking**, order matters. MRR emphasizes the rank of the first relevant result: reciprocal rank is $1/r$ where $r$ is the position of the first relevant item, then averaged across queries or users. It is appropriate when one early success dominates utility. MAP averages precision at the ranks where relevant items occur and then averages across users; it rewards retrieving multiple binary-relevant items early. DCG allows graded relevance and discounts lower ranks, commonly with $1/\log_2(i+1)$. NDCG divides DCG by the ideal DCG for that user, making scores more comparable across users with different relevance sets. Its contract must define gain, discount, cutoff, zero-IDCG behavior, and label scale.

AUC and log-loss evaluate a different object. AUC measures pairwise ordering probability over scored positives and negatives and is threshold-free, but it ignores top-$k$ concentration and can look strong while top recommendations are poor. Log-loss evaluates probabilistic predictions and heavily penalizes confident mistakes. If scores are used as probabilities—for expected value, auctions, thresholds, or risk—**calibration** matters: among predictions near $p$, the event should occur about fraction $p$ of the time. Good ranking does not imply good calibration, and good calibration does not imply good top-$k$ ranking.

Then I add **system- and product-level metrics**. Coverage asks how much of the catalog, users, or eligible inventory the system can meaningfully serve. Novelty measures how non-obvious or non-popular recommendations are, but must be defined relative to a reference popularity or user-history distribution. Diversity measures dissimilarity within a slate or across exposure; it depends critically on the item-similarity definition. These metrics often trade off against immediate relevance.

For product outcomes, I use metrics aligned to the vertical: watch time and completion for video, conversion and revenue for commerce, perhaps saves, hides, retention, or satisfaction for other surfaces. I distinguish **per-impression**, **per-user**, **per-session**, and **long-term** aggregation because optimizing one can create pathological behavior in another. Revenue alone can over-rank expensive items; watch time can reward addictive or overly long content; CTR can reward clickbait. Long-term metrics such as retention, repeat visits, satisfaction, creator or seller health, and churn are closer to durable value but are delayed, noisy, and harder to attribute.

The Staff-level rule is: **match the metric to the stage and decision, then define semantics before measuring**. Retrieval metrics diagnose candidate-set ceiling; ranking metrics diagnose ordering; probabilistic metrics diagnose score semantics; coverage/diversity/novelty diagnose ecosystem behavior; and online product metrics validate actual utility. I would always inspect slices—new users, new items, head/tail inventory, geography, device, and traffic source—because aggregate gains can hide regressions. Finally, I would validate offline improvements with online experiments when the product outcome is causal and exposure-dependent, because logged offline metrics inherit the behavior and biases of the previous policy.

## Learn the Concepts

### Foundation

A recommendation system makes two broad kinds of decisions:

1. **Which items are worth considering?** This is retrieval or candidate generation.
2. **In what order should those items be shown?** This is ranking and reranking.

Metrics are measurements attached to those decisions. A useful mental model is:

**candidate survival → ordering quality → score semantics → slate/catalog behavior → product outcome**

Different metrics answer different questions. The first mistake to avoid is asking, “What is the best recommender metric?” There is no universal answer because each metric measures a different object.

#### Basic objects and terminology

For a user $u$:

- $G_u$ is the set of items considered relevant or positive for that user in the evaluation window.
- $R_k(u)$ is the ordered list of the top $k$ recommended items.
- $\operatorname{rel}_u(i)$ is the relevance label for the item at rank $i$; it may be binary, such as click/no-click, or graded, such as 0–3 relevance.
- A **cutoff** $k$ says how far down the ranked list the metric looks.
- A **candidate universe** is the set of items the system was allowed to choose from.
- A **metric contract** is the complete definition of how a metric is computed: labels, population, cutoff, candidate universe, edge cases, averaging, deduplication, ties, censoring, and sampling.

A metric name without its contract is incomplete. “Recall@100 = 0.72” is not fully interpretable until the evaluation population, relevance definition, candidate universe, and treatment of edge cases are known.

#### Precision@k

Precision@k asks: **Of the $k$ recommended items, how many are relevant?**

$$
\operatorname{Precision@k}(u)
=
\frac{|R_k(u) \cap G_u|}{k}.
$$

If the system recommends five items and two are relevant, Precision@5 is $2/5=0.4$.

Precision rewards purity of the shown set. It does not care how many relevant items existed but were missed.

#### Recall@k

Recall@k asks: **Of all relevant items for the user, how many survived into the top $k$?**

$$
\operatorname{Recall@k}(u)
=
\frac{|R_k(u) \cap G_u|}{|G_u|}.
$$

If a user has four relevant items and the top 20 contains three, Recall@20 is $3/4=0.75$.

Recall is especially important for candidate generation because a later ranker cannot recover an item that retrieval discarded.

#### HitRate@k

HitRate@k asks only whether **at least one** relevant item appears in the top $k$:

$$
\operatorname{HitRate@k}(u)
=
\mathbf{1}\{R_k(u)\cap G_u\neq \emptyset\}.
$$

It is useful when one success is enough, but it throws away multiplicity. A user with one hit out of one relevant item and a user with one hit out of twenty both count as a hit.

#### MRR

Mean Reciprocal Rank focuses on the **first relevant item**. If the first relevant result is at rank $r_u$:

$$
\operatorname{RR}(u)=\frac{1}{r_u}.
$$

Then MRR is the average of reciprocal rank across users or queries.

Ranks 1, 2, and 10 contribute $1$, $0.5$, and $0.1$, respectively. MRR is therefore appropriate when the user mainly needs one good result quickly.

#### MAP

Average Precision rewards placing **multiple relevant items** early. For binary relevance:

$$
\operatorname{AP@k}(u)
=
\frac{1}{Z_u}
\sum_{i=1}^{k}
\operatorname{Precision@i}(u)\,\operatorname{rel}_u(i),
$$

where $Z_u$ is defined by the evaluation contract, commonly the number of relevant items up to the cutoff or the total number of relevant items. MAP is mean AP across users.

AP only adds precision at ranks containing relevant items, so early relevant items improve later precision terms as well.

#### DCG and NDCG

DCG handles **graded relevance** and rank discounting. A common version is:

$$
\operatorname{DCG@k}
=
\sum_{i=1}^{k}
\frac{2^{\operatorname{rel}_i}-1}{\log_2(i+1)}.
$$

The numerator gives larger gain to highly relevant items. The denominator discounts items appearing lower in the list.

NDCG normalizes by the best possible DCG for the same relevance labels:

$$
\operatorname{NDCG@k}
=
\frac{\operatorname{DCG@k}}{\operatorname{IDCG@k}}.
$$

A perfect ordering gives 1.0 when IDCG is nonzero.

#### AUC and log-loss

AUC asks whether the model tends to assign higher scores to positives than negatives. One interpretation is:

$$
\operatorname{AUC}
=
P(s^+ > s^-),
$$

with a tie convention defined separately.

AUC is a global pairwise-ordering metric. It is not inherently top-$k$.

Binary log-loss measures probabilistic prediction quality:

$$
\ell(y,p)
=
-y\log p-(1-y)\log(1-p).
$$

Confidently predicting $p\approx 0$ for an event that occurs produces a very large penalty. Log-loss therefore evaluates probability quality rather than only ordering.

#### Calibration

A model is calibrated when predictions mean what they say probabilistically. Among events receiving predicted probability around 0.20, approximately 20% should occur, subject to sampling noise and conditioning choices.

Calibration is essential when downstream logic multiplies a probability by value, sets thresholds, or compares expected utilities.

#### Coverage, novelty, and diversity

These describe behavior that relevance metrics alone can miss.

- **Coverage**: how much of the eligible catalog, user population, or provider inventory receives meaningful recommendations or exposure.
- **Novelty**: how non-obvious or non-popular recommended items are, often measured from item popularity, self-information, or distance from user history.
- **Diversity**: how dissimilar items within a slate or across exposure are. The answer depends on the chosen similarity representation: category, creator, embedding, taxonomy, or another semantic space.

#### Product and long-term metrics

Examples include:

- watch time;
- completion rate;
- conversion rate;
- revenue or margin;
- saves, likes, hides, reports;
- repeat sessions;
- retention;
- satisfaction surveys;
- churn;
- creator or seller health.

These metrics are often delayed, exposure-dependent, and influenced by factors outside the recommender. They are therefore closer to product utility but harder to estimate cleanly offline.

#### Worked example

Suppose a user has three relevant products: A, C, and E. The recommender returns:

1. A
2. B
3. C
4. D
5. F

At $k=5$:

- Precision@5 = $2/5 = 0.4$ because A and C are relevant.
- Recall@5 = $2/3 \approx 0.667$ because two of the user's three relevant items were retrieved.
- HitRate@5 = 1 because at least one relevant item appears.
- Reciprocal rank = 1 because the first result is relevant.

If the list instead starts B, D, A, C, F, Precision@5 and Recall@5 remain identical, but reciprocal rank drops to $1/3$ and DCG/NDCG drop because the relevant items moved downward. This shows why set-based metrics and rank-sensitive metrics measure different things.

Important beginner distinctions:

- Precision and recall are not opposites; both can increase if the system improves.
- HitRate does not measure how many relevant items were found.
- MRR cares only about the first relevant result.
- MAP and NDCG care about multiple relevant results and their ordering, but NDCG naturally supports graded labels.
- AUC can improve even when top-$k$ ranking does not.
- A well-ranked list is not automatically well calibrated.
- Offline relevance is not the same as online causal product value.
- A metric formula is not a full metric definition; the contract supplies the semantics.

### Core Interview Reasoning

A strong answer can be reconstructed with the sequence:

**stage → decision being evaluated → metric family → metric contract → blind spot → complementary metric → online validation**

The sequence matters because it prevents listing metrics as a glossary.

**1. Start with the stage.** Candidate generation needs ceiling/coverage metrics; ranking needs order-sensitive metrics; probability-producing models need probabilistic metrics; reranking needs constraint/diversity metrics; the product needs behavioral and long-term outcomes.

**2. State the decision each metric evaluates.** Precision@k asks about top-$k$ purity; Recall@k asks about relevant-item survival; MRR asks how early the first success occurs; MAP and NDCG ask about ordered relevance; AUC asks about global positive-vs-negative ordering; log-loss and calibration ask about probability semantics.

**3. Define the metric contract before interpreting a number.** At minimum specify: unit of evaluation, relevance label, cutoff $k$, candidate universe, temporal window, negative set, user inclusion rule, aggregation, duplicate handling, tie handling, and edge cases such as no positives or IDCG = 0.

**4. Name the blind spot.** Every metric discards information. Recall ignores ordering inside the retrieved set. MRR ignores every relevant item after the first. AUC underweights top-of-list behavior. NDCG depends on gain and discount choices. Revenue can reward expensive items even if user utility falls. Coverage can improve through irrelevant exposure.

**5. Use complementary metrics rather than one scalar.** A retrieval stage might report Recall@1000 plus latency and source coverage. A ranker might report NDCG@10 plus calibration, diversity, and segment slices. A commerce surface might validate conversion, revenue, returns/cancellations, satisfaction, and seller concentration online.

**6. Slice the evaluation.** Aggregate metrics can hide failure on new users, long-tail items, sparse-history users, regions, devices, inventory classes, or provider groups. Segment metrics are part of the contract, not an afterthought.

**7. Treat offline metrics as evidence, not proof of product impact.** Offline evaluation is based on logged exposure and labels generated by an existing policy. Candidate-set mismatch, position bias, selection bias, delayed outcomes, and sampled negatives can all distort apparent gains. When the goal is user or business value, an online experiment or another valid causal design is usually the final validation.

A compact reconstruction structure for an interview is:

**Retrieval ceiling → ranking order → probability semantics → slate/catalog health → product outcome → contract + slices + online validation.**

### Deeper Reasoning and Derivations

#### Precision, recall, and the candidate ceiling

Let $G_u$ be all relevant items for user $u$, and $R_k(u)$ the retrieved top-$k$. Recall@k is the fraction of $G_u$ that survives retrieval. If retrieval recall is 0.80, then even an oracle downstream ranker cannot place the missing 20% of relevant items in the final slate. This gives retrieval recall a special causal role: it bounds downstream opportunity under the candidate set.

Precision@k uses $k$ in the denominator, so increasing $k$ often decreases precision while increasing recall. This is not necessarily a model regression. It may be the intended trade-off when retrieval expands the candidate set to give a stronger ranker more opportunities.

The metric contract must define what happens when $|G_u|=0$. Common choices include excluding that user from recall aggregation or defining a special value. Setting recall to zero without thought mixes “system missed relevant items” with “no evaluable positive existed.”

#### HitRate versus Recall

For a user with $|G_u|=1$, HitRate@k and Recall@k are identical. When $|G_u|>1$, they diverge. This makes HitRate suitable for leave-one-out protocols but potentially misleading for multi-positive domains such as feeds, playlists, or shopping sessions.

A system can raise HitRate by finding one easy popular positive per user while failing to improve breadth over the user's other relevant items.

#### Why reciprocal rank heavily rewards the top

Reciprocal rank decays hyperbolically: rank 1 contributes 1, rank 2 contributes 0.5, rank 5 contributes 0.2, rank 10 contributes 0.1. The difference between ranks 1 and 2 is much larger than between ranks 9 and 10. That encodes a specific utility assumption: the first useful result is disproportionately valuable.

MRR is therefore aligned with navigational or one-answer behavior but not with a multi-item feed where the quality of the whole slate matters.

#### MAP as precision accumulated at relevant ranks

Suppose binary relevance over five ranks is $[1,0,1,1,0]$. Precision at relevant ranks is $1/1$, $2/3$, and $3/4$. AP averages these terms under the chosen normalization. Moving a relevant item earlier raises its own precision contribution and can raise later contributions, so AP captures both retrieval and ordering of multiple positives.

However, MAP assumes binary relevance unless extended; a mild preference and a purchase can receive the same relevance indicator, which may be inappropriate for graded utility.

#### DCG, gains, discounts, and normalization

DCG can be written generically as:

$$
\operatorname{DCG@k}
=
\sum_{i=1}^{k} g(\operatorname{rel}_i)d(i),
$$

where $g$ is a gain function and $d(i)$ is a decreasing discount. The common choices $g(r)=2^r-1$ and $d(i)=1/\log_2(i+1)$ encode two assumptions: moving from relevance 2 to 3 is more valuable than moving from 0 to 1, and top ranks matter more.

NDCG divides by IDCG, the DCG from the ideal ordering of the same labels. This controls for differing amounts of attainable relevance. But the normalization creates an edge case when IDCG is zero. The contract must choose whether to exclude the example, define NDCG as zero, or use another policy.

Because NDCG depends on the gain scale, labels such as click=1, cart=2, purchase=3 should not be chosen casually. Under exponential gain, purchase receives far more than three times the gain of click.

#### AUC's pairwise interpretation and why it can miss top-k quality

AUC is equivalent to the probability that a randomly drawn positive receives a higher score than a randomly drawn negative, with a tie rule. In highly imbalanced recommendation problems there may be millions of easy negatives. Correctly ordering those easy pairs can dominate AUC even if the model mishandles the hardest negatives competing for the top 10 slots.

Therefore AUC is useful for broad ranking discrimination but weak as the only metric for top-k recommendation.

#### Log-loss, proper scoring, and probability semantics

Expected log-loss is minimized by predicting the true conditional event probability under the model's information set. This makes log-loss a proper scoring rule. If downstream business logic computes expected value such as

$$
\operatorname{EV}(i)=P(\text{purchase}\mid x_i)\times \operatorname{margin}(i),
$$

then probability quality matters directly. A pure ordering score may produce excellent NDCG but unusable expected-value calculations.

Class reweighting, negative sampling, or biased logging can change the relationship between raw model scores and deployment probabilities, so calibration must be checked on a representative distribution.

#### Calibration is conditional frequency agreement, not ranking quality

Two models can produce exactly the same ordering but different calibration. If Model A outputs $[0.9,0.8,0.7]$ and Model B outputs $[0.3,0.2,0.1]$, ranking metrics are identical, yet probability semantics differ dramatically.

Calibration should be checked overall and by segments because aggregate calibration can hide segment-specific overconfidence or underconfidence. Reliability diagrams, expected calibration error, Brier score, or proper scoring rules can support this analysis, but binning choices themselves form part of the evaluation contract.

#### Coverage, concentration, novelty, and diversity require reference definitions

Catalog coverage might be:

$$
\frac{\text{unique items recommended}}{\text{eligible catalog size}}.
$$

But this treats one impression and one million impressions equally. Exposure concentration metrics, long-tail share, entropy, or Gini-style statistics answer a different question.

Novelty often uses inverse popularity, for example self-information $-\log p(i)$, but the popularity distribution must be defined over a specific window and event type. Diversity can use average pairwise distance in category or embedding space, but the result is only meaningful relative to that similarity function.

Improving novelty or diversity mechanically can lower relevance. The appropriate objective is usually a measured trade-off or constrained optimization, not maximizing diversity in isolation.

#### Product metrics are policy- and exposure-dependent

CTR, watch time, conversion, and revenue are observed only for exposed items. A change in ranking changes who sees what, which changes the label-generating process. Offline logs therefore reflect the old policy. This creates selection and position bias and means that offline replay of a new policy may not estimate its causal online effect without additional assumptions or counterfactual methods.

Long-term metrics are even more difficult because of delayed outcomes, censoring, repeated exposures, and interference. The closer a metric is to ultimate product value, the harder it may be to attribute rapidly and with low variance.

#### Macro, micro, and weighted aggregation

A metric can be averaged per user and then across users (macro), or computed from pooled events (micro). These answer different questions. Macro averaging gives each user equal weight; micro averaging gives heavy users more weight because they contribute more events. Weighted aggregation may intentionally prioritize revenue, traffic, or other strata.

The aggregation rule can reverse conclusions when user activity is highly skewed, so it belongs in the metric contract.

#### Candidate-set evaluation and sampled negatives

Metrics computed against 100 sampled negatives are not necessarily comparable with metrics computed against the full catalog. The ranking problem is easier when the candidate universe is small or negatives are sampled uniformly rather than drawn from realistic hard candidates. Sampled-negative evaluation can substantially inflate Recall@k or NDCG@k and distort model comparisons if sampling interacts with popularity.

The evaluation contract should therefore specify whether ranking occurs over the full corpus, a production-retrieved candidate set, or a sampled set, and how that set was constructed.

### Advanced Staff-Depth Considerations

The universal Staff reasoning loop is:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate**

A compressed form is:

**Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**

For R04, the baseline is the evaluation contract: which stage is being assessed, what counts as relevance, which candidate universe is eligible, how ranking position is valued, what population is aggregated, and what product outcome matters. A change in one of those assumptions can make an unchanged metric number mean something different. The mechanism is therefore often not “the model changed,” but “the mapping from behavior to metric changed.” The observables are stage-specific metric families, slices, score/calibration distributions, exposure distributions, and online outcomes. The Staff decision is to change the metric, its contract, the system objective, or the evaluation design only after identifying which semantic assumption failed.

#### 1. Changed Constraints and Transfer Logic

Metric choice is constraint-dependent. The invariant is that the metric must remain aligned with the decision being evaluated. What changes is the product regime: number of relevant items, interaction horizon, display surface, candidate budget, or business constraint. For example, if a single-slot recommendation becomes a 20-item feed, HitRate@1 no longer captures slate quality. The system now needs order-sensitive multi-item metrics and potentially diversity or redundancy terms.

A robust transfer process asks which utility assumption the old metric encoded. If that assumption no longer holds, the metric should change before model comparison proceeds. Otherwise the team can “improve” a metric that is now semantically obsolete.

* Original assumption: one early relevant item is the dominant user utility.
* Changed constraint: the product becomes a 20-item scrolling feed with many potentially relevant items.
* Invariant: evaluation must reward useful items appearing early.
* Broken assumption: quality is no longer determined primarily by the first relevant result.
* Consequence: MRR can remain high while the rest of the slate is redundant or poor.
* Design change: prioritize NDCG@k or MAP@k for ordering, plus diversity/coverage and product engagement metrics.
* Metric impact: the evaluation becomes sensitive to multiple relevant items and slate composition.
* Trade-off: more metrics increase interpretation complexity and may expose competing objectives.
* Validation: compare offline metrics with session-level satisfaction/engagement in an online experiment.

#### 2. Failure Modes and Diagnosis

Metric failures can originate from label construction, candidate evaluation, formula implementation, aggregation, slicing, or objective mismatch. A common symptom is a large offline gain that does not reproduce online. The first task is to separate execution failure from semantic failure.

Use the chain:

**logged exposure → labels → candidate universe → scores/order → metric computation → aggregation/slices → online exposure → product outcome**

If candidate recall is stable and NDCG rises, inspect whether labels, negative sampling, or offline candidate sets differ from production. If offline rankings are truly better under the intended contract but online behavior worsens, investigate calibration, diversity, business constraints, position/exposure effects, latency/serving regressions, and whether the offline metric is aligned with product utility.

* Symptom: offline NDCG@10 improves 6%, but online conversion falls 4%.
* Stage decomposition: labels/candidates → ranker scores → offline metric → serving → exposure → conversion.
* Slices: new vs returning users, head vs tail items, device, category, traffic source, inventory state.
* Competing hypotheses: evaluation leakage; sampled-negative artifact; score calibration shift; serving feature skew; diversity loss; price/inventory mix change.
* Discriminating evidence: full-candidate replay, calibration curves, feature parity checks, candidate recall, exposure concentration, latency and timeout logs.
* Offline/online comparison: reproduce production candidates and filters, then compare ranking metrics and product slices on identical requests.
* Replay/isolation: deterministic replay with model/index/feature versions pinned.
* First divergence: the earliest stage where treatment differs unexpectedly from the intended evaluation assumption.
* Immediate mitigation: rollback or restore the prior objective/serving bundle if user harm is material.
* Permanent prevention: versioned metric definitions, production-shaped replay, slice dashboards, and automated contract tests.

#### 3. Latency and Resource Trade-offs

Most evaluation metrics are offline and do not directly consume serving latency, but metric choice affects resource decisions. Raising retrieval $k$ can improve Recall@k while increasing ranker compute and p99 latency. Using a heavier ranker may improve NDCG but reduce throughput. Computing expensive diversity constraints online may improve slate quality while consuming deadline budget. Therefore quality metrics must be paired with resource metrics when comparing deployable systems.

The relevant budget is not “metric computation latency” but the system cost required to achieve a target point on the quality curve. A Staff evaluation compares Pareto frontiers such as Recall@1000 versus retrieval p99, or NDCG@10 versus ranker FLOPs and end-to-end p99.

* Budget: fixed end-to-end p99, for example 120 ms.
* Cost decomposition: retrieval + feature hydration + ranker + reranker/constraints + orchestration.
* Dominant cost: often candidate-dependent ranking/feature work after retrieval expands $k$.
* Quality driver: higher candidate recall and stronger ranking over informative features.
* Cost driver: candidate count, feature reads, model complexity, and reranking work.
* Optimization knobs: candidate pruning, pre-ranking, caching, precompute, vectorization, batching, distillation, quantization, cheaper diversity approximations.
* Fallback/degradation: smaller candidate count, cached/popular candidates, lighter ranker, deterministic constraint fallback.
* Trade-off curve: report quality metrics against p95/p99 latency, throughput, memory, or cost.
* Decision: choose a quality-resource operating point that satisfies the SLO rather than maximizing offline relevance unconstrained.

#### 4. Scale and Capacity

At small scale, full-catalog evaluation and per-request logging may be feasible. As users, items, and event volume grow, the first broken assumption is often that exact evaluation can scan all candidates or that every metric can be computed on all traffic at full granularity.

Scale can introduce sampled evaluation, distributed aggregation, approximate quantiles, delayed joins, and storage constraints. Those optimizations can change semantics. For example, sampled negatives make top-k metrics easier; approximate exposure counts can distort coverage; late conversion labels can make recent cohorts look worse. Capacity engineering must preserve the metric contract while reducing cost.

* Scaling dimension: candidate universe grows from 100K to 100M items and evaluation traffic grows 100×.
* Baseline scale assumption: exact full-catalog scoring and centralized metric aggregation are tractable.
* First bottleneck: compute and I/O for candidate scoring plus event-log joins.
* Second-order effects: distributed skew, delayed labels, storage growth, partial data, approximate aggregation, and slower recomputation.
* Architectural response: stage-specific sampled diagnostics plus periodic exact or high-fidelity benchmark sets; distributed aggregation keyed by stable metric version.
* Partitioning/replication/caching/batching: partition by date/user or request, batch score computations, cache static relevance metadata, replicate metric definitions as versioned code rather than ad hoc SQL.
* Consistency/freshness consequence: different shards or jobs must use the same metric version and label cutoff.
* Operational failure mode: mixed metric versions create a false trend break.
* Validation: shadow new pipelines against a trusted reference implementation on fixed fixtures and representative full-fidelity samples.

#### 5. Freshness, State, and Versioning

Metrics depend on state that changes over time: relevance labels, catalog eligibility, item popularity, user histories, experiment assignment, and delayed outcomes. Staleness can make an unchanged model appear better or worse.

A metric definition should therefore be versioned together with label windows, cutoff rules, filters, gain mappings, and candidate-set construction. Popularity-based novelty requires a time window; conversion metrics require mature attribution windows; coverage requires a contemporaneous eligible catalog. Recomputing yesterday's metric with today's catalog can silently alter the denominator.

* State that becomes stale: labels, eligibility, popularity statistics, catalog inventory, and user-history context.
* Why freshness matters: denominators and relevance judgments determine the meaning of the metric.
* Required freshness: aligned to the product event horizon; some metrics can be daily while session intent may require near-real-time context.
* Refresh cost: event processing, late-data reconciliation, joins, and recomputation.
* Update architecture: immutable event logs plus versioned daily/streaming aggregates and late-arrival backfills.
* Version consistency: metric code version, label cutoff, catalog snapshot, and model/index version should be recorded together.
* Failure from version skew: apparent metric shifts caused by changed eligibility or label maturity rather than model behavior.
* Fallback: hold back immature metrics, expose provisional versus finalized values separately, and retain stable benchmark windows.
* Measurement: track late-label completion, denominator changes, and differences between provisional and finalized metrics.
* Decision: optimize freshness only to the point required by the decision; prioritize semantic consistency over arbitrarily real-time dashboards.

#### 6. Implementation, Serving, and Observability

A production metric system needs more than formulas. It needs a versioned library or evaluator, reproducible candidate and label construction, explicit aggregation semantics, test fixtures, telemetry linking recommendations to outcomes, and dashboards that preserve stage boundaries.

Offline and online metric definitions should share contracts where possible, but the data sources may differ. Serving should log request ID, user/context version, candidate source attribution, model/index/feature versions, scores, final slate, positions, eligibility/filter reasons, experiment assignment, and downstream outcomes. Without exposure logging, click or conversion metrics cannot be interpreted correctly.

* Conceptual object: a versioned metric contract for each stage and product outcome.
* Training/data implementation: point-in-time labels and candidate sets generated from immutable exposure/outcome logs.
* Stored artifact/state: metric-definition version, evaluation dataset snapshot, gain/discount configuration, eligibility snapshot, and aggregation outputs.
* Serving path: emit candidates, scores, final ranks, and exposure metadata needed to reconstruct evaluation.
* Component contract: every metric declares population, labels, $k$, candidate universe, edge-case rules, and aggregation.
* Logging: exposure, position, scores, candidate source, model/index/feature versions, experiment IDs, and outcome timestamps.
* Versioning: metric definitions are code/config artifacts with stable IDs.
* Failure mode: dashboard trends compare values computed under different semantics.
* Observability: metric health checks include denominator size, missing labels, zero-positive rate, slice coverage, and event-lag distributions.
* Rollback: preserve prior metric and model definitions so regressions can be replayed under consistent semantics.
* Testing/replay: hand-computed fixtures, ideal/worst rankings, no-positive users, duplicates, ties, cutoff boundaries, sampled-negative tests, and deterministic production replay.

#### 7. Vertical Transfer

The invariant across verticals is: **first identify the decision and data-generating process, then choose stage-appropriate metrics and define the contract.** What changes is relevance, exposure, delay, utility, and the cost of bad recommendations.

For **e-commerce**, retrieval recall and NDCG may use purchase/cart relevance, but conversion, revenue, margin, returns, availability, and seller concentration matter. A purchase is delayed and exposure-dependent, and expensive items can dominate revenue metrics.

For **video/feed**, graded engagement may include watch time, completion, skips, hides, or satisfaction. A longer video naturally offers more watch-time opportunity, so raw watch time can be length-biased. Diversity, freshness, and session-level metrics matter strongly.

For **ads**, ordering quality is insufficient because scores may feed auctions or expected value. Calibration of pCTR/pCVR, advertiser value, budget pacing, frequency caps, and user-experience guardrails are central.

For **notifications**, false positives are expensive because the system interrupts the user. Open or click rate alone can reward over-sending. Opt-outs, fatigue, downstream sessions, and long-term retention are necessary counterweights.

For **marketplaces**, user relevance must be balanced with provider exposure, supply health, concentration, and inventory constraints.

Representative transfer template — e-commerce:

* Invariant: retrieval and ranking metrics must reflect whether useful products survive and appear early.
* Different data-generating process: purchases are sparse, delayed, and conditional on exposure, availability, price, and inventory.
* Different objective: combine user relevance with conversion/value and durable satisfaction.
* Different candidates/features: inventory, price, seller, category, substitutes/complements, and availability matter.
* Different constraints: unavailable items cannot be served; seller concentration and business rules may constrain the slate.
* Metric change: use Recall/NDCG plus conversion, revenue or margin, returns/cancellations, coverage, and seller-exposure slices.
* Serving change: evaluate only eligible inventory at request time and log filters/version state.
* Ecosystem effect: maximizing short-term conversion can over-concentrate exposure on head sellers or products.
* Validation: online experiment with user and provider guardrails plus delayed conversion maturation.

#### 8. Objective and Metric Mismatch

Execution failure means the system failed to implement the intended objective—for example, stale features caused the ranker served online to differ from the model evaluated offline. Objective mismatch means the system correctly optimized a proxy that was not the true product goal—for example, NDCG on click labels improved, but the new ranking induced clickbait and reduced satisfaction.

This distinction is central to R04 because metrics define what “better” means. Before changing a model after an online regression, verify whether the treatment actually delivered the intended ranking under the intended contract. If yes, then the problem may be the metric itself, the labels, or omitted product factors.

* Offline/model metric: NDCG@10 on click-based graded relevance.
* Online/product outcome: short-term CTR rises, but repeat sessions and satisfaction fall.
* Execution verification: serving replay confirms intended model, features, filters, and ranks were delivered.
* Metric semantics: click labels reward immediate attraction, not durable satisfaction.
* Blind spots: clickbait, redundancy, negative feedback, session abandonment, and long-term effects.
* Missing product factor: satisfaction and repeated-use utility.
* Repair: add negative feedback/quality labels, long-term guardrails, and multi-objective or constrained ranking.
* Trade-off: short-term CTR may decline while durable user value improves.
* Online validation: randomized experiment with mature retention/satisfaction outcomes and predefined guardrails.

## Material Follow-ups / Scenario Variants

### Offline NDCG improves substantially, but online conversion drops. What do you do first?

First verify execution before declaring metric mismatch. Pin the production candidate set, features, model/index versions, filters, and final ranks and replay representative requests. If the intended ranking was not actually served, localize the first divergence and fix the serving/data issue. If execution is correct, then inspect whether offline evaluation used sampled negatives, stale eligibility, click-oriented relevance, or a candidate universe unlike production. Next compare calibration, exposure concentration, price/inventory mix, and key user/item segments. If the gain is real under the intended contract but conversion still drops, treat it as objective mismatch: the offline relevance proxy is not capturing the product outcome. Repair the objective or metric suite, then validate with another controlled experiment.

### How would you choose between Recall@k and NDCG@k for candidate generation?

Use Recall@k as the primary retrieval metric because candidate generation's job is to preserve relevant opportunities for downstream ranking. NDCG at retrieval can be secondary if the retrieval order is itself consumed or the downstream stage only scores a prefix. If the downstream ranker receives all $k$ candidates, fine-grained retrieval ordering is less important than whether the relevant items survived. Pair recall with latency, memory/cost, source-level marginal recall, and segment coverage.

### What should the contract say for users with no relevant items?

Do not silently assign zero. A zero can mean either “the system failed to retrieve a positive” or “there was no positive to retrieve,” which are different states. Define whether such users are excluded from metrics whose denominator requires positives, evaluated with another metric, or assigned a special value. Always report the fraction of zero-positive evaluation units because excluding them can itself create selection bias.

### Why can a model have higher AUC but worse Recall@10 or NDCG@10?

AUC averages pairwise ordering over positives and negatives across the entire score distribution. With many easy negatives, a model can improve a huge number of unimportant pairs while worsening the handful of hard competitors near the top. Recall@10 and NDCG@10 concentrate on the top of the ranked list, where product exposure occurs. The metrics therefore weight errors differently rather than contradicting each other.
