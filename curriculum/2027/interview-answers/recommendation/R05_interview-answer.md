---
type: interview-answer
item: "2027:R05"
title: "Cold Start and Bootstrap Strategies"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - cold-start
  - personalization
---

## Canonical Staff-Depth Question

Distinguish new-user, new-item, new-surface, and sparse-history cold start. Explain priors, content features, popularity, exploration, onboarding signals, and evaluation slices.

## Mastery Answer

Cold start is not one problem; it is a family of situations where the system lacks the behavioral evidence that its normal personalized policy expects. I would first identify which entity is cold, because the fallback signal and the failure mode differ for a new user, a new item, a new surface, and a sparse-history user.

For a **new user**, the system has little or no user-specific interaction history. I would start from a population or segment prior, then update quickly from contextual and onboarding signals: locale, device, entry point, declared interests, followed creators or categories, and the first few impressions, skips, clicks, or watches. Popularity is useful as a safe baseline, but I would make it contextual rather than globally dominant, otherwise the system over-serves head content and learns little about the user. Controlled exploration is important because early recommendations are also information-gathering actions.

For a **new item**, the problem is inverted: users may be well known, but the item has no interaction history and therefore cannot enter collaborative or popularity-driven retrieval reliably. I would bootstrap it from content and metadata features, seller/creator/category priors, and possibly an embedding generated from the item itself. I would allocate bounded exploration traffic so the system can collect unbiased-enough evidence about the item rather than requiring popularity before exposure. Guardrails matter because aggressive exploration can hurt users or create marketplace unfairness.

A **new surface** is different again. The users and items may be known, but the new placement has little surface-specific feedback, and behavior may not transfer because intent, position, layout, and exposure policy changed. I would start with transferable representations and priors from related surfaces, but calibrate or retrain the final policy on the new surface. The key assumption to test is transportability: whether response patterns learned elsewhere remain valid under the new context.

A **sparse-history** user is not the same as a truly new user. There is some evidence, but it is noisy or incomplete. I would shrink the personalized estimate toward a broader prior rather than either ignoring the history or overfitting to a few actions. The less evidence we have, the more weight the prior should receive; as evidence accumulates, personalization should dominate.

Across all four cases, I would think in terms of **prior → early signals → controlled exploration → rapid updating**. Priors can come from global, segment, contextual, or hierarchical statistics. Content features let us generalize before collaborative evidence exists. Popularity supplies a robust fallback but creates concentration and feedback-loop risk. Onboarding can accelerate preference identification but adds user friction and may suffer from stated-versus-revealed preference mismatch. Exploration buys information at the cost of short-term exploitation quality, so it should be risk-bounded and instrumented.

Evaluation must make cold start explicit. Aggregate CTR, NDCG, conversion, or watch time can look healthy while cold entities fail because warm traffic dominates. I would report dedicated slices such as users with 0, 1–3, 4–10, and 10+ prior interactions; item age or exposure-count buckets; new-surface cohorts; and performance as a function of time-to-first-useful-signal. I would compare against simple priors and popularity baselines and measure both short-term utility and learning speed. The goal is not to make cold start disappear in averages; it is to define deliberate bootstrap behavior whose quality, exploration cost, and transition to the warm policy are measurable.

## Learn the Concepts

### Foundation

A recommender normally learns from **behavioral evidence**: what a user clicked, watched, bought, skipped, hid, or repeatedly ignored. Cold start happens when the entity or context being recommended does not yet have enough of that evidence for the normal personalized model to behave reliably.

The central mental model is:

**cold entity/context → weak evidence → use a prior → gather informative signals → update toward personalization**

A **prior** is a reasonable default belief before much entity-specific evidence is available. In recommendation systems, a prior may be global popularity, category popularity, segment preferences, seller or creator quality, content similarity, or a learned representation transferred from related data.

A **content feature** describes the user or item without depending on interaction history. For an item, examples include category, text, image embedding, brand, price, creator, language, or taxonomy. For a user, examples include locale, device, acquisition channel, or explicitly selected interests. Content features are valuable in cold start because they exist before collaborative behavior does.

**Popularity** means recommending based on aggregate interaction counts or rates. It is often a strong fallback because it is stable and cheap, but it is not personalized and can amplify already-popular entities.

