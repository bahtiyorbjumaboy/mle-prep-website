# 2026 Generalist MLE Coding Set — FINAL

**Status:** ACTIVE 2026 GENERALIST CODING SET  
**Roadmap window:** Sunday, September 6, 2026 through Thursday, December 31, 2026  
**Count:** 100 coding IDs = 69 roadmap-core + 31 generalist-depth extension IDs  
**Scope:** Deep Generalist MLE interview readiness across SWE/DSA, SQL/data work, Python/NumPy/pandas, classical ML implementation, PyTorch/framework coding, debugging/testing, and production-shaped implementation. Search/IR + Recommendation/Ranking specialization coding remains deferred to the separate specialization curriculum.

## Track counts

| Track | Roadmap core | Depth extension | Total |
|---|---:|---:|---:|
| DSA / SWE Algorithms | 26 | 6 | 32 |
| SQL | 9 | 4 | 13 |
| Python / NumPy / pandas | 11 | 7 | 18 |
| General ML Implementation | 9 | 8 | 17 |
| PyTorch / Framework | 7 | 4 | 11 |
| Debugging / Testing / Existing Code | 7 | 2 | 9 |
| **Total** | **69** | **31** | **100** |

## Mastery contract

- **0 — Unseen**
- **1 — Learned:** serious attempt completed; solution understood after review/hints if needed.
- **2 — Interview-ready:** solved independently under the intended time box with correct explanation.
- **3 — Mastered:** solved cold after spacing with edge cases, testing, follow-ups, and complexity/resource defense.

Mastery requires **recognition → reasoning → implementation → validation → explanation**.

Problem formats:
- **LIVE** — realistic interview-sized unit.
- **EXTENDED_DRILL** — staged broader implementation.
- **CAPSTONE** — project/integration work.

For every ★ problem, where applicable, include:
1. one hand-computed fixture;
2. one boundary/empty/singleton case;
3. one invariant/property test;
4. one adversarial bug-revealing case;
5. deterministic-seed/reproducibility checks when randomness exists.


## Practice workflow — VS Code + pytest

Use this workflow whenever a coding ID is turned into a local practice workspace. The purpose is to preserve learner ownership while making every problem executable, testable, reviewable, and easy to revisit cold.

### Default workspace

Create one directory per coding ID:

```text
problems/<problem_id>/
  README.md
  solution.py
  test_solution.py
  notes.md
```

Adapt filenames only when the problem genuinely requires SQL, multiple modules, data fixtures, or framework-specific structure. Keep one canonical problem directory per ID rather than creating a new directory for every attempt.

### File contract

**`README.md`**
- copy the exact canonical interview prompt from this bank;
- state required function/class signatures, inputs, outputs, constraints, and allowed libraries;
- include clarification questions or assumptions that an interviewer could reasonably expect;
- do **not** include the target solution, giveaway pseudocode, or the name of a hidden algorithmic primitive when the interview prompt itself would not reveal it.

**`solution.py`**
- provide imports, public signatures/interfaces, docstrings where useful, and `TODO` markers only;
- do not prefill the intended algorithm in **INTERVIEW** mode;
- the learner owns the implementation.

**`test_solution.py`**
- use deterministic `pytest` tests;
- include ordinary correctness cases plus specification-derived edge cases;
- for ★ problems, include applicable hand-computed fixtures, boundary cases, invariants/properties, adversarial bug-revealing cases, and deterministic-seed checks;
- tests may encode the specification, but should not reveal the intended implementation strategy;
- use tolerances deliberately for floating-point code (`pytest.approx`, `numpy.testing`, or equivalent);
- test shapes, dtypes, ordering, determinism, mutation/state behavior, and failure contracts when they are part of the problem;
- for randomized algorithms, test statistical or deterministic-seed properties rather than brittle exact samples unless exact samples are part of the contract.

**`notes.md`**
- before coding, record clarification, baseline, invariant/objective, intended complexity, and important edge cases;
- after the attempt, record mistakes, failed assumptions, debugging evidence, and the final reasoning;
- keep concise notes that help a later cold re-attempt; do not turn the notes into a copied solution transcript.

### Session modes

Use one explicit mode per practice session:

- **INTERVIEW — default.** Create scaffold + tests, but reveal no solution or giveaway pseudocode. The learner first explains the approach and implements independently under the intended time box.
- **HINT.** Provide the smallest next hint needed: first a diagnostic question, then an invariant/shape/data-grain clue, then a more concrete direction only if needed. Do not jump directly to the solution.
- **REVIEW/SOLUTION.** Enter only after an independent attempt is complete or the learner explicitly requests it. At this point compare implementations, explain the canonical mechanism, repair bugs, improve tests, and discuss alternatives/trade-offs.

### Standard practice loop

For each problem:

1. **Generate the workspace.** Create `README.md`, learner-owned implementation file(s), `test_solution.py`, and `notes.md` from the canonical ID.
2. **Clarify before coding.** State input/output contracts, assumptions, shapes or row grain, edge cases, and allowed libraries.
3. **Reason aloud.** Give a simple baseline, identify the key invariant/objective/equation, and state expected time/memory cost before implementation.
4. **Implement independently.** Stay inside the intended interview time box when doing a timed attempt. Do not consult the solution during INTERVIEW mode.
5. **Run focused tests.** Start with a small relevant subset, then run the full suite, for example:

   ```bash
   pytest -q
   ```

   or, while localizing one failure:

   ```bash
   pytest -q test_solution.py::test_name
   ```

6. **Debug from evidence.** Read the traceback/assertion, localize the failing contract, form a root-cause hypothesis, make the smallest justified fix, rerun the focused test, then rerun the full suite. Do not patch randomly until tests turn green.
7. **Defend the solution.** Explain correctness, complexity/resources, numerical or data issues, tests, and at least one changed-constraint follow-up.
8. **Review only after ownership.** If needed, switch to REVIEW/SOLUTION and compare against a stronger implementation or alternative approach.
9. **Record the lesson.** Update `notes.md` with the specific mistake or transferable insight rather than copying the full answer.
10. **Cold re-attempt later.** Re-solve after spacing, ideally with changed surface wording, inputs, constraints, or one hidden failure mode. Passing the original tests immediately after review is not mastery.

### Workspace setup checklist

A reusable setup checklist is:

```text
Start from the 2026 Generalist MLE coding-set Markdown file.
Set up problem <ID> in INTERVIEW mode for VS Code.
Create the problem workspace with README.md, solution.py (or the appropriate implementation file), test_solution.py, and notes.md.
Preserve the exact canonical prompt and interfaces.
Create a strong deterministic pytest suite, including applicable edge, adversarial, invariant, and numerical cases.
Do not reveal the solution, giveaway pseudocode, or hidden implementation strategy.
```

For SQL problems, use an appropriate SQL file plus deterministic fixture/expected-result tests. For PyTorch, data, or multi-file problems, adapt the workspace while preserving the same ownership and testing contract.

### Pytest acceptance rule

`pytest` passing is necessary but not sufficient. A problem reaches **Interview-ready** only when the learner can also explain why the implementation is correct, derive or state the relevant ML/math mechanism when applicable, reason about complexity/resources, handle material edge cases, and answer the problem's follow-ups without solution dependence.


## Transfer / surprise-resistance contract

The bank is intentionally finite; no problem list can guarantee that an interview will never contain an unfamiliar task. The target is therefore **transfer**, not memorization. Interview-ready performance requires being able to convert an unfamiliar prompt into a correct implementation by identifying its underlying primitive.

For every coding family, practice the following loop:

1. restate input/output contracts and shape/grain semantics;
2. give a simple correct baseline before optimizing;
3. identify the invariant, objective, or mathematical definition being implemented;
4. implement without relying on a convenience library that hides the tested concept unless the interviewer allows it;
5. test a hand-computed example plus adversarial edge cases;
6. state time, memory, numerical-stability, and data-size limits;
7. handle one changed-constraint follow-up;
8. on later review, solve a variant whose surface wording differs from the original problem.

For **ML-concept → code** prompts specifically, be able to move in both directions:

`definition / equation → scalar reference implementation → vectorized implementation → tests → numerical edge cases → complexity`.

For **dataframe / SQL** prompts, explicitly establish row grain, key uniqueness, join cardinality, timestamp semantics, missing-value policy, and deterministic tie handling before implementation.

For **PyTorch** prompts, explicitly track tensor shapes, devices/dtypes, training/eval state, autograd graph lifetime, masking semantics, and reduction denominators.

For **SWE-leaning MLE** prompts, code production-quality interfaces: deterministic behavior where expected, explicit error handling, sensible state ownership, tests, and resource reasoning.

# First-exposure schedule

## Week 1
- **DSA-01 — Two Sum ★**
- **DSA-02 — Group Anagrams**
- **NP-01 — Shapes, Axes, Broadcasting ★**
- **ML-01 — Cosine Similarity + Retrieval**
- **DBG-01 — Leaking Pipeline ★**

