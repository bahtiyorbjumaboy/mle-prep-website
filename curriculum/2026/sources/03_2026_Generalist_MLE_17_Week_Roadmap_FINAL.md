# 2026 Generalist MLE Roadmap — FINAL

**Status:** ACTIVE 2026 GENERALIST ROADMAP  
**Start:** Sunday, September 6, 2026  
**End:** Thursday, December 31, 2026  
**Duration:** 17 roadmap weeks (Week 17 is a five-day year-end week)  
**Goal:** Generalist Machine Learning Engineer interview readiness by the end of 2026.  
**Knowledge:** all 130 core conversations across Banks 01, 02, 05, 07, 08, and 09.  
**Coding:** all 69 core coding IDs.  
**Project:** P0 — General MLE Pipeline.

## Fixed cadence

- **Knowledge:** 8 new conversations in each of Weeks 1–16; the final 2 conversations in Week 17.
- **Coding:** 5 new coding IDs in Week 1; exactly 4 new coding IDs in every Week 2–17.
- First exposure never substitutes for mastery.
- Due repairs/cold reviews outrank optional reading.
- No Search/IR + Recommendation/Ranking specialization curriculum is scheduled in 2026; that work begins in the separate 2027 specialization source set.

## Review queue

1. failed/Red repair due;
2. first re-attempt due 1–3 weeks after learning;
3. oldest ★ coding item not mastered;
4. oldest high-depth knowledge item not mastered;
5. random cross-domain core item;
6. mixed interview item if capacity remains.

## P0 requirement

P0 must demonstrate a production-shaped general ML workflow: problem definition, point-in-time-safe data, feature pipeline, baseline and stronger model, evaluation/calibration, testing, reproducibility, minimal training/serving boundary, monitoring/failure analysis, documentation, and defense.

# Week 1 — Sep 6–Sep 12, 2026 — Linear algebra foundations + coding baseline

## Knowledge — new exposure
- **Bank 01 — Linear Algebra (8):** B19, B20, B21, B23, B24, B25, A1, A2
- **New knowledge count:** 8.

## Coding — new exposure
- **DSA-01 — Two Sum ★**
- **DSA-02 — Group Anagrams**
- **NP-01 — Shapes, Axes, Broadcasting ★**
- **ML-01 — Cosine Similarity + Retrieval**
- **DBG-01 — Leaking Pipeline ★**
- **New coding count:** 5.

## Weekly tasks / milestone
- Set up the learning repo, mastery tracker, error log, and session-note convention.
- Establish cold baselines for DSA, NumPy shapes/broadcasting, cosine retrieval, and debugging.
- For linear algebra questions, derive key identities rather than memorizing definitions.
- No major project work yet.

## Mastery / review
- Establish baseline timing/error log; no forced cold re-attempts yet.

---

# Week 2 — Sep 13–Sep 19, 2026 — Linear algebra geometry, conditioning, and retrieval math

## Knowledge — new exposure
- **Bank 01 — Linear Algebra (8):** A3, A12, A6, A5, A8, A9, A11, A13
- **New knowledge count:** 8.

## Coding — new exposure
- **DSA-03 — Product Except Self**
- **DSA-05 — Container With Most Water ★**
- **SQL-01 — Aggregation / Conversion**
- **NP-02 — Batched Cosine Similarity + Top-K ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Continue linear algebra with explicit geometric and numerical-stability reasoning.
- Connect norms, similarity, projections, conditioning, eigendecomposition/SVD, and low-rank structure to ML use cases.
- Run 1–2 cold re-attempts from Week 1.
- Write one compact 'linear algebra for MLE' synthesis note.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 3 — Sep 20–Sep 26, 2026 — Probability foundations + metrics/data work

## Knowledge — new exposure
- **Bank 01 — Linear Algebra (4):** A14, A15, A16, A17
- **Bank 07 — Probability & Inference (4):** B24, B25, B26, B27
- **New knowledge count:** 8.

