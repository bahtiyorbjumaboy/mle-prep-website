---
type: interview-answer
item: "2027:R09"
title: "Negative Sampling and False Negatives"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation
  - negative-sampling
  - retrieval
  - contrastive-learning
  - exposure-bias
---

## Canonical Staff-Depth Question

Compare uniform, popularity-weighted, in-batch, hard, semi-hard, exposure-aware, and teacher-mined negatives. Explain sampling bias, accidental positives, false negatives, and correction.

## Mastery Answer

Negative sampling is necessary when the candidate universe is too large to score every non-positive item during training. The key point is that the negative sampler is not just an efficiency device: it defines which pairwise or multiclass comparisons the model sees, so it changes the effective training distribution and therefore the learned decision boundary.

I would choose a sampler by starting from the deployment task. If serving ranks a retrieved candidate set, I want training negatives that resemble mistakes the model will actually need to resolve at serving time, while still preserving enough breadth that the model learns the global geometry.

**Uniform negatives** sample items uniformly from the catalog. They are cheap, diverse, and useful early, but most are often trivially irrelevant, so gradients become low-information. **Popularity-weighted negatives** expose the model more often to popular items that are likely to appear or compete in production, but they can over-penalize popular items and amplify popularity bias unless corrected. **In-batch negatives** reuse other examples' positives as negatives, making large effective negative sets computationally cheap; however, they inherit the batch's sampling distribution and create accidental positives when two examples legitimately share an item. **Hard negatives** are high-scoring but non-labeled candidates, often retrieved by the current model. They focus learning near the decision boundary, but if mining is too aggressive they can be dominated by false negatives or outliers and destabilize training. **Semi-hard negatives** deliberately avoid the very hardest cases and often give a better information-to-noise trade-off. **Exposure-aware negatives** restrict or reweight negatives using impression/exposure logs so "not interacted with" is not automatically treated as "disliked"; this is crucial when labels are missing-not-at-random. **Teacher-mined negatives** use a stronger model to find semantically plausible competitors, improving training signal, but they transfer teacher bias and add mining cost and versioning complexity.

There are two different biases to distinguish. First, **sampling bias**: the negative distribution used in training differs from the target candidate distribution. If the loss is intended to estimate a probability or a full-softmax objective, sampled examples may require importance or log-sampling-probability correction, such as subtracting $\log q(i)$ from sampled logits in sampled-softmax-style objectives. Second, **selection/exposure bias**: the logs themselves reflect what the previous policy chose to show. Sampling correction alone does not remove this causal bias.

A **false negative** is an item sampled as negative even though the user would consider it relevant. An **accidental positive** is the common in-batch form: another row's positive is valid for the current user/query too. I mitigate these with duplicate-positive masking, multi-positive labels, history or impression checks, semantic/graph-based filters, teacher confidence, or down-weighting uncertain negatives rather than asserting a hard zero label.

Operationally, I validate the sampler, not just the final model. I log the realized negative distribution by popularity, source, rank, exposure status, and segment; measure false-negative proxies; compare uniform/popularity/in-batch/hard mixtures; and evaluate downstream Recall@k/NDCG plus calibration if scores are used probabilistically. I also ablate the sampler while keeping model architecture fixed.

The Staff-level principle is: **the best negatives are informative, plausible competitors drawn in a way that approximates the serving problem without turning unlabeled relevance into false supervision**. As retrieval quality improves, I normally move from broad/easy negatives toward a controlled mixture of in-batch and mined hard or semi-hard negatives, with explicit masking/correction and monitoring for distribution drift.

## Learn the Concepts

### Foundation

A recommender rarely has a clean dataset containing, for every user, a label for every item. Suppose a catalog has one million items and user $u$ purchased item $i^+$. We know $i^+$ is positive evidence. We do **not** know that the other 999,999 items are negatives: most were never shown, many were never examined, and some could also be relevant.

A training algorithm still needs comparisons. Negative sampling constructs a manageable subset of items that the model treats as competitors to the positive.

A useful mental model is:

> positive item + sampled competitors → learning signal about what should outrank what