**Exploration** means intentionally showing options whose value is uncertain in order to learn from the response. **Exploitation** means choosing the option currently estimated to be best. Cold start requires some exploration because without exposure, the system may never learn whether a new item or unknown preference is good.

**Onboarding signals** are explicit inputs collected early, such as choosing interests, following creators, rating a few examples, or selecting use cases. They reduce uncertainty quickly, but every question adds friction and declared preferences may differ from actual behavior.

The four cold-start types are distinct:

- **New-user cold start:** the system knows little about the user's preferences.
- **New-item cold start:** the system knows little about how users respond to the item.
- **New-surface cold start:** users and items may be known, but a new placement or product surface lacks reliable surface-specific feedback.
- **Sparse-history cold start:** some behavioral history exists, but there is too little evidence to trust a strongly personalized estimate.

A beginner may conflate new-user cold start with sparse history. The difference matters because sparse history contains evidence and should usually be combined with a prior rather than discarded. Likewise, new-surface cold start is not merely a new-user problem: a known user may behave differently on a home feed, a product-detail page, a notification surface, and a search-results page.

**Worked example.** Suppose a video app has a user who just signed up. There are no watch histories, so a sequence model cannot infer a stable preference state. The app could begin with a contextual popularity prior: trending videos in the user's language and region. During onboarding, the user selects "cooking" and "football," so the prior shifts toward those categories. The first ten impressions are deliberately diverse within those topics. If the user watches two cooking videos to completion and skips football clips quickly, the posterior evidence moves the system toward cooking. The system should not wait for hundreds of interactions before personalizing, but it also should not let a single accidental click dominate.

### Core Interview Reasoning

A strong answer can be reconstructed with:

**identify what is cold → choose the prior → identify available non-behavioral signals → decide how to explore → define the transition to the warm policy → evaluate dedicated cold-start slices**

1. **Identify what is cold.**  
   This determines what information is missing. A new user lacks preference history; a new item lacks response history; a new surface lacks context-specific response data; sparse history provides weak rather than zero evidence.

2. **Choose an appropriate prior.**  
   A prior is the fallback estimate used before enough direct evidence exists. Good priors are usually hierarchical: global behavior when almost nothing is known, then segment/context priors when metadata is available, then entity-specific behavior as observations accumulate.

3. **Use features that exist before interactions.**  
   Content and metadata let the system generalize from similar known entities. For items, this enables retrieval before the item has clicks. For users, contextual features and onboarding can create an initial preference representation.

4. **Create information through exploration.**  
   A system that ranks only by current estimated value can lock out new items and keep users inside the prior. Exploration must be bounded by safety, relevance, business, or marketplace constraints.

5. **Transition smoothly to the warm policy.**  
   Cold-start handling should not be a permanent parallel product. As evidence grows, the system should gradually reduce prior weight and increase entity-specific personalization. This transition should be explicit, monotonic where possible, and measurable.

6. **Evaluate by coldness, not only globally.**  
   Slice by history length, entity age, number of exposures, surface age, or time since signup. Track both quality and learning speed. A policy that has slightly lower first-session CTR but learns the user's interests much faster may be preferable if long-term value improves.

The main trade-offs are:

- safe defaults versus personalization;
- popularity quality versus catalog concentration;
- exploration learning versus short-term utility;
- onboarding information versus friction;
- content-based transfer versus mismatch from metadata or representation errors;
- fast adaptation versus overreacting to noisy early signals.

The key edge case is feedback-loop entrenchment: if only popular or already-confident items get exposure, the system interprets lack of interaction on unseen items as lack of value. Cold-start design therefore has to reason about exposure, not just prediction.

### Deeper Reasoning and Derivations

A useful formal view is **shrinkage toward a prior**. Suppose an item has an unknown click-through rate $\theta$. With little data, an empirical estimate such as clicks divided by impressions has high variance. Instead of trusting a small sample completely, combine it with a prior.

For a Beta-Bernoulli model,

$$
\theta \sim \mathrm{Beta}(\alpha,\beta)
$$

and after observing $c$ clicks and $n-c$ non-clicks,

$$
\theta \mid \text{data}
\sim
\mathrm{Beta}(\alpha+c,\beta+n-c).
$$

The posterior mean is

$$
\mathbb{E}[\theta \mid \text{data}]
=
\frac{\alpha+c}{\alpha+\beta+n}.
$$