## Week 2
- **DSA-03 — Product Except Self**
- **DSA-05 — Container With Most Water ★**
- **SQL-01 — Aggregation / Conversion**
- **NP-02 — Batched Cosine Similarity + Top-K ★**

## Week 3
- **DSA-06 — Three Sum ★**
- **DSA-07 — Longest Substring Without Repeats ★**
- **ML-02 — Classification Metrics + ROC/PR AUC ★**
- **PD-01 — Feature Construction**

## Week 4
- **DSA-08 — Minimum-Size Subarray Sum**
- **DSA-09 — First and Last Position**
- **SQL-02 — Join Grain and Fan-Out ★**
- **ML-03 — Leakage-Safe Splitting ★**

## Week 5
- **DBG-02 — Misaligned Labels / Duplicate Rows**
- **DSA-10 — Binary Search on the Answer ★**
- **DSA-11 — Valid Parentheses**
- **NP-03 — Vectorized Confusion Matrix**

## Week 6
- **ML-04 — Stable Softmax / Cross-Entropy ★**
- **DSA-12 — Daily Temperatures ★**
- **DSA-13 — Linked-List Cycle**
- **SQL-03 — Latest Record Per Entity**

## Week 7
- **PD-02 — Latest Record + As-Of Join**
- **DSA-14 — Reverse Linked List / Reverse Sublist**
- **DSA-15 — Subsets With Duplicates**
- **PT-01 — nn.Module + Shapes**

## Week 8
- **SQL-04 — Top-N Per Group**
- **DBG-03 — Axis / Broadcasting ★**
- **DSA-16 — Combination Sum ★**
- **DSA-17 — Maximum Depth + Balanced Tree**

## Week 9
- **NP-04 — De-loop a Slow Function**
- **ML-05 — K-Means**
- **DSA-18 — Level-Order Traversal**
- **DSA-19 — Number of Islands ★**

## Week 10
- **SQL-05 — Sessionization ★**
- **PD-03 — Point-in-Time Feature Construction ★**
- **DSA-20 — Grid Shortest Path**
- **ML-06 — Logistic Regression From Scratch ★**

## Week 11
- **PT-02 — Training / Validation Loop ★**
- **DBG-04 — NaNs / Numerical Failure ★**
- **DSA-21 — Connected Components**
- **DSA-22 — Course Schedule / Topological Sort ★**

## Week 12
- **DSA-23 — Top-K Frequent Elements ★**
- **SQL-06 — Rolling Time Windows ★**
- **NP-05 — Padding / Masking / Pooling ★**
- **DSA-24 — Merge Intervals**

## Week 13
- **DSA-25 — Subarray Sum Equals K ★**
- **PD-04 — Rolling Features Per Group**
- **ML-07 — Negative Sampling ★**
- **DSA-26 — Dynamic Programming Synthesis ★**

## Week 14
- **SQL-07 — Deduplication / NULL Semantics**
- **PT-03 — Losses + Masking ★**
- **DBG-05 — PyTorch State / Lifecycle ★**
- **DSA-04 — Longest Consecutive Sequence**

## Week 15
- **SQL-08 — Ordered Funnel ★**
- **PY-01 — Standard-Library Event Processing**
- **PY-02 — Fit / Transform Component ★**
- **ML-08 — Calibration / ECE**

## Week 16
- **SQL-09 — ML / Serving Log Analysis ★**
- **PT-04 — Tensor Surgery / Silent Shape Bugs ★**
- **PT-05 — Gradient Accumulation / Clipping / Scheduler**
- **DBG-06 — Evaluation Bugs ★**

## Week 17
- **ML-09 — Bootstrap CI + Permutation Test**
- **PT-06 — Custom Dataset / Collate / Variable Lengths**
- **PT-07 — Reproducibility / Checkpoint Resume ★**
- **DBG-07 — Extend Existing Evaluator**


# Generalist-depth extension schedule

The original 69 IDs remain the **roadmap-core first-exposure schedule**. The 31 IDs below are an extension for the longer deep-generalist plan; they do not need to be forced into the original 17-week calendar. Add them only after prerequisites are comfortable, and prioritize cold re-attempts over new exposure. A practical default is 2–3 extension IDs per week while maintaining the core review queue.

## Extension Block A — ML primitives that commonly become coding questions
- **ML-10 — Entropy, Gini, and Information Gain ★**
- **ML-11 — Decision Stump / Best Tree Split ★**
- **NP-06 — Pairwise Distances + Vectorized kNN Primitives ★**
- **ML-13 — kNN Classifier / Regressor From Scratch**
- **ML-12 — Linear + Ridge Regression From Scratch ★**

## Extension Block B — numerical ML + representation mechanics
- **NP-07 — Covariance, Correlation, Standardization, Whitening**
- **ML-14 — PCA From Scratch with SVD / Eigendecomposition ★**
- **ML-15 — Naive Bayes From Scratch**
- **ML-16 — SGD, Momentum, RMSProp, Adam, AdamW Updates ★**
- **ML-17 — Gradient Checking + Tiny Neural Net Backprop ★**

## Extension Block C — dataframe and Python assessment fluency
- **PD-05 — Mixed pandas Assessment ★**
- **PD-06 — Reshape, Explode, Multi-Key Merge, and Reconciliation**
- **NP-08 — Sampling, Randomness, and Vectorized Monte Carlo ★**
- **PY-03 — Lazy Iterators, Batching, and Streaming Aggregation**
- **PY-04 — Concurrency-Safe Worker / Queue Exercise**

## Extension Block D — PyTorch implementation depth
- **PT-08 — Scaled Dot-Product Attention + Masks ★**
- **PT-09 — CNN Module + Shape / Parameter Accounting**
- **PT-10 — Mixed Precision, Inference Mode, and Batched Inference ★**
- **PT-11 — Freeze / Unfreeze Transfer Learning + Optimizer Groups**

## Extension Block E — SWE / systems coding for MLE roles
- **DSA-27 — LRU Cache ★**
- **DSA-28 — Trie / Prefix Index**
- **DSA-29 — Union-Find / Dynamic Connectivity**
- **DSA-30 — Dijkstra / Weighted Shortest Path ★**
- **DSA-31 — Heap Scheduler / Meeting Rooms + Resource Assignment**
- **DSA-32 — Token-Bucket Rate Limiter + Testable Clock ★**

## Extension Block F — SQL + production debugging
- **SQL-10 — Cohort Retention**
- **SQL-11 — Experiment Metrics + Sample-Ratio Checks ★**
- **SQL-12 — Point-in-Time Features in SQL ★**
- **SQL-13 — Data Reconciliation / Quality Invariants**
- **DBG-08 — Performance Regression / Profiling + Vectorization ★**
- **DBG-09 — Training / Serving Parity and Version-Skew Bug ★**

## Extension acceptance rule

Do not mark an extension item complete after seeing one canonical solution. For each ★ extension item, later solve at least one transfer variant with changed shapes/data types/objective/constraints. The objective is to make unfamiliar assessment wording feel like recombination of known primitives.


---

# Full problem bank

# Track A — DSA / SWE Algorithms

## DSA-01 — Two Sum ★
**First exposure:** Week 1  
**Level:** L1  
**Time box:** 15 min
**Format:** LIVE  

**Interview prompt.** Given an integer array `nums` and integer `target`, return the indices of two distinct elements whose values sum to `target`. Assume exactly one valid pair exists. Solve in one pass.

**Core concepts.** hash map; complement invariant; check-before-insert.

**Complexity / resource target.** O(n) time, O(n) space.

**Follow-ups / edge cases.** duplicates; streaming input.

## DSA-02 — Group Anagrams
**First exposure:** Week 1  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given a list of strings, group strings that contain the same characters with the same multiplicities. The order of groups and strings within groups does not matter.

**Core concepts.** canonical hash keys; count tuples vs sorting.

**Complexity / resource target.** O(total characters) with fixed-alphabet counts.

**Follow-ups / edge cases.** Unicode; stable output ordering.

## DSA-03 — Product Except Self
**First exposure:** Week 2  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given an integer array `nums`, return `out` where `out[i]` is the product of every element except `nums[i]`. Do not use division and run in O(n).

**Core concepts.** prefix/suffix products; two-pass construction.

**Complexity / resource target.** O(n) time, O(1) auxiliary space excluding output.

**Follow-ups / edge cases.** zero values; overflow discussion.

## DSA-04 — Longest Consecutive Sequence
**First exposure:** Week 14  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given an unsorted integer array, return the length of the longest set of consecutive values.

**Core concepts.** set membership; start only at run heads; amortization.

**Complexity / resource target.** O(n) expected time, O(n) space.

**Follow-ups / edge cases.** duplicates; return the sequence.

## DSA-05 — Container With Most Water ★
**First exposure:** Week 2  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given heights `h[i]`, choose two indices that maximize the contained area. Return the maximum area.

**Core concepts.** two pointers; exhaustion/correctness argument.

**Complexity / resource target.** O(n) time, O(1) space.

