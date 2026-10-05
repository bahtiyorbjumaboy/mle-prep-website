---
type: interview-answer
item: "2027:R03"
title: "Training-set construction and point-in-time correctness"
created: "2026-09-27"
updated: "2026-10-05"
tags:
  - recommendation
  - training-data
  - point-in-time-correctness
  - leakage
  - attribution
---

## Canonical Staff-Depth Question

Starting from impression, click, watch, cart, purchase, hide, dwell, and catalog logs, design a reproducible training table with grain, attribution, deduplication, censoring, temporal splits, late events, and leakage tests.

## Mastery Answer

I would start by defining the training row grain and the prediction decision time. For a recommendation ranker, a common grain is one `(request or impression, user, item)` candidate row at time $t_0$, with only information that was available by $t_0$ eligible as features. The label is then defined from future behavior inside an explicit attribution window, for example click within 30 minutes, purchase within 7 days, or watch time accrued after the impression. That separates feature time from outcome time and makes point-in-time correctness testable.

Next I would build the table from immutable raw event logs with stable event IDs and event time plus ingestion time. I would normalize identities, deduplicate retries, define how repeated impressions are treated, and join catalog/user/context features using as-of semantics: for each row, take the latest feature value whose effective timestamp is no later than the decision time. I would never use a current snapshot to reconstruct historical rows unless the source is versioned and time-travelable.

Attribution is a modeling choice, not just a join. I would specify which exposure can receive credit, the attribution window, whether credit is first-touch, last-touch, or multi-touch, and how to handle click, cart, purchase, hide, dwell, and repeated exposures. For delayed outcomes, rows near the dataset cutoff may be censored: a missing purchase is not yet evidence of a negative until its observation window has closed. I would either exclude immature rows from supervised labeling or mark them explicitly and use only mature rows for objectives that require complete outcomes.

Temporal splitting must respect deployment chronology. Training should precede validation, which should precede test, with any label horizon accounted for so outcomes used to label an earlier split cannot leak information from the evaluation period. Stateful features and candidate statistics must be recomputed independently at each historical cutoff rather than precomputed once on the full dataset.

Late-arriving events require deterministic backfill semantics. I would distinguish event time from processing/ingestion time, define a lateness policy or watermark, version the dataset build, and make reruns idempotent. A backfill should update only rows whose historical truth changed and should produce the same table given the same source snapshot and configuration.

Finally, I would prove correctness with tests rather than trust conventions: assert every feature timestamp is $\le t_0$; every attributed outcome occurs after the exposure and within its label window; deduplication is idempotent; repeated-exposure rules behave on boundary cases; censored rows are not silently treated as negatives; temporal partitions do not overlap; and deliberately injected future features or post-cutoff catalog state cause the build or validation tests to fail. I would also track row counts, label rates, duplicate rates, join coverage, and slice distributions across rebuilds so a logically valid but semantically broken dataset does not pass unnoticed.

## Learn the Concepts

### Foundation

The central mental model is: **every training row represents a historical prediction that the system could actually have made at that moment**.

A recommender training dataset is not just a table of users, items, and outcomes. It is a reconstruction of many past decision points. For each decision point, the table must answer two different questions:

1. **What was known when the prediction was made?** These values become features.
2. **What happened afterward?** These future events become labels.

Those two time directions must never be mixed.

Important terminology:

- **Event:** a logged action or state change, such as an impression, click, watch, cart, purchase, hide, or catalog update.
- **Event time:** when the event actually happened in the product.
- **Ingestion/processing time:** when the data platform received or processed the event.
- **Decision time / prediction time ($t_0$):** the instant whose historical prediction is being reconstructed.
- **Grain:** what exactly one row represents. Examples include one impression, one `(request, item)` candidate, or one `(user, item, day)` pair.
- **Feature:** information available at or before $t_0$ and supplied to the model.
- **Label:** the target outcome defined from events after $t_0$, usually within a fixed future window.
- **Attribution window:** the interval after an exposure during which an outcome can be credited to that exposure.
- **Point-in-time correctness:** for every row, features reflect only state available by the decision time.
- **Leakage:** information unavailable at prediction time enters training features or data selection.
- **Deduplication:** removing duplicate logical events caused by retries, repeated ingestion, or source defects according to an explicit identity rule.
- **Censoring:** the outcome window has not fully elapsed, so an apparent non-event is not yet a trustworthy negative.
- **Temporal split:** train/validation/test partitions are ordered by time instead of randomly mixing past and future.
- **Late event:** an event whose event time belongs to an earlier period but arrives in the data system later.
- **As-of join:** for a row at time $t_0$, join the latest feature/state record with timestamp $\le t_0$.