Let a retrieval model assign a score $s(u,i)$. A simple sampled-softmax-style loss for one positive and a sampled set $N$ is

$$
L = -\log \frac{\exp(s(u,i^+))}
{\exp(s(u,i^+))+\sum_{j\in N}\exp(s(u,j))}.
$$

The gradient pushes $s(u,i^+)$ upward relative to the sampled competitors. If the sampled competitors are all absurdly irrelevant, the model quickly separates them and learns little. If the competitors are useful but mislabeled relevant items, the model receives destructive supervision. Negative sampling is therefore a signal-quality problem.

**Uniform sampling.** Every item has equal sampling probability. This gives broad catalog coverage and low implementation complexity. Its main weakness is that a large catalog contains many obvious negatives.

**Popularity-weighted sampling.** Sample item $i$ with probability related to its empirical frequency, for example $q(i)\propto f_i^\alpha$. This creates more realistic competition with head items and can reduce the number of useless negatives. But the sampler itself now reflects popularity, which can bias training toward suppressing head items or underrepresenting tail geometry.

**In-batch negatives.** With a batch of positive pairs $(u_b,i_b^+)$, each $i_{b'}^+$ can serve as a negative for $u_b$ when $b'\neq b$. A batch of size $B$ gives roughly $B-1$ negatives per example almost for free because the item embeddings are already computed. This is why large batches are attractive in two-tower contrastive training.

**Hard negatives.** A hard negative has a high model score but is not labeled positive. It is informative because it lies near the current boundary. Common mining sources are the current ANN index, a lexical/co-visitation retriever, or a stronger teacher.

**Semi-hard negatives.** These are plausible but not maximally confusing. They avoid wasting most training mass on trivial examples while reducing the false-negative/noise risk of the absolute hardest examples.

**Exposure-aware negatives.** If impression logs exist, distinguish:
- unexposed item;
- exposed but not clicked/consumed;
- exposed and positively interacted with.

An exposed-but-ignored item is usually stronger negative evidence than an arbitrary unexposed item, although even non-click can reflect position, examination, UI, or context rather than dislike.

**Teacher-mined negatives.** A high-capacity cross-encoder, mature ranker, or other teacher identifies items that are semantically close or highly competitive. These can be excellent training examples for a cheaper student retriever, but teacher errors and biases become part of the student's training distribution.

**False negative.** A sampled item receives negative treatment even though it is actually relevant.

**Accidental positive.** In in-batch training, another example's positive may also be positive for the current example. For instance, two users in the same household may both legitimately purchase the same printer cartridge, or two near-duplicate queries may have the same relevant product.

**Worked example.** Suppose a user clicked running shoe A. From a one-million-item catalog:
- a random refrigerator is a uniform but trivial negative;
- a best-selling running shoe B is a popularity-weighted negative;
- another user's clicked running shoe C in the same batch is an in-batch negative;
- shoe D retrieved at rank 2 by the current model but not clicked is a hard negative;
- a moderately similar shoe E at rank 40 could be semi-hard;
- shoe F was actually shown above A and ignored, so it is an exposure-aware negative;
- shoe G is selected by a strong cross-encoder as highly confusable, so it is teacher-mined.

The dangerous case is that shoe D or G may have been perfectly relevant but never exposed. Treating it as a definite negative would teach the model to suppress a good result.

Important distinctions:
- **unobserved is not negative**;
- **hard is not necessarily correct**;
- **sampled distribution is not automatically deployment distribution**;
- **sampling correction is not the same as causal debiasing**;
- **ranking quality and calibrated probability semantics are different goals**.

### Core Interview Reasoning

A strong interview reasoning sequence is:

**deployment candidate distribution → label semantics → sampler family → bias/noise controls → correction → validation**

1. **Start with the serving problem.**  
   Ask what items compete at inference. A first-stage retriever over a huge catalog has a different negative distribution from a heavy ranker operating on 500 retrieved candidates. The training sampler should support the stage's actual discrimination task.

2. **Define what "negative" means.**  
   In implicit-feedback systems, absence of interaction is usually missing data, not a clean zero. Exposure logs materially strengthen label semantics. Delayed conversion, repeat impressions, user history, and multiple positives complicate binary labels.

3. **Choose a difficulty spectrum rather than one magical sampler.**  
   Easy/broad negatives establish global separation and coverage. Harder negatives refine local boundaries. Industrial systems often use mixtures because each sampler has different failure modes.

4. **Control false negatives.**  
   Before increasing hardness, add masking or uncertainty handling:
   - do not sample known positives;
   - mask duplicate positives in a batch;
   - use multi-positive objectives where appropriate;
   - exclude recent historical positives;
   - use impression/context evidence;
   - avoid top teacher candidates when teacher confidence implies likely relevance;
   - down-weight uncertain negatives.

5. **Correct when the objective requires it.**  
   If items are sampled from $q(i)$ rather than the population distribution, the uncorrected loss optimizes the sampled task. For sampled-softmax-like objectives, a standard correction adjusts the sampled logit using the sampling probability:
   $$
   \tilde{s}(u,i)=s(u,i)-\log q(i).
   $$
   This compensates for items appearing more frequently solely because the sampler chose them more frequently. The exact correction depends on the loss and sampling procedure.

6. **Validate the sampler directly.**  
   Measure realized sampling distributions, hardness, false-negative proxies, and downstream metrics. Do not compare only training loss because a sampler can make the objective harder while producing a better model, or easier while producing a worse one.

Trade-offs:
- more hardness → better local discrimination, but more label noise;
- larger in-batch sets → better efficiency, but more accidental positives and batch-distribution dependence;
- popularity weighting → more realistic head competition, but stronger popularity distortion;
- exposure-aware labels → stronger supervision, but inherit logging-policy and examination bias;
- teacher mining → high-quality competitors, but extra compute and teacher dependence.

Meaningful edge cases include:
- multiple positives for the same user/query;
- duplicates or near-duplicates;
- rapidly changing catalogs;
- long-tail items that rarely appear in mined sets;
- delayed labels;
- repeated exposures;
- retriever changes that shift what counts as "hard";
- a sampler that is correct on average but poor for new users or tail segments.

### Deeper Reasoning and Derivations

Negative sampling changes the empirical objective because the expectation is taken under the sampling distribution. Suppose the desired negative expectation is under a target distribution $p(i)$, but negatives are drawn from $q(i)$. For some per-negative quantity $g(i)$,

$$
\mathbb{E}_{i\sim p}[g(i)]
=
\mathbb{E}_{i\sim q}\left[\frac{p(i)}{q(i)}g(i)\right],
$$

provided $q(i)>0$ wherever $p(i)>0$. This is the basic importance-sampling identity. It explains why nonuniform sampling can require weights or log-probability corrections if the estimator is meant to represent the original target distribution.

However, modern contrastive objectives are not always trying to estimate an unbiased full-catalog probability. Sometimes the sampled objective is intentionally chosen because it emphasizes a useful decision boundary. In that case "bias" is not automatically bad; the key question is whether the biased training task aligns with serving.

For in-batch negatives, let the batch be drawn from a data distribution whose item marginal is $q_{\text{batch}}(i)$. Then the negative distribution is approximately that marginal, not uniform over items. Popular items appear more often because they appear as positives more often. This is one reason in-batch negatives can implicitly act like popularity sampling.

In two-tower retrieval, a common corrected logit has the form

$$
\ell(u,i)=\frac{u^\top v_i}{\tau}-\log q(i),
$$

where $\tau$ is a temperature and $q(i)$ approximates the probability that item $i$ is sampled as a negative. The correction reduces the artificial advantage/disadvantage caused by sampling frequency. If $q(i)$ is poorly estimated, stale, or mismatched to the actual batching/mining process, the correction can itself be wrong.

**Why hard-negative mining can collapse.** Consider a model that retrieves its top non-labeled candidates. Early in training, high-scoring candidates may be high because of representation errors. Later, high-scoring candidates increasingly include genuinely relevant alternatives. Therefore hardness and false-negative rate can rise together. If every mined item near the positive is forced downward, the model can destroy useful semantic neighborhoods. A mixture with easier negatives, positive filtering, or semi-hard selection often stabilizes training.

**Hard-negative curriculum.** One practical progression is:
1. broad uniform/popularity negatives;
2. large in-batch negatives;
3. mined negatives from a reasonably trained retriever;
4. refreshed mining as the model evolves;
5. controlled teacher mining or cross-model mining.

This is not a universal schedule, but it follows the principle that the model must first possess enough structure for "hardness" to be meaningful.

**Exposure-conditioned semantics.** Suppose $E$ means exposed and $Y$ means interaction. Observing $Y=0$ without knowing $E$ mixes two cases:
- $E=0$: user had no opportunity to interact;
- $E=1,Y=0$: user had an opportunity but did not interact.

The second provides more evidence against relevance, but still depends on examination and position. Thus exposure-aware negative sampling improves semantic validity without fully solving policy bias.

**False-negative impact.** For a pairwise loss such as
$$
L=-\log \sigma(s(u,i^+)-s(u,i^-)),
$$
if $i^-$ is actually relevant, the gradient explicitly forces $s(u,i^+)>s(u,i^-)$ even though the desired ordering may allow both to score highly. With many such errors, the representation can fragment semantically coherent regions and hurt Recall@k.

**Sampler evaluation should be stage-aware.** For retrieval, emphasize candidate Recall@k, hit rate, tail coverage, and ANN interaction. For ranking, emphasize NDCG/MRR/conversion-oriented metrics and calibration if probabilities are consumed downstream. The same negative scheme need not be optimal for both stages.

### Advanced Staff-Depth Considerations

#### 1. Changed Constraints and Transfer Logic

**Baseline.** A two-tower retriever for a large catalog uses in-batch negatives plus a small mined-hard-negative pool, duplicate-positive masking, and measured logQ correction.

**If the catalog grows 100×:** uniform negatives become even more dominated by trivial items. Increase efficient broad coverage through larger in-batch/cross-batch pools, then mine candidates from the serving index. Validate that tail items remain represented rather than allowing popularity and mining loops to erase them.

**If exposure logs become available:** stop treating arbitrary non-interactions as equivalent. Use exposed-but-ignored examples more heavily, preserve unexposed examples as weak or unlabeled data, and account for position/examination effects when interpreting non-clicks.

**If labels are delayed:** avoid mining recent "non-converters" as hard negatives before the attribution window closes. Use censoring logic or delayed-label-safe windows. Otherwise the hardest recent items may simply be pending positives.

**If latency forces a smaller candidate set:** the retriever's local ordering quality becomes more important because downstream rankers have less room to recover. Mine more serving-like competitors and evaluate Recall at the reduced candidate budget, not only at a generous $k$.

**If privacy constraints remove user history:** false-negative filters based on historical positives weaken. Shift toward contextual/exposure evidence, item semantics, aggregate signals, and conservative uncertainty handling.

The invariant is that the sampler should produce informative competitors while preserving valid label semantics. What changes is the best proxy for the serving candidate distribution and the available evidence for whether an item is truly negative.

#### 2. Failure Modes and Diagnosis

**Symptom: training loss improves, retrieval Recall@100 falls.**
Competing hypotheses:
- hard negatives contain many false negatives;
- popularity weighting over-suppresses head items;
- logQ correction is wrong;
- mining index is stale or from a mismatched model;
- duplicate positives are not masked.

Discriminating evidence:
- slice sampled negatives by known-positive overlap and semantic similarity;
- compare exact scores before/after sampler change;
- inspect realized $q(i)$ and correction values;
- rerun with fixed architecture and previous sampler;
- measure Recall by popularity and user-history segment.

Immediate mitigation: revert to the last known-good sampler or reduce hard-negative weight.  
Permanent prevention: sampler dashboards, mined-set versioning, false-negative tests, controlled ablations, and rollout gates.

**Symptom: aggregate Recall improves but tail-item exposure collapses.**
Hypothesis: popularity/in-batch distributions dominate training. Check negative and positive marginals by popularity decile, candidate-source recall, and long-tail slices. Correct by mixing samplers, stratifying, capping head-item negative frequency, or using segment-aware objectives where product goals require it.

**Symptom: performance degrades only after several mining rounds.**
Hypothesis: iterative hard-negative mining has become self-reinforcing. The model mines its own blind spots or increasingly mines unlabeled positives. Compare mining rounds, overlap, hardness histograms, label confidence, and embedding-neighborhood purity.

#### 3. Latency and Resource Trade-offs

Negative sampling is primarily a training concern, but it changes serving economics indirectly. Better negatives can improve retrieval quality at fixed embedding dimension and candidate count, potentially avoiding a larger model or larger ANN probe budget.

Resource costs include:
- item-embedding computation for negative sets;
- all-gather/network cost for cross-device in-batch negatives;
- ANN retrieval for mined negatives;
- teacher inference for teacher-mined negatives;
- storage and refresh of mined-negative datasets;
- extra masking/deduplication metadata.

For a local batch size $B$ across $G$ workers, cross-device in-batch negatives can expose roughly $BG-1$ competitors per example but may require all-gathering embeddings. If embeddings are dimension $d$ in $b$ bytes per coordinate, one gathered item-embedding tensor is on the order of $BGdb$ bytes per step per participating worker, ignoring framework overhead. At large scale, communication rather than dot products can dominate.

A Staff answer should compare marginal quality per unit training cost, not maximize negative count blindly.

#### 4. Scale and Capacity

At very large item counts:
- exact full-softmax becomes infeasible;
- mining infrastructure must itself be scalable;
- stale mined negatives become a serious lifecycle issue;
- duplicate/near-duplicate detection may need approximate structures;
- long-tail support can disappear because mining repeatedly samples head competition.

Capacity planning should estimate:
- positives per training window;
- negatives per positive;
- storage footprint of materialized mined sets;
- refresh frequency;
- ANN mining QPS;
- teacher scoring throughput;
- cross-device communication.

If 1 billion positive examples each store 50 negative item IDs as 64-bit integers, IDs alone require about
$$
10^9 \times 50 \times 8 \approx 400\text{ GB},
$$
before metadata, compression, or replicas. This can motivate online or partially materialized mining rather than storing every negative set.

#### 5. Freshness, State, and Versioning

A mined negative is stateful: it was produced by a specific model, embedding space, item corpus, index, filters, and timestamp.

Track at least:
- mining model version;
- item-embedding/index version;
- catalog snapshot;
- feature/data window;
- sampler configuration;
- teacher version if used.

If the query tower changes while the mining index remains old, "hardness" is no longer measured in the current representation space. If the catalog changes rapidly, deleted or unavailable items can contaminate training. If a teacher is updated, negative difficulty may jump abruptly.

Safe practice includes immutable versioned mining jobs, explicit compatibility checks, sample-level provenance, and rollback to a known sampler/index tuple.

#### 6. Implementation, Serving, and Observability

Implementation should make the sampler an explicit, testable component rather than buried in the dataloader.

Useful interfaces expose:
- sampler type and mixture weights;
- random seed/version;
- exclusion sets;
- exposure constraints;
- hardness source;
- $q(i)$ or enough information to compute correction;
- provenance/version metadata.

Tests should cover:
- positives are never sampled as hard negatives when known;
- duplicate positives in a batch are masked;
- sampling frequencies match configured distributions statistically;
- zero-probability support bugs are detected;
- deleted/unavailable items are excluded;
- delayed-positive windows are respected;
- correction terms match the actual sampler.

Observability should include:
- negative source mix;
- item-popularity deciles;
- score/hardness quantiles;
- false-negative proxy rate;
- duplicate-positive mask rate;
- sampler entropy/coverage;
- per-segment sample composition;
- mining freshness/version skew;
- downstream retrieval/ranking metrics by slice.

Serving does not execute the sampler, but serving candidate logs should feed sampler validation because deployment candidates define the distribution that training is supposed to prepare for.

#### 7. Vertical Transfer

**E-commerce.** Purchases are sparse and delayed; exposure and availability matter. A non-purchase of an unavailable or never-shown item is meaningless. Hard negatives from substitute products can be useful, but complements may be relevant rather than negatives.

**Video/feed.** Multiple items can be relevant in the same session. Dwell/completion/skip semantics are richer than click/non-click. In-batch negatives from globally popular videos create many accidental positives.

**Ads.** Exposure is explicit, but auction policy strongly selects which ads are shown. Non-clicks are observed under position, price, budget, and eligibility constraints. Sampling must preserve auction-relevant competition and should not be mistaken for causal debiasing.

**Marketplace.** Provider exposure and inventory constraints matter. Popularity-weighted negatives can amplify concentration. Evaluate both consumer relevance and supply/provider slices.

**Notifications.** The candidate universe is small and highly policy-filtered. Overly broad catalog negatives may be irrelevant to the decision actually made at send time; use decision-set or eligibility-aware negatives.

Across verticals, the invariant is to model the actual choice set and observation process before defining a negative.

#### 8. Objective and Metric Mismatch

A sampler can improve the sampled training objective while hurting the product objective.

Examples:
- hard-negative training improves pairwise separation but decreases catalog coverage;
- popularity negatives improve head-query Recall but harm tail discovery;
- exposure-aware negatives improve click prediction but still inherit position bias;
- teacher mining improves NDCG but produces poorly calibrated scores;
- aggressive false-negative filtering improves semantic neighborhoods but removes useful discrimination among close substitutes.

Therefore evaluate a chain of metrics:
1. sampler diagnostics;
2. training objective;
3. stage metric such as Recall@k or NDCG;
4. slice metrics such as tail/new-user/locale;
5. score semantics/calibration if consumed downstream;
6. online product metrics.

If offline ranking improves while online utility drops, investigate whether the sampler changed the learned notion of relevance, coverage, diversity, or exposure rather than assuming serving is at fault.

## Material Follow-ups / Scenario Variants

### Why can in-batch negatives be both efficient and biased?

They reuse embeddings already computed for other positives, so the marginal cost per negative is low and a batch of size $B$ creates roughly $B-1$ competitors per example. But those negatives are distributed according to the batch's positive-item marginal, not necessarily the serving candidate distribution. Popular items can be overrepresented, and legitimate shared positives become accidental negatives. Use representative batching, duplicate/multi-positive masking, optional sampling correction, and validation against the actual serving candidate distribution.

### When would you prefer hard negatives over uniform negatives?

Prefer hard negatives once the model has enough quality that its high-scoring errors are meaningful and the label pipeline can control false negatives. They are especially valuable when serving must discriminate among semantically similar candidates. Keep some broad negatives for global geometry/coverage, use semi-hard examples when the hardest set is noisy, and verify gains with fixed-model sampler ablations.

### Does subtracting $\log q(i)$ solve exposure bias?

No. A log-sampling-probability correction addresses distortion introduced because the training sampler draws items with unequal probability. Exposure bias is upstream: the historical policy determined what users had a chance to interact with. Correcting $q(i)$ does not make unexposed items observed counterfactual outcomes. Exposure/position/policy bias needs appropriate logging, experimental data, propensity/counterfactual methods, or other causal assumptions.

### A harder-negative rollout improves offline Recall@100 but online CTR falls. What do you check?

First verify that the offline gain is real by reproducing it with a fixed evaluation set and exact candidate semantics. Then inspect whether false negatives increased, whether head/tail and new-user slices shifted, whether the training sampler no longer matches serving candidates, and whether score calibration or downstream thresholds changed. Also rule out serving-version skew. If candidate recall improved but CTR fell, the model may be retrieving more technically relevant but less click-worthy/diverse/fresh items, so examine downstream ranker interaction and product-objective mismatch rather than attributing the issue solely to retrieval quality.

### How should negative sampling change as a retriever matures?

Early training can rely more on broad uniform/popularity/in-batch negatives to establish coarse geometry. As quality improves, introduce serving-like hard or semi-hard negatives, refresh them periodically, and increase filtering/masking because false-negative risk rises with semantic quality. Keep a mixture rather than converging to only the hardest examples, and continuously validate the realized sampler distribution against current serving traffic.