**Follow-ups / edge cases.** prove why moving the shorter side is safe.

## DSA-06 — Three Sum ★
**First exposure:** Week 3  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given an integer array, return all unique triplets whose values sum to zero.

**Core concepts.** sort + two pointers; duplicate skipping.

**Complexity / resource target.** O(n^2) time after sort.

**Follow-ups / edge cases.** general target; k-sum decomposition.

## DSA-07 — Longest Substring Without Repeats ★
**First exposure:** Week 3  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given a string, return the length of the longest substring containing no repeated characters.

**Core concepts.** variable sliding window; shrink-while-invalid.

**Complexity / resource target.** O(n) time.

**Follow-ups / edge cases.** last-seen jump; fixed-window warm-up.

## DSA-08 — Minimum-Size Subarray Sum
**First exposure:** Week 4  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given positive integers `nums` and positive integer `target`, return the minimum length of a contiguous subarray whose sum is at least `target`, or 0 if none exists.

**Core concepts.** sliding window; shrink-while-valid; positivity assumption.

**Complexity / resource target.** O(n) time.

**Follow-ups / edge cases.** why negative values break the method.

## DSA-09 — First and Last Position
**First exposure:** Week 4  
**Level:** L1/L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given a sorted array containing duplicates and a target, return the first and last index of the target, or `[-1,-1]`.

**Core concepts.** lower/upper bounds; binary-search invariants.

**Complexity / resource target.** O(log n) time.

**Follow-ups / edge cases.** insertion point; half-open intervals.

## DSA-10 — Binary Search on the Answer ★
**First exposure:** Week 5  
**Level:** L3  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Given nonnegative `nums` and integer `k`, split `nums` into `k` nonempty contiguous subarrays so that the largest subarray sum is minimized. Return that minimum.

**Core concepts.** monotonic feasibility predicate; search bounds.

**Complexity / resource target.** O(n log(sum(nums))).

**Follow-ups / edge cases.** prove monotonicity; infeasible k.

## DSA-11 — Valid Parentheses
**First exposure:** Week 5  
**Level:** L1  
**Time box:** 15 min
**Format:** LIVE  

**Interview prompt.** Given a string containing `()[]{}`, return whether it is well formed.

**Core concepts.** stack; nesting invariant; early rejection.

**Complexity / resource target.** O(n) time, O(n) space.

**Follow-ups / edge cases.** minimum deletions to balance.

## DSA-12 — Daily Temperatures ★
**First exposure:** Week 6  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given daily temperatures, return for each day the number of days until a warmer temperature, or 0 if none exists.

**Core concepts.** monotonic stack; indices; amortized analysis.

**Complexity / resource target.** O(n) time.

**Follow-ups / edge cases.** next greater element; circular variant.

## DSA-13 — Linked-List Cycle
**First exposure:** Week 6  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given the head of a singly linked list, determine whether a cycle exists and, if so, return the node where it begins.

**Core concepts.** Floyd pointers; phase-two proof.

**Complexity / resource target.** O(n) time, O(1) space.

**Follow-ups / edge cases.** cycle length.

## DSA-14 — Reverse Linked List / Reverse Sublist
**First exposure:** Week 7  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Reverse a singly linked list iteratively. Then reverse only nodes from positions `m` through `n` inclusive and return the new head.

**Core concepts.** pointer rewiring; dummy head; reconnection.

**Complexity / resource target.** O(n) time, O(1) space.

**Follow-ups / edge cases.** recursive full-list reversal and stack cost.

## DSA-15 — Subsets With Duplicates
**First exposure:** Week 7  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Return all subsets of a list. Then support duplicate input values without returning duplicate subsets.

**Core concepts.** backtracking; choose/explore/unchoose; duplicate skipping.

**Complexity / resource target.** O(2^n) output-sensitive.

**Follow-ups / edge cases.** iterative generation.

## DSA-16 — Combination Sum ★
**First exposure:** Week 8  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given distinct positive candidate values and a target, return all unique combinations summing to the target; each candidate may be used repeatedly.

**Core concepts.** backtracking; start-index invariant; pruning.

**Complexity / resource target.** output-sensitive exponential.

**Follow-ups / edge cases.** each candidate usable once.

## DSA-17 — Maximum Depth + Balanced Tree
**First exposure:** Week 8  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** For a binary tree, return its maximum depth and determine whether it is height-balanced.

**Core concepts.** tree DFS; return information upward.

**Complexity / resource target.** O(n) optimized.

**Follow-ups / edge cases.** diameter; naive O(n^2) balance check.

## DSA-18 — Level-Order Traversal
**First exposure:** Week 9  
**Level:** L1  
**Time box:** 15 min
**Format:** LIVE  

**Interview prompt.** Return a binary tree's level-order traversal as a list of levels.

**Core concepts.** BFS; queue; level boundaries.

**Complexity / resource target.** O(n) time.

**Follow-ups / edge cases.** zigzag traversal.

## DSA-19 — Number of Islands ★
**First exposure:** Week 9  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given a binary grid, count 4-directionally connected components of land.

**Core concepts.** grid DFS/BFS; visited state; bounds.

**Complexity / resource target.** O(rows*cols).

**Follow-ups / edge cases.** largest island; mutation vs visited set.

## DSA-20 — Grid Shortest Path
**First exposure:** Week 10  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given an unweighted obstacle grid, return the shortest path length from the top-left cell to the bottom-right cell using 4-directional moves, or -1 if unreachable.

**Core concepts.** BFS shortest path; visited-at-enqueue.

**Complexity / resource target.** O(rows*cols).

**Follow-ups / edge cases.** return the path; bidirectional BFS discussion.

## DSA-21 — Connected Components
**First exposure:** Week 11  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given `n` nodes and an undirected edge list, return the number of connected components.

**Core concepts.** adjacency construction; graph traversal from all roots.

**Complexity / resource target.** O(V+E).

**Follow-ups / edge cases.** implicit graph recognition; solve the same problem with DSU/Union-Find and explain path compression plus union by rank/size.

## DSA-22 — Course Schedule / Topological Sort ★
**First exposure:** Week 11  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given courses and prerequisite pairs, determine whether all courses can be completed. If so, return one valid order.

**Core concepts.** indegree; Kahn's algorithm; cycle detection.

**Complexity / resource target.** O(V+E).

**Follow-ups / edge cases.** DFS three-color solution.

## DSA-23 — Top-K Frequent Elements ★
**First exposure:** Week 12  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given an integer array and `k`, return the `k` most frequent values.

**Core concepts.** frequency map; min-heap; buckets.

**Complexity / resource target.** O(n log k) heap solution.

**Follow-ups / edge cases.** streaming top-k.

## DSA-24 — Merge Intervals
**First exposure:** Week 12  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given intervals `[start,end]`, merge all overlapping intervals.

**Core concepts.** sort + sweep; interval invariant.

**Complexity / resource target.** O(n log n).

**Follow-ups / edge cases.** insert interval; endpoint semantics.

## DSA-25 — Subarray Sum Equals K ★
**First exposure:** Week 13  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given an integer array and integer `k`, return the number of contiguous subarrays whose sum equals `k`.

**Core concepts.** prefix sum + frequency map; `{0:1}` identity.

**Complexity / resource target.** O(n) expected time.

**Follow-ups / edge cases.** contrast with sliding window.

## DSA-26 — Dynamic Programming Synthesis ★
**First exposure:** Week 13  
**Level:** L3  
**Time box:** 45 min
**Format:** EXTENDED_DRILL  

**Interview prompt.** In one extended sitting: (1) solve maximum non-adjacent sum; (2) solve unique grid paths, then obstacles, then minimum path sum; (3) implement edit distance.

**Core concepts.** state definition; recurrence; base cases; update order; rolling memory.

**Complexity / resource target.** problem-dependent; target O(n) or O(mn).

**Follow-ups / edge cases.** LCS recurrence; reconstruct edit sequence.

---

# Track B — SQL

## SQL-01 — Aggregation / Conversion
**First exposure:** Week 2  
**Level:** L1  
**Time box:** 15 min
**Format:** LIVE  

**Interview prompt.** Using `users` and `orders`, return one row per country with 2026 signups, users with at least one qualifying order, conversion rate, and paid-search signup share. Keep countries with at least 100 signups.

**Core concepts.** conditional aggregation; HAVING; COUNT(DISTINCT); left joins.

**Complexity / resource target.** single grouped scan after joins.

**Follow-ups / edge cases.** FILTER syntax; zero-conversion countries.

## SQL-02 — Join Grain and Fan-Out ★
**First exposure:** Week 4  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Using `orders`, `order_items`, and `items`, return per-user spend and distinct items purchased, then per-category spend and distinct buyers. Exclude cancelled/returned orders.

**Core concepts.** table grain; fan-out; pre-aggregation; COUNT(DISTINCT).

**Complexity / resource target.** reason about cardinality before complexity.

**Follow-ups / edge cases.** construct a 2x overcount example.