#### Worked example

Suppose a shopping recommender shows user `U1` item `A` at **10:00 on Monday**.

At that instant:

- item price is `$20`;
- item category is `shoes`;
- user has clicked 3 shoe products in the previous 7 days;
- the item has 120 historical purchases.

Then:

- `10:02`: the user clicks item `A`;
- `11:30`: the price changes to `$18`;
- Tuesday `09:00`: the user purchases item `A`;
- Wednesday: the catalog pipeline backfills a corrected brand field.

If one row represents the Monday 10:00 impression, then its features must use the `$20` price, the user history as of 10:00, and the catalog state known by 10:00. The `$18` price and Wednesday correction are future state relative to the decision and cannot be used as features for that row.

If the click label is "click within 30 minutes," the label is positive because the click occurred at 10:02. If the purchase label is "purchase within 7 days," the label is also positive because the Tuesday purchase falls inside the attribution window.

If the dataset is generated Monday at 10:05, the purchase window has not matured. Treating "no purchase yet" as a negative would be wrong; the row is censored for the 7-day purchase objective until the observation window closes.

This example captures the essential rule:

$$
\text{feature time} \le t_0 < \text{label event time} \le t_0 + \text{label horizon}.
$$

### Core Interview Reasoning

A compact reasoning structure for this problem is:

**decision point → row grain → labels/attribution → point-in-time features → event hygiene → censoring → temporal splits → late-data/rebuild policy → leakage tests**

Each part exists because a training table is a causal-temporal reconstruction, not a static join.

#### 1. Define the decision point and grain

The grain determines what the model is learning to score.

Examples:

- one row per impression;
- one row per candidate shown in a request;
- one row per `(user, item)` exposure;
- one row per `(session, item)` exposure.

A candidate-ranking model usually needs rows tied to the actual ranking opportunity. If a request generated 100 candidates but only 10 were shown, the table must distinguish **candidate**, **exposed**, and **unexposed** items rather than silently equating missing interaction with a negative.

The grain also determines the primary key. A robust logical key may be `(request_id, item_id)` or `(impression_id, item_id)`, with an immutable source event ID where possible.

#### 2. Define labels and attribution

Behavioral events have different semantics and delay distributions.

- **Click:** usually fast; often attributed to the triggering impression.
- **Watch/dwell:** continuous or thresholded; may need truncation and bot/background-play handling.
- **Cart:** stronger intent than click, usually slower.
- **Purchase:** high value but delayed, sparse, cancellable, and potentially attributable to several prior exposures.
- **Hide/report:** explicit negative signal but with different product meaning from mere non-click.
- **Non-interaction:** not automatically a negative because the user may not have examined the item.

Attribution requires an explicit contract:

- eligible source exposure;
- outcome type;
- attribution horizon;
- first-touch, last-touch, closest-touch, or multi-touch policy;
- cross-device/user identity rules;
- repeated-impression behavior;
- whether one outcome may label multiple exposures.

A join like `user_id + item_id` without time and exposure semantics can duplicate labels across many rows and create severe target inflation.

#### 3. Enforce point-in-time feature correctness

The governing invariant is:

$$
t_{\text{feature}} \le t_{\text{decision}}.
$$

For mutable data, this requires historical versions or event-sourced reconstruction.

Examples:

- user 7-day click count must include only clicks before $t_0$;
- item popularity must be computed from events before $t_0$;
- item price must be the price effective at $t_0$, not today's price;
- inventory must reflect the historical availability state;
- embeddings or model-derived features must use the version available at that time if the production system depended on versioned artifacts.