This can be read as a weighted blend of prior evidence and observed evidence. When $n$ is small, the prior contributes strongly. As $n$ grows, the entity's own data dominates. Production recommenders need not use this exact Bayesian model, but the mechanism explains why shrinkage, hierarchical priors, regularization, and calibrated fallbacks are useful in sparse-history settings.

For user representations, a similar principle appears in interpolation. Let $u_{\text{history}}$ be an embedding estimated from observed behavior and $u_{\text{prior}}$ a contextual or segment prior. A cold-start representation can be written schematically as

$$
u
=
\lambda(n)\,u_{\text{history}}
+
\left(1-\lambda(n)\right)u_{\text{prior}},
$$

where $\lambda(n)$ increases with the amount and reliability of user history. The important point is not the exact formula but the confidence-weighted transition.

**Why content features help new items.** Collaborative methods require interactions linking users and items. A brand-new item has no such edges, so purely collaborative retrieval cannot place it meaningfully. Content encoders can map the item into a representation space from metadata available at creation time. That gives the item a provisional neighborhood and candidate eligibility before interaction data arrives.

**Why popularity is both useful and dangerous.** Popularity has low variance because it pools many observations, so it performs well when little else is known. But exposure causes interactions and interactions reinforce popularity. This creates a feedback loop in which items with initial exposure gain more data and future exposure, while potentially good new items remain unobserved. Popularity is therefore a prior, not proof of relevance.

**Why exploration is necessary.** If the policy always selects the currently highest-estimated items, it may never collect information about uncertain options. This is a partial-feedback problem: only exposed items produce observable responses. Exploration assigns some traffic to uncertain but plausible options so the system can reduce uncertainty. The correct amount depends on the cost of a bad exposure, the value of information, traffic volume, and how quickly the environment changes.

**New-surface transfer is a covariate and policy problem.** A model learned on one surface observes behavior under a particular layout, intent, candidate set, and ranking policy. Moving the model to another surface changes the data-generating process. Reusing shared embeddings may be sensible, but the response model or calibration may not transfer. Surface-specific validation and controlled launch are therefore required.

**Evaluation needs a time dimension.** Cold-start quality is not just "CTR for new users." A better view includes a learning curve: performance after 0, 1, 3, 10, or 50 observations. Useful quantities include time-to-first-relevant-result, regret during exploration, cold-to-warm transition quality, new-item exposure coverage, and downstream retention or conversion by coldness bucket.

### Advanced Staff-Depth Considerations

The universal Staff reasoning loop for cold start is:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate**

The baseline is the warm recommender, which assumes enough behavioral evidence to estimate user/item preference reliably. The change is that one of those assumptions fails: the user, item, surface, or history is cold. Mechanistically, collaborative estimates become unavailable or high variance, the exposure policy can entrench uncertainty, and aggregate metrics can hide the damage. The right measurements are coldness slices, learning curves, exposure coverage, uncertainty, and transition-to-warm behavior. The response is to combine priors, content/context signals, exploration, and explicit fallback logic. The trade-off is typically short-term certainty versus information gain or personalization. Validation requires both offline replay/slicing and controlled online experiments.

Compressed form:

**Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**

For R05, the central assumption is "the warm policy has enough reliable behavioral history." When that assumption fails, the system must make uncertainty explicit rather than pretending the warm score remains trustworthy.

#### 1. Changed Constraints and Transfer Logic

Cold-start design should preserve the invariant that the user receives a reasonable, safe slate even when personalized evidence is weak. What changes is the information source used to estimate value. If history disappears, the system must substitute priors and content/context signals; if the cost of exploration rises, exploration must become more conservative; if traffic rises, more sophisticated uncertainty-aware exploration may become affordable because evidence accumulates quickly.

A changed constraint propagates through the bootstrap policy. For example, moving from a low-risk entertainment feed to a high-cost marketplace recommendation makes a poor exploratory exposure more expensive. The exploration mechanism must therefore tighten while the invariant—collect enough evidence to escape cold start—still holds.

