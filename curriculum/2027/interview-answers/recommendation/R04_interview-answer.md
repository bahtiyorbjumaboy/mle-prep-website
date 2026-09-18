---
type: interview-answer
item: "2027:R04"
title: "Recommendation Metrics and Metric Contracts"
created: "2026-09-18"
updated: "2026-09-18"
tags:
  - recommendation
  - ranking-metrics
  - evaluation
  - metric-contracts
---

## Canonical Staff-Depth Question

Derive/compare Precision@k, Recall@k, HitRate@k, MRR, MAP, DCG/NDCG, AUC/log-loss, calibration, coverage, novelty, diversity, watch-time/completion, conversion/revenue, and long-term metrics.

## Mastery Answer

I would start by defining the **metric contract** before computing any number: the evaluation unit, candidate universe, relevance/label definition, cutoff $k$, treatment of multiple positives, no-positive cases, duplicates and ties, averaging scheme, sampled negatives, attribution/censoring window, and whether the metric is computed over all requests or only eligible requests. Without that contract, two teams can report the same metric name and mean different things.

For top-$k$ ranking quality, **Precision@$k$** measures how much of the displayed top-$k$ is relevant,

$$
P@k = \frac{|\mathrm{TopK} \cap R|}{k},
$$

while **Recall@$k$** measures how much of the relevant set was recovered,

$$
R@k = \frac{|\mathrm{TopK} \cap R|}{|R|}.
$$

Precision is useful when display slots are scarce; recall is especially important in candidate generation because the ranker cannot recover an item that retrieval missed. **HitRate@$k$** is the indicator that at least one relevant item appears in the top $k$; it is useful for next-item or one-success tasks but saturates quickly and ignores additional hits.

**MRR** averages the reciprocal rank of the first relevant item,

$$
\mathrm{MRR} = \frac{1}{N}\sum_q \frac{1}{\mathrm{rank}_q^{(1)}},
$$

with a defined value, usually $0$, when there is no hit. It is appropriate when the first useful result dominates utility and deliberately ignores later relevant items. **Average Precision** accumulates Precision@$i$ at ranks containing relevant items; **MAP** averages AP over evaluation units. MAP therefore rewards ranking all relevant items early, but its denominator and cutoff semantics must be specified, especially when there are more relevant items than $k$.

For graded relevance, **DCG** assigns larger gain to more relevant items and discounts lower ranks, commonly

$$
\mathrm{DCG}@k = \sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)}.
$$

**NDCG** divides by the ideal DCG for that unit,

$$
\mathrm{NDCG}@k = \frac{\mathrm{DCG}@k}{\mathrm{IDCG}@k},
$$

so it is normalized across queries/users with different attainable gain. The contract must state the gain function, discount, and what happens when $\mathrm{IDCG}=0$.

**AUC** is fundamentally a pairwise ordering metric: it can be read as the probability that a randomly chosen positive receives a higher score than a randomly chosen negative, with tie handling defined explicitly. It is threshold-independent but can look strong while the top few positions are poor, so it is rarely sufficient for a top-$k$ recommender. **Log-loss** evaluates probabilistic predictions rather than just ordering:

$$
-\left[y\log p + (1-y)\log(1-p)\right].
$$

It heavily penalizes confident wrong predictions and is appropriate when score semantics matter. If negatives were sampled or the evaluation class mix differs from deployment, raw log-loss may no longer represent deployment probability quality without correction.

**Calibration** asks whether predicted probabilities have empirical meaning: among events scored near $0.2$, roughly $20\%$ should occur under the relevant conditioning. Calibration is crucial when scores feed thresholds, expected-value calculations, auctions, pacing, or other downstream arithmetic. A model can have excellent AUC/NDCG and poor calibration, or vice versa.

Ranking accuracy is not the whole product. **Coverage** measures breadth, such as catalog coverage or the fraction of users for whom the system can produce valid recommendations. **Novelty** measures how non-obvious or non-popular recommendations are, often using self-information such as $-\log p(i)$ from an item popularity distribution. **Diversity** measures non-redundancy inside a slate, for example average pairwise dissimilarity. These three are distinct: a list can be diverse but composed entirely of popular items, or novel but highly redundant.

