---
type: interview-answer
item: "2027:R02"
title: "Explicit, Implicit, and Exposure-Conditioned Feedback"
created: "2026-09-18"
updated: "2026-09-18"
tags:
  - recommendation
  - implicit-feedback
  - exposure-bias
  - labels
---

## Canonical Staff-Depth Question

Compare explicit and implicit feedback. Explain why non-interaction is not a negative and model exposure, examination, missing-not-at-random labels, repeated impressions, and delayed conversion.

## Mastery Answer

Explicit feedback is an intentional preference signal such as a rating, like/dislike, hide, or survey response. It is usually semantically clearer but sparse and highly selected: the users who choose to rate are not a random sample. Implicit feedback is behavior such as impressions, clicks, dwell, watch time, carts, purchases, skips, or repeated visits. It is abundant, but its semantics are weaker because behavior is produced jointly by user preference, the recommendation policy, position, UI, context, and opportunity to act.

The key mistake is treating every non-interaction as a negative. If an item was never exposed, the absence of a click tells us nothing about preference. Even after exposure, a user may not have examined the item because it was below the fold, in a low-attention position, or the session ended. A better data-generating view is:

`policy chooses exposure → user may examine → user may act → some outcomes arrive later`.

So labels should be exposure-conditioned. I would distinguish at least:

- **unexposed:** unknown / unlabeled for this interaction objective;
- **exposed but not reliably examined:** usually unknown or lower-confidence evidence;
- **exposed and examined but ignored after the observation window:** a defensible negative for the chosen objective;
- **positive interaction:** click, watch, cart, purchase, etc., depending on the target;
- **explicit negative:** hide, dislike, "not interested," return, or another action whose product semantics make it negative.

This is a missing-not-at-random problem because whether we observe feedback depends on the serving policy and user behavior. Popular or highly ranked items get more opportunities to collect labels, so the observed dataset is not the same as the preference distribution we ultimately care about. Exposure-aware negative construction helps training, and logged propensities or counterfactual methods become important when we need to compare policies rather than merely fit the logged one.

Repeated impressions must not be treated as independent identical negatives. Ten ignored impressions can overweight one user-item pair, and later impressions may reflect fatigue or changed context. I would define the row grain explicitly—often impression-level for CTR, but user-item-session/window-level for broader preference—then deduplicate or cap repeated evidence, preserve impression count/recency as features when useful, and distinguish first exposure from repeated exposure.

Delayed conversion creates right-censoring. A click today with no purchase yet is not a mature negative if purchases commonly arrive over the next several days. I would define an attribution window and only mark the example negative once that window has closed, or use a delayed-feedback/survival-style treatment when the delay distribution itself matters.

The interview-level principle is: **a label is valid only after defining the opportunity to observe it.** Before creating positives and negatives, specify exposure, examination, action semantics, repeated-exposure treatment, and label-maturity window.

## Learn the Concepts

### 1. Explicit versus implicit feedback

**Explicit feedback** is deliberately provided by the user to express preference. Examples include star ratings, thumbs-up/down, "not interested," hides, survey responses, or preference settings. Its advantage is semantic clarity: the action is intended to communicate something about preference. Its disadvantages are sparsity and selection bias. Users who rate are often unusually engaged, polarized, or motivated, so explicit feedback is not automatically representative.

**Implicit feedback** is inferred from behavior. Examples include impression, click, hover, dwell, watch, skip, cart, purchase, repeat visit, or abandonment. It is much denser and is generated naturally at serving scale, but it is ambiguous. A click may reflect relevance, curiosity, misleading presentation, or position. No click may reflect dislike, lack of examination, distraction, or insufficient time.

The same event can have different label semantics for different objectives. A click is a positive for a CTR model, but not necessarily a positive for purchase propensity or long-term satisfaction. A two-second video watch may be positive under a naive play objective but negative under a satisfaction objective.

### 2. The data-generating process

A recommender does not observe user-item preference uniformly. The system first chooses what the user can see. A useful causal ordering is:

$$
\text{policy} \rightarrow E \rightarrow X \rightarrow Y,
$$

where $E$ is exposure, $X$ is examination or meaningful opportunity to inspect, and $Y$ is the interaction or outcome. Context, position, UI, user state, and item properties can affect several of these variables.

The observed interaction rate is therefore closer to $P(Y=1 \mid E=1)$, often further conditioned on examination and the logged policy, than to an unconditional preference probability $P(Y=1)$. This distinction is why recommendation logs are policy-conditioned data.

### 3. Why non-interaction is not a negative

Suppose a catalog contains 100 items. The system shows 10, the user actually scrolls far enough to examine 5, clicks 1, and eventually purchases that item.

- The **90 unexposed items** are not negatives. The user never had an opportunity to interact.
- The **5 exposed but unexamined items** are also weak evidence; absence of action may simply mean absence of attention.
- The **4 examined-but-ignored items** are plausible negatives for a click objective, assuming the examination signal and observation window are trustworthy.
- The **clicked item** is positive for click, but its purchase label is unresolved until the purchase attribution window matures.

This makes implicit recommendation data resemble a **positive-unlabeled** problem more than ordinary fully labeled classification.

### 4. Exposure and examination are different

An impression event often means the system rendered or logged an item, not that the user actually processed it. Examination can depend on:

- rank/position;
- viewport visibility;
- scrolling depth;
- carousel position;
- dwell on the containing surface;
- whether the app was foregrounded;
- whether the session ended before the item was reachable.

If reliable examination telemetry exists, use it. If it does not, be explicit that exposed-but-unclicked labels are noisy negatives whose error rate depends on position and UI behavior.

### 5. Missing-not-at-random labels

The missing labels are not random. The serving policy preferentially exposes some items—often popular, historically strong, sponsored, fresh, or already predicted to be relevant. Those items collect more interaction data and therefore influence the next model more strongly. This can create a feedback loop:

$$
\text{policy preference} \rightarrow \text{more exposure} \rightarrow \text{more observed positives} \rightarrow \text{stronger future preference}.
$$

This matters both for **training** and **evaluation**. Exposure-aware training avoids treating never-shown items as ordinary negatives. For unbiased policy comparison, however, label construction alone is not sufficient; one may need propensities, randomized traffic, IPS/SNIPS/DR-style methods, or online experiments. Those are deeper topics owned by later IDs such as R25/R26.

### 6. What counts as a defensible negative?

A "true negative" in recommender training is usually an operational definition, not a metaphysical statement that the user dislikes the item. A stronger negative has more of the following evidence:

1. the item was exposed;
2. it was plausibly examined;
3. the user had enough time/opportunity to act;
4. the outcome window has matured;
5. the user chose a competing item or explicitly rejected this one;
6. the semantics match the modeled objective.

An explicit hide/dislike is often stronger negative evidence than a non-click. A completed exposure followed by a rapid skip can be strong negative evidence for a video-satisfaction target, but may be irrelevant for a purchase target.

### 7. Repeated impressions

Repeated exposure creates several problems if each impression is naively inserted as an independent negative:

- **overweighting:** one user-item pair can dominate the loss simply because the serving policy repeatedly showed it;
- **dependence:** impressions from the same user/session are not independent samples;
- **fatigue:** the meaning of the fifth impression may differ from the first;
- **policy confounding:** frequent exposure may reflect the old model's preference, not true user preference.

The correct treatment depends on the training objective and row grain. For impression-level CTR, repeated impressions may legitimately remain separate rows, but weighting, user/session clustering, and position/context features matter. For preference or retrieval objectives, it is often better to aggregate or cap repeated user-item negatives within a time/session window while retaining count, recency, or exposure history as features.

### 8. Delayed conversion and censoring

Clicks, watches, and purchases can arrive on different timescales. Consider an ad or commerce recommendation shown at time $t_0$. If purchases often happen up to seven days later, labeling the example as a purchase-negative at $t_0+1$ hour is incorrect. The example is **right-censored**: the final outcome has not had time to arrive.

