---
type: interview-answer
item: "2027:R02"
title: "Explicit, Implicit, and Exposure-Conditioned Feedback"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - implicit-feedback
  - exposure-bias
  - label-construction
  - delayed-feedback
---

## Canonical Staff-Depth Question

Compare explicit and implicit feedback. Explain why non-interaction is not a negative and model exposure, examination, missing-not-at-random labels, repeated impressions, and delayed conversion.

## Mastery Answer

The key distinction is that **explicit feedback directly expresses a user's stated preference**, while **implicit feedback records behavior from which preference must be inferred**. Ratings, likes/dislikes, or survey responses are explicit. Clicks, watch time, dwell, add-to-cart, purchase, skips, and non-interactions are implicit. Explicit labels are usually semantically cleaner but sparse and selectively provided; implicit labels are abundant but confounded by what the system chose to show and what the user actually had a chance to notice.

For recommendation data, I would therefore start from the **data-generating process**, not from a naive binary label. A user can interact with an item only if the item was eligible, selected for exposure, rendered, and usually examined. So a missing interaction can mean many things: the item was never shown, it was shown below the fold and never examined, it was seen and ignored, the user intended to act later, or the logging failed. Treating every user-item pair with no click or purchase as a negative collapses these states and creates biased labels.

A practical label taxonomy is at least:

- **unexposed**: the user had no recorded opportunity to interact;
- **exposed but outcome unknown or not yet mature**: the item was shown, but examination or the conversion window is uncertain;
- **exposed and examined but ignored**: stronger negative evidence;
- **positive**: the target action occurred within a defined attribution window;
- **explicit negative**, when available: hide, dislike, dismiss, return, report, or another action with negative semantics.

This matters because recommendation logs are generally **missing not at random**. The current policy decides what gets exposure, and exposure depends on user/item/context features and previous model scores. As a result, observed labels overrepresent items the existing system believed were promising. The model is trained on a selective sample of the user-item space, so raw observed outcomes are not an unbiased picture of preference.

Examination adds another layer. An impression event is not always equivalent to a meaningful opportunity. Position, viewport visibility, device, scroll depth, carousel placement, and latency can determine whether the user actually saw the item. If examination is important, I would log enough UI context to distinguish "rendered" from "likely examined," or use an examination model when direct instrumentation is unavailable.

Repeated impressions need an explicit unit of analysis. Five ignored impressions can be stronger evidence than one ignored impression, but they are not five independent negatives. Repetition may reflect persistence by the serving policy, position bias, or user fatigue. I would define the training grain—impression-level, session-item, or user-item-time-window—and aggregate or weight repeated exposures accordingly.

Delayed conversion means labels cannot be finalized immediately. A click today may convert tomorrow. If I label all not-yet-converted impressions as negatives at training cutoff, recent examples are systematically censored. I would define a conversion horizon, delay finalization until the label is mature, or use censoring/delay-aware methods when fast retraining is required.

The operational principle is: **condition labels on opportunity and label maturity**. Separate unexposed from exposed, distinguish exposure from examination when material, make repeated-exposure semantics explicit, and do not declare a negative until the user plausibly had the chance to act and the outcome window has matured. That produces labels aligned with the behavior the model is actually supposed to learn.

## Learn the Concepts

### Foundation

A recommender observes only a small slice of a user's possible choices. Suppose an online store has 1,000,000 products. A user visits one product page and the recommender shows 20 items. The user clicks one item and ignores the other 19.

The central mental model is:

**preference is latent; logs are observations produced by both the user and the serving policy.**

The system does not directly observe, "Would this user like item X?" It observes events such as:

`eligible → selected by policy → rendered → examined → acted on → possibly converted later`

Each arrow can fail. Therefore the absence of a final action cannot automatically be interpreted as dislike.

**Explicit feedback** is a direct statement such as a 1–5 rating, thumbs-up/down, "not interested," or survey response. Its advantage is semantic clarity. Its disadvantages are sparsity, user-selection bias, and often a mismatch between what people say and what they later do.

**Implicit feedback** is behavior that indirectly reveals preference: clicks, dwell time, completion, add-to-cart, purchase, save, share, skip, hide, repeat consumption, or abandonment. It is abundant and naturally generated, but its meaning is ambiguous. A click can mean curiosity rather than satisfaction; a purchase can reflect price or inventory; a skip can reflect presentation rather than content quality.