## Coding — new exposure
- **DSA-06 — Three Sum ★**
- **DSA-07 — Longest Substring Without Repeats ★**
- **ML-02 — Classification Metrics + ROC/PR AUC ★**
- **PD-01 — Feature Construction**
- **New coding count:** 4.

## Weekly tasks / milestone
- Build probability foundations around random variables, conditioning, expectation/variance, likelihood, and classification metrics.
- Practice translating probability assumptions into modeling/evaluation consequences.
- Use pandas/ML coding work to reinforce feature construction and metric correctness.
- Cold-retest one Week 1–2 coding item.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 4 — Sep 27–Oct 3, 2026 — Probability estimation, Bayes, and leakage-safe evaluation

## Knowledge — new exposure
- **Bank 07 — Probability & Inference (8):** B28, B29, B30, A1, A2, A3, A6, A7
- **New knowledge count:** 8.

## Coding — new exposure
- **DSA-08 — Minimum-Size Subarray Sum**
- **DSA-09 — First and Last Position**
- **SQL-02 — Join Grain and Fan-Out ★**
- **ML-03 — Leakage-Safe Splitting ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Emphasize estimation, Bayes, leakage-safe splitting, uncertainty, and correct join/data grain.
- Run the first 30–45 minute mixed mini-mock: DSA + probability/ML explanation.
- Create explicit tests for data leakage and train/test contamination.
- Repair any Red items before optional reading.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

## Gate — Foundation mini-mock
- Score framing, correctness, depth, implementation/testing, trade-offs, communication, and repair needs.

---

# Week 5 — Oct 4–Oct 10, 2026 — Hypothesis testing, experiments, and statistical decision-making

## Knowledge — new exposure
- **Bank 07 — Probability & Inference (8):** A8, A13, A15, A17, A5, A11, A12, A14
- **New knowledge count:** 8.

## Coding — new exposure
- **DBG-02 — Misaligned Labels / Duplicate Rows**
- **DSA-10 — Binary Search on the Answer ★**
- **DSA-11 — Valid Parentheses**
- **NP-03 — Vectorized Confusion Matrix**
- **New coding count:** 4.

## Weekly tasks / milestone
- Finish the main probability/inference surface: testing, confidence, experiments, power/variance-reduction concepts, and decision thresholds.
- Practice explaining p-values/CIs/experiment assumptions without rote definitions.
- Run 2–3 due cold re-attempts.
- Create one experiment-design checklist for later P0 work.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 6 — Oct 11–Oct 17, 2026 — Core ML foundations + system-design framing

## Knowledge — new exposure
- **Bank 07 — Probability & Inference (4):** A20, A21, A22, A23
- **Bank 02 — Core ML (4):** B21, B22, B23, B24
- **New knowledge count:** 8.

## Coding — new exposure
- **ML-04 — Stable Softmax / Cross-Entropy ★**
- **DSA-12 — Daily Temperatures ★**
- **DSA-13 — Linked-List Cycle**
- **SQL-03 — Latest Record Per Entity**
- **New coding count:** 4.

## Weekly tasks / milestone
- Start Core ML: objectives, bias/variance, regularization, feature/model assumptions, and reusable ML system-design framing.
- Use stable softmax/cross-entropy and SQL latest-record work to connect mathematical correctness with data correctness.
- Begin a reusable generalist ML system-design framework.
- No specialization content.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 7 — Oct 18–Oct 24, 2026 — Core ML generalization, validation, trees/ensembles

## Knowledge — new exposure
- **Bank 02 — Core ML (7):** B25, B26, A1, A10, A2, A3, A4
- **Bank 09 — ML System Design (1):** A1
- **New knowledge count:** 8.

## Coding — new exposure
- **PD-02 — Latest Record + As-Of Join**
- **DSA-14 — Reverse Linked List / Reverse Sublist**
- **DSA-15 — Subsets With Duplicates**
- **PT-01 — nn.Module + Shapes**
- **New coding count:** 4.