Common strategies include:

- train only on examples whose attribution window has closed;
- define explicit conversion windows, such as purchase within 7 days of click or impression;
- keep unresolved examples out of the negative class until maturity;
- model time-to-event or delayed feedback directly when latency of conversion is itself important.

Longer windows improve label completeness but make training data older. Shorter windows increase freshness but create false negatives. The window is therefore a modeling and product decision, not a logging afterthought.

### 9. Label table design

A useful conceptual label table has one row per chosen grain, for example user-item-impression or user-item-session, with fields such as:

- `exposed`;
- `examined` or examination proxy;
- position / surface / policy version;
- impression count and recency;
- positive action(s);
- explicit negative action(s);
- event timestamps;
- attribution-window end;
- `label_mature`;
- final task-specific label.

The important part is not the exact schema. It is that **unknown**, **weak negative**, **mature negative**, and **positive** are not silently collapsed into one binary target before the assumptions are made explicit.

### 10. Relationship to negative sampling

Negative sampling is downstream of label semantics. First determine which items are eligible negatives. Then decide how to sample them efficiently. Uniformly sampling from the whole catalog can accidentally treat unexposed but relevant items as negatives. Exposure-aware negatives are usually more defensible for an interaction objective because the user had an opportunity to respond. Hard-negative mining adds another layer and can increase false-negative risk if "hard" means "highly plausible positive."

### 11. Failure modes to diagnose

If a recommender's offline metric improves while online quality degrades, label construction is one place to inspect. Warning signs include:

- a surge in negative examples caused by logging more impressions rather than genuine behavior change;
- changed viewport or impression semantics after a client release;
- treating late conversions as negatives;
- counting the same impression/action multiple times;
- a policy rollout changing exposure distribution while the model is trained as if data were IID;
- aggregate gains driven only by popular, heavily exposed items.

The diagnostic sequence starts by reconstructing the logged data-generating process and checking label counts by exposure state, position, policy version, delay, and repeated-impression count.

## Material Follow-ups / Scenario Variants

### Construct labels for a commerce recommender

For a purchase-oriented ranker, I would not define every non-purchase as negative. I would start from eligible exposures, record whether the product was actually viewable, preserve clicks/carts as intermediate outcomes, and wait until a defined purchase window matures. An explicit "not interested" or product dismissal can be a stronger negative. Recently exposed examples with open conversion windows stay unresolved rather than entering the negative class.

### What changes for a short-video feed?

Exposure and examination are closer together because content may autoplay, but they are still not identical. A rendered thumbnail is weaker exposure than playback start. A very fast swipe can be an explicit negative-like signal; meaningful watch duration or completion is stronger positive evidence. Repeated impressions can create fatigue, and the objective must distinguish accidental play from satisfaction.

### What changes for ads?

Use viewable impressions rather than merely requested ads when possible. For CTR, a mature viewable impression with no click can serve as a negative. For conversion, no click or no purchase immediately after the impression is not enough because conversion is delayed. Position and auction policy create strong selection bias, so counterfactual evaluation requires propensity/experiment information beyond simple binary labels.

### What changes for notifications?

"Sent" is not necessarily exposure. Delivery success, device state, and whether the notification was actually presented matter. An unopened notification should not be labeled negative if delivery failed. Open and downstream-action windows may also differ, so label maturity must be objective-specific.

### Changed constraint: no examination telemetry

If I cannot observe examination, I would not pretend impression-without-click is a clean negative. I would use the best available opportunity proxies such as position, viewport eligibility, scroll depth, or surface dwell, treat the remaining negatives as noisy, slice metrics by position/surface, and consider small randomized exposure experiments to estimate how much the logging policy is distorting behavior.

### Changed constraint: heavy repeated exposure

If some user-item pairs receive many impressions, I would inspect whether the training objective is unintentionally weighting the old serving policy. Depending on the task, I would cap or aggregate negatives per user-item-window, add exposure-count/recency features, and evaluate separately on first-exposure versus repeated-exposure cases.