The typical implementation is an as-of join or point-in-time feature materialization keyed by entity and effective timestamp.

#### 4. Handle duplicates and repeated exposures deliberately

Two distinct problems are often confused:

- **Duplicate records:** the same logical event appears multiple times because of retries or ingestion defects.
- **Repeated real events:** the user genuinely sees the same item multiple times.

Duplicate records should normally collapse by stable event ID or a defensible composite key. Real repeated impressions should not be blindly deduplicated; they affect exposure, examination, fatigue, and attribution.

If event IDs are unavailable, heuristic deduplication using user/item/timestamp windows is risky because it can erase legitimate repeats.

#### 5. Handle censoring

Suppose the purchase label window is 7 days and the raw data ends at September 30.

An impression on September 29 has only one day of observable future. If no purchase is visible, the row is not a fully observed negative.

A simple mature-row rule is:

$$
t_0 + H \le T_{\text{data cutoff}},
$$

where $H$ is the label horizon.

Rows failing this condition are censored for that label. They can be excluded, delayed until mature, or modeled with methods that explicitly account for censoring, depending on the objective.

#### 6. Split by deployment chronology

Random row splits often leak future behavior patterns into training and make evaluation unrealistically easy.

A temporal scheme should resemble:

$$
\text{train period} < \text{validation period} < \text{test period}.
$$

But timestamps on rows are not enough. All derived features, aggregates, negatives, candidate pools, and labels must also obey the corresponding cutoff.

If a 7-day label horizon is used, split boundaries may need a gap or careful maturity rules so labels are complete without using future evaluation information in feature construction.

#### 7. Make late-data handling reproducible

Because event time and ingestion time differ, a training table must define which source snapshot it represents.

A reproducible build records at least:

- input dataset versions or partitions;
- maximum accepted ingestion time;
- event-time window;
- lateness/watermark policy;
- transformation code/config version;
- feature/label definitions;
- output version.

Rerunning the same versioned inputs and configuration should produce the same logical rows.

#### 8. Prove temporal correctness with tests

Useful invariants include:

$$
t_{\text{feature}} \le t_0
$$

and, for an attributed label,

$$
t_0 < t_{\text{outcome}} \le t_0 + H.
$$

Other high-value tests:

- duplicate input replay does not duplicate output rows;
- future catalog updates cannot change historical features unless a source correction is intentionally backfilled;
- a click before exposure cannot become the exposure's positive label;
- an outcome outside the attribution window is not credited;
- rows whose label horizon has not matured are not silently negative;
- train/validation/test primary keys and time intervals obey the split contract;
- feature aggregations are recomputed from cutoff-safe inputs;
- deliberately injected future information causes a test failure.

### Deeper Reasoning and Derivations

#### Why grain errors change the learning problem

Suppose one request shows 10 items and receives one click. If the intended task is ranking the 10 displayed items, a natural grain is one displayed item per request. The clicked item gets a positive click label and the other displayed items are potential non-click outcomes, subject to examination assumptions.

If instead the dataset collapses to one row per user-item-day, several exposures may be merged. A click after the third exposure may make all earlier exposures appear positive, destroying the temporal relationship between exposure and response.

Thus row grain is part of the statistical target.

#### Why point-in-time leakage can survive ordinary train/test splitting

Assume the test rows are chronologically separated correctly, but the feature `item_purchase_rate_30d` is computed once using the full event table and then joined to all rows.

For a row at time $t_0$, the aggregate may include purchases after $t_0$:

$$
\hat p_i(t_0)
=
\frac{
\#\{\text{purchases of item }i \text{ in a window that extends beyond } t_0\}
}{
\#\{\text{eligible exposures}\}
}.
$$

Even though the row itself belongs to the training period, the feature contains future outcome information. The split is temporal; the feature is not.

This is why temporal splitting and point-in-time feature generation are separate correctness requirements.

#### Attribution can create label duplication

Consider three impressions of the same item at 09:00, 12:00, and 17:00, followed by a purchase at 18:00.

A naive user-item join may mark all three impressions positive. Last-touch attribution marks only the 17:00 impression positive. A multi-touch policy may give fractional or repeated credit. These choices imply different targets and different learned behavior.