## Weekly tasks / milestone
- Cover validation, model selection, trees/ensembles, preprocessing, and generalization failure modes.
- Use point-in-time/as-of data coding to reinforce production-safe feature construction.
- Practice PyTorch module/shape reasoning.
- Run a mixed Core ML + coding review.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 8 — Oct 25–Oct 31, 2026 — Core ML metrics, calibration, clustering, debugging

## Knowledge — new exposure
- **Bank 02 — Core ML (7):** A5, A7, A11, A12, A13, A9, A14
- **Bank 09 — ML System Design (1):** A4
- **New knowledge count:** 8.

## Coding — new exposure
- **SQL-04 — Top-N Per Group**
- **DBG-03 — Axis / Broadcasting ★**
- **DSA-16 — Combination Sum ★**
- **DSA-17 — Maximum Depth + Balanced Tree**
- **New coding count:** 4.

## Weekly tasks / milestone
- Finish major Core ML interview surface: metrics, calibration, class imbalance, clustering, drift/debugging, and model-comparison reasoning.
- Run a 45–60 minute mixed core mock: DSA + SQL/data + Core ML.
- Select P0 dataset/theme and define target, schema, leakage constraints, and evaluation.
- Do not start specialization work.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

## Gate — Core ML gate
- Score framing, correctness, depth, implementation/testing, trade-offs, communication, and repair needs.

---

# Week 9 — Nov 1–Nov 7, 2026 — Deep learning foundations + P0 definition

## Knowledge — new exposure
- **Bank 02 — Core ML (5):** A16, A17, A18, A19, A20
- **Bank 09 — ML System Design (1):** A8
- **Bank 05 — Deep Learning & Optimization (2):** B30, B31
- **New knowledge count:** 8.

## Coding — new exposure
- **NP-04 — De-loop a Slow Function**
- **ML-05 — K-Means**
- **DSA-18 — Level-Order Traversal**
- **DSA-19 — Number of Islands ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Start Deep Learning: forward/backprop mechanics, activations, initialization, normalization, embeddings/attention prerequisites.
- P0: freeze public/synthetic dataset, problem statement, split policy, and initial feature pipeline.
- Use NumPy/vectorization and K-means/tree/graph coding to maintain broad implementation fluency.
- Cold-retest one earlier PyTorch/ML item if due.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 10 — Nov 8–Nov 14, 2026 — Optimization/training loops + point-in-time ML pipeline

## Knowledge — new exposure
- **Bank 05 — Deep Learning & Optimization (7):** B32, B33, B36, A1, A4, A2, A3
- **Bank 09 — ML System Design (1):** A11
- **New knowledge count:** 8.

## Coding — new exposure
- **SQL-05 — Sessionization ★**
- **PD-03 — Point-in-Time Feature Construction ★**
- **DSA-20 — Grid Shortest Path**
- **ML-06 — Logistic Regression From Scratch ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Cover optimization/training dynamics, loss behavior, numerical stability, and train/validation loop correctness.
- P0: implement point-in-time feature pipeline, baseline model, tests, and initial training loop.
- Debug NaN/numerical failures systematically.
- Start recording reproducibility seeds/configuration.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 11 — Nov 15–Nov 21, 2026 — Deep learning architectures + P0 baseline

## Knowledge — new exposure
- **Bank 05 — Deep Learning & Optimization (7):** A5, A7, A8, A10, A13, A11, A12
- **Bank 09 — ML System Design (1):** A13
- **New knowledge count:** 8.

## Coding — new exposure
- **PT-02 — Training / Validation Loop ★**
- **DBG-04 — NaNs / Numerical Failure ★**
- **DSA-21 — Connected Components**
- **DSA-22 — Course Schedule / Topological Sort ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Cover DL architecture/system concepts relevant to generalist MLE interviews: CNN/sequence/attention/transformer-level understanding, representation learning, and failure diagnosis.
- P0: preprocessing contract, stronger baseline/PyTorch model, evaluation harness.
- Practice graph/DP/SQL rolling-window coding under time pressure.
- Run 3–4 due re-attempts.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 12 — Nov 22–Nov 28, 2026 — DL training/evaluation + generalist mock