For media/feed systems, **watch time** captures absolute engagement while **completion** normalizes by content duration; each has bias and gaming modes. For commerce, **conversion** and **revenue/value** are closer to the business outcome but are sparse, delayed, attribution-sensitive, and affected by price, inventory, returns, and exposure. **Long-term metrics** such as retention, return rate, satisfaction, lifetime value, churn, or creator/provider health target durable utility but have longer feedback loops and usually require online experimentation or careful causal design rather than naive offline correlation.

I would select metrics by stage. Candidate retrieval is primarily judged by Recall@$K$/HitRate@$K$, marginal recall by source, coverage, and latency/resource cost. A ranker is judged by NDCG/MAP/MRR depending on label structure and user utility, with AUC/log-loss/calibration as score-level diagnostics when relevant. Reranking/slate construction adds diversity, novelty, coverage, and constraint metrics while monitoring relevance loss. The final product is judged online by engagement, conversion/value, long-term outcomes, and guardrails. The key Staff-level point is that **offline ranking metrics are stage diagnostics and proxies, not the product objective itself**.

## Learn the Concepts

### 1. Start with the metric contract

A metric name is incomplete until its semantics are fixed. Define at least:

- **Evaluation unit:** user, session, request, impression, query, or another grain.
- **Candidate universe:** full catalog, retrieved candidate set, logged impressions, or a sampled negative pool.
- **Relevance:** binary, graded, implicit engagement, purchase, watch threshold, human judgment, etc.
- **Cutoff $k$:** and whether fewer than $k$ returned items change the denominator.
- **No-positive cases:** include as zero, exclude, or report separately.
- **Duplicates / ties:** how repeated items and equal scores are handled.
- **Averaging:** macro per request/user, micro over events, or weighted by traffic/value.
- **Sampling:** whether negatives are exhaustive or sampled and whether correction is required.
- **Time / attribution:** label window, late events, censoring, returns/cancellations.
- **Eligibility:** whether unavailable, filtered, policy-blocked, or unjudgeable items are part of the denominator.

Metric-contract disagreements are not implementation trivia. They can reverse conclusions and invalidate experiment comparisons.

### 2. Precision@$k$, Recall@$k$, and HitRate@$k$

Let $R$ be the relevant set and $L_k$ the first $k$ recommended items.

$$
P@k = \frac{|L_k \cap R|}{k}
$$

answers: **Of the slots I used, how many were relevant?**

$$
R@k = \frac{|L_k \cap R|}{|R|}
$$

answers: **Of all relevant items, how many did I recover?**

$$
HR@k = \mathbf{1}[|L_k \cap R| > 0]
$$

answers: **Did I get at least one success?**

Example: suppose two items are relevant.

- Ranking A: relevant, irrelevant, irrelevant.
- Ranking B: irrelevant, relevant, relevant.

At $k=3$, A has $P@3=1/3$, $R@3=1/2$, $HR@3=1$. B has $P@3=2/3$, $R@3=1$, $HR@3=1$. HitRate cannot distinguish them because it intentionally discards the number and positions of later hits.

**Stage connection:** Recall@$K$ is the central retrieval-ceiling metric. If a useful item is absent from the candidate set, no downstream ranker can place it in the final slate.

### 3. MRR and MAP

**MRR** focuses only on the first relevant item. If the first relevant ranks at positions $1$, $2$, and $10$ for three requests, the reciprocal ranks are $1$, $1/2$, and $1/10$ before averaging. It is excellent when the user mainly needs one good answer and weaker when utility depends on several good recommendations.

For binary relevance, an AP-style metric is

$$
AP@k = \frac{1}{Z}\sum_{i=1}^{k} P@i\cdot rel_i,
$$