There is no universal attribution rule; the rule must match the intended decision and product semantics.

#### Negative labels are observation-policy dependent

For implicit feedback, the fact that an item was not clicked can mean:

- it was shown and examined but rejected;
- it was shown but not examined;
- it was below the fold;
- it was retrieved but never shown;
- it was never considered by the serving system.

These are not equivalent negatives. Training-set construction therefore interacts with exposure bias and negative sampling. R03's data contract should retain enough exposure metadata to allow later modeling choices rather than destroying these distinctions.

#### Event time versus ingestion time

A purchase may happen at 12:00 but arrive at 12:10 because a mobile client was offline.

For semantic attribution, event time usually determines whether the purchase falls inside the label window. For reproducible rebuilds, ingestion time determines whether that event was available to a particular pipeline run.

Both timestamps may be required:

- event time answers "when did reality happen?";
- ingestion time answers "when did the data system know?".

#### Backfills and corrected history

A late event can be a newly observed fact about the past; a source correction can revise a previously stored fact. A reproducible system must decide whether a historical dataset version is immutable or whether a new version supersedes it.

A strong design treats output tables as versioned products. "Yesterday's training table" should mean a specific version or source cutoff, not whatever the warehouse happens to return today.

#### Failure modes

Common failures include:

- current catalog snapshot joined onto historical rows;
- aggregate features computed over the full dataset;
- random splits on temporally dependent data;
- purchase outcomes duplicated across repeated impressions;
- retry events counted as multiple clicks or purchases;
- label windows that cross the available-data cutoff but are treated as negative;
- user/item identity merges that use information learned later;
- deleting unavailable items from historical candidate sets using today's availability;
- selecting "active users" using activity that occurred after the row time;
- negative sampling from an item universe that did not exist at $t_0$;
- using a future-trained embedding or model score as a historical feature;
- backfills that append instead of replace/idempotently upsert and therefore duplicate rows.

### Advanced Staff-Depth Considerations

The reusable Staff-level backbone for this item is:

`Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate`

Equivalently:

`Assumption → Mechanism → Evidence → Decision → Trade-off → Validation`

For this question, the baseline is: The baseline is a historical prediction reconstruction: each row represents a decision at time $t_0$, features may use only information available by $t_0$, and labels come from explicitly defined future outcomes. Reproducibility means the same versioned inputs/configuration rebuild the same logical table.

The eight subsections below apply that same loop from different angles. Each explanation teaches the mechanism first; the filled template then compresses it into a reusable interview scaffold.

#### 1. Changed Constraints and Transfer Logic

Constraint changes should preserve the temporal contract. A longer label horizon changes censoring, attribution ambiguity, split gaps, retention, and backfill scope; cheaper snapshots or coarser joins are acceptable only if they do not introduce information unavailable at serving time.

A useful reasoning chain is:

`changed assumption → affected mechanism/stage → invariant → broken assumption → consequence → redesign → metric impact → trade-off → validation`

**Filled template for this item**

- **Original assumption:** Purchase labels mature within a 7-day horizon and the pipeline retrains daily.
- **Changed constraint:** The purchase horizon becomes 30 days while daily retraining continues.
- **Invariant:** Features remain point-in-time correct and negatives require a fully observed label window.
- **Broken assumption:** Recent daily rows are no longer mature enough for direct 30-day purchase supervision.
- **Consequence:** Freshness falls, repeated-exposure attribution becomes more ambiguous, and backfill/split windows lengthen.
- **Design change:** Train purchase objectives on mature history; use faster proxy/auxiliary objectives or delayed-feedback modeling for recent behavior.
- **Metric impact:** Track maturity fraction, attribution distance, data age, and performance by label age/horizon.
- **Trade-off:** Better capture of delayed conversion yields older fully observed labels or more modeling assumptions.
- **Validation:** Rebuild fixed historical cutoffs and compare correctness/utility across horizon and maturity policies.

#### 2. Failure Modes and Diagnosis