## Knowledge — new exposure
- **Bank 05 — Deep Learning & Optimization (7):** A15, A16, A17, A19, A20, A21, A23
- **Bank 09 — ML System Design (1):** A9
- **New knowledge count:** 8.

## Coding — new exposure
- **DSA-23 — Top-K Frequent Elements ★**
- **SQL-06 — Rolling Time Windows ★**
- **NP-05 — Padding / Masking / Pooling ★**
- **DSA-24 — Merge Intervals**
- **New coding count:** 4.

## Weekly tasks / milestone
- Finish remaining Deep Learning core and system-design items scheduled this week.
- P0: richer features, evaluation slices, leakage documentation, and error analysis.
- Run a 60-minute generalist MLE mock: DSA + data/SQL + ML/DL explanation.
- Keep holiday load moderate; reviews outrank optional additions.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

## Gate — Generalist midpoint mock
- Score framing, correctness, depth, implementation/testing, trade-offs, communication, and repair needs.

---

# Week 13 — Nov 29–Dec 5, 2026 — MLE practice foundations + reproducibility

## Knowledge — new exposure
- **Bank 05 — Deep Learning & Optimization (4):** A25, A26, A27, A28
- **Bank 09 — ML System Design (1):** A10
- **Bank 08 — ML Engineering Practice (3):** B23, B24, B25
- **New knowledge count:** 8.

## Coding — new exposure
- **DSA-25 — Subarray Sum Equals K ★**
- **PD-04 — Rolling Features Per Group**
- **ML-07 — Negative Sampling ★**
- **DSA-26 — Dynamic Programming Synthesis ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Start ML Engineering Practice: testing/CI, data validation, reproducibility, dependency/environment control, training/serving boundaries, and operational correctness.
- P0: checkpointing/resume, deterministic tests, packaging/reproducible environment.
- Use DP/rolling-feature/negative-sampling coding to keep algorithmic fluency.
- Create an MLE production-readiness checklist.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 14 — Dec 6–Dec 12, 2026 — MLE deployment/testing/monitoring + P0 hardening

## Knowledge — new exposure
- **Bank 08 — ML Engineering Practice (7):** B26, B27, B28, A1, A2, A3, A5
- **Bank 09 — ML System Design (1):** A2
- **New knowledge count:** 8.

## Coding — new exposure
- **SQL-07 — Deduplication / NULL Semantics**
- **PT-03 — Losses + Masking ★**
- **DBG-05 — PyTorch State / Lifecycle ★**
- **DSA-04 — Longest Consecutive Sequence**
- **New coding count:** 4.

## Weekly tasks / milestone
- Cover deployment, safe rollout/rollback, feature consistency, monitoring, retraining, state/lifecycle bugs, and evaluator correctness.
- P0: calibration/threshold analysis, minimal inference/batch-scoring interface, debugging regression tests.
- Practice Python component design and PyTorch masking/state correctness.
- Run an incident-style mock: identify → explain → fix → test.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 15 — Dec 13–Dec 19, 2026 — MLE reliability/latency/scaling + system design

## Knowledge — new exposure
- **Bank 08 — ML Engineering Practice (7):** A7, A9, A10, A11, A13, A14, A15
- **Bank 09 — ML System Design (1):** A3
- **New knowledge count:** 8.

## Coding — new exposure
- **SQL-08 — Ordered Funnel ★**
- **PY-01 — Standard-Library Event Processing**
- **PY-02 — Fit / Transform Component ★**
- **ML-08 — Calibration / ECE**
- **New coding count:** 4.

## Weekly tasks / milestone
- Cover latency, batch-vs-online design, scaling, fairness/replay/idempotency and related MLE operational trade-offs.
- Continue ML system-design scenarios with explicit capacity/SLO/monitoring thinking.
- P0: harden observability, failure analysis, README, and architecture diagram.
- Run 3–4 mixed cold coding re-attempts.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

---

# Week 16 — Dec 20–Dec 26, 2026 — System design synthesis + P0 defense preparation