where $rel_i\in\{0,1\}$ and the normalization $Z$ must be specified. Common contracts use either the total number of relevant items or a cutoff-aware quantity such as $\min(|R|,k)$. **MAP** is the mean AP across users/queries.

MAP answers a different question from MRR: it rewards repeatedly placing relevant items early, not just the first one.

### 4. DCG and NDCG

DCG is designed for **graded relevance**. Two choices create its behavior:

1. **Gain:** how much more valuable grade 3 is than grade 2. The common exponential gain $2^{rel}-1$ makes high grades disproportionately important.
2. **Discount:** how quickly value decays with rank. The common $\log_2(i+1)$ denominator penalizes deep positions but not linearly.

NDCG normalizes against the best possible ordering for the same judged items, making scores more comparable across requests with different relevance distributions.

Important edge case: if a request has no positive gain, $\mathrm{IDCG}=0$. The evaluator must decide whether its NDCG is $0$, excluded, or separately reported. Silently choosing one policy changes aggregate results.

### 5. AUC, log-loss, and calibration are not top-$k$ substitutes

**AUC** measures global pairwise ordering. This is useful for diagnosing whether positives generally score above negatives, but it weights many pairs that never affect the product's top slots. With enormous negative universes, a model may achieve high AUC while still making poor top-$k$ choices.

**Log-loss** is a proper probabilistic scoring rule. It distinguishes a model that says $p=0.51$ from one that says $p=0.99$ even when their ordering is identical. This matters when the score is intended to represent CTR, conversion probability, completion probability, etc.

**Calibration** checks semantic correctness of those probabilities. Common diagnostics include reliability curves, expected calibration error, or Brier score, but calibration should also be inspected by important segment because aggregate calibration can hide segment drift.

A useful separation is:

- NDCG/MAP/MRR: **Is the ordering useful?**
- Log-loss: **Are probabilistic predictions accurate?**
- Calibration: **Can downstream systems interpret the score as a probability?**

### 6. Coverage, novelty, and diversity

These are often confused.

**Catalog coverage** can be defined as

$$
\frac{|\{\text{items recommended in the evaluation window}\}|}{|\text{eligible catalog}|}.
$$

It measures global breadth, not whether any individual slate is diverse.

**Novelty** often uses inverse popularity. One simple item-level score is

$$
novelty(i) = -\log p(i),
$$

where $p(i)$ is historical exposure or interaction frequency under a specified time window. Smoothing is needed for unseen items.

**Intra-list diversity** can use pairwise dissimilarity:

$$
ILD(L) = \frac{2}{n(n-1)}\sum_{i<j}(1-sim(i,j)).
$$

The similarity definition is part of the contract: category similarity, content embeddings, seller/creator identity, or another representation can produce very different conclusions.

These metrics are usually paired with a relevance metric because maximizing them alone can recommend irrelevant tail items.

### 7. Watch time and completion

For video/media:

- **Watch time** measures absolute consumed time, which can favor longer content and may be distorted by autoplay or passive consumption.
- **Completion rate** measures fraction completed or an event such as reaching a threshold, which can favor short content.

Neither is automatically equivalent to satisfaction. Hides, skips, reports, session exits, survey signals, and return behavior may be needed as guardrails or long-horizon outcomes.

### 8. Conversion and revenue/value

Conversion is closer to downstream commerce utility but creates harder labels:

- conversions are sparse;
- labels arrive late;
- attribution windows matter;
- stockouts/availability affect opportunity;
- price and promotions affect conversion;
- returns/cancellations can reverse apparent value;
- revenue can reward expensive items even when user utility or margin falls.

Therefore the metric contract should distinguish orders, GMV/revenue, margin/profit, expected value, and realized post-return value rather than using the word “revenue” loosely.

### 9. Long-term metrics

Long-term objectives include retention, repeat sessions, durable satisfaction, churn reduction, lifetime value, creator/provider health, and marketplace sustainability. They are strategically important but statistically difficult because they are delayed, sparse, confounded, and influenced by many product surfaces.