**Exposure** means the system gave the user some opportunity to encounter the item. This is stronger than merely saying the item existed in the catalog.

**Examination** means the user likely noticed the exposed item. Exposure and examination are not always the same. An item can be rendered below the fold, appear in a long feed, or be placed in a carousel slot the user never reaches.

**Non-interaction** means no target action was observed. It is not a semantic label by itself.

**Missing-not-at-random (MNAR)** means whether an observation is missing depends on variables related to the quantity being modeled. In recommendation systems, the serving policy preferentially exposes certain items. Therefore the observed interactions are concentrated in parts of the user-item space chosen by prior models, business rules, popularity, inventory, or position.

**Delayed conversion** means a target outcome can occur after the initial exposure. Purchases, subscriptions, bookings, or downstream retention can have hours- or days-long delays.

#### Worked example

Assume a user opens a product page and the recommender serves these four items:

1. Item A is at position 1, clearly visible, and clicked.
2. Item B is at position 2, clearly visible, but ignored.
3. Item C is at position 15 in a horizontal carousel the user never scrolls to.
4. Item D is eligible in the catalog but was never retrieved or shown.

A naive dataset might create:

- A = positive;
- B = negative;
- C = negative;
- D = negative.

That is wrong because these rows do not represent the same opportunity.

A better interpretation is:

- A = exposed, likely examined, positive;
- B = exposed, likely examined, no positive action: plausible negative evidence;
- C = exposed at the rendering layer but probably not examined: weak or unknown evidence;
- D = unexposed: no direct preference evidence.

If the target is purchase within seven days and A was clicked today but not yet purchased, A may not yet have a mature purchase label. Calling it a purchase-negative today would introduce censoring bias.

Important beginner distinctions:

- **unexposed is not the same as negative;**
- **exposed is not always the same as examined;**
- **ignored is not always the same as disliked;**
- **one impression is not automatically one independent training example;**
- **not converted yet is not the same as never converted;**
- **more logged data does not imply unbiased data.**

### Core Interview Reasoning

A strong reusable reasoning sequence for this question is:

**feedback type → opportunity process → label semantics → bias mechanism → temporal/repetition semantics → training/evaluation consequence**

1. **Classify the feedback signal.**  
   Ask what the event actually means. Ratings and direct dislikes have explicit semantics. Clicks, dwell, purchase, and skips are behavioral proxies whose meaning depends on context.

2. **Reconstruct the opportunity process.**  
   Ask whether the user could have produced the event. The item must usually be eligible, retrieved, ranked into an exposed position, rendered, and examined before a click or conversion can occur.

3. **Define label states instead of forcing binary labels too early.**  
   At minimum distinguish unexposed, exposed-but-unexamined or uncertain, exposed-and-ignored, positive, and explicit negative where available.

4. **Identify selection bias.**  
   The logging policy determines which items become observable. Because policy selection depends on estimated relevance, popularity, business rules, or prior interactions, the missingness is not random.

5. **Define repeated-exposure semantics.**  
   Choose a grain such as impression, session-item, or user-item-window. Avoid treating highly correlated repeated impressions as independent evidence without justification.

6. **Define label maturity and attribution.**  
   For delayed outcomes, specify the attribution window and the time at which a negative label becomes final.

7. **Connect to model consequences.**  
   Bad labels teach the model policy artifacts. Naively sampling unexposed items as negatives can reinforce popularity and exposure bias; prematurely labeling delayed conversions as negatives biases recent examples; treating unexamined impressions as negatives teaches position/UI effects as preference.

8. **Connect to evaluation and logging.**  
   Reliable offline evaluation requires knowing which candidates were exposed, under what policy, in what position/context, and whether labels had matured.

The compact interview outline is:

**Explicit vs implicit → non-interaction ambiguity → exposure/examination → MNAR → repeated impressions → delayed conversion → label construction.**

### Deeper Reasoning and Derivations

The deepest idea is that an observed interaction is the product of several events, not a direct readout of preference.

Let:

- $R_{ui}$ represent latent relevance or utility for user $u$ and item $i$;
- $E_{ui}$ indicate exposure;
- $X_{ui}$ indicate examination;
- $Y_{ui}$ indicate the final observed action, such as click or purchase.

A simplified causal factorization is:

$$
P(Y_{ui}=1)
=
P(E_{ui}=1)
\cdot
P(X_{ui}=1 \mid E_{ui}=1)
\cdot
P(Y_{ui}=1 \mid X_{ui}=1, E_{ui}=1)
$$

This is not meant to assert strict independence; it is a useful decomposition of the opportunity process. If $E_{ui}=0$, the user typically cannot generate an observed action even when latent relevance is high.

That explains why a zero in the interaction matrix is ambiguous. It can represent at least:

$$
\text{zero}
\in
\{
\text{unexposed},
\text{unexamined},
\text{examined-and-ignored},
\text{not-yet-converted},
\text{logging failure}
\}
$$

The model only sees a clean binary target if the data pipeline chooses to collapse these states. That collapse is itself a modeling assumption.

#### Why missingness is not random

Suppose the current recommender exposes items with high historical popularity or high predicted click probability. Then:

$$
P(E_{ui}=1 \mid u,i)
$$

is larger for already-favored items. The training data therefore overrepresent those items, and future models trained naively on this data may interpret "frequently observed and clicked" as pure user preference rather than partly a consequence of the old policy.

This creates a feedback loop:

`old policy → selective exposure → selective labels → new model → similar selective exposure`

The bias can intensify if unexposed items are sampled as negatives, because the model is explicitly taught that regions never explored by the previous policy are undesirable.

#### Exposure versus examination

For ranked interfaces, position affects examination. A simple click model separates:

$$
P(\text{click})
=
P(\text{examine})
\cdot
P(\text{click} \mid \text{examine})
$$

If lower-ranked items are rarely examined, raw click-through rate by position mixes two phenomena:

1. how relevant the item is if seen;
2. how likely the item is to be seen in that position.

Adding position as an ordinary feature can help prediction under the same policy, but it does not magically recover unbiased preference. The model may simply learn the policy's presentation pattern.

#### Repeated impressions

Assume a user sees the same item five times and never clicks. There are multiple possible training semantics:

- five impression-level negatives;
- one user-item-session negative;
- one user-item-window negative with an exposure-count feature;
- a weighted negative whose confidence increases with examination count.

The correct choice depends on the objective. Repeated ignored exposures can contain stronger evidence, but they are correlated observations. Treating them as independent can overweight persistent serving policies and high-frequency users.

A useful confidence-style abstraction is:

$$
w_{ui} = f(n_{\text{examined impressions}}, \text{recency}, \text{position}, \text{context})
$$

where $w_{ui}$ controls how strongly the absence of action should influence training. The important point is not a specific formula; it is that "zero interaction" can have different evidential strength.

#### Delayed conversion and censoring

Let the target be purchase within seven days of an impression. For an impression that occurred one hour ago, the seven-day outcome is not yet observable. Labeling it 0 creates **right censoring**: the observation window ended before the outcome window matured.

A simple safe rule is:

`training cutoff - impression time >= attribution horizon`

before declaring a negative. If rapid retraining makes that too slow, delay-aware or survival-style modeling can be used, but the pipeline must still encode which labels are mature and which are censored.

#### True negative is objective-dependent

"True negative" should not mean "the user did nothing." It should mean that, under the objective and observation contract, there is sufficient evidence that the target outcome did not occur despite a meaningful opportunity.

For click prediction, an examined impression with no click may be a defensible negative.

For purchase prediction, an examined impression with no immediate purchase may still be unresolved until the conversion window closes.

For satisfaction, even a click can be negative evidence if it is followed by an immediate bounce or hide.

Therefore label semantics must be tied to the model's target.

### Advanced Staff-Depth Considerations

The universal Staff reasoning loop is:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate**

A compressed form is:

**Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**

For R02, the baseline is a logging and label-construction contract: which items were eligible, exposed, examined, acted on, and when labels become mature. The fragile assumptions are that impressions represent opportunity, that ignored items are informative negatives, that repeated impressions are independent enough for the chosen grain, and that the attribution window is complete. The observables are impression/examination logs, position and UI context, exposure counts, label-age distributions, conversion-delay curves, and segment-level outcomes. Decisions concern label states, weighting/sampling, attribution windows, and instrumentation.

#### 1. Changed Constraints and Transfer Logic

The mechanism is stable across recommender surfaces: labels are trustworthy only relative to the opportunity process. What changes is how opportunity and outcome should be defined.

