---
type: interview-answer
item: "2027:R03"
title: "Training-Set Construction and Point-in-Time Correctness"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - training-data
  - point-in-time-correctness
  - temporal-leakage
  - data-quality
---

## Canonical Staff-Depth Question

Starting from impression, click, watch, cart, purchase, hide, dwell, and catalog logs, design a reproducible training table with grain, attribution, deduplication, censoring, temporal splits, late events, and leakage tests.

## Mastery Answer

I would start by defining the **prediction decision** and the **row grain**, because every other choice depends on what one row means. For a ranking model, a common grain is one `(request or impression, user, item, decision_time)` row: the item was eligible and exposed at a specific decision time, and all features must represent information available no later than that time. I would persist stable identifiers for the request, impression, user/session, item, surface, position, policy/model version, and event timestamps so the table can be rebuilt exactly.

Next I define labels as **attribution rules**, not as raw joins. A click may be attributed within minutes, a cart within hours, and a purchase within days. Those windows determine which downstream events belong to which impression. I would explicitly handle repeated impressions, multi-touch behavior, and precedence rules so one purchase is not accidentally credited to several training rows unless that is intentionally the target definition. I would distinguish event time from ingestion time and define whether labels are based on event occurrence or observation by a cutoff.

Then I make the table **point-in-time correct**. For a row at time $t$, every feature join is an as-of join using only records with an availability timestamp at or before $t$. Catalog state, inventory, price, user history, aggregates, embeddings, and model-derived features must all use versions that existed at that decision time. A feature with an event timestamp before $t$ can still leak if it was not actually available to the online system until after $t$, so I track both event time and availability/processing time where necessary.

I handle **deduplication and identity** before labeling. Logs often contain retries, duplicate events, client/server copies, repeated clicks, or idempotency failures. I deduplicate with stable event IDs when possible, otherwise with a documented composite key and time tolerance. The rule must be deterministic and tested, because silent duplication changes both feature statistics and label prevalence.

I handle **censoring** explicitly. If a purchase label requires a 7-day observation window, rows from the last 7 days cannot yet be treated as negatives. I either exclude them from supervised training, mark the label unresolved, or use a method designed for delayed outcomes. This prevents “not observed yet” from becoming “negative.”

For splitting, I use **temporal splits** based on decision time, with any required gap or embargo to prevent label-window overlap. I never randomly split rows when user behavior, catalog state, or exposure policy evolves over time, because that allows future regimes to inform the past and inflates offline performance.

Late-arriving events are handled through immutable raw logs plus versioned rebuilds or bounded backfills. A run records its input snapshot/watermark, code/config version, attribution policy, feature definitions, and output version. Re-running the same logical snapshot must produce the same table.

Finally, I prove correctness with **leakage and invariant tests**: no feature availability time exceeds decision time; no label event falls outside its attribution window; censored rows are not negative; dedup keys are unique; temporal partitions do not overlap illegally; and synthetic fixtures deliberately containing future events must fail. At D3 depth, the key principle is that every row, feature, and label is a modeling decision with a temporal contract, and reproducibility means that contract is encoded, versioned, and testable.

## Learn the Concepts

### Foundation

The central mental model is:

**A training row is a historical simulation of one prediction-time decision.**

If the production recommender had to rank an item for a user at 10:00 AM on Tuesday, then the training row representing that decision must contain only what the production system could have known by 10:00 AM Tuesday. The row's target can describe what happened later, but its inputs cannot.

That gives us two different time directions:

- **Features look backward** from the decision time.
- **Labels look forward** from the decision time, but only inside a defined observation/attribution window.

This is the essence of point-in-time correctness.

A useful row grain for recommendation ranking is:

`one eligible/exposed item for one user/session at one ranking decision time`

Depending on the system, the grain may instead be one candidate, one impression, one user-item-day, or one session-item opportunity. The important point is that the grain is explicit. If the grain is unclear, duplication, attribution, and leakage become almost impossible to reason about.

Key terms:

- **Impression:** evidence that an item was actually rendered or exposed to the user.
- **Interaction:** an event such as click, watch, dwell, cart, purchase, or hide.
- **Decision time:** when the recommender had to make the prediction.
- **Event time:** when an event actually happened.
- **Ingestion time:** when the data system received the event.
- **Availability time:** when a value could actually have been used by the online/offline feature pipeline.
- **Attribution window:** the time interval in which a downstream event is credited to an earlier exposure.
- **Censoring:** a label is unresolved because not enough future time has elapsed to observe the outcome.
- **Temporal leakage:** future information is present in a feature or data-selection rule for an earlier prediction.
- **Deduplication:** converting repeated records for the same logical event into one deterministic event.
- **Late event:** an event whose ingestion/processing happens substantially after its event time.

A beginner often conflates **event time** with **feature availability**. Suppose a warehouse correction says an item's inventory was 0 at 9:55 AM, but the correction was not written into the feature store until 10:10 AM. For a ranking decision at 10:00 AM, using the corrected value leaks future operational knowledge even though its business event time is 9:55 AM.

Another common conflation is **non-interaction equals negative**. If an item was never shown, its lack of click is not evidence that the user rejected it. Even among impressions, a non-click may reflect position, examination, or insufficient observation time. R03 is primarily about building the temporal table correctly; the exposure-bias interpretation is handled more deeply elsewhere, but the table must preserve enough exposure metadata to support that reasoning.

**Worked example**

Assume a recommendation carousel shows item `A` to user `U` at 12:00.

- Impression: 12:00
- Click: 12:03
- Cart: 12:20
- Purchase: 18:00
- Price changed from $20 to $25 at 14:00
- A user-history batch was computed at 11:50 and published at 11:57
- Another history aggregate was computed at 11:59 but published at 12:05

If the training row's decision time is 12:00:

- the $20 price is valid; the $25 price is future information;
- the 11:57-published history is valid;
- the 12:05-published aggregate is invalid even if it summarizes only events before noon;
- click/cart/purchase can become labels if their attribution windows include those times;
- if the purchase label uses a 24-hour window, the row must not be finalized as a negative until 12:00 the next day.

That one example contains the major temporal rules for the entire question.

### Core Interview Reasoning

A strong answer can be reconstructed with this sequence:

**decision + grain → event contract → attribution/labels → point-in-time features → deduplication → censoring → temporal split → late-event/rebuild policy → leakage/invariant tests**

1. **Decision + grain**

   First say what the model predicts and what one row means. For example, “one exposed candidate at one request time.” This anchors uniqueness, features, labels, and split semantics.

2. **Event contract**

   Identify the source logs and the identifiers/timestamps required to connect them: request ID, impression ID, user/session ID, item ID, event ID, event time, ingestion time, position, surface, policy/model version, and catalog version. Without a logging contract, downstream SQL cannot recover truth reliably.

3. **Attribution and labels**

   Turn raw outcomes into explicit modeling targets. A click, watch, dwell threshold, cart, purchase, and hide each needs its own attribution semantics. Define windows, repeated-exposure policy, precedence, and multi-touch handling.

4. **Point-in-time features**

   For every feature, ask: “What exact value was available at the decision time?” Use as-of semantics and versioned snapshots. A historical value is not automatically valid; it must also have been available to the system at that time.

5. **Deduplication**

   Define one logical event and a deterministic uniqueness rule. Deduplication must happen before aggregates and labels when duplicates could inflate counts or produce multiple positives.

6. **Censoring**

   Do not convert “outcome not observed yet” into a negative. Delay finalization, exclude unresolved rows, or explicitly model delayed feedback.

7. **Temporal splitting**

   Train on earlier decisions and validate/test on later decisions. Account for label windows and any overlap that could transmit information across the boundary.

8. **Late events and reproducibility**

   Choose a watermark/backfill policy. Preserve immutable raw events, table-building code/config, source snapshot IDs, and output dataset versions so a historical build can be recreated.