## SQL-03 — Latest Record Per Entity
**First exposure:** Week 6  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Return each user's most recent qualifying order with total value. Then return the latest prediction for every `(user_id,item_id)`. Solve the first part once with `ROW_NUMBER()` and once without it.

**Core concepts.** window ranking; deterministic ties; filtering order.

**Complexity / resource target.** window + sort per partition.

**Follow-ups / edge cases.** ROW_NUMBER vs RANK; correlated subquery.

## SQL-04 — Top-N Per Group
**First exposure:** Week 8  
**Level:** L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Return the top 3 sold items in every category over a time window, including rank and units sold. Then change the tie semantics so tied items share rank.

**Core concepts.** ROW_NUMBER/RANK/DENSE_RANK; partitioned ordering.

**Complexity / resource target.** group + window sort.

**Follow-ups / edge cases.** top 3 plus ties.

## SQL-05 — Sessionization ★
**First exposure:** Week 10  
**Level:** L3  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Ignore the stored session ID. Define a session as a maximal sequence of user events where consecutive events are at most 30 minutes apart. Assign session numbers and return session start/end, event count, purchase flag, and gap from the previous session.

**Core concepts.** LAG; new-session flag; cumulative SUM; gaps-and-islands.

**Complexity / resource target.** sort per user.

**Follow-ups / edge cases.** incremental nightly version.

## SQL-06 — Rolling Time Windows ★
**First exposure:** Week 12  
**Level:** L3  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Produce one row per user per calendar day from first purchase through the dataset end date with daily purchases, rolling 7-day purchases, rolling 30-day spend, and change in rolling 7-day count. Include inactive days.

**Core concepts.** date spine; RANGE vs ROWS; densification; LAG.

**Complexity / resource target.** calendar expansion + windows.

**Follow-ups / edge cases.** rolling distinct counts.

## SQL-07 — Deduplication / NULL Semantics
**First exposure:** Week 14  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Deduplicate exact and near-duplicate events, then return users who never clicked and items with impressions but no clicks.

**Core concepts.** ROW_NUMBER dedup; NOT EXISTS; anti-join; three-valued logic.

**Complexity / resource target.** sort/partition for dedup.

**Follow-ups / edge cases.** exact NOT IN failure example.

## SQL-08 — Ordered Funnel ★
**First exposure:** Week 15  
**Level:** L3  
**Time box:** 35 min
**Format:** LIVE  

**Interview prompt.** For a given day, compute `search → impression → click → add_to_cart → purchase` where each stage must occur after the previous stage in the same session and within 30 minutes. Return counts and step conversion rates, then split by acquisition channel.

**Core concepts.** ordered events; conditional timestamps; user/session grain.

**Complexity / resource target.** depends on self-join/window design.

**Follow-ups / edge cases.** sessions spanning midnight; first vs latest qualifying prior event.

## SQL-09 — ML / Serving Log Analysis ★
**First exposure:** Week 16  
**Level:** L3  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Using impressions, clicks, predictions, and experiment assignments: compute CTR by model version and position bucket; compute clean per-variant CTR/cart rate excluding multi-assigned users; find high-score items with >=100 impressions and zero clicks.

**Core concepts.** left-join denominators; experiment hygiene; NTILE; user vs impression grain.

**Complexity / resource target.** group/window heavy.

**Follow-ups / edge cases.** position bias; confounding between model versions.

---

# Track C — Python / NumPy / pandas

## NP-01 — Shapes, Axes, Broadcasting ★
**First exposure:** Week 1  
**Level:** L1  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** Given arrays of shapes `(B,D)`, `(D,)`, `(B,1)`, and boolean masks, predict the output shape or error for additions, reductions, matmul, masking, and normalization expressions. Then implement row normalization, column standardization, masked mean, and weighted row mean.

**Core concepts.** broadcasting; axis; keepdims; boolean indexing.

**Complexity / resource target.** vectorized O(BD) operations.

**Follow-ups / edge cases.** views vs copies; zero denominators.

## NP-02 — Batched Cosine Similarity + Top-K ★
**First exposure:** Week 2  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given `Q(m,d)` and `X(n,d)`, return `(m,k)` candidate indices and cosine scores for the top-k candidates per query without Python loops over queries/candidates. Support chunking when the full score matrix does not fit memory.

**Core concepts.** normalization; matmul; argpartition; stable top-k.

**Complexity / resource target.** O(mnd) scoring.

**Follow-ups / edge cases.** ties; k>n; zero vectors; ANN threshold.

**Required mastery tests.** Nonzero normalized rows have unit norm within tolerance; top-k agrees with a full-sort reference on a small fixture.

## NP-03 — Vectorized Confusion Matrix
**First exposure:** Week 5  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given integer `y_true` and `y_pred` over `C` classes, build the `(C,C)` confusion matrix without a Python loop and compute per-class precision/recall/F1 plus micro/macro F1.

**Core concepts.** bincount/add.at; row/column sums; zero division.

**Complexity / resource target.** O(n+C^2).

**Follow-ups / edge cases.** multilabel extension.

## NP-04 — De-loop a Slow Function
**First exposure:** Week 9  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** You are given correct but slow nested-loop code that scores ragged user-item candidate lists with dot products and softmax. Vectorize it, preserve output order, and prove equivalence with a tolerance.

**Core concepts.** gather; matmul/einsum; ragged batching; allclose.

**Complexity / resource target.** same asymptotic math, lower Python overhead.

**Follow-ups / edge cases.** padding vs flat segments; float32.

## NP-05 — Padding / Masking / Pooling ★
**First exposure:** Week 12  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given variable-length sequences of d-dimensional vectors, construct a padded `(B,T,d)` array and `(B,T)` mask, then compute masked mean and mean over the last five real positions.

**Core concepts.** padding; masking; masked denominators.

**Complexity / resource target.** O(total real elements + BTd).

**Follow-ups / edge cases.** zero-length sequences; masked max.

## PD-01 — Feature Construction
**First exposure:** Week 3  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** From `events` and `items`, build one row per user with counts, distinct sessions/items, purchase count/spend, clicked-item mean price, top clicked category with deterministic tiebreak, and recency features.

**Core concepts.** groupby.agg; nunique; merge validation; deterministic tie handling.

**Complexity / resource target.** roughly O(n log n) if sorting.

**Follow-ups / edge cases.** transform vs agg; shape assertions.

## PD-02 — Latest Record + As-Of Join
**First exposure:** Week 7  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given historical profile updates and orders, attach to every order the profile state that was current at the order timestamp; separately return latest profile per user.

**Core concepts.** merge_asof; sorted keys; temporal semantics.

**Complexity / resource target.** O(n log n) dominated by sort.

**Follow-ups / edge cases.** exact boundary; searchsorted implementation.

## PD-03 — Point-in-Time Feature Construction ★
**First exposure:** Week 10  
**Level:** L3  
**Time box:** 35 min
**Format:** LIVE  

**Interview prompt.** For each label row `(user_id,label_ts)`, compute 1/7/30-day event counts, 30-day amount, days since previous event, and distinct event types using only events strictly before `label_ts`. Preserve label-row order.

**Core concepts.** strict temporal boundary; rolling/searchsorted; leakage.

**Complexity / resource target.** better than O(labels*events).

**Follow-ups / edge cases.** late-arriving data; timezone semantics.

**Required mastery test.** For every label row, assert that every event used satisfies `event_ts < label_ts`.

## PD-04 — Rolling Features Per Group
**First exposure:** Week 13  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given sparse daily user activity, produce dense per-user daily rows with rolling 7-day count, 28-day spend, a rolling ratio, and first-active-day flag.

**Core concepts.** resample/reindex; rolling offset windows; safe division.

**Complexity / resource target.** memory trade-off from densification.

**Follow-ups / edge cases.** rolling(7) vs rolling('7D').

## PY-01 — Standard-Library Event Processing
**First exposure:** Week 15  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Using only Python's standard library, process unsorted JSONL events plus an item-category CSV to produce user sessions, top clicked categories, highest spender, and malformed-line count. Explain what can and cannot be streamed.

**Core concepts.** json/csv; Counter/defaultdict; heapq; generators; defensive parsing.

**Complexity / resource target.** depends on buffering/sorting.

**Follow-ups / edge cases.** sorted-input variant; parallelization; expose one iterator/generator interface and define exception behavior for malformed records.

## PY-02 — Fit / Transform Component ★
**First exposure:** Week 15  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Implement `FeatureTransformer.fit`, `transform`, and `fit_transform` for numeric standardization/imputation/missing flags and categorical one-hot encoding with unknown buckets. Expose stable `feature_names_`.

**Core concepts.** stateful preprocessing; stable schema; train/inference contract.

**Complexity / resource target.** O(rows*features).

**Follow-ups / edge cases.** second fit resets state; serialization; partial_fit; dataclass/class invariants; context-managed persistence or resource handling; API error contracts.

---

# Track D — General ML Implementation