* Original assumption: Low-cost recommendation mistakes are acceptable during early exploration.
* Changed constraint: Each poor recommendation consumes scarce seller inventory or creates material user cost.
* Invariant: The system still needs evidence to distinguish promising cold items.
* Broken assumption: Random or broad exploration is cheap.
* Consequence: Naive exploration creates unacceptable user/business harm.
* Design change: Use eligibility filters, uncertainty-aware exploration, contextual priors, and bounded traffic allocation.
* Metric impact: Short-term discovery may slow, while harmful exposure and regret decrease.
* Trade-off: Slower learning in exchange for safer exploration.
* Validation: Compare cold-item learning curves, regret, user utility, and guardrail violations in a controlled experiment.

#### 2. Failure Modes and Diagnosis

Cold-start failures often masquerade as generic relevance problems. The useful decomposition is:

**eligibility/candidate generation → prior/content representation → ranking score → exploration allocation → exposure → observed response → warm-policy transition**

Typical failures include new items never entering candidates, poor metadata causing bad content similarity, popularity dominating every cold user, onboarding signals being ignored, exploration traffic not being logged, or the system remaining on a fallback long after enough evidence exists.

Diagnosis should find the first divergence. If candidate coverage for new items is near zero, ranking quality is downstream and cannot fix the issue. If exposure is healthy but response is poor only for one metadata category, content representation or priors are more likely. If first-session quality is acceptable but users never improve with history, the update/transition mechanism is suspect.

* Symptom: New-item conversion is far below warm-item conversion and stays low after several days.
* Stage decomposition: Ingestion → candidate eligibility → content representation → retrieval → rank → exploration → exposure → response → transition.
* Slices: Item age, exposure count, category, seller, metadata completeness, traffic source.
* Competing hypotheses: New items are not retrieved; content embeddings are poor; exploration is too weak; warm transition never triggers.
* Discriminating evidence: Candidate recall and exposure rate by item age, embedding-neighbor quality, exposure-count curves, policy-state logs.
* Offline/online comparison: Offline content similarity can look healthy even when online candidate eligibility is broken.
* Replay/isolation: Replay requests with and without cold-item eligibility/exploration rules.
* First divergence: New items receive adequate index coverage but almost no quota in candidate blending.
* Immediate mitigation: Reserve a bounded cold-item quota within eligible segments.
* Permanent prevention: Add cold-item coverage SLOs, transition-state monitoring, and regression tests for quota allocation.

#### 3. Latency and Resource Trade-offs

Cold-start logic is usually not the dominant compute cost, but it can add extra retrieval channels, feature lookups, onboarding-state reads, or exploration policy work. The main resource question is whether the system can obtain and combine cold-start signals without expanding the critical path excessively.

Content retrieval may require ANN lookup over item embeddings, while popularity and segment priors are often cacheable. Onboarding features should usually be pre-materialized or cheaply accessible. Exploration should be implemented as a lightweight policy or reranking decision, not as an expensive separate model when simpler uncertainty scores suffice.

* Budget: Preserve the recommender's existing end-to-end p99 SLO.
* Cost decomposition: Base retrieval + content/cold-start retrieval + feature hydration + rank + exploration/rerank.
* Dominant cost: Extra candidate retrieval and feature hydration, not the prior itself.
* Quality driver: Candidate coverage and informative early exposures.
* Cost driver: Number of cold-start channels and online feature reads.
* Optimization knobs: Cache priors, precompute item embeddings, parallelize retrieval channels, cap cold-start candidate quotas.
* Fallback/degradation: Use contextual popularity when content or exploration services time out.
* Trade-off curve: More cold candidates improve discovery but increase latency and ranker load.
* Decision: Keep the bootstrap path simple and bounded; spend latency only where cold-slice quality materially improves.

#### 4. Scale and Capacity

As users, items, and event volume grow, the first scaling problem is often not model compute but state and exposure accounting. A large catalog may introduce millions of cold or low-exposure items. Exploring all of them uniformly is impossible, and computing rich content features synchronously at request time does not scale.

The architecture therefore needs tiered eligibility, precomputed representations, exposure counters, and efficient cohort statistics. At scale, cold-start policies also interact with marketplace concentration: small percentage allocations can represent huge traffic volumes and materially affect supply.