Unexpected offline gains after dataset changes should be treated as correctness incidents until proven real. Data-pipeline bugs can improve every downstream model metric. Diagnose shape, keys, labels, timestamps, historical joins, split chronology, artifact lineage, and row-level replay before attributing lift to modeling.

**Filled template for this item**

- **Symptom:** Offline NDCG jumps from roughly 0.42 to 0.61 after a training-table refactor with unchanged model code.
- **Stage decomposition:** raw events → dedup/grain → attribution/labels → point-in-time features → split → dataset artifact → training/evaluation.
- **Slices:** Time, label maturity, feature source, user/item segment, row multiplicity, and mutable catalog fields.
- **Competing hypotheses:** Join explosion; duplicated attribution; immature negatives; future-feature leakage; current-snapshot leakage; split contamination.
- **Discriminating evidence:** Primary-key uniqueness, label prevalence, feature timestamp/dependency lineage, attribution distance, and suspicious feature importance.
- **Offline/online comparison:** Compare historical features with what serving could actually know, including lag and artifact versions.
- **Replay/isolation:** Reconstruct selected impression IDs from immutable logs through the new and old pipeline.
- **First divergence:** Earliest transform where row count, label, or feature state differs semantically from the baseline.
- **Immediate mitigation:** Freeze/rollback the refactor and stop promoting models trained on suspect data.
- **Permanent prevention:** Point-in-time invariants, dependency lineage checks, golden fixtures, idempotence tests, and versioned dataset manifests.

Memory aid: `Symptom → Slice → Stage → Hypotheses → Evidence → First divergence → Fix`.

#### 3. Latency and Resource Trade-offs

R03 is mainly offline, so the relevant resource trade-off is temporal fidelity versus compute/storage/rebuild cost. Current snapshots, full-history aggregates, or coarse materializations are cheap shortcuts only when they preserve what would have been available at $t_0$. The right optimization changes execution, not the logical contract.

**Filled template for this item**

- **Budget:** Dataset-build SLA, storage budget, and affordable cost for point-in-time joins/backfills.
- **Cost decomposition:** Event scans + deduplication + as-of joins + stateful aggregates + attribution + validation + write/backfill.
- **Dominant cost:** Historical state joins and recomputation of large aggregates over long windows.
- **Quality driver:** Finer temporal fidelity and complete historical versions reduce leakage and semantic error.
- **Cost driver:** More snapshots/history and exact joins increase storage, shuffle, and compute.
- **Optimization knobs:** Partitioning, sorted/as-of joins, incremental aggregates, replayable materialization, bucketed snapshots with bounded error, targeted backfills.
- **Fallback/degradation:** Drop unavailable mutable features or restrict history rather than silently use current state.
- **Trade-off curve:** Build cost/runtime versus temporal error/leakage tests and downstream quality.
- **Decision:** Use the cheapest representation that preserves the information-availability invariant for each feature.

Memory aid: `Budget → Breakdown → Bottleneck → Knobs → Quality loss → Fallback`.

#### 4. Scale and Capacity

At billions of events, correctness remains non-negotiable but execution must become incremental and partition-aware. Stable event IDs, deterministic transforms, historical feature state, bounded source snapshots, and targeted backfills are the mechanisms that let scale change without changing the target.

**Filled template for this item**

- **Scaling dimension:** Event volume grows to billions with long attribution horizons and many mutable features.
- **Baseline scale assumption:** Full scans and straightforward as-of joins are affordable.
- **First bottleneck:** Shuffle-heavy temporal joins and repeated aggregate recomputation dominate cost.
- **Second-order effects:** Larger retention windows, backfill blast radius, dedup state, and lineage metadata grow.
- **Architectural response:** Partitioned immutable logs, historized dimensions, incremental/replayable aggregates, and targeted partition rebuilds.
- **Partitioning/replication/caching/batching:** Partition by event time/entity, cluster join keys, materialize versioned state, batch backfills by affected windows.
- **Consistency/freshness consequence:** Incremental state must remain reproducible from source snapshots and watermarks.
- **Operational failure mode:** Partial backfill or non-idempotent upsert duplicates rows or leaves mixed label versions.
- **Validation:** Projected-volume rebuild tests plus key uniqueness, lineage, watermark, idempotence, and temporal invariant checks.

