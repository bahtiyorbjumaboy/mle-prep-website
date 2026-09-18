---
type: interview-answer
item: "2027:R03"
title: "Training-set construction and point-in-time correctness"
created: "2026-09-18"
updated: "2026-09-18"
tags:
  - recommendation
  - training-data
  - point-in-time-correctness
  - leakage
---

## Canonical Staff-Depth Question

Starting from impression, click, watch, cart, purchase, hide, dwell, and catalog logs, design a reproducible training table with grain, attribution, deduplication, censoring, temporal splits, late events, and leakage tests.

## Mastery Answer

I would start by defining the **decision event and row grain**, because every later choice depends on it. For a ranking model trained from served recommendations, a natural row is one candidate impression: `(user_id, item_id, impression_id, impression_time, context)`. That row means: *at this historical instant, with only information available then, what outcome followed this exposure?* I would preserve `impression_id` as the stable key rather than collapsing immediately to user-item pairs, because repeated exposures are real events and need an explicit modeling policy rather than accidental deduplication.

Next I would define **labels and attribution windows before building joins**. A click might be attributed within minutes or a session, a cart within hours, and a purchase within several days. For an impression at time $t$, a purchase label with horizon $\Delta$ is conceptually

$$
y_{\text{purchase}}(t)=
\mathbf{1}\{\text{an attributable purchase occurs in }(t,t+\Delta]\}.
$$

The attribution rule must be deterministic: for example, attribute a conversion to the most recent eligible impression for that user-item within the conversion window, or keep separate multi-touch labels if that is the product definition. Click, watch, dwell, cart, purchase, and hide should not be silently collapsed into a single notion of relevance; they may be separate targets, a hierarchy, or inputs to a composite target depending on the objective. Unexposed user-item pairs are not ordinary negatives. The clean negative for an exposure-conditioned objective is usually an eligible impression whose outcome window matured without the target action.

All **features are as-of the impression time**, not the training-job time and not the conversion time. Historical user counts, item popularity, price, availability, seller state, inventory, category metadata, and catalog eligibility must come from versions whose effective timestamps are at or before the decision time. A point-in-time join therefore has the form “latest feature state with `feature_time <= impression_time`.” This includes catalog state: joining yesterday's impression to today's price or availability is leakage even though both values come from a legitimate catalog table.

I would handle **repeated impressions and duplicates** explicitly. Exact duplicate log deliveries should be idempotently removed using stable event IDs. Distinct repeated impressions should normally remain distinct unless the modeling contract says otherwise. If repeated exposures within a short window create excessive dependence or incumbent-policy overweighting, I might collapse them to one user-item-session exposure, use only the first eligible impression, or weight repeated exposures down. Whichever rule I choose changes the statistical target and must be documented and tested.

I would handle **censoring** by requiring labels to mature. If purchases are observed for seven days after an impression, then an impression from less than seven days before the dataset snapshot cannot safely be labeled `0`; its outcome is unknown. I would either exclude those rows from that target, mark the label as censored, or use a survival/time-to-event formulation. For a multi-task table, a recent row may have a mature click label but an immature purchase label, so label availability can differ by task.

For **late-arriving events**, I would distinguish event time from ingestion time. Point-in-time correctness is about what happened and what was knowable at the historical decision; reproducibility additionally requires a fixed data snapshot or ingestion cutoff. A training run should record raw-data snapshot IDs, code/config versions, event-time and ingestion-time policies, attribution-window versions, timezone rules, and any watermark. If a purchase happened inside the valid seven-day window but arrived two days late, a future rebuild may incorporate it only according to the declared snapshot/backfill policy. Otherwise the same nominal training date can silently produce different labels months later.

The **split must be temporal** and must respect label windows. I would choose train, validation, and test boundaries by decision time, not randomly. If a label for an impression can depend on the following seven days, I need either a purge/embargo around boundaries or a maturity rule that prevents outcomes crossing into a later evaluation period from contaminating earlier construction. Feature-generating aggregates must also be recomputed as-of each row; fitting a global encoder, popularity statistic, normalization constant, or target encoding over the full dataset can leak the future even when the rows themselves are temporally split.

Finally, I would make temporal correctness testable rather than aspirational. I would include fixtures that fail on: a feature timestamp later than its impression; a future catalog state; an attribution exactly outside the window; an event exactly on each boundary; duplicate event delivery; repeated legitimate impressions; click-without-impression when exposure is required; late events before and after the ingestion watermark; a recent row whose conversion label is not mature; join fan-out; and any random split. I would also rebuild a historical slice from the same declared snapshots and assert row-level reproducibility. The D3 standard is that I can explain why every row exists, why every label has its value, and demonstrate with tests that no future information entered the feature or label construction.