9. **Leakage and invariant tests**

   Convert correctness claims into executable assertions. The strongest answer ends with proof obligations rather than “we are careful with timestamps.”

The ordering matters. If attribution is defined before grain, it is unclear which exposure owns an event. If features are built before decision time is defined, point-in-time correctness is undefined. If splitting occurs before censoring is handled, the newest validation rows may be systematically mislabeled.

### Deeper Reasoning and Derivations

**1. Why point-in-time joins require an availability timestamp**

For a feature row to be valid for a decision at time $t_d$, the core condition is not merely

$$
t_{\text{event}} \le t_d.
$$

The stronger operational condition is

$$
t_{\text{available}} \le t_d.
$$

A value can describe the past and still leak if it was computed, corrected, or published only in the future. This is why mature pipelines often track event time, processing time, and feature/materialization time separately.

**2. Attribution is part of the statistical target**

Suppose a purchase occurs after three impressions of the same item. Crediting all three impressions as positive creates three training positives from one business outcome. Crediting only the last impression imposes a last-touch assumption. Crediting the first imposes another assumption. There is no attribution-free label here: the training target is partly defined by the attribution policy.

A defensible pipeline therefore versions attribution logic just like model code.

**3. Censoring changes apparent class balance**

Assume a purchase label has a 7-day conversion window. A row generated yesterday has had only one day to convert. If it is marked negative today, the recent part of the data is biased toward negatives. This can create a false temporal trend in label rate and make newer validation slices appear harder than older ones.

A simple maturity condition is:

$$
t_{\text{dataset cutoff}} - t_{\text{decision}} \ge W,
$$

where $W$ is the maximum observation window required to finalize the label. Rows that do not satisfy it are unresolved unless the modeling method explicitly handles censoring.

**4. Temporal splitting must respect the target window**

Suppose training decisions end on June 30 and validation begins July 1, while purchase labels use a 7-day window. A June 30 training row can depend on a July 5 purchase. That may be acceptable if the split is defined by decision time and the objective is future generalization, but it means the training dataset cannot be finalized on June 30. It also means any features or aggregates derived from outcomes must not feed those July events back into earlier feature values.

For some evaluation protocols, an embargo or gap is useful when derived statistics, shared entities, or policy changes create cross-boundary dependence. The gap should be justified by the actual leakage mechanism, not applied ritualistically.

**5. Deduplication is a causal data issue, not cleanup trivia**

If a client retries a click event three times, an undeduplicated table may:

- turn one click into three labels;
- inflate user/item popularity;
- distort dwell or frequency features;
- alter negative sampling and class weights.

Deduplication therefore belongs before downstream aggregation. Stable event IDs are best; heuristic deduplication by `(user, item, event_type, time_bucket)` is weaker and should be documented because it can collapse legitimate repeated interactions.

**6. Late events create a reproducibility-versus-completeness choice**

A table built on Monday may differ from the same logical query rerun on Friday because late purchases have arrived. There are two legitimate products:

- an **as-known-at-the-time snapshot**, useful for audit/replay of what the pipeline knew then;
- a **latest-corrected historical snapshot**, useful for training with the most complete labels.

They are not interchangeable. Reproducibility requires naming which one is being built and versioning the input watermark/snapshot.

**7. Leakage can arise from row selection, not only feature columns**

Examples include:

- selecting only items that are known later to remain in the catalog;
- generating negatives from a future catalog snapshot;
- using a future popularity table to decide which examples enter training;
- filtering out users based on activity measured after the decision date.

A table can have individually “past-looking” features and still leak through its inclusion/exclusion logic.

**8. Leakage tests should be adversarial**

Static schema checks are insufficient. Useful tests intentionally construct:

- a future price update;
- a late-arriving purchase;
- duplicate retries;
- two repeated impressions before one conversion;
- a row whose label window is incomplete;
- a catalog item introduced after the decision time.

The test should fail if the pipeline admits any of these future facts into an earlier row.

### Advanced Staff-Depth Considerations

