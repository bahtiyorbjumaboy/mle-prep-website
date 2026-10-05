---
type: interview-answer
item: "2027:R05"
title: "Cold Start and Bootstrap Strategies"
created: "2026-10-02"
updated: "2026-10-05"
tags:
  - recommendation-systems
  - cold-start
  - bootstrap
  - exploration
  - evaluation
---

## Canonical Staff-Depth Question

Distinguish new-user, new-item, new-surface, and sparse-history cold start. Explain priors, content features, popularity, exploration, onboarding signals, and evaluation slices.

## Mastery Answer

Cold start means the recommender does not yet have enough interaction evidence for the entity or context it normally personalizes from. I separate four cases because the missing information is different in each one.

For a **new user**, there is little or no behavioral history, so I start from population or segment priors, contextual signals, onboarding choices, and safe popularity/trending candidates, then explore to learn preferences quickly. For a **new item**, user history may be rich but the item has no interaction statistics, so I rely on content or metadata representations, creator/seller/category priors, and controlled exploration to earn exposure. For a **new surface**, the main problem is domain transfer: even known users and items may have unknown behavior because position, intent, UI, and objective differ, so I use conservative priors, transferable features, and explicit experiments rather than assuming old-surface behavior transfers. For **sparse history**, there is some evidence but not enough to trust a highly personalized model, so I shrink estimates toward priors and blend personalized signals with robust fallback sources.

The bootstrap strategy should be explicit in the serving policy. I usually combine: a prior or fallback ranking, content-based retrieval or scoring, popularity/trending with guardrails, onboarding/context signals when available, and exploration that is bounded by product risk. As evidence accumulates, the system should transition smoothly from prior-driven to behavior-driven ranking rather than switching abruptly.

I would evaluate cold start on dedicated slices rather than aggregate metrics: zero-history users, low-history users, item-age buckets, first-impression or first-N-impression items, and new-surface cohorts. I would measure both immediate utility and learning speed—for example CTR/conversion/watch metrics plus coverage, exposure of new items, time-to-first-good-recommendation, and regret or downstream quality from exploration. The main failure modes are popularity lock-in, starving new items of exposure, over-personalizing from tiny samples, unsafe exploration, and hiding poor cold-start performance inside strong mature-user averages.

## Learn the Concepts

### Foundation

A recommender predicts or ranks items using **evidence** about users, items, context, and prior interactions. Cold start happens when one of the evidence sources the system normally relies on is missing or too weak.

The central mental model is:

> **When personalized evidence is weak, start from a reasonable prior, use side information that does not require interaction history, gather informative feedback safely, and gradually let observed behavior outweigh the prior.**

This is a bootstrap problem. The system begins with uncertainty, chooses useful defaults, observes outcomes, and updates its beliefs or scores as evidence arrives.

Key terminology:

- **Prior:** A default belief or estimate used before much entity-specific evidence exists. A prior can be global, segment-specific, category-specific, geographic, contextual, or hierarchical.
- **Behavioral history:** Past impressions, clicks, watches, purchases, likes, skips, hides, dwell time, or other interaction signals associated with a user or item.
- **Content features:** Attributes available without interaction history, such as text, category, brand, image embeddings, creator, price, language, topic, or metadata.
- **Popularity / trending:** Scores derived from aggregate behavior across users. They provide strong defaults but can create feedback loops if used without exploration or diversity controls.
- **Exploration:** Intentionally allocating some exposure to uncertain options so the system can learn their value rather than repeatedly exploiting only known winners.
- **Onboarding signals:** Explicit information collected early, such as selected interests, followed creators, preferred categories, location, language, or stated goals.
- **Evaluation slice:** A subset of traffic evaluated separately because aggregate metrics can hide systematic failure. Cold-start slices are usually defined by user-history length, item age/exposure count, or surface age.
- **Shrinkage:** Combining a noisy entity-specific estimate with a more stable prior so that sparse evidence does not dominate too early.

The four cold-start cases differ in what evidence is missing:

1. **New-user cold start:** the user has little or no behavior.
2. **New-item cold start:** the item has little or no exposure or interaction history.
3. **New-surface cold start:** the product surface itself lacks behavioral evidence, even if users and items are known elsewhere.
4. **Sparse-history cold start:** some history exists, but it is too little or too noisy to support fully personalized estimates.

#### Concrete worked example

Consider a retail recommender with a user named Amina and a new running shoe.

Amina has just created an account. The shoe was added to the catalog this morning.

If the system depends only on collaborative filtering, both sides are problematic: Amina has no user interaction vector and the shoe has no interaction-derived item vector. A practical bootstrap policy might do the following:

- Start Amina with a prior based on broad site popularity plus context such as country, device, current page, and season.
- Ask one lightweight onboarding question such as preferred product categories or brands.
- Represent the new shoe from content: category = running shoes, brand, price, text description, image embedding, size availability, and other catalog metadata.
- Retrieve the shoe for users whose content or contextual profile is compatible even before the shoe has clicks or purchases.
- Allocate a controlled amount of exploration exposure so the system can observe whether the shoe performs well.
- As Amina clicks, saves, purchases, or skips products, increase the weight of her personal behavioral signals.
- As the shoe receives impressions and outcomes, increase the weight of its interaction-derived statistics.

The design is not simply "show popular items until data arrives." The goal is to combine useful priors with non-behavioral information and deliberate data acquisition so the system can move out of cold start efficiently.

### Core Interview Reasoning

A compact reasoning structure for R05 is:

**1. Identify what is cold.**

Ask which evidence source is missing: user history, item history, surface-specific behavior, or simply enough observations for a stable estimate. The remedy depends on the missing evidence.

**2. Choose a prior or fallback.**

Use a robust default such as global popularity, segment popularity, category priors, editorial/business rules, or a broad non-personalized ranker. The prior should be safe, measurable, and appropriate to the product objective.

**3. Add side information that does not require the missing history.**

For users, use context, onboarding, geography, language, device, referral source, or declared interests. For items, use metadata, text, image/audio/video embeddings, brand, creator, category, price, or graph relationships that exist at ingestion time.

**4. Explore to acquire information.**

Without exposure, new items cannot generate interaction data. Without trying diverse options, a new user's preferences may remain unknown. Exploration should be controlled so the system learns without causing excessive quality loss or violating product constraints.

**5. Transition from prior-driven to evidence-driven behavior.**

Avoid a hard switch after an arbitrary number of events. Instead, increase trust in entity-specific estimates as evidence becomes more reliable. A generic shrinkage form is:

$$
\hat{s} = \frac{n}{n + \lambda} \hat{s}_{\text{entity}} + \frac{\lambda}{n + \lambda} s_{\text{prior}},
$$

where $n$ is the amount of evidence and $\lambda$ controls how strongly the system trusts the prior. When $n$ is small, the prior dominates; as $n$ grows, the entity-specific estimate dominates.

**6. Evaluate cold-start slices explicitly.**

Aggregate metrics are dominated by mature users and mature items in many systems. Report zero-history, low-history, new-item-age, and first-N-exposure slices separately. Measure both user utility and whether the system is actually learning fast enough to leave cold start.

#### New-user cold start

What is missing: user-specific behavioral evidence.

Useful mechanisms:

- global or segment priors;
- contextual ranking;
- onboarding interests;
- popularity/trending;
- content-based recommendations from the current session;
- session signals as soon as they appear;
- exploration across categories or creators.

Important trade-off: onboarding can produce high-information signals quickly, but every extra question adds friction and may reduce activation. Passive context has low friction but can be weak or noisy.

#### New-item cold start

What is missing: item-specific exposure and response data.

Useful mechanisms:

- content or multimodal embeddings;
- category/brand/creator priors;
- seller or source quality signals;
- semantic similarity to established items;
- controlled exploration or new-item quotas;
- temporary freshness boosts with caps.

Important trade-off: a system that ranks only by observed engagement can create an exposure trap. New items receive no impressions because they lack engagement, and they lack engagement because they receive no impressions.

#### New-surface cold start

What is missing: evidence that behavior transfers to the new UI, placement, intent, or objective.

Examples include launching a new home-page module, a new notification channel, or a new "short video" surface inside an existing product.