## Learn the Concepts

A useful mental model is to treat every row as a **historical prediction contract**.

For a row with decision time $t$:

- **Features** answer: what could the production system have known at $t$?
- **Eligibility/candidate state** answers: could this item actually have been shown at $t$?
- **Label** answers: what happened after $t$ inside a predefined outcome window?
- **Snapshot metadata** answers: which version of history are we claiming to reconstruct?

That creates a strict temporal boundary:

$$
\text{feature information time} \le t
\quad < \quad
\text{label outcome time} \le t+\Delta.
$$

The inequality is necessary but not sufficient. A record may have an old event timestamp yet have arrived late, a catalog table may contain a corrected historical value written much later, or an aggregate may have been recomputed using future events. That is why robust pipelines track **event time**, **ingestion time**, and often an **effective time/version** for mutable dimensions.

### 1. Grain: what does one row mean?

Before writing SQL, say the row in English.

Possible grains include:

- one **impression-candidate** row;
- one **user-item-session** row;
- one **request-item** row;
- one **user-day-item** row.

For ranking from impression logs, one impression-candidate row is often the cleanest because it preserves the exposure policy. A row can contain:

```text
user_id
request_id
impression_id
item_id
position
surface
impression_time
context/features as of impression_time
label_click
label_cart
label_purchase
label_hide
...
```

Changing grain changes the statistical question. Collapsing ten impressions of the same item into one row is not mere cleanup; it changes the weighting of users/items and the meaning of the target.

A useful invariant is:

> Every row has one unambiguous historical decision time.

If a row has no single cutoff time, it becomes difficult to prove feature correctness.

### 2. Exposure-conditioned labels

Recommendation logs are generated by an existing policy. You observe outcomes mainly for items the system chose to expose. Therefore:

- **unexposed** does not mean negative;
- **exposed and ignored after a mature observation window** can serve as a negative for many exposure-conditioned objectives;
- **exposed and acted on** is some form of positive, depending on the target.

This is why impression logging is foundational. If you only have clicks or purchases but not what was shown, the missing examples are entangled with the old recommender's policy.

For multiple actions, define targets separately unless the product objective justifies combining them. For example:

- click: dense but noisy;
- dwell/watch: richer engagement signal but needs threshold semantics;
- cart: stronger intent but sparser;
- purchase: high value, delayed, sparse, and vulnerable to attribution ambiguity;
- hide/report: explicit negative feedback.

A multi-task setup may keep these as separate labels rather than forcing them into one scalar.

### 3. Attribution is a modeling decision

Suppose item $i$ is shown to user $u$ three times before a purchase. Which impression gets credit?

Common deterministic rules include:

- **last eligible touch**;
- **first eligible touch**;
- **all eligible touches with weights**;
- session-scoped attribution;
- channel-specific attribution.

There is no universally correct choice. The rule should match the downstream target and experiment semantics.

Example:

```text
12:00 impression A
12:05 impression A
12:10 click A
next day purchase A
```

A last-touch policy may assign the purchase to the 12:05 impression. A first-touch policy may assign it to 12:00. Keeping both as independent purchase positives without saying why can overcount evidence.

Attribution windows are also part of the label definition. A purchase at exactly $t+\Delta$ must have a declared inclusion rule, such as $(t,t+\Delta]$. Boundary behavior should be tested explicitly.

### 4. Deduplication versus repeated exposure

There are two very different phenomena:

**Transport/log duplicates** are accidental copies of the same event. Remove them idempotently using a stable event ID or a deterministic composite key.

**Repeated real impressions** are legitimate exposures. Do not remove them merely because user and item repeat.

Repeated impressions can still be problematic because they create correlation and encode the incumbent policy's persistence. Possible treatments:

- preserve every exposure;
- collapse within session;
- keep the first exposure;
- cap or down-weight repeated exposures;
- create features such as prior-exposure count.

The choice changes training weights and therefore model behavior.

### 5. Censoring and label maturity

A missing future action is only a negative after you have waited long enough to observe it.

If the purchase horizon is seven days and the raw-data snapshot is `"2026-09-18 00:00"`, an impression from `"2026-09-17"` does **not** yet have a mature seven-day purchase label. Labeling it zero creates false negatives concentrated in the most recent data.

