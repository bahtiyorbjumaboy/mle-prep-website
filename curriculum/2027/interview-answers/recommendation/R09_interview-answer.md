---
type: interview-answer
item: "2027:R09"
title: "Negative Sampling and False Negatives"
created: "2026-10-04"
updated: "2026-10-05"
tags:
  - recommendation
  - negative-sampling
  - retrieval
  - contrastive-learning
  - sampling-bias
---

## Canonical Staff-Depth Question

Compare uniform, popularity-weighted, in-batch, hard, semi-hard, exposure-aware, and teacher-mined negatives. Explain sampling bias, accidental positives, false negatives, and correction.

## Mastery Answer

Negative sampling is a computational and statistical design choice: instead of contrasting each positive interaction against the full item catalog, training contrasts it against a sampled subset. The sampler therefore determines which distinctions the model is trained to make and, unless corrected, changes the effective training distribution.

I would choose a sampler by first defining the deployment comparison set. Uniform negatives give broad catalog coverage and are cheap, but spend many updates on obviously irrelevant items. Popularity-weighted negatives better reflect frequently competing items and create harder comparisons, but can over-train against head items and hurt tail representation. In-batch negatives are very efficient because other examples' positives are reused as negatives, but their distribution is whatever the batch construction induces; popular items are often overrepresented, and another user's true positive can be a false negative. Hard negatives, such as top-scoring non-positives from the current retriever, are informative but can become dominated by mislabeled positives or near-duplicates. Semi-hard negatives keep informativeness while avoiding the most ambiguous examples. Exposure-aware negatives restrict or emphasize items the user actually had a chance to interact with, which makes "ignored" items more defensible negatives, but changes the target toward the logging policy's exposure distribution. Teacher-mined negatives use a stronger model to find confusable items and can accelerate learning, at the cost of teacher bias, mining freshness, and extra infrastructure.

The central failure mode is treating "not observed positive" as "negative." In implicit-feedback systems, many unclicked or unpurchased items were never exposed, and some sampled negatives are latent positives. Accidental positives and false negatives create contradictory gradients: the objective pushes semantically or behaviorally relevant items away from the query/user. Typical mitigation is to mask known positives, deduplicate equivalent items, respect temporal interaction history, use exposure information when available, downweight or exclude suspicious hard negatives, and refresh mined negatives as the model changes.

Sampling also creates bias. If negatives are drawn from proposal distribution $q(i)$ rather than the distribution implied by the full-catalog objective or serving competition, the sampled loss optimizes a reweighted problem. When the desired objective is a full softmax or another known target distribution, one can apply proposal correction such as subtracting $\log q(i)$ from sampled logits or using importance weights, subject to variance and support constraints. Correction is not automatic: the appropriate method depends on the loss and what distribution the deployed system should rank against.

I would not select a sampler from training loss alone. I would compare sampler variants using full-catalog or serving-faithful retrieval evaluation, head/mid/tail and cold-item slices, candidate Recall@k, false-negative audits, realized negative-frequency diagnostics, and stability across refreshes. Under extreme popularity skew I would usually mix sources—for example some uniform coverage, some popularity- or exposure-aware negatives, and a controlled fraction of semi-hard or teacher-mined examples—then tune the mixture against deployment metrics rather than assuming the hardest sampler is best.

## Learn the Concepts

### Foundation

#### Central mental model

A recommender often learns from positive events such as clicks, watches, carts, or purchases. Suppose a user clicked item $A$. The training system needs examples that teach:

> "Score $A$ above other items that could plausibly compete with it."

The catalog may contain millions of items. Comparing $A$ against every other item on every training step is often too expensive. **Negative sampling** chooses a smaller set of comparison items.

A useful mental model is:

**A negative sampler chooses the questions the model practices answering.**

If training repeatedly asks easy questions such as "Should this running-shoe shopper prefer the clicked shoe or a random industrial bolt?", the model may learn little about fine ranking. If training asks only extremely hard questions such as near-identical shoes, some of those "negatives" may actually be products the user would happily buy, so the labels become wrong.