The universal Staff reasoning loop for R03 is:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate**

The baseline is a versioned training-table contract: one explicit row grain, timestamp semantics, attribution rules, point-in-time feature joins, maturity/censoring rules, and deterministic split/rebuild semantics. A change might be a longer conversion delay, a streaming feature source, a new surface, increased event volume, or a revised catalog policy. The mechanism is the way that change alters which facts are legally observable for a row, how outcomes can be attributed, or when labels become final. Evidence comes from timestamp distributions, duplication rates, label-maturity curves, row-count reconciliation, replay diffs, and deliberately adversarial leakage tests. The decision is usually a change to the data contract, watermark/backfill policy, join semantics, or label definition. The trade-off is among freshness, completeness, reproducibility, compute cost, and bias. Validation means rebuilding known fixtures and historical slices and proving temporal invariants.

The compressed form is:

**Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**

For R03, the key invariant is: **every feature and row-selection fact must have been available at the historical decision time, while every label must obey an explicit future observation contract.**

#### 1. Changed Constraints and Transfer Logic

The baseline assumes that event delays, label windows, and feature publication delays are sufficiently stable to encode in deterministic temporal rules. What should remain invariant is the historical-decision simulation: changing infrastructure or product behavior must not allow a training row to see information its production counterpart could not have seen.

Fragile assumptions include short conversion delays, one exposure per item/session, batch-complete logs, stable catalog identifiers, and a single recommendation surface. If conversions move from same-session to 30-day delayed outcomes, the label-maturity rule must change; if events become streaming and out of order, watermarks and event-time semantics become central; if multiple surfaces can expose the same item, attribution needs surface/request identity.

The propagation is:

**changed assumption → temporal/identity mechanism affected → original invariant retained → old rule becomes invalid → bias or irreproducibility appears → data contract changes → label/coverage/freshness metrics move → cost/freshness trade-off → replay and leakage tests validate**

Representative template:

- Original assumption: purchase labels mature within 7 days.
- Changed constraint: a new replenishment product has a 30-day conversion cycle.
- Invariant: an unresolved future purchase must never be encoded as a negative.
- Broken assumption: 7 days is enough to finalize purchase labels.
- Consequence: recent rows are mislabeled negative and newer temporal slices look artificially weak.
- Design change: use a 30-day maturity rule for that target/segment or separate short- and long-horizon targets.
- Metric impact: apparent positive rate drops initially; after correction, calibration and conversion recall should become more stable by cohort age.
- Trade-off: slower availability of fully labeled training data versus lower label bias.
- Validation: plot conversion accumulation by days-since-impression and run fixtures proving rows inside the 30-day window remain unresolved.

#### 2. Failure Modes and Diagnosis

R03 failures localize along a data-construction chain:

**raw events → identity/dedup → exposure grain → attribution/labels → point-in-time features → row selection → temporal split → materialized dataset**

Common failures include duplicate events, mismatched IDs, future feature joins, wrong catalog snapshots, conversion double-credit, immature negatives, late events omitted from some partitions, and temporal splits that accidentally share future-derived aggregates.

Diagnosis should look for the first stage where a reproducible count or timestamp invariant diverges. Start with cohort slices by decision date, surface, user segment, item age, and event-lag bucket. Compare raw event counts to deduplicated counts, exposed rows to labeled rows, and label rates as a function of cohort maturity. Replay a small historical interval using pinned snapshots.

Representative template:

- Symptom: offline validation AUC/NDCG jumps after a training-data rewrite.
- Stage decomposition: raw logs → dedup → impression rows → label attribution → feature joins → split.
- Slices: decision date, feature freshness lag, item age, and rows near split boundary.
- Competing hypotheses: genuine feature improvement, future feature join, duplicated positives, or censored negatives removed asymmetrically.
- Discriminating evidence: compare feature availability times to decision times, uniqueness counts, and label rates by cohort age.
- Offline/online comparison: offline gain with no online change raises suspicion that dataset semantics changed rather than model capability.
- Replay/isolation: rebuild a fixed week under old and new table code using the same immutable raw snapshot.
- First divergence: new feature join includes values published after decision time.
- Immediate mitigation: revert to the prior dataset version and block model promotion.
- Permanent prevention: add availability-time join guards and a synthetic future-feature test to CI.