## ML-01 — Cosine Similarity + Retrieval
**First exposure:** Week 1  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given one query vector and `n` candidate vectors, return top-k by cosine similarity. First write the arithmetic directly; then vectorize and batch multiple queries.

**Core concepts.** cosine formula; norms; top-k selection; precomputation.

**Complexity / resource target.** O(nd) scoring.

**Follow-ups / edge cases.** zero vectors; unit-normalized candidates.

## ML-02 — Classification Metrics + ROC/PR AUC ★
**First exposure:** Week 3  
**Level:** L2/L3  
**Time box:** 35 min
**Format:** LIVE  

**Interview prompt.** Given binary labels and scores, implement confusion matrix, precision, recall, F1, ROC-AUC, and average precision/PR-AUC without sklearn. Handle tied scores correctly.

**Core concepts.** threshold metrics; rank/sweep AUC; imbalance.

**Complexity / resource target.** O(n log n).

**Follow-ups / edge cases.** zero positives; all scores equal.

## ML-03 — Leakage-Safe Splitting ★
**First exposure:** Week 4  
**Level:** L3  
**Time box:** 35 min
**Format:** LIVE  

**Interview prompt.** Implement grouped split, temporal split with embargo, deterministic hash-based group assignment, and a checker that reports violated leakage invariants.

**Core concepts.** group leakage; temporal leakage; reproducibility; hashing.

**Complexity / resource target.** O(n) plus sorting for temporal.

**Follow-ups / edge cases.** one giant group; boundary ties.

**Required mastery tests.** No group overlap; temporal ordering invariant; deterministic repeatability; stable hash assignment for existing groups when new groups arrive.

## ML-04 — Stable Softmax / Cross-Entropy ★
**First exposure:** Week 6  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Implement `softmax`, `logsumexp`, multiclass cross-entropy from logits, BCE-with-logits, and a stable sigmoid. Demonstrate inputs that break naive implementations.

**Core concepts.** numerical stability; max subtraction; fused loss.

**Complexity / resource target.** O(BC).

**Follow-ups / edge cases.** ±1e4 logits; wrong axis.

## ML-05 — K-Means
**First exposure:** Week 9  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Implement Lloyd's k-means algorithm including initialization, assignment, update, convergence, max iterations, and deterministic seeding.

**Core concepts.** clustering objective; vectorized distance; empty clusters.

**Complexity / resource target.** O(nkd) per iteration.

**Follow-ups / edge cases.** k>n; identical points.

## ML-06 — Logistic Regression From Scratch ★
**First exposure:** Week 10  
**Level:** L3  
**Time box:** 35 min
**Format:** LIVE  

**Interview prompt.** Warm up with linear-regression gradient descent, then implement binary logistic regression with intercept, stable BCE, L2, mini-batches, loss history, `predict_proba`, and thresholded prediction.

**Core concepts.** gradient derivation; vectorization; regularization.

**Complexity / resource target.** O(nd) per batch/iteration.

**Follow-ups / edge cases.** perfect separation; unscaled features; diverging LR.

## ML-07 — Negative Sampling ★
**First exposure:** Week 13  
**Level:** L2/L3  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Given positive user-item interactions and a large catalog, generate deterministic negatives using uniform and popularity-weighted sampling while excluding known positives.

**Core concepts.** rejection/exclusion; sampling distribution; false negatives.

**Complexity / resource target.** expected O(P*n_neg) plus sampler setup.

**Follow-ups / edge cases.** near-full-catalog users; hard-negative follow-up.

## ML-08 — Calibration / ECE
**First exposure:** Week 15  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Given probabilities and labels, compute reliability bins, observed positive rate, mean predicted probability, ECE, MCE, and a quantile-binning alternative.

**Core concepts.** calibration; binning; weighted denominators.

**Complexity / resource target.** O(n+b), O(n log n) for quantiles.

**Follow-ups / edge cases.** empty bins; identical probabilities.

## ML-09 — Bootstrap CI + Permutation Test
**First exposure:** Week 17  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Given user-level control/treatment metrics, compute a percentile bootstrap CI for difference in means, a two-sided permutation-test p-value, and a bootstrap CI for a ratio metric.

**Core concepts.** resampling unit; randomization inference; ratio metrics.

**Complexity / resource target.** O(Rn) resampling.

**Follow-ups / edge cases.** unequal groups; deterministic seed.

---

# Track E — PyTorch / Framework

## PT-01 — nn.Module + Shapes
**First exposure:** Week 7  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Implement an MLP classifier with one categorical embedding, continuous features, two hidden layers, ReLU, dropout, and C-way logits. Annotate every intermediate shape.

**Core concepts.** Module structure; embeddings; concat; logits.

**Complexity / resource target.** forward O(B*parameters used).

**Follow-ups / edge cases.** batch size 1; out-of-range ids.

## PT-02 — Training / Validation Loop ★
**First exposure:** Week 11  
**Level:** L2/L3  
**Time box:** 35 min
**Format:** EXTENDED_DRILL  

**Interview prompt.** Write a complete Dataset/DataLoader, training loop, validation loop, loss, optimizer, epoch metrics, and best-checkpoint tracking. Explain what breaks if each lifecycle call is omitted.

**Core concepts.** autograd lifecycle; train/eval; no_grad; devices.

**Complexity / resource target.** standard epoch cost.

**Follow-ups / edge cases.** short final batch; loss.item; empty validation.

**Required mastery test.** Two evaluation passes on identical data are identical when stochastic training-only layers are present.

## PT-03 — Losses + Masking ★
**First exposure:** Week 14  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Compute CE using `F.cross_entropy`, `log_softmax+nll_loss`, and a manual logsumexp implementation; then compute masked sequence loss using both ignore-index and explicit masks.

**Core concepts.** stable losses; masked denominators; class weights.

**Complexity / resource target.** O(BTC).

**Follow-ups / edge cases.** all-padding sequence; weighted reduction.

## PT-04 — Tensor Surgery / Silent Shape Bugs ★
**First exposure:** Week 16  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Implement batched matmul, einsum, embedding lookup, masked pooling, and a causal mask; then diagnose a pairwise-distance function that silently broadcasts incorrectly for particular shapes.

**Core concepts.** shape reasoning; unsqueeze; mask-before-softmax.

**Complexity / resource target.** problem-dependent vectorized cost.

**Follow-ups / edge cases.** B==K silent coincidence.

## PT-05 — Gradient Accumulation / Clipping / Scheduler
**First exposure:** Week 16  
**Level:** L2  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Modify a training loop to emulate a larger batch with microbatches, add global-norm clipping, and apply warmup + cosine scheduling at the correct cadence.

**Core concepts.** loss scaling; deferred optimizer step; scheduling.

**Complexity / resource target.** same total examples; less activation memory.

**Follow-ups / edge cases.** partial final accumulation; BatchNorm caveat.

## PT-06 — Custom Dataset / Collate / Variable Lengths
**First exposure:** Week 17  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Build a Dataset and custom `collate_fn` for variable-length sequences that pads examples, returns masks and labels/metadata, and supports device transfer.

**Core concepts.** irregular batching; padding; collate logic.

**Complexity / resource target.** O(total batch tokens).

**Follow-ups / edge cases.** empty sequence; sorting/bucketing by length.

## PT-07 — Reproducibility / Checkpoint Resume ★
**First exposure:** Week 17  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** Implement deterministic setup and checkpoint/resume of model, optimizer, scheduler, epoch/step, and relevant RNG state. Verify resumed training matches expected behavior within stated limits.

**Core concepts.** state serialization; RNG; deterministic kernels.

**Complexity / resource target.** checkpoint I/O proportional to state.

**Follow-ups / edge cases.** nondeterministic kernels; changed dataloader order.

---

# Track F — Debugging / Testing / Existing Code

## DBG-01 — Leaking Pipeline ★
**First exposure:** Week 1  
**Level:** L1/L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** You receive a training pipeline with suspiciously high validation performance. Find and fix three leaks: preprocessing fit before the split, target encoding that sees the row's own target, and a recency feature computed with future information. Write tests that expose each leak.

**Core concepts.** data leakage; temporal leakage; target leakage.

**Complexity / resource target.** diagnostic rather than asymptotic.

**Follow-ups / edge cases.** which leak survives grouped/temporal splits.

**Required mastery test.** Demonstrate that the regression test fails on the supplied broken version and passes after the fix.

## DBG-02 — Misaligned Labels / Duplicate Rows
**First exposure:** Week 5  
**Level:** L1/L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** You receive code that shuffles X and y independently, deduplicates after splitting, and creates a tiny-positive validation fold. Diagnose the resulting metric behavior and fix the pipeline.

**Core concepts.** row identity; split integrity; stratification; duplicates.

**Complexity / resource target.** diagnostic.

**Follow-ups / edge cases.** why misalignment can still appear above chance.

**Required mastery test.** Demonstrate that the regression test fails on the supplied broken version and passes after the fix.