The goal is therefore not "find the hardest negatives." The goal is:

$$
\text{informative comparisons}
\quad+\quad
\text{reasonable label validity}
\quad+\quad
\text{distributional match to deployment}.
$$

#### Minimum terminology

**Positive:** an observed item treated as relevant for the training objective, such as a clicked or purchased item.

**Negative:** an item used as the contrasting class/example for that training event.

**Implicit feedback:** behavior such as clicks or watches where absence of interaction does not prove dislike.

**Exposure:** whether the user was actually shown or otherwise had a realistic chance to interact with an item.

**False negative:** an item labeled or sampled as negative even though it is actually relevant to the user/query.

**Accidental positive:** a sampled "negative" that is known to be positive under another observation or equivalence rule, such as another item the same user clicked or a duplicate product.

**Hard negative:** a non-positive item the model currently scores highly or finds very similar to the positive.

**Semi-hard negative:** an informative but not maximally ambiguous negative; it is closer to the decision boundary without being the most likely mislabeled example.

**Proposal distribution $q(i)$:** the probability distribution used to sample item $i$ as a negative.

**Sampling bias:** the training problem changes because sampled negatives occur with a different frequency from the comparison population one ultimately cares about.

#### The sampler families

**Uniform sampling.** Every eligible catalog item has roughly equal probability of being sampled.

- Strength: broad coverage, simple, cheap.
- Weakness: with a huge catalog, many negatives are trivial.
- Typical effect: good global separation, weak pressure on realistic competitors.

**Popularity-weighted sampling.** Frequently interacted-with items are sampled more often.

- Strength: head items really do compete often at serving time; negatives are usually more informative.
- Weakness: amplifies head-item dominance and may undertrain tail discrimination.
- Variant: use a tempered distribution such as $q(i)\propto f_i^\alpha$ with $0<\alpha<1$ instead of raw popularity.

**In-batch negatives.** In a batch of positive pairs $(u_1,i_1),\dots,(u_B,i_B)$, item $i_j$ is reused as a negative for user $u_k$ when $j\neq k$.

- Strength: almost free additional negatives; matrix multiplication makes training efficient.
- Weakness: the negative distribution inherits the batch's sampling distribution.
- Risk: another row's positive may also be relevant to the current user.

**Hard negatives.** Retrieve items that the current model scores highly but that are not labeled positive.

- Strength: forces the model to distinguish confusing items.
- Weakness: the hardest items have the highest chance of being unlabeled positives, substitutes, duplicates, or annotation errors.
- Operational issue: mining must be refreshed because "hard" changes as the model changes.

**Semi-hard negatives.** Select negatives that are more confusing than random negatives but avoid the very highest-scoring ambiguous cases.

- Strength: often a better information-versus-label-noise trade-off.
- Weakness: requires a policy for what counts as "semi-hard."

**Exposure-aware negatives.** Prefer items that were actually shown to the user but not engaged with, or condition the negative definition on exposure.

- Strength: "shown and ignored" is generally a stronger negative signal than "never shown."
- Weakness: the logging policy determines what was exposed, so the model can inherit historical exposure bias.
- Important distinction: exposure-aware does not mean unbiased; it means the negative label has a more defensible behavioral interpretation.

**Teacher-mined negatives.** Use a stronger model, cross-encoder, production ranker, or ensemble to identify confusing candidates for a cheaper student/retriever.

- Strength: high-information examples can improve a weaker model efficiently.
- Weakness: teacher errors and preferences are transferred; mining adds compute and versioning complexity.

#### Concrete worked example

Assume a user purchased a trail-running shoe, and a training step needs four negatives from a catalog of one million products.

A uniform sampler might return:

- frying pan,
- phone case,
- office chair,
- children's puzzle.

All four may be valid negatives, but they are very easy.

A popularity-weighted sampler might return:

- bestselling road shoe,
- popular sneaker,
- hiking boot,
- another popular trail shoe.

These are more realistic competitors, but repeated use of popular products can cause the training distribution to be dominated by head items.

A hard-negative miner might return:

- same shoe in another color,
- previous version of the same shoe,
- competing trail shoe,
- duplicate marketplace listing.

These are highly informative, but the first, second, and fourth may actually be desirable to the user. Treating all of them as definite negatives creates false-negative gradients.

An exposure-aware sampler may use products that were shown on the same recommendation surface but skipped. Those labels are behaviorally stronger, but they reflect what the old recommender chose to expose.

A robust design might mix:

- one uniform negative for catalog coverage,
- one popularity-weighted or exposure-aware negative for realistic competition,
- two semi-hard mined negatives for decision-boundary learning,

while masking known purchases/clicks and duplicate-equivalent products.

### Core Interview Reasoning

A compact reasoning structure for R09 is:

**1. State why sampling exists.**  
The full candidate universe is too large, so training approximates the comparison problem with sampled items.

**2. Compare samplers by three axes.**

- **informativeness:** does the negative produce useful gradient?
- **label validity:** how likely is the "negative" actually relevant?
- **distribution match:** does training resemble the candidate competition seen at deployment?

**3. Explain the bias/noise mechanisms.**

- non-interaction is not necessarily a negative;
- the sampling proposal $q(i)$ reweights item frequency;
- hard/in-batch sampling can create false negatives;
- exposure data itself is policy-biased.

**4. Explain mitigation/correction.**

- masks and deduplication;
- temporal positive-history checks;
- semi-hardness or confidence weighting;
- proposal-distribution correction where mathematically appropriate;
- mixtures of samplers;
- regular negative-pool refresh.

**5. Validate against deployment.**

Use serving-faithful or full-catalog metrics and slices, not sampled training loss alone.

This structure works because it moves from **objective → sampler mechanism → induced bias/noise → correction → validation**.

#### Why each sampler changes the gradient

Suppose a two-tower model gives a score

$$
s(u,i)=z_u^\top z_i.
$$

For one positive item $i^+$ and sampled negative set $N$, a common contrastive loss is

$$
L
=
-\log
\frac{\exp(s(u,i^+)/\tau)}
{\exp(s(u,i^+)/\tau)+\sum_{j\in N}\exp(s(u,j)/\tau)}.
$$

A negative with very low score contributes little to the denominator and therefore little gradient. A high-scoring negative contributes much more. This is why hard negatives can be sample-efficient.

But if that high-scoring item is actually relevant, the same large gradient becomes harmful: training strongly pushes apart a pair that should perhaps remain close.

This produces the fundamental hard-negative trade-off:

$$
\text{more informative}
\Longleftrightarrow
\text{often more ambiguous}.
$$

#### Why in-batch negatives are efficient

With batch size $B$, compute user embeddings and item embeddings once:

$$
U\in\mathbb{R}^{B\times d},
\qquad
V\in\mathbb{R}^{B\times d}.
$$

Then

$$
S=UV^\top
$$

produces all $B^2$ pair scores. The diagonal contains the intended positive pairs, while off-diagonal entries can serve as negatives.

This converts one positive per row into roughly $B-1$ cheaply available negatives. The caveat is that these are sampled according to how positive items enter the batch, not uniformly from the catalog.

#### Why popularity weighting can help and hurt

If item $i$ appears with frequency $f_i$, a popularity sampler might use

$$
q(i)\propto f_i^\alpha.
$$

When $\alpha=0$, this becomes uniform. Larger $\alpha$ increasingly favors popular items.

Benefits:

- popular items are plausible competitors;
- more sampled negatives have nontrivial scores;
- head-item discrimination improves.

Risks:

- tail items receive little negative-side training;
- the effective prior can become even more popularity-heavy than serving requires;
- the model may learn overly strong repulsion from popular items or weak geometry in the tail.

A tempered $\alpha$ or mixture sampler is often preferable to an extreme.

#### Sampling bias versus false-negative noise

These are different problems.

**Sampling bias:** a truly negative item is sampled too often or too rarely relative to the target comparison distribution.

**False-negative noise:** the item should not have been labeled negative in the first place.