A label-specific eligibility condition is:

$$
t_{\text{impression}}+\Delta_{\text{label}}
\le
t_{\text{observation cutoff}}.
$$

With multiple targets, maturity differs:

- click window: maybe minutes;
- watch/dwell: seconds or minutes;
- cart: hours/days;
- purchase: days/weeks.

So a row may be usable for click training but not yet for purchase training.

### 6. Point-in-time features

The classic point-in-time join is:

```sql
feature.entity_id = row.entity_id
AND feature.effective_time <= row.impression_time
```

then select the latest eligible feature version.

Examples of leakage:

- joining an impression to the user's **current** lifetime purchase count;
- computing item popularity using events after the impression;
- using the item's current category after it was reclassified;
- using today's price for last month's impression;
- joining future inventory or seller status;
- fitting target encodings over the full dataset;
- normalizing with statistics computed from train + validation + test.

Point-in-time correctness applies to both learned features and "boring" business metadata.

A subtle issue is **backfilled dimensions**. Suppose a catalog record is later corrected but written with an old effective date. If historical reproducibility matters, you need bitemporal/versioned semantics or snapshotting; otherwise today's query can rewrite yesterday's truth.

### 7. Event time versus ingestion time

Let:

- $t_e$ = when the user action happened;
- $t_i$ = when the pipeline received it.

For an on-time event, $t_i$ is close to $t_e$. For late mobile/offline events, $t_i$ may be hours or days later.

Two separate questions arise:

1. **Semantic correctness:** did the event happen inside the label/feature window?
2. **Reproducibility:** was that event included in the exact historical dataset snapshot being rebuilt?

A robust pipeline declares a watermark or data snapshot. For example:

```text
include events with event_time <= cutoff
and ingestion_time <= snapshot_ingestion_cutoff
```

Later, you can run an explicit backfill that advances the ingestion cutoff and produces a new dataset version. You do not silently mutate an old dataset version.

### 8. Temporal splitting

Random train/test splits are usually wrong for this problem because production predicts the future from the past.

Use decision time:

```text
train: earlier impressions
validation: later impressions
test: latest held-out impressions
```

But simply sorting by impression time is not enough. Check:

- labels must mature;
- aggregates must only use earlier information;
- user/item encoders must be fitted on the training period when appropriate;
- temporal windows must not cross boundaries improperly;
- repeated or near-duplicate events should not leak across splits if that violates the intended generalization test.

If the label horizon is long, introduce a **purge/embargo** between periods or use observation cutoffs that guarantee all labels are mature without borrowing future information.

### 9. Catalog logs are part of the model input contract

Catalog data determines both features and eligibility.

For an e-commerce recommender, historical catalog state may include:

- price;
- stock/availability;
- seller;
- category;
- product status;
- region eligibility;
- policy restrictions.

An unavailable item should not magically appear as a valid negative just because it exists in the current catalog, and today's catalog cannot be used to reconstruct an old candidate universe. Ideally, the training pipeline can answer:

> What items were eligible, and what metadata did they have, at this exact historical request time?

### 10. Reproducibility

"Rebuild yesterday's model exactly" requires more than code in Git.

Record at least:

- immutable or versioned raw-log snapshot IDs;
- dataset-builder code version;
- config version;
- timezone/calendar rules;
- row-grain definition;
- attribution rules and windows;
- dedup key/rule;
- label-maturity policy;
- event-time/ingestion-time watermark;
- feature/catalog snapshot versions;
- train/validation/test boundaries;
- sampled-negative seed and sampling policy if applicable.

A dataset version should behave like a build artifact, not a live query whose answer changes as warehouses backfill.

### 11. Leakage and correctness tests

High-value tests are adversarial. Build tiny fixtures where the expected rows are hand-computable.

**Future-feature test**
A feature update occurs one second after the impression. The join must use the older state.

**Boundary test**
Put conversions exactly before, at, and after the attribution boundary. Assert the declared interval semantics.

**Late-event test**
A purchase occurs inside the event-time window but arrives after the snapshot watermark. The old dataset version must exclude it; an explicit backfill may include it in a new version.

**Duplicate-delivery test**
The same event ID arrives twice. Labels and counts must not double.

**Repeated-real-impression test**
Two distinct impression IDs for the same user-item must follow the declared repeated-exposure policy.

**Censoring test**
An impression whose purchase horizon has not matured must never be silently labeled zero.