Memory aid: `What grows? → What stops fitting? → What bottlenecks? → How do we partition? → What new failure appears?`.

#### 5. Freshness, State, and Versioning

Dataset freshness is bounded by both pipeline cadence and outcome maturity. Rebuilding hourly cannot produce a fully observed 14-day purchase label for yesterday. Separate fast-changing feature state, fresh behavioral monitoring, and slower mature supervised labels rather than conflating them.

**Filled template for this item**

- **State that becomes stale:** Feature snapshots, mutable catalog/user state, dataset labels, attribution decisions, and source snapshots.
- **Why freshness matters:** Old features reduce relevance; immature labels create false negatives; late events revise recent historical truth.
- **Required freshness:** Match production feature lag while respecting each label horizon.
- **Refresh cost:** More frequent builds, late-event reconciliation, historical snapshots, and repeated backfills.
- **Update architecture:** Streaming/incremental feature state plus scheduled mature-label dataset builds and targeted late-event backfills.
- **Version consistency:** Dataset manifest must bind source snapshots, feature definitions, model-derived artifacts, attribution rule, and code/config.
- **Failure from version skew:** A row can have legal timestamps but depend on a future-trained encoder or current catalog snapshot.
- **Fallback:** Train on mature windows and omit unreconstructable mutable features rather than fabricate history.
- **Measurement:** Feature age, label maturity, late-event rate, rebuild version, lineage completeness, and freshness-sliced quality.
- **Decision:** Optimize freshness subject to complete outcomes and point-in-time correctness, not wall-clock recency alone.

Memory aid: `What goes stale? → How fast does it matter? → What does refresh cost? → How do versions stay consistent?`.

#### 6. Implementation, Serving, and Observability

Treat the training table as a versioned product. Immutable raw events, stable IDs, event/ingestion times, historized entity state, deterministic attribution, idempotent deduplication, split configuration, manifests, and replay/backfill support are part of the model system—not incidental ETL.

**Filled template for this item**

- **Conceptual object:** A reproducible point-in-time training row at decision time $t_0$.
- **Training/data implementation:** Normalize/dedup events, define grain/attribution, as-of join features, mature labels, temporal split, validate invariants.
- **Stored artifact/state:** Immutable events, SCD/event-sourced entity history, feature snapshots/aggregates, dataset manifest, lineage, and output version.
- **Serving path:** Historical generation must reproduce production availability lag and artifact semantics, even though training is offline.
- **Component contract:** Feature definitions must specify value semantics and availability/effective time.
- **Logging:** Event ID, event/ingestion time, request/impression identity, source versions, and mutable-state versions.
- **Versioning:** Source snapshot, code/config, feature/label definitions, model-derived features, and output dataset version.
- **Failure mode:** Current state or future-trained artifacts leak into historical rows.
- **Observability:** Row/key counts, label rates, join coverage, temporal violations, duplicates, missingness, and drift across rebuilds.
- **Rollback:** Restore prior dataset version and source/config manifest; rebuild affected partitions deterministically.
- **Testing/replay:** Golden historical rows, adversarial future-feature injections, idempotence, and exact cutoff replay.

Memory aid: `Train → Store → Serve → Version → Log → Monitor → Roll back`.

#### 7. Vertical Transfer

The mechanism should transfer; the assumptions must be re-derived. Use the checklist:

`labels → candidate sources → objectives → features → constraints → evaluation → experiments → serving/freshness → ecosystem effects`

Representative verticals:

- **Video/feed:** **Invariant:** Historical decision reconstruction transfers. **Different assumption:** Watch/skip/dwell labels mature quickly but autoplay complicates examination. **Technical consequence:** Preserve exposure/view state and time-bounded watch outcomes.
- **E-commerce:** **Invariant:** Point-in-time features and delayed labels transfer. **Different assumption:** Price, inventory, promotion, and purchase delays make mutable catalog history essential. **Technical consequence:** Historize catalog state and use explicit conversion windows.
- **Ads:** **Invariant:** Temporal correctness transfers. **Different assumption:** Auction/exposure context and delayed multi-touch conversion are central. **Technical consequence:** Bind labels to auction/impression identity and version attribution rules.
- **Marketplace:** **Invariant:** Decision-time reconstruction transfers. **Different assumption:** Provider availability and two-sided outcomes change during attribution windows. **Technical consequence:** Historize supply state and avoid imputing demand from unavailable offers.
- **Notifications:** **Invariant:** Temporal grain/attribution transfers. **Different assumption:** Send, delivery, display, open, and downstream action have distinct timestamps. **Technical consequence:** Use explicit opportunity stages and suppression/frequency state at decision time.

**Filled transfer template — Video/feed**

- **Invariant:** Historical decision reconstruction transfers.
- **Different data-generating process:** Watch/skip/dwell labels mature quickly but autoplay complicates examination.
- **Different objective:** Re-derive the primary product utility for this vertical rather than copying the base objective.
- **Different candidates/features:** Candidate sources and features should reflect the vertical-specific context and available signals.
- **Different constraints:** Watch/skip/dwell labels mature quickly but autoplay complicates examination.
- **Metric change:** Retain transferable stage metrics, then add vertical-specific outcomes and guardrails.
- **Serving change:** Preserve exposure/view state and time-bounded watch outcomes.
- **Ecosystem effect:** Check creator/provider/seller/advertiser or user-side concentration where relevant.
- **Validation:** Evaluate both transferable retrieval/ranking quality and the vertical-specific product outcome.

Memory aid: `Keep the mechanism; re-derive the assumptions.`

#### 8. Objective and Metric Mismatch

A temporally correct table can still encode the wrong target, while a leaky table can make the “right” metric look spectacular. Distinguish execution/data correctness from objective validity. First prove that the table reconstructs the intended historical decision; then ask whether the chosen label/attribution window represents product value.

**Filled template for this item**

- **Offline/model metric:** NDCG/AUC or another downstream metric improves sharply after data changes.
- **Online/product outcome:** No comparable lift, or product metrics regress.
- **Execution verification:** Prove grain, labels, joins, cutoffs, dependency lineage, split chronology, and serving lag match the intended contract.
- **Metric semantics:** Offline metric evaluates the target encoded by the rebuilt table.
- **Blind spots:** Wrong attribution horizon, repeated-exposure semantics, delayed value, exposure bias, or product factors omitted from the label.
- **Missing product factor:** The table may be correct for click while the product cares about purchase/retention/value.
- **Repair:** Correct temporal bugs first; then revise label/attribution/objective or add multi-task/guardrail evaluation.
- **Trade-off:** Better product targets are often sparser, delayed, noisier, and costlier to reconstruct.
- **Online validation:** Experiment only after dataset correctness is established, with primary product outcomes and data-quality guardrails.

Memory aid: `Did we execute the objective incorrectly, or correctly optimize the wrong objective?`

## Material Follow-ups / Scenario Variants

### Staff Variant — Purchase horizon changes from 7 days to 30 days, but daily retraining must continue

The core invariants do not change: each row still represents a historical decision at $t_0$; features must be available by $t_0$; outcomes are defined after $t_0$; deduplication must distinguish transport duplicates from genuine repeated exposures; and the dataset build must remain reproducible. The changed assumption is the label horizon, from 7 to 30 days.

That longer horizon has several consequences. First, more recent examples are censored for longer, so the newest fully mature purchase-labeled rows are roughly 30 days old. Second, attribution becomes more ambiguous because more repeated impressions may be eligible for credit. Third, backfills and late-arriving outcomes can revise a longer historical window. Fourth, temporal split boundaries must account for the longer maturity horizon.

The key redesign is to separate **training cadence** from **label maturity**. The purchase training dataset can still rebuild and the model can still retrain every day, but fully supervised 30-day purchase labels should come only from mature rows. To incorporate genuinely recent behavior, use faster-maturing signals such as clicks, dwell, or carts as auxiliary objectives, separate models, or serving-time features. A more sophisticated alternative is explicit delayed-feedback or censoring-aware modeling, but that adds assumptions and complexity rather than making unknown outcomes observable.