Importance weighting can address certain forms of sampling bias. It cannot magically repair a wrong label. A mislabeled positive with a very large importance weight can be even more damaging.

### Deeper Reasoning and Derivations

#### Full-softmax target versus sampled objective

Suppose the intended conditional model is

$$
p(i\mid u)
=
\frac{\exp(s(u,i))}
{\sum_{j\in\mathcal I}\exp(s(u,j))}.
$$

The denominator over all items $\mathcal I$ may be too expensive. Sampled objectives approximate it using negatives drawn from $q(j)$.

If frequent proposal items are included without correction, the learner sees them disproportionately often. For sampled-softmax-style objectives, a common correction adjusts a sampled logit by its proposal probability:

$$
\tilde s(u,j)=s(u,j)-\log q(j),
$$

with exact details depending on the estimator and sampling scheme.

The intuition is that an item should not look more competitive merely because the sampler selected it frequently.

This correction requires:

- $q(j)$ to be known or estimable;
- the target objective to justify the correction;
- sufficient support: items relevant to the target cannot have zero sampling probability;
- manageable variance.

If $q(j)$ is tiny, importance-style factors can become unstable. Clipping or a mixture with uniform sampling can trade some bias for lower variance.

#### False-negative mechanism

Assume user $u$ has latent relevant set $R_u$, but logs reveal only observed positive subset $O_u\subset R_u$.

Naive sampling draws from

$$
\mathcal I\setminus O_u.
$$

A sampled item can still lie in

$$
R_u\setminus O_u,
$$

which is a false negative.

This set can be large when:

- exposure is sparse;
- conversion is delayed;
- users interact with substitutes but only one purchase is observed;
- item duplicates/variants exist;
- labels are censored by time;
- the surface historically showed only a narrow subset of the catalog.

The key point is epistemic: "not observed positive" means **unknown**, not necessarily negative.

#### Why harder mining raises false-negative risk

A model's high-scoring candidates are often close to the positive in semantic or behavioral space. That is exactly why they are useful training examples, but closeness is also evidence that they may genuinely satisfy the user.

Therefore the probability

$$
P(\text{false negative}\mid \text{very hard candidate})
$$

can be substantially higher than

$$
P(\text{false negative}\mid \text{uniform random candidate}).
$$

Hard-negative mining should therefore be paired with filtering, confidence controls, deduplication, or semi-hard bands.

#### Exposure-aware reasoning

Suppose item $j$ was never shown. The event "no click on $j$" contains almost no preference information because the user had no opportunity to click.

If item $j$ was shown in a visible position and ignored, the non-click carries more information. But even then, position, UI, trust, context, and competition affect examination.

So an exposure-aware negative is better interpreted as:

> "This item was available under the logging policy and did not receive the target action."

It is not equivalent to:

> "The user dislikes this item."

This distinction matters when transferring the model to a new exposure policy.

#### Diagnosing a bad sampler

Common symptoms and hypotheses:

**Training loss improves, full-catalog Recall@k worsens.**
- sampled task has become too easy or too distribution-specific;
- correction is wrong or absent;
- mined negatives are stale.

**Head recall improves, tail recall falls.**
- popularity-weighted negatives dominate;
- batch construction overrepresents head items;
- insufficient uniform/tail coverage.

**Embedding neighborhoods lose obvious substitutes.**
- false negatives are repelling semantically valid alternatives;
- hard-negative miner is too aggressive.

**Performance jumps on sampled evaluation but not production-like evaluation.**
- evaluation uses the same biased negative sampler as training;
- sampled metrics do not reflect full-catalog competition.

**Hard-negative training becomes unstable after several epochs.**
- negatives became stale as the retriever changed;
- hardest examples are increasingly false negatives;
- teacher/current-model score scale changed.

### Advanced Staff-Depth Considerations

The reusable Staff-level backbone for this item is:

`Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate`

Equivalently:

`Assumption → Mechanism → Evidence → Decision → Trade-off → Validation`