## DBG-03 — Axis / Broadcasting ★
**First exposure:** Week 8  
**Level:** L1/L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** A NumPy scoring function returns plausible but wrong results because softmax uses the wrong axis, row weights broadcast along the wrong dimension, and a global mean collapses structure. Find, fix, and test all three.

**Core concepts.** shape invariants; row equivariance; keepdims.

**Complexity / resource target.** diagnostic.

**Follow-ups / edge cases.** construct a shape where the bug becomes an error.

**Required mastery test.** Demonstrate that the regression test fails on the supplied broken version and passes after the fix.

## DBG-04 — NaNs / Numerical Failure ★
**First exposure:** Week 11  
**Level:** L1/L2  
**Time box:** 20 min
**Format:** LIVE  

**Interview prompt.** A training loss becomes NaN. Instrument the computation to identify the first non-finite tensor among unstable softmax, `log(0)`, zero-norm normalization, and an excessive learning rate. Fix the root cause and add regression tests.

**Core concepts.** finite checks; overflow; 0/0; learning-rate diagnosis.

**Complexity / resource target.** diagnostic.

**Follow-ups / edge cases.** why clipping can mask rather than fix.

**Required mastery test.** Demonstrate that the regression test fails on the supplied broken version and passes after the fix.

## DBG-05 — PyTorch State / Lifecycle ★
**First exposure:** Week 14  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** A PyTorch train/eval script has poor validation, growing GPU memory, and occasional device errors. Find lifecycle bugs involving `eval`, `no_grad`, graph retention, gradient zeroing, and device placement.

**Core concepts.** framework state; graph lifecycle; devices.

**Complexity / resource target.** diagnostic.

**Follow-ups / edge cases.** determinism test and memory trace.

**Required mastery test.** Demonstrate that the regression test fails on the supplied broken version and passes after the fix.

## DBG-06 — Evaluation Bugs ★
**First exposure:** Week 16  
**Level:** L2  
**Time box:** 25 min
**Format:** LIVE  

**Interview prompt.** An evaluation function applies a 0.5 threshold to logits, averages per-batch precision, uses the wrong recall denominator, and evaluates on an oversampled validation population. Fix it and write hand-computed tests.

**Core concepts.** metric semantics; aggregation; base rates.

**Complexity / resource target.** diagnostic.

**Follow-ups / edge cases.** which bugs inflate vs deflate metrics.

**Required mastery test.** Demonstrate that the regression test fails on the supplied broken version and passes after the fix.

## DBG-07 — Extend Existing Evaluator
**First exposure:** Week 17  
**Level:** L2/L3  
**Time box:** 30 min
**Format:** LIVE  

**Interview prompt.** Given a tested ranking evaluator with `add_query`, `compute`, and `reset`, add per-segment metrics, arbitrary `recall@k`, and streaming accumulation where mathematically possible without breaking existing tests.

**Core concepts.** backward compatibility; unfamiliar code; streaming state.

**Complexity / resource target.** depends on metric state.

**Follow-ups / edge cases.** which ranking metrics require global state.

**Required mastery test.** Preserve the existing evaluator regression suite unchanged and passing; add specification-derived tests for the new segment metrics, arbitrary `recall@k`, and streaming behavior that fail before the extension is implemented and pass afterward.


---

# Generalist-depth extension problem bank

These IDs strengthen the original 69 without replacing them. They target surfaces that can appear in ML-flavored coding screens, SWE-leaning MLE interviews, data-manipulation assessments, framework rounds, and production-debugging exercises.

# Track A extension — DSA / SWE Algorithms

## DSA-27 — LRU Cache ★
**First exposure:** Depth extension  
**Level:** L2/L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Implement an `LRUCache(capacity)` supporting `get(key)` and `put(key, value)` in O(1) average time. Do not use an ordered-map convenience type for the core version. Define update semantics when an existing key is overwritten.

**Core concepts.** hash map + doubly linked list; recency invariant; stateful class design.

**Complexity / resource target.** O(1) average `get`/`put`; O(capacity) memory.

**Follow-ups / edge cases.** capacity 0/1; thread safety; TTL interaction; serialization.

**Required mastery tests.** deterministic eviction order; overwrite updates recency; repeated gets move entries; capacity boundary.

## DSA-28 — Trie / Prefix Index
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Implement a trie with `insert`, exact `contains`, prefix `starts_with`, and enumeration of up to `k` completions. Preserve deterministic completion order.

**Core concepts.** prefix trees; node ownership; DFS/BFS enumeration; memory/branching trade-offs.

**Complexity / resource target.** O(length) insert/lookup; output-sensitive completion enumeration.

**Follow-ups / edge cases.** deletion; Unicode; frequency-ranked completions; compressed trie.

## DSA-29 — Union-Find / Dynamic Connectivity
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 25 min  
**Format:** LIVE  

**Interview prompt.** Implement disjoint-set union with path compression and union by rank/size, then use it to count connected components and process incremental connectivity queries.

**Core concepts.** representative invariant; path compression; union by rank/size; amortized analysis.

**Complexity / resource target.** near-constant amortized operations, O(alpha(n)).

**Follow-ups / edge cases.** dynamic additions; cycle detection; why deletions are harder.

## DSA-30 — Dijkstra / Weighted Shortest Path ★
**First exposure:** Depth extension  
**Level:** L2/L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Given a directed graph with nonnegative edge weights, return shortest distances from a source and reconstruct one shortest path to a target.

**Core concepts.** priority queue; stale-entry handling; relaxation invariant; predecessor reconstruction.

**Complexity / resource target.** O((V+E) log V) with adjacency lists and binary heap.

**Follow-ups / edge cases.** unreachable nodes; zero-weight edges; negative edges; A* heuristic.

**Required mastery tests.** stale heap entries; multiple equal paths; disconnected graph; explicit negative-edge rejection.

## DSA-31 — Heap Scheduler / Meeting Rooms + Resource Assignment
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Given jobs with start/end times, compute the minimum number of workers required and return a deterministic worker assignment for every job.

**Core concepts.** sort + min-heap; resource reuse; stable tie handling.

**Complexity / resource target.** O(n log n).

**Follow-ups / edge cases.** inclusive/exclusive endpoints; worker-specific eligibility; online arrivals.

## DSA-32 — Token-Bucket Rate Limiter + Testable Clock ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Implement a token-bucket limiter supporting configurable capacity/refill rate and `allow(cost=1)` without sleeping. Inject a clock so behavior can be tested deterministically.

**Core concepts.** stateful systems code; monotonic time; lazy refill; floating-point boundaries; API contracts.

**Complexity / resource target.** O(1) per request and O(1) state per limiter.

**Follow-ups / edge cases.** per-user map; concurrency; distributed limiter trade-offs; clock rollback.

**Required mastery tests.** burst capacity, partial refill, exact boundary, fake-clock determinism, invalid cost.

# Track B extension — SQL

## SQL-10 — Cohort Retention
**First exposure:** Depth extension  
**Level:** L2/L3  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** From `users(user_id, signup_ts)` and `events(user_id, event_ts)`, build weekly signup cohorts and return week-0 through week-8 retained-user counts and retention rates. Each user counts once per cohort-week.

**Core concepts.** cohort anchoring; date arithmetic; distinct grain; pivot/conditional aggregation.

**Complexity / resource target.** one event join plus grouped aggregation; reason about deduplication before aggregation.

**Follow-ups / edge cases.** calendar vs elapsed weeks; missing cohort-weeks; rolling retention.

## SQL-11 — Experiment Metrics + Sample-Ratio Checks ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Given assignment, exposure, conversion, and revenue tables, produce one row per variant with assigned users, exposed users, converters, conversion rate, revenue/user, and assignment share. Flag duplicate assignment, post-conversion exposure, and obvious sample-ratio mismatch inputs for downstream statistical testing.

**Core concepts.** experiment grain; exposure semantics; deduplication; conditional aggregation; data-quality checks.

**Complexity / resource target.** pre-aggregate to user/variant before final metrics; avoid event-level fan-out.

**Follow-ups / edge cases.** multiple exposures; triggered analysis; identity changes; CUPED-input extraction.

**Required mastery tests.** a fixture where naive event joins double revenue; duplicate assignment; unexposed assigned users.

## SQL-12 — Point-in-Time Features in SQL ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** For label rows `(entity_id, label_ts)`, compute strictly-prior 1/7/30-day event counts, 30-day amount, and latest known profile value without future leakage. Preserve one output row per label row.

**Core concepts.** temporal joins; correlated ranges/window alternatives; grain preservation; strict boundary semantics.

**Complexity / resource target.** reason about indexes/partition pruning and why a naive label×events join can explode.

**Follow-ups / edge cases.** late events; identical timestamps; slowly changing dimensions; database-specific `AS OF` support.

**Required mastery tests.** every contributing event satisfies `event_ts < label_ts`; no label-row duplication.