The product trade-off is explicit:

$$
\text{longer purchase horizon}
\Rightarrow
\text{better capture of delayed conversion}
$$

but also

$$
\text{longer purchase horizon}
\Rightarrow
\text{older fully observed supervised labels}.
$$

It is impossible to have a fully observed 30-day outcome for an impression from yesterday. The design must therefore accept staler mature purchase labels, use fresher proxy/auxiliary objectives, or adopt delayed-feedback modeling.

### Staff Variant — Offline NDCG jumps from 0.42 to 0.61 after a training-table refactor

Treat the unexplained jump as a data-correctness incident until proven otherwise. Diagnose in an order that localizes the first divergence:

1. **Dataset shape:** compare total rows, unique primary keys, duplicate rate, rows per request/impression, join coverage, and missingness. A join explosion or deduplication regression can change the learning problem without any model-code change.
2. **Label distributions:** compare positive rates overall and by date/segment, attribution-distance distributions, repeated-exposure multiplicity, and censored-row fractions. A sudden prevalence change may indicate duplicated attribution or immature labels becoming negatives.
3. **Temporal invariants:** verify $t_{\text{feature}} \le t_0$ and $t_0 < t_{\text{outcome}} \le t_0 + H$. Audit the dependency graph as well: a feature can carry a legal timestamp but still leak if its aggregate, embedding, or encoder was built with future data.
4. **Joins and historical state:** inspect whether historical catalog/user state was replaced by current snapshots, whether as-of join semantics changed, whether missingness unexpectedly fell, or whether one feature suddenly became implausibly predictive.
5. **Temporal split correctness:** confirm train, validation, and test chronology, label maturity at boundaries, and cutoff-safe feature/aggregate generation. Merely splitting rows by date is not enough if features were computed on the full dataset.
6. **Row-level replay:** select a small set of impression IDs and reconstruct them from raw logs: what the system knew, what was shown, which outcome occurred, which exposure received credit, and which feature/artifact version produced the row.
7. **Adversarial leakage test:** deliberately inject future information, such as tomorrow's purchase count or a current catalog value into a historical row, and verify that dataset validation fails.

Only after the data contract survives these checks should the NDCG gain be treated as a plausible real improvement.

### Staff Variant — Historical rebuild is required, but the catalog stores only the latest price, category, and availability

The immutable impression/click/purchase logs are sufficient to reconstruct behavioral events, but they are **not sufficient to reconstruct historical mutable catalog state**. If only the current catalog row is stored, the system cannot know with certainty what price, category, or availability was effective at an impression six months ago. That information has been destroyed unless another source, audit log, snapshot, CDC stream, or upstream system retains the history.

For the immediate six-month backfill, first search for an authoritative historical source such as warehouse snapshots, change-data-capture logs, object-store exports, catalog audit tables, or source-system history. If none exists, do not silently join today's values and call the result point-in-time correct. Options are to exclude mutable catalog fields from the historical rebuild, restrict the rebuild to the time range for which trustworthy snapshots exist, or use an explicitly documented approximation only if the modeling risk is acceptable. The approximation must be labeled as such because exact reconstruction is impossible from the current state alone.

For future correctness, change the data contract so mutable catalog state is historized. Common patterns are immutable change events, slowly changing dimension Type 2 records with effective intervals, versioned snapshots, or an event-sourced catalog. Each record should preserve an entity key, effective-from/effective-to semantics or change timestamp, ingestion/version metadata, and stable lineage. Then historical feature construction can use an as-of join:

$$
x(t_0)=\text{latest catalog state whose effective time}\le t_0.
$$

The broader system rule is that point-in-time correctness is a property of the full dependency graph. If a feature depends on mutable state, the platform must retain enough history to reconstruct what was actually knowable at the decision time.

### Point-in-time joins are too expensive at scale

Preserve the same logical contract while changing execution: pre-materialize versioned snapshots, bucket timestamps, use incremental aggregates with replayable state, partition by entity/time, or restrict backfills to affected windows. Any approximation should document the maximum temporal error and demonstrate that it cannot introduce information unavailable at serving time.