For this question, the baseline is: The baseline is that the negative sampler defines the comparisons the model practices. Good sampling balances informativeness, label validity, and match to the deployment comparison distribution. Sampling bias and false-negative noise are distinct: reweighting can correct some proposal bias, but no importance weight can make a mislabeled positive into a true negative.

The eight subsections below apply that same loop from different angles. Each explanation teaches the mechanism first; the filled template then compresses it into a reusable interview scaffold.

#### 1. Changed Constraints and Transfer Logic

As catalog size, popularity skew, exposure sparsity, or churn changes, the sampler mixture should change rather than defaulting to “harder.” Huge catalogs make uniform negatives easier; skew can let head items dominate; sparse exposure weakens exposure-aware coverage; fast-changing catalogs stale mined pools. Preserve broad support and defensible labels.

A useful reasoning chain is:

`changed assumption → affected mechanism/stage → invariant → broken assumption → consequence → redesign → metric impact → trade-off → validation`

**Filled template for this item**

- **Original assumption:** Current mix of uniform/in-batch/mined negatives gives useful coverage and hardness.
- **Changed constraint:** Popularity becomes extremely skewed and catalog grows sharply.
- **Invariant:** Training should preserve informative comparisons across the serving universe without systematic false-negative or tail collapse.
- **Broken assumption:** Raw popularity/in-batch frequency no longer approximates a healthy competition distribution.
- **Consequence:** Head items dominate the denominator while tail geometry receives weak coverage; false negatives can rise for popular items.
- **Design change:** Temper popularity, stratify head/mid/tail, mix uniform/exposure/semi-hard sources, and mask known positives/equivalents.
- **Metric impact:** Track realized negative frequency, false-negative audits, head/mid/tail Recall@K, norm/score distributions, and full-catalog quality.
- **Trade-off:** More balanced coverage can reduce average hardness/sample efficiency.
- **Validation:** Compare sampler mixtures on deployment-faithful retrieval and tail/cold slices, not sampled training loss alone.

#### 2. Failure Modes and Diagnosis

Sampler regressions often masquerade as representation or ANN failures. Diagnose the realized training distribution and false-negative rate, then isolate serving infrastructure. A tail-only recall loss after popularity-heavy sampling points toward training distribution only if exact retrieval also shows it and ANN/index controls are healthy.

**Filled template for this item**

- **Symptom:** Head recall improves but tail recall drops after switching to popularity-heavy/in-batch negatives.
- **Stage decomposition:** batch/data sampling → negative source/masks → loss/correction → learned embeddings → exact retrieval → ANN serving.
- **Slices:** Item popularity/head-mid-tail, user sparsity, item age, sampler source, hardness, batch frequency, model/index version.
- **Competing hypotheses:** Head-heavy proposal; missing logQ/importance correction where justified; false negatives; batch construction; ANN serving issue.
- **Discriminating evidence:** Realized q(i), per-source frequencies, known-positive mask rate, false-negative audit, exact per-bucket recall.
- **Offline/online comparison:** Use full-catalog/serving-faithful evaluation rather than sampled evaluation built from the same proposal.
- **Replay/isolation:** Train/evaluate a stable uniform/stratified baseline and compare exact retrieval before ANN.
- **First divergence:** Training/exact retrieval if tail loss exists before ANN; serving if exact is healthy.
- **Immediate mitigation:** Reduce hard/popularity fraction, restore stratified/uniform coverage, refresh pools, strengthen masks.
- **Permanent prevention:** Sampler-source logging, distribution dashboards, false-negative audits, versioned mining pools, and exact-serving regression gates.

Memory aid: `Symptom → Slice → Stage → Hypotheses → Evidence → First divergence → Fix`.

#### 3. Latency and Resource Trade-offs

Negative sampling moves cost into training rather than request serving, but hard/teacher mining can dominate training-cycle resources. In-batch negatives trade larger batches/memory for many cheap comparisons; ANN/teacher mining adds retrieval passes, storage, filtering, and refresh orchestration. Judge the sampler by quality gained per training-cycle cost and freshness burden.

**Filled template for this item**