## SQL-13 — Data Reconciliation / Quality Invariants
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Given raw events, a transformed feature table, and a prediction table, write queries that reconcile row counts and amounts, find missing/duplicate keys, identify orphaned foreign keys, detect impossible timestamp orderings, and summarize failures by day/source.

**Core concepts.** anti-joins; set differences; uniqueness; reconciliation; invariant-based debugging.

**Complexity / resource target.** scalable grouped checks rather than exporting data for row-by-row comparison.

**Follow-ups / edge cases.** tolerance for floating amounts; slowly arriving partitions; null-key semantics.

# Track C extension — Python / NumPy / pandas

## NP-06 — Pairwise Distances + Vectorized kNN Primitives ★
**First exposure:** Depth extension  
**Level:** L2/L3  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Given query matrix `Q(m,d)` and reference matrix `X(n,d)`, compute pairwise squared Euclidean distances without a Python loop over pairs, return exact top-k nearest indices, and support chunked queries when `m*n` scores do not fit memory.

**Core concepts.** norm expansion; broadcasting vs matmul; `argpartition`; memory-aware vectorization.

**Complexity / resource target.** O(mnd) arithmetic; explain O(mn) score-memory and chunking.

**Follow-ups / edge cases.** cosine equivalence after normalization; ties; float error yielding tiny negative squared distances.

**Required mastery tests.** compare against a double-loop reference; clamp only numerical negatives; k>n handling.

## NP-07 — Covariance, Correlation, Standardization, Whitening
**First exposure:** Depth extension  
**Level:** L2/L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Implement column standardization, sample covariance, correlation, and a whitening transform from NumPy primitives. Clearly define ddof and behavior for zero-variance columns.

**Core concepts.** centering; covariance normalization; eigendecomposition/SVD; numerical epsilon; matrix shapes.

**Complexity / resource target.** O(nd^2 + d^3) for dense covariance + decomposition.

**Follow-ups / edge cases.** d>>n; rank deficiency; ZCA vs PCA whitening.

## NP-08 — Sampling, Randomness, and Vectorized Monte Carlo ★
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Using an explicit RNG object/seed, implement categorical sampling from probability rows, weighted sampling without accidental normalization bugs, Monte Carlo estimation of an expectation, and a vectorized bootstrap resample primitive.

**Core concepts.** RNG ownership; probability normalization; cumulative distribution/search; vectorized simulation; reproducibility.

**Complexity / resource target.** O(samples * categories) or better where library primitives permit; make memory trade-offs explicit.

**Follow-ups / edge cases.** all-zero weights; very small probabilities; independent streams.

**Required mastery tests.** deterministic seeded fixture plus distributional sanity check with tolerance, not exact random counts.

## PD-05 — Mixed pandas Assessment ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 45 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Given messy `users`, `events`, `orders`, and `items` DataFrames, produce a user-level modeling table requiring filtering, missing-value handling, deduplication, validated merges, grouped aggregations, within-group ranking, timestamp features, one reshape/pivot, and deterministic tie handling. One supplied column intentionally leaks future information; exclude it and explain why.

**Core concepts.** integrated pandas fluency; grain; merge validation; `groupby/agg/transform`; ranking; datetime operations; reshaping; leakage.

**Complexity / resource target.** vectorized/columnar operations; identify the most expensive sort/join and avoid row-wise `apply` unless justified.

**Follow-ups / edge cases.** categorical dtype; nullable dtypes; chained assignment; memory reduction.

**Required mastery tests.** row-grain assertion; unique-key assertion; hand-computed user fixture; no future timestamp contribution.

## PD-06 — Reshape, Explode, Multi-Key Merge, and Reconciliation
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Normalize a DataFrame containing list-valued fields, explode it, join against a multi-key dimension table, compute per-entity aggregates, pivot a categorical measure into columns, and reconcile totals before/after reshape.

**Core concepts.** `explode`; multi-key merge; pivot/pivot_table; duplicate semantics; conservation checks.

**Complexity / resource target.** understand row multiplication and peak memory after explode.

**Follow-ups / edge cases.** empty lists; duplicate dimension keys; sparse wide output.

## PY-03 — Lazy Iterators, Batching, and Streaming Aggregation
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Implement reusable iterator utilities that lazily read records, validate/transform them, batch them by count, and maintain streaming aggregates without loading the full dataset. Preserve exceptions with useful context.

**Core concepts.** iterators/generators; lazy evaluation; state; batching; defensive parsing.

**Complexity / resource target.** O(batch_size + aggregate_state) memory.

**Follow-ups / edge cases.** partial final batch; backpressure; retryable record source.

## PY-04 — Concurrency-Safe Worker / Queue Exercise
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Implement a small worker pool around a bounded queue that consumes tasks, captures successes/failures, supports clean shutdown, and never loses a task silently. Tests must not depend on arbitrary sleeps.

**Core concepts.** threads/queues; synchronization; sentinel/shutdown protocols; exception propagation; deterministic testing.

**Complexity / resource target.** bounded in-flight work; discuss CPU-bound vs I/O-bound behavior and the GIL.

**Follow-ups / edge cases.** worker exception; duplicate/retry semantics; process-pool alternative.

# Track D extension — General ML Implementation

## ML-10 — Entropy, Gini, and Information Gain ★
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 25 min  
**Format:** LIVE  

**Interview prompt.** Implement entropy and Gini impurity from either class labels or class probabilities. Then compute weighted child impurity and information gain for a proposed binary split.

**Core concepts.** empirical class probabilities; `0 log 0 = 0`; weighted impurity; pure-node behavior.

**Complexity / resource target.** O(n+C) for labels depending on counting method.

**Follow-ups / edge cases.** multiclass labels; sample weights; base-2 vs natural log; empty child rejection.

**Required mastery tests.** pure set => zero entropy/Gini; balanced binary entropy; split whose children are pure; invariant to label renaming.

## ML-11 — Decision Stump / Best Tree Split ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Given dense numeric `X(n,d)` and classification labels, find the best `(feature, threshold)` split for a depth-1 tree using information gain or Gini decrease. Return child predictions. Then adapt the scorer for regression MSE reduction.

**Core concepts.** candidate thresholds; greedy split search; impurity reduction; sorting; leaf predictions.

**Complexity / resource target.** start with a clear baseline; then explain how sorting each feature enables O(d*n log n) rather than recomputing every partition naively.

**Follow-ups / edge cases.** repeated feature values; min leaf size; sample weights; missing values.

**Required mastery tests.** no threshold between equal adjacent values; deterministic tie break; classification and regression fixtures.

## ML-12 — Linear + Ridge Regression From Scratch ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Implement linear regression with intercept using gradient descent, then add ridge regularization. Separately compute a closed-form reference with a numerically appropriate solver rather than explicit matrix inversion. Compare predictions/coefficients on a small well-conditioned fixture.

**Core concepts.** MSE gradient; intercept handling; regularization; conditioning; solve vs inverse.

**Complexity / resource target.** O(nd) per gradient step; dense solve cost depends on d.

**Follow-ups / edge cases.** standardized features; rank deficiency; intercept should normally not be regularized; SGD variant.

**Required mastery tests.** finite-difference gradient check on tiny data; ridge shrinks coefficients on a correlated fixture.

## ML-13 — kNN Classifier / Regressor From Scratch
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Build `fit/predict` kNN for classification and regression using exact distances. Support uniform and inverse-distance weighting with deterministic tie handling.

**Core concepts.** lazy learning; distance scaling; nearest-neighbor selection; vote/reduction semantics.

**Complexity / resource target.** O(q*n*d) prediction; O(nd) storage.

**Follow-ups / edge cases.** zero-distance neighbors; feature scaling; large-n index alternatives.

## ML-14 — PCA From Scratch with SVD / Eigendecomposition ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Implement PCA `fit`, `transform`, and `inverse_transform`: center data, learn components using SVD (and explain the covariance-eigendecomposition equivalent), return explained-variance ratios, and reconstruct data from `k` components.

**Core concepts.** centering; right singular vectors; variance; sign ambiguity; low-rank reconstruction.

**Complexity / resource target.** state dense SVD cost and memory; discuss randomized/truncated alternatives conceptually.

**Follow-ups / edge cases.** k>rank; scaling vs centering; component sign differences.

**Required mastery tests.** reconstruction improves monotonically with k; transformed covariance is diagonal within tolerance for full-rank fixture.

## ML-15 — Naive Bayes From Scratch
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Implement multinomial Naive Bayes for count features with Laplace smoothing and log-space prediction. Return class log-priors, feature log-probabilities, predicted classes, and optional normalized probabilities.

**Core concepts.** conditional independence; smoothing; log probabilities; sparse-count semantics.

**Complexity / resource target.** O(nnz) training/prediction for sparse representation, O(nd) dense.

**Follow-ups / edge cases.** unseen vocabulary; Bernoulli NB; why normalization is unnecessary for argmax.

## ML-16 — SGD, Momentum, RMSProp, Adam, AdamW Updates ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Given parameter arrays and gradients, implement one optimizer step for vanilla SGD, momentum, RMSProp, Adam with bias correction, and AdamW-style decoupled weight decay. Keep optimizer state explicit.