Useful mechanisms:

- transfer user/item representations that are likely to remain meaningful;
- use conservative priors from related surfaces;
- preserve surface-specific context features;
- randomize or explore enough to measure the new surface independently;
- train a new surface-specific ranker once sufficient logs exist.

Important trade-off: cross-surface transfer reduces data requirements, but blindly reusing old-surface engagement can encode the wrong objective or position/examination behavior.

#### Sparse-history cold start

What is missing: reliable statistical evidence, not necessarily all evidence.

Useful mechanisms:

- Bayesian or empirical-Bayes shrinkage;
- regularization;
- blending personalized and global scores;
- confidence-aware ranking;
- minimum-support thresholds for volatile features;
- hierarchical priors, for example user → segment → global or item → category → global.

Important trade-off: reacting too quickly creates unstable personalization; reacting too slowly wastes useful early signals.

### Deeper Reasoning and Derivations

#### Why priors matter

Suppose a new item has 1 click from 1 impression. Its empirical CTR is 100%, but ranking it as a proven 100% CTR item is unreasonable because the sample is tiny. A mature item with 5,000 clicks from 100,000 impressions has a 5% CTR estimate supported by far more evidence.

A prior prevents tiny samples from causing extreme estimates. One simple Bayesian model is a Beta prior for a Bernoulli event such as click/no-click:

$$
p \sim \mathrm{Beta}(\alpha, \beta).
$$

After observing $c$ clicks and $m-c$ non-clicks, the posterior is

$$
p \mid \text{data} \sim \mathrm{Beta}(\alpha + c, \beta + m - c).
$$

The posterior mean is

$$
\mathbb{E}[p \mid \text{data}] = \frac{\alpha + c}{\alpha + \beta + m}.
$$

The prior contributes pseudo-count-like evidence. When $m$ is small, it prevents extreme estimates; as $m$ grows, the observed data dominates. The same logic appears in non-Bayesian shrinkage and regularized ranking features.

#### Why popularity is useful and dangerous

Popularity is useful because it is a low-variance aggregate signal. For a user with no history, popular items are often better than random items.

But popularity is endogenous to exposure. Items that are shown more often have more opportunities to collect clicks, which can increase their future score and cause a feedback loop:

$$
\text{more exposure} \rightarrow \text{more interactions} \rightarrow \text{higher estimated quality} \rightarrow \text{more exposure}.
$$

Therefore popularity should generally be combined with freshness, exploration, content relevance, diversity, and exposure-aware evaluation rather than treated as ground-truth quality.

#### Why exploration is necessary

A system cannot estimate the value of an item it never shows. Pure exploitation can therefore make uncertainty permanent.

Exploration trades short-term expected reward for information. The exact mechanism can range from simple randomization or quota-based exposure to contextual bandits. The core interview point is not that every cold-start system needs a sophisticated bandit; it is that the serving policy must create enough support to learn about uncertain users or items.

Exploration should be bounded by risk. For example:

- do not explore unavailable or policy-violating items;
- reduce exploration on high-stakes surfaces;
- use eligibility filters before exploration;
- cap the fraction of a slate or traffic devoted to exploration;
- monitor user harm, hide/report rates, conversion loss, or other guardrails.

#### Why new-surface cold start is different

A new surface can have known users and known items but still be cold because behavior is conditional on presentation and intent. A user's preference on a product-detail page may not transfer directly to push notifications. Position bias, attention, session intent, latency constraints, and reward definition can all change.

The transferable part is often the representation of users/items or broad priors. The non-transferable part is often the calibration, objective, exposure mechanism, and surface-specific interaction pattern.

#### Why aggregate metrics hide the problem

Assume 95% of traffic comes from mature users with CTR 10%, while 5% comes from new users with CTR 2%.

Aggregate CTR is

$$
0.95(0.10) + 0.05(0.02) = 0.096.
$$

A 9.6% aggregate CTR can look healthy even though the new-user experience is dramatically worse. If new users are strategically important, aggregate performance is not sufficient evidence of product quality.

Cold-start evaluation therefore needs explicit slices and enough sample size per slice.

#### Important failure modes