- **Budget:** Training-step memory/throughput plus acceptable mining wall-clock and refresh cost.
- **Cost decomposition:** Sampling + extra encodes/batch matrix + ANN/teacher mining + pool storage/filtering + loss computation.
- **Dominant cost:** Periodic hard/teacher mining and large-batch memory for sophisticated samplers.
- **Quality driver:** More/harder realistic negatives improve decision-boundary learning.
- **Cost driver:** Mining many candidates/teachers and large batches increase compute, memory, and pipeline complexity.
- **Optimization knobs:** In-batch reuse, semi-hard bands, cached pools, ANN mining depth, refresh cadence, mixture fractions, stratified samplers.
- **Fallback/degradation:** Revert to stable uniform/popularity/stratified mixture if miner is unavailable or unstable.
- **Trade-off curve:** Full-catalog Recall@K/segments/false-negative rate versus training throughput, memory, and mining cost.
- **Decision:** Use the cheapest sampler mixture that materially improves deployment-like retrieval without unacceptable noise.

Memory aid: `Budget → Breakdown → Bottleneck → Knobs → Quality loss → Fallback`.

#### 4. Scale and Capacity

At 100M+ items, full-catalog comparison is impossible per step and uniform negatives become overwhelmingly easy. Scalable training therefore needs efficient in-batch/sampled proposals plus selective hard mining, while preserving support across head/tail/new items and maintaining tractable pool refresh.

**Filled template for this item**

- **Scaling dimension:** Catalog grows 100K → 100M items and training volume increases.
- **Baseline scale assumption:** Simple uniform/popularity sampling yields enough informative negatives without expensive mining.
- **First bottleneck:** Uniform hardness collapses and full-catalog mining/evaluation becomes expensive.
- **Second-order effects:** Larger item-frequency skew, storage for mined pools, ANN mining infrastructure, stale pool versions, and tail undercoverage.
- **Architectural response:** In-batch negatives, stratified/mixture samplers, ANN/teacher mining on selected examples, and tractable exact/high-recall benchmark subsets.
- **Partitioning/replication/caching/batching:** Alias/stratified tables, distributed batch negatives, sharded mining indexes, cached versioned pools.
- **Consistency/freshness consequence:** Sampler/miner/index versions can drift from the model and catalog.
- **Operational failure mode:** Training appears healthy on sampled metrics while full-catalog tail quality deteriorates.
- **Validation:** Deployment-like Recall@K, sampler distribution, false-negative audits, training throughput, pool refresh time, and projected-scale tests.

Memory aid: `What grows? → What stops fitting? → What bottlenecks? → How do we partition? → What new failure appears?`.

#### 5. Freshness, State, and Versioning

Hardness is model-relative. A pool mined by version $v$ becomes easier, irrelevant, or differently mislabeled as the model/catalog evolves. Freshness telemetry should measure pool age and current-model hardness, not only wall-clock timestamps.

**Filled template for this item**

- **State that becomes stale:** Hard/teacher negative pools, miner model/index, catalog eligibility, known-positive history, and exposure context.
- **Why freshness matters:** Stale negatives stop being informative or include deleted/changed items; masks may miss new positives.
- **Required freshness:** Refresh when current-model hardness/overlap materially decays, with faster cadence in high-churn catalogs.
- **Refresh cost:** ANN/teacher passes, storage writes, filtering, and orchestration.
- **Update architecture:** Versioned periodic mining with incremental refresh for high-value/changed segments when practical.
- **Version consistency:** Training examples should record miner model, index, catalog snapshot, sampler config, and mask version.
- **Failure from version skew:** A pool generated under old geometry can distort current training or include invalid items.
- **Fallback:** Semi-hard/in-batch/stratified sampler when mined pool is stale or unavailable.
- **Measurement:** Pool age, current-model score/hardness, topK persistence, invalid/false-negative rate, and version metadata.
- **Decision:** Refresh based on information decay and catalog/model change, not a fixed cadence alone.

Memory aid: `What goes stale? → How fast does it matter? → What does refresh cost? → How do versions stay consistent?`.