If a product changes from a paginated grid, where most rendered items are visible, to an infinite feed, "impression" can become much weaker evidence of examination. The label pipeline cannot preserve the old assumption that rendered equals seen. It may need viewport instrumentation, dwell thresholds, or exposure-confidence weighting.

The invariant is that a negative should correspond to a sufficiently observed opportunity for the target outcome. The fragile part is the operational definition of "sufficiently observed."

Filled template:

- Original assumption: a logged impression closely approximates user examination.
- Changed constraint: the surface becomes an infinite scroll feed with substantial off-screen rendering.
- Invariant: negative labels require credible opportunity to interact.
- Broken assumption: rendered items are no longer reliably seen.
- Consequence: many apparent negatives are actually unexamined examples.
- Design change: log viewport visibility and construct negatives from examined impressions or lower-confidence weights.
- Metric impact: raw impression-level CTR may fall mechanically; examination-conditioned CTR becomes more interpretable.
- Trade-off: better label semantics at the cost of more client instrumentation and possible missing telemetry.
- Validation: compare viewport-based exposure rates, click propensity conditional on visibility, and offline/online results by scroll-depth slice.

#### 2. Failure Modes and Diagnosis

Common failures are label contamination, exposure logging gaps, position/examination confounding, over-counted repeated impressions, and immature delayed labels.

A useful diagnostic chain is:

`eligibility → retrieval/ranking policy → rendering → examination → action → delayed outcome → label table`

The objective is to find the first stage where the expected contract diverges.

For example, if offline training metrics improve but online CTR drops, inspect whether a logging change caused many below-the-fold impressions to become negatives. If the model then penalizes items commonly served lower in the list, a presentation artifact has entered the target.

Filled template:

- Symptom: offline AUC improves after a new impression logger, but online engagement falls.
- Stage decomposition: eligibility → served candidates → rendered impressions → viewport examination → labels → model.
- Slices: position, device, viewport size, feed depth, new vs returning users.
- Competing hypotheses: better negative coverage; unexamined impressions mislabeled as negatives; duplicated impressions; feature/model change.
- Discriminating evidence: ratio of rendered to visible impressions and click rate conditional on visibility before/after the logger change.
- Offline/online comparison: improvement concentrated in raw impression labels but not examination-conditioned slices.
- Replay/isolation: rebuild the dataset using only viewport-confirmed impressions and retrain/replay.
- First divergence: label-construction stage after rendering.
- Immediate mitigation: revert to previous label contract or filter uncertain impressions.
- Permanent prevention: versioned exposure semantics, schema tests, and dashboarded rendered-to-examined ratios.

#### 3. Latency and Resource Trade-offs

R02 is primarily a data/label question, so online inference latency is not the dominant concern. The important resource trade-off is **instrumentation and data processing cost** versus label fidelity.

Tracking viewport visibility, scroll depth, repeated exposure IDs, attribution chains, and delayed outcomes increases event volume, storage, joins, and backfill complexity. More precise examination modeling may also add offline compute.

The safe optimization principle is to preserve the minimum logs needed to reconstruct opportunity and label maturity. Do not discard policy, position, request, impression, and timestamp information merely to save storage if those fields are required to interpret labels.

Filled template:

- Budget: offline logging/storage/ETL budget rather than inference p99.
- Cost decomposition: client events + event transport + storage + temporal joins + deduplication + label finalization.
- Dominant cost: high-volume impression/examination events and temporal attribution joins.
- Quality driver: correctly distinguishing unexposed, unexamined, ignored, and converted examples.
- Cost driver: event cardinality and retention horizon.
- Optimization knobs: sampled low-value telemetry, compact schemas, deduplication, aggregated exposure counts, tiered retention.
- Fallback/degradation: preserve canonical impression/action logs even if fine-grained examination telemetry is temporarily reduced.
- Trade-off curve: lower telemetry cost versus weaker ability to debias or diagnose labels.
- Decision: keep event lineage and label-critical fields; optimize representation before deleting semantics.

#### 4. Scale and Capacity

At small scale, a team may join impression and conversion tables directly. At large scale, event volume, repeated impressions, and long attribution windows become the first bottlenecks.

If billions of impressions are logged daily, materializing every possible user-item pair is impossible and unnecessary. Training data should be constructed from observed opportunities plus principled sampled negatives, with explicit semantics for what sampling represents.