* Scaling dimension: Catalog size and rate of new-item arrival.
* Baseline scale assumption: New items are few enough that a simple exploration bucket gives each one useful exposure.
* First bottleneck: Exploration capacity becomes insufficient relative to item arrival.
* Second-order effects: Long cold queues, skewed seller exposure, stale content embeddings, larger candidate sets.
* Architectural response: Segment cold items, prioritize by predicted eligibility/quality, use precomputed content retrieval, and allocate exploration adaptively.
* Partitioning/replication/caching/batching: Partition candidate pools by market/category; batch embedding generation; cache priors.
* Consistency/freshness consequence: Newly ingested items may exist in catalog storage before their embeddings or exploration metadata are ready.
* Operational failure mode: Items appear "active" but are never retrievable.
* Validation: Monitor ingestion-to-retrieval delay, exposure distribution, and cold-to-warm conversion by arrival cohort.

#### 5. Freshness, State, and Versioning

Cold-start systems depend on rapidly changing state: user history length, recent session actions, item age, item exposure count, onboarding selections, item metadata, content embeddings, and policy thresholds. Staleness can keep an entity classified as cold too long or cause the system to miss newly available signals.

The required freshness differs by state. Session actions may need seconds-level updates; item embeddings may tolerate minutes; population priors may refresh hourly or daily. The bootstrap state and warm model must agree on identity and versions so that an item does not become eligible under one representation but scored under an incompatible one.

* State that becomes stale: User-history count, item exposure count, content embeddings, cold/warm policy state.
* Why freshness matters: Stale state causes poor personalization or delays transition out of fallback behavior.
* Required freshness: Session signals near-real-time; exposure counts near-real-time or short-window; embeddings on item-ingestion cadence.
* Refresh cost: Streaming state updates and re-embedding new catalog items.
* Update architecture: Hybrid streaming counters/session state plus batch or incremental embedding generation.
* Version consistency: Couple item embedding version with retrieval index and ranker expectations.
* Failure from version skew: A new item may be present but represented inconsistently across retrieval and ranking.
* Fallback: Contextual popularity or metadata-only scoring until compatible state is available.
* Measurement: State-age distributions and time from first evidence to policy transition.
* Decision: Spend freshness where it changes early recommendations; tolerate slower refresh for stable priors.

#### 6. Implementation, Serving, and Observability

In production, cold start must be an explicit policy, not an accidental consequence of missing features. Training data should preserve entity age, history length, exposure counts, and surface identity so evaluation can reproduce cold slices. Serving should expose a feature or policy state that indicates how much direct evidence exists and which bootstrap path is active.

The system should log candidate sources, prior type, onboarding/context features used, exploration propensity or reason code, entity age/history bucket, and transition state. This enables replay and attribution when a cold cohort underperforms.

* Conceptual object: Confidence-weighted bootstrap policy for cold users/items/surfaces.
* Training/data implementation: Point-in-time history counts, entity age, exposure logs, context/onboarding features, content embeddings.
* Stored artifact/state: Priors, content representations, coldness counters, policy thresholds/config.
* Serving path: Detect coldness → retrieve fallback/content candidates → score with prior/context → apply bounded exploration → log exposure.
* Component contract: The warm ranker cannot interpret missing history as ordinary zero-valued history without an explicit missing/coldness signal.
* Logging: Candidate source, policy branch, exploration reason/propensity, history bucket, exposure, response.
* Versioning: Couple embeddings, index, model features, and cold-start policy config.
* Failure mode: A missing feature defaults silently to zero and sends known users through the cold path.
* Observability: Cold-slice quality, coverage, learning curve, branch rate, transition rate, and state freshness.
* Rollback: Revert to a known safe contextual-popularity policy.
* Testing/replay: Synthetic zero-history/new-item fixtures and replay by historical coldness bucket.

#### 7. Vertical Transfer

The mechanism transfers: when direct evidence is weak, use a prior, content/context signals, bounded exploration, and explicit cold-slice evaluation. What must be re-derived is the data-generating process, the cost of exploration, the relevant context, and the product objective.

**E-commerce/items:** The invariant is useful product discovery. New items can use taxonomy, text/image embeddings, brand, price, availability, and seller signals. Exploration is constrained by inventory, margin, and user purchase intent.

**Video/feed:** The invariant is rapid preference learning. New users provide rich implicit signals—watch time, completion, skips—within a session, so the system can adapt quickly. The cost of a poor exposure is often lower than in commerce, allowing more exploration.