#### 6. Implementation, Serving, and Observability

A production sampler is a versioned data-generation component. Every negative should have source/proposal metadata where feasible, masks should use temporal known-positive/equivalence rules, mined pools should bind to miner/index/catalog versions, and evaluation must be independent enough not to reproduce the same sampling pathology.

**Filled template for this item**

- **Conceptual object:** A proposal mechanism q(i|context) plus masking/correction policy defining training comparisons.
- **Training/data implementation:** Sample/mine negatives, apply known-positive/equivalence/exposure filters, compute corrections/weights when justified, log source/hardness.
- **Stored artifact/state:** Sampler config, alias/strata tables, mined pools, miner/index/catalog versions, mask/positive-history state.
- **Serving path:** No direct sampler in online serving, but training distribution should represent the candidates the deployed retriever competes against.
- **Component contract:** Proposal probabilities/source, eligibility universe, positive masks, objective/correction semantics, and mining version.
- **Logging:** Negative source, q(i) when needed, popularity bucket, hardness score, mask/filter reason, miner/index version, pool age.
- **Versioning:** Sampler mixture, correction rule, miner/index/catalog snapshot, and known-positive rules.
- **Failure mode:** Sampled loss improves while full-catalog retrieval deteriorates because evaluation shares the same biased proposal.
- **Observability:** Realized negative distribution, mask rate, false-negative audits, hardness, head/tail recall, exact-vs-ANN serving quality.
- **Rollback:** Restore a stable sampler mixture/pool and compatible correction/objective settings.
- **Testing/replay:** Fixed batches should reproduce sampling/masking distributions under seeded/versioned configs.

Memory aid: `Train → Store → Serve → Version → Log → Monitor → Roll back`.

#### 7. Vertical Transfer

The mechanism should transfer; the assumptions must be re-derived. Use the checklist:

`labels → candidate sources → objectives → features → constraints → evaluation → experiments → serving/freshness → ecosystem effects`

Representative verticals:

- **Video/feed:** **Invariant:** Sampler principles transfer. **Different assumption:** Skip/dwell after meaningful exposure may be stronger negatives; interruption/session context complicates labels. **Technical consequence:** Prefer exposure-aware/semi-hard negatives with session-aware false-negative caution.
- **E-commerce:** **Invariant:** Sampler principles transfer. **Different assumption:** Substitutes, variants, and delayed purchases create many latent positives. **Technical consequence:** Mask equivalents/history and avoid treating unpurchased substitutes as definite negatives.
- **Ads:** **Invariant:** Proposal/correction logic transfers. **Different assumption:** Exposure is auction/policy-conditioned and calibration matters downstream. **Technical consequence:** Use exposure/auction-aware negatives and validate calibration/auction outcomes.
- **Marketplace:** **Invariant:** Coverage and false-negative logic transfer. **Different assumption:** Provider exposure is policy-concentrated and supply eligibility varies. **Technical consequence:** Stratify/provider-aware sampling so old exposure policy does not freeze provider concentration.
- **Search:** **Invariant:** Hard-negative logic transfers. **Different assumption:** Near-miss lexical/semantic documents can be genuinely relevant under incomplete judgments. **Technical consequence:** Mine hard negatives but use judgment/multi-positive filters and evaluate unbiased relevance sets.

**Filled transfer template — Video/feed**

- **Invariant:** Sampler principles transfer.
- **Different data-generating process:** Skip/dwell after meaningful exposure may be stronger negatives; interruption/session context complicates labels.
- **Different objective:** Re-derive the primary product utility for this vertical rather than copying the base objective.
- **Different candidates/features:** Candidate sources and features should reflect the vertical-specific context and available signals.
- **Different constraints:** Skip/dwell after meaningful exposure may be stronger negatives; interruption/session context complicates labels.
- **Metric change:** Retain transferable stage metrics, then add vertical-specific outcomes and guardrails.
- **Serving change:** Prefer exposure-aware/semi-hard negatives with session-aware false-negative caution.
- **Ecosystem effect:** Check creator/provider/seller/advertiser or user-side concentration where relevant.
- **Validation:** Evaluate both transferable retrieval/ranking quality and the vertical-specific product outcome.