**Fan-out test**
A supposedly one-to-one/as-of join accidentally yields two feature rows. Fail rather than multiply training rows.

**Exposure-integrity test**
If the training contract requires an impression, a click/purchase without a valid linked impression should be quarantined, separately modeled, or explicitly handled—not silently treated as a normal exposed example.

**Temporal-split test**
No validation/test decision time may precede training examples in a way that violates the split contract, and fitting statistics must come only from their allowed partition.

### 12. A compact worked example

Suppose:

```text
impression_time = "2026-01-10 12:00"
purchase_horizon = 7 days
dataset_snapshot = "2026-01-20 00:00"
```

Historical state:

```text
user 30d purchases at 12:00 = 3
item price at 12:00 = $20
item stock at 12:00 = in-stock
item price changes at 15:00 to $18
purchase occurs Jan 14
purchase event arrives Jan 15
```

Correct row:

```text
features:
  user_30d_purchases = 3
  price = 20
  stock = in-stock

label_purchase_7d = 1
```

The later `$18` price is forbidden because it was not known at the decision time. The purchase is valid because its event time falls inside the seven-day label window and, for this dataset snapshot, it has already arrived.

Now move the dataset snapshot to `"2026-01-14 12:00"`. The purchase event has not arrived yet. If reproducibility uses ingestion cutoffs, that older dataset version must not retroactively contain the purchase. A later backfill creates a new version.

### 13. Why this is Staff-depth rather than ETL trivia

Many apparent model wins or regressions are actually data-definition changes:

- changing the dedup rule reweights examples;
- changing attribution alters the target;
- changing censoring changes false-negative rates;
- using current catalog state changes the candidate universe;
- allowing late events to mutate history changes reproducibility;
- using future aggregates creates leakage;
- random splitting inflates offline metrics.

The important habit is to treat the training-table builder as part of the model specification. Data construction choices define the learning problem.

## Material Follow-ups / Scenario Variants

### Variant: purchases arrive up to 30 days late

Keep event time and ingestion time separately. Define a fixed observation horizon plus a watermark/snapshot policy. Do not silently mutate prior dataset versions as late events arrive. Either wait for sufficient maturity, accept a declared incompleteness rate, or produce versioned backfills. If business needs demand very fresh training, use dense short-delay targets such as click/cart for recent rows and let purchase labels mature later, potentially in a multi-task setup.

### Variant: video/feed instead of e-commerce

The same temporal contract holds, but horizons and repeated-exposure semantics change. Watch time, completion, skip, and hide are observed quickly, so censoring is shorter. Session state changes rapidly, repeated impressions create fatigue, and the exact feed position/exposure context matters more. Features must capture state strictly before the impression; using the remainder of the session to construct "current session" features leaks future intent.

### Variant: marketplace with changing inventory

Eligibility must be historical. A seller/item that is inactive today may have been valid at training-row time, and vice versa. Join seller status, inventory, region availability, and policy state as-of the impression. Candidate negatives should generally come from the historically eligible universe, not today's catalog.

### Variant: no reliable impression logs

State the limitation explicitly: you cannot cleanly distinguish unexposed items from exposed-and-ignored items, so ordinary negative labels are not identifiable from clicks/purchases alone. You can train with sampled/unobserved negatives under additional assumptions, use positive-unlabeled or pairwise formulations, or repair logging first. Offline metrics must be interpreted as conditional on those assumptions.

### Variant: a teammate says "all feature timestamps are before the label, so there is no leakage"

That is insufficient. The relevant cutoff is the **decision/impression time**, not the label time. A feature generated after the impression but before the purchase is still future information relative to the prediction being reconstructed. Also inspect aggregate computation windows, global preprocessing statistics, corrected/backfilled historical dimensions, and ingestion-time semantics.

### Variant: exact reproducibility versus best-known corrected history

These are two different products. Exact reproducibility freezes the historical snapshot used by the original run. Best-known corrected history allows backfills and corrections and therefore produces a new dataset version. Keep both semantics explicit; never let a supposedly immutable training dataset silently drift from one meaning to the other.

### Variant: proving correctness in code

A good test suite should construct a tiny synthetic timeline containing future feature versions, exact-window-boundary events, late arrivals, duplicate deliveries, repeated legitimate impressions, immature labels, and a join-fan-out trap. The expected output should be hand-computed. The point is not merely that the pipeline runs; it is that deliberately invalid temporal states fail loudly and deterministically.