Second-order effects include skew from heavy users, popular items, high-frequency campaigns, and duplicated retries. Large attribution windows increase state and join cost.

Filled template:

- Scaling dimension: impression/event volume.
- Baseline scale assumption: all relevant impressions can be retained and joined with outcomes directly.
- First bottleneck: storage and temporal join/shuffle cost.
- Second-order effects: heavy-user/item skew, duplicate events, longer backfills, delayed finalization.
- Architectural response: partitioned event tables, stable impression/request IDs, pre-aggregation at chosen grain, and sampled training negatives.
- Partitioning/replication/caching/batching: partition by event time plus stable entity keys; batch label finalization by maturity horizon.
- Consistency/freshness consequence: late events can revise labels and require deterministic backfills.
- Operational failure mode: duplicate impressions over-weight negatives after replay.
- Validation: event-count conservation, dedupe invariants, label-maturity checks, and segment distribution comparisons.

#### 5. Freshness, State, and Versioning

The relevant state is the logging policy, exposure semantics, attribution horizon, and label maturity. All can change over time.

A model trained on labels defined under one UI surface or policy may be inconsistent with later data if "impression" semantics change. The dataset therefore needs versioned event schemas and label definitions.

For delayed outcomes, freshness conflicts with correctness. Retraining hourly provides fresher models, but recent examples may not yet have mature labels. Options include excluding recent rows, using mature targets only, or explicitly modeling delay/censoring.

Filled template:

- State that becomes stale: recent outcome labels and exposure/examination semantics.
- Why freshness matters: behavior and inventory may move quickly, but immature labels are systematically biased.
- Required freshness: depends on product dynamics; training data can be fresh only up to the mature-label boundary for the target.
- Refresh cost: waiting reduces sample freshness; delay-aware modeling increases complexity.
- Update architecture: append events continuously, finalize labels after the attribution horizon, and version label logic.
- Version consistency: record label-policy/schema version with each training build.
- Failure from version skew: combining old "rendered impression" labels with new "viewport-visible impression" labels as if equivalent.
- Fallback: train on the latest fully mature and semantically consistent window.
- Measurement: conversion-delay CDF, fraction of censored examples, and label distributions by version.
- Decision: prefer slightly older but mature labels over fresher systematically censored labels unless delay is modeled explicitly.

#### 6. Implementation, Serving, and Observability

The conceptual distinctions must appear in the event schema and training pipeline.

A production-grade implementation should preserve stable request/impression IDs, user/session/item IDs, serving policy/model version, rank/position, surface/module, timestamps, eligibility or candidate provenance when available, render/examination events, target actions, and attribution identifiers.

The training pipeline should deterministically deduplicate, join outcomes only within the attribution window, mark immature labels, and retain enough provenance to replay how a row was constructed.

Filled template:

- Conceptual object: opportunity-conditioned user-item outcome.
- Training/data implementation: temporal joins from exposure/examination events to actions with deduplication and maturity logic.
- Stored artifact/state: versioned impression/action logs plus label-generation configuration.
- Serving path: ranker emits ordered items; client/server logging records which items were actually exposed and under which policy.
- Component contract: each training label must reference a valid opportunity event and a defined observation window.
- Logging: request ID, impression ID, item, position, surface, policy/model version, timestamps, action events.
- Versioning: schema, policy, and label-generation version.
- Failure mode: dropped examination logs turn uncertain examples into negatives.
- Observability: exposure counts, examined/exposed ratio, action rate by position, label-age distribution, dedupe rate.
- Rollback: rebuild from immutable raw events under the prior label contract.
- Testing/replay: synthetic timelines covering unexposed items, duplicate impressions, late conversions, and attribution boundaries.

#### 7. Vertical Transfer

The invariant across verticals is: **interpret behavior relative to opportunity and target semantics.** What changes is the data-generating process.

In e-commerce, purchase is high-value but delayed and affected by price, inventory, and checkout friction. Clicks and add-to-cart are earlier proxies.

In video/feed, examination can be close to viewport exposure, but watch time, completion, skip, and replay carry richer graded semantics. Autoplay can further weaken the meaning of "play."

In ads, exposure and position are tightly coupled to an auction and eligibility constraints. Click/conversion logs are strongly policy-selected, and propensities may matter for counterfactual analysis.