#### 3. Latency and Resource Trade-offs

R03 is primarily an offline data-correctness problem, so online inference latency is not the dominant resource term. The important resource trade-off is **training-data build latency and cost versus temporal fidelity and completeness**.

Exact point-in-time joins over large event histories can be expensive because they require sorting/indexing by entity and time, versioned snapshots, and potentially repeated backfills. Long attribution windows increase the amount of state that must remain open before labels mature. Rebuilding corrected history after late events can consume substantial warehouse/storage bandwidth.

Quality-improving work includes finer-grained snapshots, exact as-of joins, longer label windows, and more complete late-event backfills. Cost can be controlled with partition pruning, incremental materialization, precomputed valid-time intervals, compact change-data-capture tables, and bounded backfill horizons when business semantics permit.

Representative template:

- Budget: finish the daily training-table build before the scheduled training job while preserving exact temporal semantics.
- Cost decomposition: raw scan + dedup + temporal joins + label attribution + validation + write/materialization.
- Dominant cost: repeated as-of joins over high-volume user/event history.
- Quality driver: using the correct historical feature version and complete-enough labels.
- Cost driver: event-history scan volume and backfill range.
- Optimization knobs: date/entity partitioning, incremental state tables, valid-time intervals, materialized historical features, and bounded recomputation.
- Fallback/degradation: train on the most recent fully validated prior dataset rather than silently relaxing point-in-time rules.
- Trade-off curve: fresher training data versus more compute and greater late-event uncertainty.
- Decision: prefer stale-but-correct data over fresh-but-temporally-invalid data.

#### 4. Scale and Capacity

The main scaling dimensions are event volume, number of users/items, feature count, history length, and number of surfaces. The first assumption that often breaks is that a full historical rebuild is cheap enough to run routinely.

At larger scale, temporal joins become shuffle-heavy, user histories become skewed, hot items generate enormous impression groups, and long attribution windows require more pending state. A single global table may also become operationally awkward when surfaces have different label semantics.

The response is usually partitioned incremental construction: immutable raw logs, compact deduplicated event layers, keyed historical feature snapshots, per-date/surface partitions, and deterministic backfill jobs. Scaling introduces new risks: partial partition rebuilds, inconsistent watermark cutoffs, schema/version skew, and hot-key stragglers.

Representative template:

- Scaling dimension: daily impression volume grows from tens of millions to billions.
- Baseline scale assumption: one daily warehouse rebuild can scan all relevant history.
- First bottleneck: shuffle and sort cost for user/item temporal joins.
- Second-order effects: hot-key skew, longer job tails, partial retries, and greater backfill cost.
- Architectural response: incremental event normalization plus partitioned point-in-time feature materialization.
- Partitioning/replication/caching/batching: partition by decision date and stable entity hash; cache/version slowly changing catalog state.
- Consistency/freshness consequence: each output partition must record the exact upstream watermark and feature snapshot versions.
- Operational failure mode: only some partitions are rebuilt after a late-event correction, creating mixed semantics.
- Validation: reconcile partition-level row/label counts and replay sampled entities end to end.

#### 5. Freshness, State, and Versioning

Freshness is central because R03 is about reconstructing what was known when. Relevant state includes user history, catalog/price/inventory state, derived aggregates, labels, attribution rules, schema versions, and experiment/policy assignments.

There are two distinct freshness questions:

1. Was the value fresh enough for the production decision at the time?
2. Has the historical dataset incorporated late corrections that arrived later?

Those lead to different artifacts. An audit snapshot may intentionally preserve “what we knew then,” while a retraining snapshot may incorporate corrected late labels. Both need explicit versions.

Representative template:

- State that becomes stale: user behavior aggregates and delayed purchase labels.
- Why freshness matters: stale features misrepresent the production state; immature labels misrepresent outcomes.
- Required freshness: feature freshness must match the serving contract; labels must satisfy their maturity window.
- Refresh cost: incremental feature recomputation plus bounded historical backfill.
- Update architecture: streaming or micro-batch feature updates with versioned daily training snapshots and late-event backfills.
- Version consistency: dataset version pins raw-log watermark, feature-definition version, catalog snapshot, attribution policy, and code/config commit.
- Failure from version skew: features built under one policy are paired with labels or catalog state built under another.
- Fallback: use the latest fully validated consistent snapshot.
- Measurement: feature-age distributions, late-event curves, snapshot-diff counts, and cohort label maturity.
- Decision: expose freshness/completeness as explicit dataset metadata rather than implicit pipeline behavior.

#### 6. Implementation, Serving, and Observability

The conceptual answer becomes operable only if the system records enough identity and timing metadata at serving time. A training pipeline cannot reconstruct impression-level decisions if serving logs omit candidate/exposure identifiers, model/policy versions, positions, or timestamps.

A production implementation typically has immutable raw event storage, a deterministic normalization/dedup layer, point-in-time feature reconstruction, a label-attribution job, versioned dataset manifests, validation gates, and replay tooling. Training consumes only published dataset versions that passed invariants.

Representative template:

- Conceptual object: one historical ranking opportunity with temporally valid features and explicitly attributed outcome.
- Training/data implementation: normalized impression/interactions joined by stable IDs, as-of feature joins, maturity-aware labels, temporal partitions.
- Stored artifact/state: immutable raw logs plus a versioned training-table manifest and materialized partitions.
- Serving path: recommender logs request/impression IDs, candidate/exposure metadata, feature/model versions, position, and decision time.
- Component contract: every feature source exposes availability/version semantics; every event source exposes stable identity and event/ingestion time.
- Logging: request, impression, item, user/session, position, policy/model version, event timestamps, and relevant catalog/version IDs.
- Versioning: code/config + raw watermark + feature definitions + attribution policy + catalog snapshot + dataset output version.
- Failure mode: training reconstructs rows from incomplete serving logs and silently invents exposure semantics.
- Observability: row counts, dedup rates, attribution rates, unresolved-label fraction, feature-age distributions, leakage-test results, and build lineage.
- Rollback: pin the previous validated dataset version and retrain/redeploy from it if a data release is invalid.
- Testing/replay: synthetic temporal fixtures plus sampled end-to-end historical replays.

#### 7. Vertical Transfer

The mechanism transfers across verticals: define the historical decision, preserve exposure identity, join only information available at that decision, define outcome windows, and separate unresolved from negative labels. What changes is the data-generating process.

- **E-commerce/items:** purchases may be delayed by hours or days, inventory and price change quickly, and repeated product views complicate attribution. Point-in-time catalog state and long conversion windows matter.
- **Video/feed:** watch time, completion, skip, and hide happen quickly, but session sequence creates strong dependence. Row grain may be an impression within a slate/session rather than an independent user-item example.
- **Ads:** exposure identity, auction context, propensity/policy logging, and conversion attribution are critical. Multiple ads/campaign touches make attribution especially policy-sensitive.
- **Notifications:** delivery, open, downstream session, and opt-out outcomes occur on different horizons; the system must distinguish sent, delivered, seen, and opened.
- **Marketplace:** item/seller availability and provider-side state change over time; labels may include both consumer response and provider/ecosystem outcomes.

Representative transfer template for ads:

- Invariant: features must be available at auction time and labels must follow explicit observation rules.
- Different data-generating process: exposure comes through an auction/pacing policy rather than a simple recommender carousel.
- Different objective: click/conversion/value may be combined with advertiser and platform constraints.
- Different candidates/features: bid, budget, campaign, auction, and pacing features become part of the row.
- Different constraints: policy eligibility, budget exhaustion, frequency caps, and auction mechanics.
- Metric change: calibration/value and policy-aware evaluation become more important.
- Serving change: exact auction/policy version and propensity/exposure context must be logged.
- Ecosystem effect: data is strongly policy-shaped; retraining on logged outcomes can reinforce allocation bias.
- Validation: replay auction-time state and verify no post-auction budget/conversion facts appear in features.