- **Popularity lock-in:** popular items dominate, reducing discovery and making exposure inequality self-reinforcing.
- **New-item starvation:** items without interactions receive too little exposure to ever accumulate evidence.
- **Overreaction to tiny samples:** one or two positive events create extreme personalization or item scores.
- **Underreaction:** strong early user intent is ignored for too long because the fallback remains dominant.
- **Bad transfer across surfaces:** old behavior is reused where intent or examination patterns differ.
- **Onboarding mismatch:** explicit stated preferences are treated as permanently authoritative even after observed behavior disagrees.
- **Unsafe exploration:** uncertain candidates violate quality, policy, inventory, or trust constraints.
- **Aggregate-metric blindness:** mature traffic hides poor new-user or new-item outcomes.
- **Exposure-biased evaluation:** new items look weak because they were only shown in difficult contexts or rarely exposed.
- **No transition policy:** the system has a cold-start fallback but no principled rule for when and how to rely more on learned personalization.

### Advanced Staff-Depth Considerations

The reusable Staff-level backbone for this item is:

`Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate`

Equivalently:

`Assumption → Mechanism → Evidence → Decision → Trade-off → Validation`

For this question, the baseline is: The baseline cold-start policy is: identify which evidence is missing, start from a robust prior, add side information that does not require the missing history, explore safely to acquire information, and transition smoothly from prior-driven to behavior-driven ranking. Coldness is a state of uncertainty, not a binary label.

The eight subsections below apply that same loop from different angles. Each explanation teaches the mechanism first; the filled template then compresses it into a reusable interview scaffold.

#### 1. Changed Constraints and Transfer Logic

Cold-start design changes with the availability and cost of information. Rich item metadata favors content retrieval; high onboarding friction favors passive context and fast session adaptation; risky surfaces require conservative exploration; rapidly changing supply makes ingestion freshness part of cold-start correctness.

A useful reasoning chain is:

`changed assumption → affected mechanism/stage → invariant → broken assumption → consequence → redesign → metric impact → trade-off → validation`

**Filled template for this item**

- **Original assumption:** The product can use moderate onboarding/context and bounded exploration to learn quickly.
- **Changed constraint:** Exploration becomes expensive or risky and onboarding friction must be near zero.
- **Invariant:** The system still needs useful first-request quality and a path to reduce uncertainty.
- **Broken assumption:** It can no longer acquire information aggressively through explicit questions or broad exploratory exposure.
- **Consequence:** Learning slows and popularity/prior lock-in becomes more likely.
- **Design change:** Strengthen content/context priors, use low-friction session signals, route exploration to safer slots/surfaces, and apply confidence-aware blending.
- **Metric impact:** Track first-session utility, learning speed, exploration cost/harm, cold-slice coverage, and time-to-stable personalization.
- **Trade-off:** Safer experience versus slower preference/item-quality discovery.
- **Validation:** Compare onboarding/exploration policies in cold slices using immediate utility plus learning/regret and guardrail metrics.

#### 2. Failure Modes and Diagnosis

Cold-start failures should be localized by whether the system fails to generate viable candidates, rank them, expose them enough to learn, or measure them correctly. Aggregate mature-user metrics are especially misleading because they can hide new-user/new-item starvation.

**Filled template for this item**

- **Symptom:** Aggregate metrics remain healthy but new-item recall/exposure and first-session user utility deteriorate.
- **Stage decomposition:** ingest/content features → candidate generation → prior/blend/rank → exploration/exposure → feedback collection → transition policy.
- **Slices:** User-history count/recency, item age/impression count, surface age, source attribution, onboarding completion, exploration flag.
- **Competing hypotheses:** Content/index ingestion lag; popularity domination; exploration allocation collapse; ranker missing defaults; biased aggregate evaluation.
- **Discriminating evidence:** Content-source recall, time-to-retrievable, exposure share by item age, fallback/source mix, and learning curves.
- **Offline/online comparison:** Ensure cold items/users are represented under realistic exposure and missing-feature semantics.
- **Replay/isolation:** Compare cold routes with/without content source, exploration, or prior blending on identical requests.
- **First divergence:** Earliest point where cold entities lose candidate opportunity or exposure relative to baseline.
- **Immediate mitigation:** Increase safe fallback/content quotas or revert a starvation-causing policy.
- **Permanent prevention:** Cold-slice SLOs, minimum exposure/support rules, ingestion freshness alerts, and transition-policy tests.