Offline ranking metrics should therefore be treated as **diagnostics/proxies**. Long-term claims usually need online experiments, switchbacks/cluster designs when interference matters, or causal/off-policy methods when experimentation is constrained.

### 10. Metric selection by recommender stage

| Stage | Primary questions | Typical metrics |
|---|---|---|
| Candidate retrieval | Did we recover items the user could value? | Recall@$K$, HitRate@$K$, source marginal recall, coverage, latency/memory |
| Ranker | Did we order candidates correctly? | NDCG@$k$, MAP@$k$, MRR, sometimes AUC |
| Probability model | Do score magnitudes have meaning? | Log-loss, calibration, Brier/ECE-style diagnostics |
| Reranker/slate | Is the slate useful and non-redundant under constraints? | NDCG/relevance loss + diversity, novelty, coverage, constraint violations |
| Online product | Did behavior/business improve? | CTR, watch/completion, conversion, revenue/value, satisfaction |
| Long horizon | Did durable utility/ecosystem health improve? | retention, return rate, churn, LTV, provider/creator health |

### 11. Common evaluation failures

- Reporting NDCG without defining relevance grades or no-positive behavior.
- Comparing Recall@$K$ across systems with different candidate universes.
- Computing AUC on sampled negatives and treating it as if it were full-population AUC.
- Treating a ranking score as a probability without calibration evidence.
- Averaging per-user metrics in one experiment and event-weighted metrics in another.
- Ignoring delayed conversion censoring.
- Letting unavailable or policy-blocked items inflate offline ranking quality.
- Optimizing diversity/novelty without measuring relevance loss.
- Treating offline metric gain as proof of online or long-term product gain.

## Material Follow-ups / Scenario Variants

### Which metric would you choose for a two-stage recommender?

For candidate generation I would optimize Recall@$K$ at a reasonably large $K$, sliced by important user/item segments, while tracking marginal recall from each candidate source and latency/resource cost. For the final ranker I would use NDCG@$k$ if relevance is graded or MAP/MRR depending whether multiple relevant items or the first hit dominates utility. Final product acceptance would depend on online business/user metrics rather than offline rank metrics alone.

### Why can AUC improve while NDCG@$10$ gets worse?

AUC averages ordering over positive-negative pairs across the score distribution. The model can improve many easy pairs far below the displayed cutoff while making worse mistakes among the highest-scored candidates. NDCG@$10$ is concentrated on the top ranks, so the two metrics can move in opposite directions.

### When does calibration matter in recommendation?

Calibration matters whenever a score participates in arithmetic or thresholds rather than only sorting: expected conversion value $p(\mathrm{purchase})\times value$, auction bids, pacing, notification thresholds, risk controls, or multi-objective score blending. If the score is used only as an ordering function, monotonic transformations preserve ranking but change probability semantics.

### E-commerce transfer

For an e-commerce “items you may like” system, I would track candidate Recall@$K$, ranker NDCG@$k$ or MAP@$k$, calibration if pCTR/pCVR feeds expected value, catalog/seller coverage and novelty as ecosystem diagnostics, and online conversion plus revenue/margin with explicit attribution/return windows. Availability and out-of-stock items must be handled consistently in the evaluation contract.

### Video/feed transfer

For a video/feed system, binary clicks are usually insufficient. I would use graded engagement signals such as watch-time/completion in offline ranking metrics, then evaluate online watch quality, skips/hides/reports, diversity, and return/retention. Completion must be interpreted with duration bias in mind, and absolute watch time can be gamed by long content or passive consumption.

### Changed constraint: only one relevant item exists per request

Recall@$k$ and HitRate@$k$ become nearly equivalent binary success measures, while MRR adds sensitivity to where that one item appears. MAP contributes little beyond reciprocal-rank-style behavior in this setting.

### Changed constraint: relevance is multi-grade and top positions dominate

Use DCG/NDCG with a documented gain and discount function. Precision/Recall collapse graded information and are less aligned with the product utility.