#### 8. Objective and Metric Mismatch

For R03, an execution failure means the table violates the intended semantics: future features leak, duplicates inflate outcomes, or rows are mislabeled because the pipeline is wrong. Objective mismatch is different: the table is constructed exactly as specified, but the specified label/grain/attribution target is not the product behavior the model should optimize.

For example, a perfectly point-in-time-correct click label can still be the wrong objective if the business wants long-term purchase value and clickbait recommendations increase clicks while reducing purchases. Likewise, a last-touch purchase attribution policy can be implemented flawlessly and still assign credit in a way that biases the model toward late-stage exposures.

Representative template:

- Offline/model metric: NDCG/AUC/log-loss on impression-level click or attributed purchase labels.
- Online/product outcome: conversion, revenue, satisfaction, retention, or reduced hides/complaints.
- Execution verification: prove row uniqueness, temporal feature validity, attribution-window validity, and split correctness.
- Metric semantics: state exactly what a positive label means and which exposure receives credit.
- Blind spots: unexposed items, delayed outcomes, position/examination bias, multi-touch effects, and long-term value.
- Missing product factor: user satisfaction or long-horizon conversion value not represented by the immediate label.
- Repair: redefine or multi-task the target, preserve richer outcome fields, and redesign attribution/evaluation if needed.
- Trade-off: slower/sparser labels and more complex evaluation versus better alignment with product value.
- Online validation: controlled experiment with primary business metrics and guardrails, segmented by cohort and exposure regime.

## Material Follow-ups / Scenario Variants

### A purchase can happen 30 days after exposure, but the team wants daily retraining. What do you do?

Keep feature freshness and label maturity as separate concerns. Daily retraining does not require pretending yesterday's 30-day conversion label is complete. Train on the newest cohort whose labels are mature for the long-horizon target, or combine a fast-maturing short-horizon target with a delayed long-horizon target. Measure the conversion accumulation curve by days-since-exposure, choose the maturity cutoff from observed delay rather than convenience, and record the cutoff in the dataset manifest. If fresher behavior is essential, use recent rows for features or auxiliary objectives without falsely finalizing their long-horizon labels.

### One purchase follows five impressions of the same item across home, search, and email. Which row is positive?

There is no universally correct row; this is an attribution-policy choice. First preserve all five exposures with stable surface/request identity. Then choose the target semantics: last touch, first touch, bounded multi-touch credit, or a model that treats conversion attribution separately. The critical requirement is not to let a join accidentally label all five rows as independent full positives. Version the policy, quantify how label counts change under alternatives, and validate online because each rule teaches the ranker a different notion of credit.

### Late events keep changing last week's table. How can the dataset be both reproducible and correct?

Version two notions explicitly. An **as-known snapshot** pins the raw-event watermark and reproduces exactly what the pipeline knew at build time. A **corrected historical snapshot** can incorporate later-arriving events and is assigned a new dataset version. Never let the same dataset identifier silently mutate. Store the watermark, backfill policy, source partitions, code/config version, attribution policy, and output checksum so both artifacts are reproducible for their stated semantics.

### Offline performance jumps after a table rewrite, but serving code and model class are unchanged. What is your diagnostic?

Treat the data pipeline as the suspect until proven otherwise. Rebuild a fixed historical interval under old and new code from the same immutable raw snapshot. Compare row counts, uniqueness, positive rate, unresolved-label rate, feature availability-time violations, and split-boundary cohorts. Then diff features and labels for the same stable row IDs. The goal is to find the first semantic divergence. If the gain disappears after enforcing availability-time joins or censoring rules, it was leakage or label-definition drift, not a model improvement.