Memory aid: `Symptom → Slice → Stage → Hypotheses → Evidence → First divergence → Fix`.

#### 3. Latency and Resource Trade-offs

Cold-start mechanisms are often ideal for precomputation: popularity/segment priors, item content embeddings, catalog metadata, and fallback lists. Under a tight request budget, move expensive item understanding to ingestion and keep online logic to lightweight context/session features and deterministic blending.

**Filled template for this item**

- **Budget:** Tight request p99 for the first/cold interaction.
- **Cost decomposition:** Context/user state + candidate sources + content/vector retrieval + blending/ranking + exploration/constraints.
- **Dominant cost:** Online content encoding or too many cold-start sources if not precomputed.
- **Quality driver:** Richer content/context and more source diversity improve cold-start relevance and coverage.
- **Cost driver:** More online encoders/fan-out/features increase latency and compute.
- **Optimization knobs:** Precompute item embeddings, cache priors, compact session features, route sources by cold state, batch ANN, and simplify blends.
- **Fallback/degradation:** Global/segment priors plus safe content/popularity candidates with hard constraints.
- **Trade-off curve:** Cold-slice utility/coverage/learning speed versus p99 and serving cost.
- **Decision:** Preserve the highest-information low-cost signals and move expensive stable work off the request path.

Memory aid: `Budget → Breakdown → Bottleneck → Knobs → Quality loss → Fallback`.

#### 4. Scale and Capacity

At scale, cold-start handling must be a first-class route, not a rare exception. High catalog churn creates a continuous population of new items; large user growth creates sustained new-user traffic. Ingestion, feature/index readiness, prior computation, and exploration accounting must scale continuously.

**Filled template for this item**

- **Scaling dimension:** Catalog/users grow while new items arrive continuously and must be recommendable within minutes.
- **Baseline scale assumption:** Content features/index insertion and cold-state routing keep up with arrivals.
- **First bottleneck:** Ingestion-to-retrievable latency and exploration capacity become limiting.
- **Second-order effects:** Larger fresh-item queues, stale embeddings, source imbalance, feedback sparsity, and provider exposure concentration.
- **Architectural response:** Streaming/incremental item feature+embedding generation, fresh-item side channel/delta index, scalable priors, and explicit cold-state routing.
- **Partitioning/replication/caching/batching:** Partition indexes by domain/region, batch embedding generation where safe, cache segment priors, and meter exploration quotas.
- **Consistency/freshness consequence:** New items can exist in catalog but not in features/index, creating silent exclusion.
- **Operational failure mode:** “Available” supply is systematically unretrievable until the main index refreshes.
- **Validation:** Time-to-retrievable SLO, cold-item recall/exposure, ingestion backlog, p99, and projected-arrival load tests.

Memory aid: `What grows? → What stops fitting? → What bottlenecks? → How do we partition? → What new failure appears?`.

#### 5. Freshness, State, and Versioning

Cold-start quality is unusually freshness-sensitive because an entity may have no fallback behavioral signal. If content embeddings or index insertion lag, a new item can be invisible; if trending priors are stale, the cold-user default can become actively wrong. Freshness clocks should be explicit by source.

**Filled template for this item**

- **State that becomes stale:** New-item metadata/embeddings/index state, popularity/trending priors, session intent, onboarding signals, and cold-state counters.
- **Why freshness matters:** Stale state can exclude new items or make cold users receive outdated priors.
- **Required freshness:** Minutes for newly ingestible supply in dynamic products; seconds/minutes for session intent; product-dependent for priors.
- **Refresh cost:** Embedding generation, index insertion, popularity aggregation, cache invalidation, and routing updates.
- **Update architecture:** Incremental/streaming ingestion for new supply plus periodic stable priors and online session state.
- **Version consistency:** Item metadata/embedding/index versions and cold-state counters must align with serving eligibility.
- **Failure from version skew:** Item appears eligible but has no compatible vector/index entry or stale attributes.
- **Fallback:** Fresh-item content/exact side channel until primary ANN/index catches up.
- **Measurement:** Catalog-create-to-retrievable age, prior age, session-state age, and cold-slice quality by freshness bucket.
- **Decision:** Prioritize freshness where missing state would otherwise make the cold entity effectively invisible.