In notifications, a sent notification is not necessarily seen; delivery, OS suppression, opening, and downstream action are separate stages, and excessive repeated exposure can itself change user behavior.

Filled transfer template for video/feed:

- Invariant: negative evidence requires a meaningful viewing opportunity.
- Different data-generating process: content is continuously surfaced and often auto-plays in a ranked feed.
- Different objective: satisfaction/watch quality rather than simple click.
- Different candidates/features: fresh content, session intent, creator/content features.
- Different constraints: rapid freshness, creator diversity, safety, fatigue.
- Metric change: watch time, completion, skip, hide/report, long-term retention.
- Serving change: session state and rapid feedback refresh become more important.
- Ecosystem effect: repeated exposure can affect creator concentration and user fatigue.
- Validation: evaluate by exposure depth, content age, session stage, and creator/user segments.

#### 8. Objective and Metric Mismatch

Execution failure and objective mismatch are different.

An execution failure occurs when the intended label contract is not implemented correctly—for example, unexamined items are accidentally marked as negatives.

Objective mismatch occurs when the label contract is implemented perfectly but the chosen target is the wrong product objective—for example, optimizing clicks increases curiosity-driven taps while reducing purchase or satisfaction.

R02 matters because ambiguous implicit signals are especially vulnerable to proxy misuse. A technically clean click label can still optimize the wrong behavior.

Filled template:

- Offline/model metric: click log-loss or AUC on exposed impressions.
- Online/product outcome: purchase, satisfaction, retention, or revenue.
- Execution verification: confirm exposure/examination and label windows are correct.
- Metric semantics: click measures immediate interaction, not necessarily utility.
- Blind spots: post-click dissatisfaction, price sensitivity, returns, long-term fatigue.
- Missing product factor: downstream value after the click.
- Repair: multi-stage/multi-task target, value-weighted objective, guardrails, or a more appropriate label.
- Trade-off: potentially lower click rate for better downstream quality.
- Online validation: randomized experiment with downstream and segment guardrails.

## Material Follow-ups / Scenario Variants

### You have only clicks and no reliable impression log. Can you train a recommender?

Yes, but the task and claims must be narrower. Positive interactions are still useful, but the absence of a click cannot be interpreted as a clean negative because opportunity is unknown. Candidate training can use heuristic or sampled negatives, but those negatives represent a modeling approximation, not observed rejection. Evaluation is also limited because exposure-conditioned rates cannot be reconstructed. The highest-value fix is usually instrumentation: start logging request, candidate/ranked result, position, and actual impression/examination events. Until then, prefer objectives robust to positive-only or implicit data and avoid claiming unbiased preference estimates.

### When is an ignored impression a reasonable negative?

When the target is immediate enough, the item had a credible opportunity to be examined, the label window has matured, and the action semantics make absence meaningful. An above-the-fold item that was visible for sufficient time and received no click may be a reasonable click-negative. The same row may still be unresolved for a seven-day purchase target. Negative semantics are always target-specific.

### Should five ignored impressions count as five negatives?

Not automatically. They contain more evidence than one exposure, but they are correlated and may be caused by the serving policy repeatedly choosing the same item. A defensible design defines the grain explicitly—impression-level, session-item, or user-item-window—and may aggregate exposure count or use confidence weighting. Validate whether additional repeated exposures improve calibration and ranking or merely amplify policy/popularity bias.

### A new model gets higher offline accuracy when all unobserved user-item pairs are treated as negatives. Why might that be misleading?

Because the test distribution is dominated by easy "negatives" the user never had a chance to consider. The model can score well by separating observed positives from the huge unexposed catalog without improving ranking among plausible exposed candidates. The evaluation should better match the serving decision: use exposure-conditioned examples or a candidate set representative of deployment, temporal splits, stage-appropriate ranking metrics, and segment analysis.

### How would you handle a purchase target with a 14-day conversion window while retraining daily?

Maintain a clear maturity boundary. The simplest correct design trains only on impressions at least 14 days old when assigning final purchase negatives, while newer rows remain censored/unlabeled for that target. If product freshness makes a 14-day lag unacceptable, introduce a delay-aware approach or auxiliary faster labels such as click/add-to-cart, but preserve the distinction between mature and censored purchase outcomes. Validate using the empirical conversion-delay distribution and ensure recent examples are not systematically mislabeled.