## Knowledge — new exposure
- **Bank 08 — ML Engineering Practice (6):** A16, A18, A21, A22, A29, A30
- **Bank 09 — ML System Design (2):** A5, A6
- **New knowledge count:** 8.

## Coding — new exposure
- **SQL-09 — ML / Serving Log Analysis ★**
- **PT-04 — Tensor Surgery / Silent Shape Bugs ★**
- **PT-05 — Gradient Accumulation / Clipping / Scheduler**
- **DBG-06 — Evaluation Bugs ★**
- **New coding count:** 4.

## Weekly tasks / milestone
- Finish most ML System Design coverage and remaining MLE Practice questions.
- P0: finalize results, reproducibility, serving contract, limitations, and project-defense narrative.
- Run a near-full generalist MLE mock with coding + ML theory + system design + P0 defense.
- Create targeted repair list for final week only.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

## Gate — Pre-final readiness mock
- Score framing, correctness, depth, implementation/testing, trade-offs, communication, and repair needs.

---

# Week 17 — Dec 27–Dec 31, 2026 — Final core coverage + generalist MLE readiness gate

## Knowledge — new exposure
- **Bank 09 — ML System Design (2):** A7, A16
- **New knowledge count:** 2.

## Coding — new exposure
- **ML-09 — Bootstrap CI + Permutation Test**
- **PT-06 — Custom Dataset / Collate / Variable Lengths**
- **PT-07 — Reproducibility / Checkpoint Resume ★**
- **DBG-07 — Extend Existing Evaluator**
- **New coding count:** 4.

## Weekly tasks / milestone
- Complete the final 2 knowledge conversations and final 4 coding first exposures.
- Run targeted repairs only; no broad rereading.
- Run the final generalist MLE readiness gate: coding segment + ML/statistics/deep-learning discussion + system-design scenario + P0 defense.
- Record unresolved Red/Yellow items for January maintenance; do not begin the 2027 specialization curriculum until the readiness gate is complete.

## Mastery / review
- Complete due spaced re-attempts before optional expansion; preserve mixed-format review.
- Any substantive mock/coding failure creates an explicit repair item and re-test date.

## Gate — Final generalist MLE readiness gate
- Pass a mixed generalist MLE interview loop without relying on specialization knowledge.
- P0 must be complete and defensible.
- Core coding should be interview-ready broadly, with high-priority items cold-mastered.
- Remaining weaknesses must be explicit and small enough for normal maintenance rather than a missing curriculum domain.

---

# Coverage audit

- Core knowledge first exposure: **130/130**.
- Bank 01 — Linear Algebra: **20/20**.
- Bank 02 — Core ML: **23/23**.
- Bank 05 — Deep Learning & Optimization: **27/27**.
- Bank 07 — Probability & Inference: **24/24**.
- Bank 08 — ML Engineering Practice: **23/23**.
- Bank 09 — ML System Design: **13/13**.
- Core coding first exposure: **69/69**.
- Coding cadence: **Week 1 = 5; Weeks 2–17 = 4 each**.
- No 2027 specialization knowledge/coding is included.

# Final acceptance — December 31, 2026

- [ ] All 130 core knowledge conversations have first exposure.
- [ ] All 69 core coding IDs have first exposure.
- [ ] Early/high-priority core items are cold-mastered; later items are at least interview-ready with re-tests queued.
- [ ] P0 is reproducible, tested, documented, and defensible.
- [ ] Can handle mixed DSA/SQL/data/PyTorch/debugging work at generalist-MLE interview level.
- [ ] Can explain ML/statistics/deep-learning concepts and diagnose common modeling/data failures.
- [ ] Can design a general ML system with data, training, serving, experiment, monitoring, latency, failure, and rollback considerations.
- [ ] Can pass a full mixed generalist MLE mock without specialization support.

# Transition to 2027

After the final 2026 gate, begin the separate 2027 Staff-depth specialization curriculum for Search/IR and Recommendation/Ranking. The 2026 core becomes a maintenance surface, not a repeated curriculum.