---
type: session-note
title: "R01 multi-stage recommender architecture"
date: "2026-09-17"
curriculum: "sprint"
session_type: "theory"
items:
  - "2027:R01"
observed_mastery:
  "2027:R01": "Learned"
sprint_result:
  "2027:R01": "Yellow"
---

## Items Covered

- `2027:R01` — Two-stage and multi-stage recommender architecture.
- Candidate generation, optional pre-ranking, ranking, reranking, and post-processing.
- Stage-specific metrics and the candidate-set quality ceiling.
- Candidate-count / latency trade-offs.
- Stage-localized debugging and production fallbacks.

## Attempt / Reconstruction Evidence

The learner independently reconstructed:
- why exhaustive heavy ranking over a large corpus is impractical;
- the funnel from millions → thousands → hundreds → tens;
- retrieval as a high-recall stage rather than final ordering;
- the use of multiple candidate sources;
- optional pre-ranking as cheap pruning;
- ranking using richer user, item, interaction, and context features;
- reranking for slate-level diversity / freshness / broader objectives;
- post-processing for hard eligibility and validity rules.

In a second reconstruction, the learner correctly mapped:
- Recall@K to retrieval;
- quality lost versus compute/latency saved to pre-ranking;
- NDCG / MRR and task objectives to ranking;
- relevance-versus-diversity / constraints to reranking;
- latency, failures, freshness, and versioning to serving.

The learner also correctly explained why CTR alone cannot localize failures in a multi-stage system.

## Repairs and Precision Corrections

- Candidate generation should be described as **retrieval**, not statistical sampling.
- The candidate-set ceiling is structural: if an item is absent upstream, downstream ranking cannot recover it. A numerical Recall@K value does not directly become the numerical upper bound of a different downstream metric such as NDCG.
- Pre-ranking is optional.
- Once the candidate set is fixed, position-sensitive metrics such as NDCG / MRR / MAP are usually more diagnostic of the ranker than recall alone.
- Reranking is broader than diversity and freshness; it may enforce slate, business, exposure, or ecosystem constraints.
- CTR is an outcome metric, not a localization metric.
- Some hard validity filters may happen earlier than post-processing when carrying invalid candidates downstream would waste compute.

## Follow-ups / Variants Completed

- Stage-specific metric selection.
- Basic stage-localization debugging.
- Candidate-count / latency reasoning introduced.

Completed deeper variant:
- heavy-ranker p99 increase from 35 ms to 70 ms under a 120 ms total budget, with four explicit mitigation/trade-off pairs.


### Latency-budget reconstruction

Prompt: the heavy ranker increases from 35 ms to 70 ms and pushes the system above a 120 ms p99 budget. Propose at least four mitigations and state the trade-off for each.

The learner independently proposed:
1. Reduce retrieval candidate count → less downstream feature hydration and ranking; trade-off: lower candidate coverage / recall.
2. Strengthen pre-ranking → fewer candidates reach the heavy ranker; trade-off: over-pruning can remove valuable candidates.
3. Precompute or cache ranker features → less online feature computation; trade-off: staleness, storage, invalidation complexity, and serving dependencies.
4. Use a distilled or quantized ranker → less compute / memory bandwidth; trade-off: reduced model capacity or numerical approximation error.

Precision correction:
- Distillation and quantization are different techniques.
- Distillation trains a smaller student model to approximate a larger teacher.
- Quantization reduces numeric precision, e.g. FP32 → FP16/BF16 or INT8/INT4 depending hardware/tooling.
- "0.64 to 0.32" is not the right description of quantization.


### Debugging-incident reconstruction

Incident:
- offline NDCG@10 improves by 4%;
- candidate Recall@1000 unchanged;
- pre-ranker preservation unchanged;
- online conversion drops by 6%;
- CTR roughly flat;
- p99 rises from 105 ms to 118 ms under a 120 ms SLO;
- fallback rate unchanged;
- conversion drop concentrated on mobile;
- new ranker uses three new real-time features.

Learner strengths:
- correctly ruled retrieval down in priority because Recall@1000 was unchanged;
- correctly ruled pre-ranking down in priority because preservation metrics were unchanged;
- correctly recognized the offline/online mismatch and shifted attention toward serving/data issues;
- correctly noticed the mobile concentration and new real-time features as strong clues;
- proposed a safe mitigation: roll back mobile traffic to the previous model while investigating.

Precision / reasoning repairs:
1. Do not conclude that 118 ms p99 is irrelevant merely because it remains below the 120 ms SLO. It is close enough to the boundary that end-to-end mobile latency, client/network sensitivity, or tail shifts could still affect conversion.
2. Flat fallback rate does not rule out serving problems. Feature freshness, feature coverage, feature-value skew, request-time defaults, device-specific feature availability, or serialization differences can occur without changing fallback rate.
3. The three new real-time features are a strong hypothesis, but freshness is only one failure mode. Also check missingness/coverage, train-serving skew, device-specific population differences, timestamp alignment, default values, and feature distribution shifts.
4. Because CTR is flat while conversion falls, ranker objective mismatch or score/calibration change that preserves clicks but worsens purchase conversion should remain in the hypothesis set.
5. A strong debugging answer should explicitly rank hypotheses and name discriminating checks before choosing a root cause.

Recommended ranked hypotheses:
1. Mobile-specific serving / feature skew involving the new real-time features.
2. Objective mismatch or score/calibration change that preserves clicks but worsens purchase conversion.
3. Mobile-sensitive latency regression despite remaining just under the server-side SLO.
4. Less likely downstream constraint/presentation or segment-specific interaction not captured by aggregate offline NDCG.

Mitigation:
- mobile rollback or traffic split to the previous model is a reasonable immediate containment action while preserving desktop if it is healthy.


### Repaired debugging reconstruction

The learner successfully repaired the debugging approach by explicitly maintaining multiple hypotheses and pairing each with discriminating evidence:

1. **Mobile feature / serving skew**
   - Hypothesis: one or more of the three new real-time features may be stale, missing, defaulted, or distributionally shifted for mobile users.
   - Checks: freshness, missingness, default-value rate, and feature distributions split by mobile vs desktop.
   - Supporting evidence would be mobile-specific feature anomalies that are absent on desktop.

2. **Objective mismatch**
   - Hypothesis: flat CTR with lower conversion may mean the model still ranks clickable items well but ranks worse purchase-quality items.
   - Checks: purchase-oriented offline/online metrics and score distributions split by device.
   - Supporting evidence would be degraded purchase-oriented metrics despite stable click-oriented behavior.

3. **Mobile-sensitive latency regression**
   - Hypothesis: the higher latency may hurt mobile conversion even if the server-side p99 remains within the formal SLO.
   - Checks: conversion by latency bucket and mobile end-to-end latency.
   - Supporting evidence would be a clear conversion drop in higher-latency buckets or a mobile-specific latency/conversion relationship.

The learner correctly stated the evidence-to-localization logic: feature anomalies support serving/data skew; worse purchase-oriented metrics support objective mismatch; conversion degradation concentrated in high-latency buckets supports latency sensitivity.

This satisfies the R01 debugging requirement for first exposure.

## Observed Sprint Result and Mastery

- Observed mastery: **Learned**
- Sprint result: **Yellow**
- Reason: architecture, stage metrics, latency trade-offs, and debugging localization have all been reconstructed successfully. First-exposure treatment is complete; later spaced cold review is still required before Mastered.

## Review Plan

Schedule a later cold re-test rather than repeating first exposure. A future review should include one debugging/incident variant and one changed-constraint architecture variant.