**Core concepts.** optimizer state; exponential moving averages; bias correction; coupled L2 vs decoupled decay.

**Complexity / resource target.** O(number of parameters) time; optimizer-state memory accounting.

**Follow-ups / edge cases.** first-step bias correction; zero gradients; mixed precision state dtype.

**Required mastery tests.** hand-computed scalar first/second step; AdamW differs from adding L2 to Adam gradient.

## ML-17 — Gradient Checking + Tiny Neural Net Backprop ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 45 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Implement forward and backward passes for a tiny two-layer NumPy network and verify selected analytic gradients with centered finite differences. Include a stable loss.

**Core concepts.** chain rule; cached intermediates; matrix shapes; finite-difference approximation; relative error.

**Complexity / resource target.** analytic backprop O(forward cost); numerical check is intentionally expensive per checked parameter.

**Follow-ups / edge cases.** nondifferentiable activation points; epsilon selection; batch gradients.

**Required mastery tests.** analytic/numeric relative error below tolerance on deterministic small fixture.

# Track E extension — PyTorch / Framework

## PT-08 — Scaled Dot-Product Attention + Masks ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 35 min  
**Format:** LIVE  

**Interview prompt.** Given `Q, K, V` tensors, implement scaled dot-product attention with padding and causal masks. Support batched multi-head shapes, apply masks before softmax, and return both outputs and attention weights.

**Core concepts.** `QK^T / sqrt(d_k)`; tensor transposes; masking; stable softmax; head/batch dimensions.

**Complexity / resource target.** O(B*H*Tq*Tk*d) compute and O(B*H*Tq*Tk) attention-score memory.

**Follow-ups / edge cases.** all-masked row policy; different query/key lengths; flash-attention conceptual follow-up.

**Required mastery tests.** causal future weights are zero; padding weights are zero; rows sum to one when at least one key is valid.

## PT-09 — CNN Module + Shape / Parameter Accounting
**First exposure:** Depth extension  
**Level:** L2  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Implement a compact image classifier using convolution, activation, pooling, adaptive pooling, and a linear head. Annotate output shapes and parameter counts after every learned layer.

**Core concepts.** NCHW; convolution output formula; channels; pooling; flatten/adaptive pooling.

**Complexity / resource target.** reason about convolution FLOPs and activation memory qualitatively/quantitatively.

**Follow-ups / edge cases.** arbitrary image size; BatchNorm train/eval behavior; replace pooling with stride.

## PT-10 — Mixed Precision, Inference Mode, and Batched Inference ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 35 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Starting from a correct FP32 training/inference loop, add device-aware autocast and gradient scaling where appropriate, then implement memory-bounded batched inference with `eval()` and inference/no-grad semantics. Collect outputs without retaining graphs.

**Core concepts.** AMP; scaler lifecycle; dtype/device; inference graph suppression; batching; host/device transfer.

**Complexity / resource target.** quantify how batch size changes activation memory/throughput; no accidental O(dataset) GPU retention.

**Follow-ups / edge cases.** CPU fallback; unsupported ops; overflow/underflow; why `eval()` and `no_grad/inference_mode` solve different problems.

**Required mastery tests.** evaluation deterministic with dropout; output equivalence to small FP32 fixture within tolerance; GPU-memory state not accumulated across batches conceptually/test where available.

## PT-11 — Freeze / Unfreeze Transfer Learning + Optimizer Groups
**First exposure:** Depth extension  
**Level:** L2/L3  
**Time box:** 30 min  
**Format:** LIVE  

**Interview prompt.** Given a pretrained backbone and new head, freeze the backbone, train only the head, then unfreeze selected layers with a lower learning rate via optimizer parameter groups. Verify which parameters receive gradients and optimizer updates.

**Core concepts.** `requires_grad`; optimizer parameter ownership; train/eval state; differential learning rates.

**Complexity / resource target.** explain compute/memory savings that freezing does and does not provide.

**Follow-ups / edge cases.** BatchNorm behavior while frozen; rebuilding optimizer after unfreeze; discriminative LR.

# Track F extension — Debugging / Testing / Existing Code

## DBG-08 — Performance Regression / Profiling + Vectorization ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** A correct NumPy/pandas feature function became 20x slower after a data-size increase. Profile enough to localize Python loops, repeated merges/sorts, unnecessary copies, and an accidental quadratic membership check. Improve it without changing outputs.

**Core concepts.** measurement before optimization; asymptotics; vectorization; allocation/copy behavior; regression tests.

**Complexity / resource target.** state before/after dominant terms plus peak-memory trade-off.

**Follow-ups / edge cases.** vectorization that increases memory too much; chunking; benchmark noise.

**Required mastery test.** correctness against reference + benchmark fixture demonstrating material speedup without hardcoding a machine-specific absolute time.

## DBG-09 — Training / Serving Parity and Version-Skew Bug ★
**First exposure:** Depth extension  
**Level:** L3  
**Time box:** 40 min  
**Format:** EXTENDED_DRILL  

**Interview prompt.** Offline predictions match expected metrics, but a serving path produces shifted scores. Given training preprocessing, serialized transformer state, model weights, and online feature code, localize one preprocessing mismatch, one stale-version mismatch, and one dtype/device/numerical discrepancy. Add parity tests that catch the first divergence.

**Core concepts.** training/serving skew; artifact/version coupling; deterministic replay; intermediate-value comparison; numerical tolerance.

**Complexity / resource target.** diagnostic; design tests that are cheap enough for CI and richer replay tests for periodic validation.

**Follow-ups / edge cases.** unknown categories; model/index coupling; feature freshness; rollback.

**Required mastery test.** a golden request produces matching intermediate features and final prediction within defined tolerance under both paths.

---

# Mixed assessment rotation — required for surprise resistance

Canonical problems build primitives; interviews often combine them. After reaching Interview-ready on most core IDs, rotate through mixed assessments that do **not** reveal which primitive is being tested.

## Mixed A — SWE-heavy MLE screen
- one unseen LeetCode-medium-style problem in 30–35 minutes;
- production-quality function/class interface;
- tests and complexity;
- one changed-constraint follow-up such as streaming, concurrency, or memory cap.

## Mixed B — SQL + pandas data screen
- 20–25 minutes SQL from raw tables;
- 20–25 minutes pandas from analogous DataFrames;
- explicitly reconcile results and explain grain/join differences.

## Mixed C — ML concept → NumPy
Randomly draw one concept from the 2026 knowledge banks and implement the computable core without sklearn/scipy hiding it. Examples include impurity, loss, distance, calibration, resampling, PCA, gradients, probability updates, or a metric. If the exact concept has no canonical coding ID, use the transfer contract rather than adding a new memorized solution immediately.

## Mixed D — PyTorch repair
Receive a short unfamiliar model/training script containing 3–5 issues across shapes, device/dtype, masking, train/eval, autograd lifetime, optimizer order, or metric aggregation. Diagnose before editing; write a focused regression test for each substantive bug.

## Mixed E — Existing-code extension
Given a tested unfamiliar repository component, add one feature without breaking public interfaces or tests. Require code reading, change localization, backward compatibility, and new specification-derived tests.

## Mixed F — Production-shaped implementation
Implement a bounded component such as a batched predictor, feature transformer, cache, rate limiter, replay evaluator, or checkpointable worker. Include API contracts, deterministic tests, failure behavior, and resource reasoning.

A learner who only recognizes canonical IDs but fails these mixed rotations is **not** yet robust to interview surprise.

# Coding acceptance

## Roadmap-core acceptance
- All original **69 roadmap-core IDs** receive serious first exposure.
- Core IDs preserve their existing identifiers and canonical intent so the 2026 roadmap/master can continue to reference them.
- First exposure alone is insufficient; Interview-ready requires independent timed solves and later cold transfer.

## Deep-generalist acceptance
- Complete the **31 depth-extension IDs** or demonstrate equivalent independent mastery through harder transfer variants.
- At least 80% of ★ items across core + extension must have a later cold variant, not a memorized replay.
- Pass at least two Mixed A, two Mixed B, three Mixed C, two Mixed D, one Mixed E, and one Mixed F assessment without solution disclosure.
- No single lane may remain a persistent red zone: SWE/DSA, SQL, NumPy/pandas, ML implementation, PyTorch, and debugging must each support independent interview performance.

## Boundary of sufficiency
This set is designed to make a broad Generalist MLE candidate difficult to surprise across common coding formats. It cannot guarantee coverage of every company-specific puzzle, obscure library API, competitive-programming trick, distributed-systems implementation, or specialization-specific Search/Recs/LLM problem. The defense against those unknowns is the transfer/surprise-resistance contract and mixed assessments, not infinite syllabus growth.

Search/IR + Recommendation/Ranking specialization coding remains owned by the separate specialization set. Future GenAI/LLM specialization should add its own framework/inference/application coding without bloating this generalist bank.