**Ads:** The invariant is allocating impressions under uncertainty, but exploration is economically constrained by advertiser budgets, auction dynamics, and user experience. Calibration and value estimates matter more because scores feed directly into economic decisions.

**Marketplace:** The invariant includes both consumer utility and provider opportunity. Cold-start treatment must prevent a rich-get-richer loop where new providers cannot obtain the exposure required to establish quality.

* Invariant: Bootstrap useful recommendations before enough direct behavioral evidence exists.
* Different data-generating process: In a marketplace, exposure itself determines whether new providers can collect transactions and ratings.
* Different objective: Consumer utility plus supply/provider health.
* Different candidates/features: Provider attributes, listing content, availability, distance, price, quality priors.
* Different constraints: Fairness, concentration, capacity, seller inventory, geographic eligibility.
* Metric change: Consumer conversion plus provider exposure/activation and concentration metrics.
* Serving change: Reserve bounded, eligibility-aware exploration capacity by market/category.
* Ecosystem effect: Too little exploration entrenches incumbents; too much harms consumer trust.
* Validation: Measure both user outcomes and provider cold-to-warm progression in experiments.

#### 8. Objective and Metric Mismatch

Execution failure and objective mismatch are different. An execution failure means the intended bootstrap policy was not actually served—for example, new items never entered the candidate pool. Objective mismatch means the policy was served correctly but optimized the wrong proxy—for example, maximizing first-session CTR by showing only globally popular items while failing to learn user preferences or provide new-item exposure.

This distinction matters because cold-start interventions often reduce an immediate metric while improving information gain, catalog health, or long-term retention. A system should therefore verify execution first, then decide whether the objective itself captures bootstrap value.

* Offline/model metric: First-session CTR or NDCG on cold users.
* Online/product outcome: Retention, conversion, satisfaction, and speed of personalization; for items, successful exposure and cold-to-warm progression.
* Execution verification: Confirm cold policy branch rates, candidate coverage, quotas, and exposure logging.
* Metric semantics: Immediate ranking quality measures exploitation, not necessarily information gain.
* Blind spots: Long-term learning, catalog/provider coverage, and exposure bias.
* Missing product factor: Value of information from early interactions.
* Repair: Optimize a constrained combination of immediate utility and learning/coverage objectives, or evaluate them jointly.
* Trade-off: Some short-term relevance may be sacrificed to learn faster or support healthy supply.
* Online validation: Run experiments with cold-slice learning curves and guardrails, not only aggregate CTR.

## Material Follow-ups / Scenario Variants

### A brand-new item has excellent content similarity but zero collaborative evidence. How should it enter the system?

Use content-based retrieval or metadata-driven candidate generation so the item is eligible immediately, then allocate bounded exploratory exposure in contexts where the prior predicts plausibility. Log every exposure and update the item estimate as feedback arrives. Do not treat lack of clicks before exposure as evidence of poor quality. Validate by item-age and exposure-count slices, and compare cold-to-warm progression against a popularity-only baseline.

### A new user skips onboarding. What is the fallback?

Start from contextual priors such as locale, device, time, acquisition context, and safe regional/category popularity. Use early behavioral signals with high information content—skips, dwell, completion, repeated clicks—to adapt quickly. Preserve diversity in the first few slates so the system can learn rather than repeatedly serving the same global head. Measure first-session quality and the rate at which personalization improves after the first few observations.

### Aggregate recommendation metrics improve, but users with fewer than three prior interactions regress sharply. What should happen?

Treat this as a slice-level product regression, not as acceptable aggregate noise. First verify execution: whether the cold-start branch, priors, onboarding signals, and exploration rules were served as intended. Then localize the loss by user-history bucket, candidate source, and surface. If warm users dominate the aggregate gain, the rollout may need to be blocked or segmented until the cold policy is repaired. Validation should require recovery of the cold slice without erasing the warm-user gain.

### How should the system decide when an entity is no longer cold?

Avoid a single arbitrary interaction-count threshold when confidence differs by signal quality. Prefer a confidence or evidence-based transition using history amount, recency, signal reliability, and posterior uncertainty. In a simpler production design, history buckets can approximate this rule. The transition should be monotonic and observable: as reliable evidence accumulates, prior weight falls and personalized weight rises. Validate with learning curves to ensure the switch does not create a discontinuity in quality.