Memory aid: `What goes stale? → How fast does it matter? → What does refresh cost? → How do versions stay consistent?`.

#### 6. Implementation, Serving, and Observability

Production cold start requires explicit coldness features/state and provenance: user history count/recency, item age/exposure/interaction count, surface ID, onboarding source/time, content-embedding version, candidate-source attribution, and exploration flag/propensity. Without them the system cannot reproduce or debug why a cold entity received its treatment.

**Filled template for this item**

- **Conceptual object:** A confidence-aware bootstrap policy that blends priors, side information, and exploration until evidence is sufficient.
- **Training/data implementation:** Build cold-slice labels/features and train/evaluate content/prior/personalized components under realistic history cutoffs.
- **Stored artifact/state:** Segment/global priors, item content embeddings, user/item cold-state counters, onboarding/context state, exploration config.
- **Serving path:** Detect cold state → route/fan out safe prior/content/context sources → blend/rank → apply exploration/constraints → log provenance.
- **Component contract:** Cold-state definitions and transition thresholds/weights must match offline evaluation and serving.
- **Logging:** History count/recency, item age/exposure, source attribution, exploration flag/propensity, onboarding provenance, versions.
- **Versioning:** Content model/index, priors, transition policy, and exploration config.
- **Failure mode:** Popularity-only fallback persists too long or new items never enter retrieval/exposure.
- **Observability:** Cold-slice recall/utility, source mix, exposure share, learning speed, ingestion freshness, and fallback frequency.
- **Rollback:** Restore prior routing/blending/exploration policy and compatible content/index versions.
- **Testing/replay:** Synthetic zero/sparse-history cases and first-N-exposure trajectories should be reproducible.

Memory aid: `Train → Store → Serve → Version → Log → Monitor → Roll back`.

#### 7. Vertical Transfer

The mechanism should transfer; the assumptions must be re-derived. Use the checklist:

`labels → candidate sources → objectives → features → constraints → evaluation → experiments → serving/freshness → ecosystem effects`

Representative verticals:

- **Video/feed:** **Invariant:** Prior → side-info → exploration → adaptation transfers. **Different assumption:** Fresh content/session intent and creator/topic diversity matter; feedback arrives rapidly. **Technical consequence:** Use content/creator embeddings, fast session adaptation, and bounded exploration.
- **E-commerce:** **Invariant:** Bootstrap logic transfers. **Different assumption:** Inventory/price, category/brand metadata, seasonal demand, and conversion value matter. **Technical consequence:** Use content/category priors with inventory-safe exploration and value-aware evaluation.
- **Ads:** **Invariant:** Uncertainty bootstrap transfers. **Different assumption:** Exploration costs money and calibration/budget constraints are strict. **Technical consequence:** Use conservative campaign/creative priors, tight eligibility, and controlled exploration.
- **Marketplace:** **Invariant:** Cold entity logic transfers to both demand and supply. **Different assumption:** Provider cold start and two-sided exposure/fairness matter. **Technical consequence:** Use provider quality priors/content and protect against exposure concentration.
- **Notifications:** **Invariant:** Need-to-learn transfers. **Different assumption:** Bad exploration is intrusive and frequency budget is scarce. **Technical consequence:** Use stronger priors/confidence thresholds and learn on less intrusive surfaces when possible.

**Filled transfer template — Video/feed**