Memory aid: `Keep the mechanism; re-derive the assumptions.`

#### 8. Objective and Metric Mismatch

Negative sampling can optimize the sampled training task rather than the deployed retrieval problem. A lower sampled loss may simply mean the sampler became easier or more self-consistent. First verify representation and serving; then ask whether q(i), correction, and labels approximate the intended full-catalog competition and product objective.

**Filled template for this item**

- **Offline/model metric:** Sampled training/validation loss improves.
- **Online/product outcome:** Full-catalog/ANN Recall@K or downstream product quality worsens.
- **Execution verification:** Compare exact and ANN serving quality, model/index versions, and candidate universe before blaming sampling.
- **Metric semantics:** Sampled loss measures discrimination against negatives drawn from the chosen proposal.
- **Blind spots:** Unseen catalog regions, false negatives, tail coverage, exposure policy, and final product utility.
- **Missing product factor:** The proposal distribution may not represent deployed candidate competition or relevance semantics.
- **Repair:** Change sampler mixture, masks, correction/importance weights when justified, and evaluate full-catalog/serving-faithful slices.
- **Trade-off:** More deployment-faithful/harder negatives cost more and can increase false-negative noise/variance.
- **Online validation:** Exact/ANN Recall@K, head/tail/cold slices, false-negative audits, training cost, and controlled product experiment when warranted.

Memory aid: `Did we execute the objective incorrectly, or correctly optimize the wrong objective?`

## Material Follow-ups / Scenario Variants

### Extreme popularity skew

If a recommender has a highly skewed catalog, raw popularity-weighted sampling may make nearly every update about the same head items. A better approach is usually to temper popularity, stratify by head/mid/tail, or mix popularity with uniform and semi-hard negatives. The correct mixture should be chosen from deployment-like Recall@k and segment metrics rather than from sampled loss.

A tail-recall regression after introducing popularity-heavy negatives should first be checked by comparing the realized negative-frequency distribution with catalog/serving frequencies, then by measuring head/mid/tail candidate recall. If the regression is isolated to the tail, reducing the popularity exponent or adding explicit tail/uniform coverage is a direct experiment.

### Hard negatives outperform early, then degrade

An early gain followed by degradation is consistent with a mined pool becoming stale or with training moving toward increasingly ambiguous false negatives. Measure current-model hardness of the stored pool, false-negative rate, duplicate/substitute rate, and pool age. Refreshing the pool or moving to semi-hard bands is preferable to blindly mining ever-harder examples.

### Exposure-aware negatives after a policy change

When a new recommender changes what users see, negatives collected under the old exposure policy are no longer a neutral sample of the new candidate space. Exposure-aware training can still be useful, but the model is partly learning the old policy's support. Mix broader negatives, preserve exploration where possible, and evaluate on slices that the old policy rarely exposed.

### When to apply sampling correction

Correction is appropriate when the training objective is intended to approximate a target such as full-catalog softmax and the proposal distribution is known. A log-proposal or importance correction compensates for items being sampled with unequal probability.

Correction is not a universal fix. It does not repair false-negative labels, may increase variance when proposal probabilities are tiny, and can be inappropriate when the deliberately reweighted sampler represents the desired training objective rather than a computational approximation.

### Diagnosing tail-only recall loss

A tail-only recall loss can arise when popularity-weighted or in-batch sampling makes head items dominate the contrastive denominator. The diagnostic sequence is:

1. compare realized negative frequencies by popularity bucket;
2. verify batch construction is not head-heavy;
3. measure per-bucket embedding norm and retrieval recall;
4. compare against a uniform or stratified baseline;
5. test a tempered/mixed sampler;
6. verify ANN/index effects separately so sampling is not blamed for a serving-layer problem.

The expected answer is not simply "use uniform negatives." It is to localize whether the tail regression comes from sampling distribution, representation learning, or retrieval infrastructure, and then restore enough tail coverage without discarding informative negatives.