- **Invariant:** Prior → side-info → exploration → adaptation transfers.
- **Different data-generating process:** Fresh content/session intent and creator/topic diversity matter; feedback arrives rapidly.
- **Different objective:** Re-derive the primary product utility for this vertical rather than copying the base objective.
- **Different candidates/features:** Candidate sources and features should reflect the vertical-specific context and available signals.
- **Different constraints:** Fresh content/session intent and creator/topic diversity matter; feedback arrives rapidly.
- **Metric change:** Retain transferable stage metrics, then add vertical-specific outcomes and guardrails.
- **Serving change:** Use content/creator embeddings, fast session adaptation, and bounded exploration.
- **Ecosystem effect:** Check creator/provider/seller/advertiser or user-side concentration where relevant.
- **Validation:** Evaluate both transferable retrieval/ranking quality and the vertical-specific product outcome.

Memory aid: `Keep the mechanism; re-derive the assumptions.`

#### 8. Objective and Metric Mismatch

Cold-start systems are vulnerable to proxy mismatch because the easiest immediate metric often rewards the safest/popular option, which can suppress exploration and future personalization. A policy can improve short-term CTR while worsening coverage, learning speed, new-item discovery, retention, or provider health.

**Filled template for this item**

- **Offline/model metric:** Immediate CTR/NDCG under the cold-start fallback improves.
- **Online/product outcome:** New-item discovery, learning speed, retention, coverage, or provider health worsens.
- **Execution verification:** Confirm routing, source quotas, exploration, priors, and cold-state detection execute as designed.
- **Metric semantics:** Short-term CTR rewards immediately safe/popular choices.
- **Blind spots:** Information gain, future personalization, exposure fairness, cold-item opportunity, long-term satisfaction.
- **Missing product factor:** The value of learning and ecosystem discovery is absent from the immediate proxy.
- **Repair:** Add learning-speed/regret, coverage/exposure, long-term/activation guardrails, or explicit exploration objectives.
- **Trade-off:** More exploration/discovery can reduce immediate reward or increase risk.
- **Online validation:** Experiment by cold cohort with immediate utility, learning trajectory, long-term outcomes, and harm guardrails.

Memory aid: `Did we execute the objective incorrectly, or correctly optimize the wrong objective?`

## Material Follow-ups / Scenario Variants

### A new user arrives with zero history. What should the first request do?

Use a robust non-personalized or lightly contextual prior rather than trying to fabricate personalization. Candidate sources might include global/segment popularity, trending, contextual relevance, editorial or policy-safe pools, and content matching to the current request. If onboarding data exists, incorporate it, but treat it as uncertain and allow observed behavior to override it. Introduce bounded exploration so the first few interactions reveal preferences. Log which source supplied each candidate so early-session performance can be measured by source and slice.

### A new item is high quality but receives almost no impressions. How would the design change?

This is an exposure problem as much as a prediction problem. If the ranker requires historical engagement, the item may never get the data needed to prove itself. Add a content-based path so the item can be retrieved immediately, then reserve controlled exposure for eligible new items or use uncertainty-aware exploration. Evaluate new items by age and impression count, not only by raw historical engagement. Guard against gaming by requiring content quality, inventory, policy, and eligibility checks before exploration.

### A new recommendation module is launched for existing users and existing items. Why is that still cold start?

Because the missing evidence is surface-specific. The UI position, interaction affordances, attention pattern, and product objective may differ from existing surfaces. Reuse user/item representations and broad priors when appropriate, but do not assume calibration, CTR, position effects, or optimal ranking weights transfer. Launch with conservative defaults and enough randomized or controlled traffic to estimate the new surface's behavior directly.

### New items arrive continuously and must be recommendable within minutes. What changes?

The ingestion-to-serving path becomes part of cold-start correctness. Content features, embeddings, eligibility state, and index insertion must be produced quickly enough that a new item can enter candidate generation before it has behavioral data. Monitor time from catalog creation to retrievable state. If the ANN or feature pipeline updates too slowly, maintain a fresh-item side channel or exact/content fallback until the main index catches up.

### How does cold start differ across e-commerce and notifications?

In e-commerce, exploration can often be performed within a slate while inventory, price, availability, and conversion value constrain ranking. New-item content and category metadata are strong bootstrap signals. In notifications, each exposure is intrusive and may consume a limited attention budget, so exploration is more expensive. The notification policy should use stronger priors, eligibility rules, frequency caps, and confidence thresholds, gathering information from less intrusive surfaces when possible before sending uncertain notifications.
