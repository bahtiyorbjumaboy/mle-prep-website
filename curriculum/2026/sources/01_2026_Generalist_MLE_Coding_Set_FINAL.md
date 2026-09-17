# 2026 Generalist MLE Coding Set — FINAL

**Status:** ACTIVE 2026 GENERALIST CODING SET  
**Roadmap window:** Sunday, September 6, 2026 through Thursday, December 31, 2026  
**Count:** 69 core coding IDs  
**Scope:** Generalist MLE interview readiness only. Search/IR + Recommendation/Ranking specialization coding is deferred to the separate 2027 specialization curriculum.

## Track counts

| Track | Count |
|---|---:|
| DSA / SWE Algorithms | 26 |
| SQL | 9 |
| Python / NumPy / pandas | 11 |
| General ML Implementation | 9 |
| PyTorch / Framework | 7 |
| Debugging / Testing / Existing Code | 7 |
| **Total** | **69** |

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

# 2026 coding acceptance

- All 69 core IDs receive first exposure by December 31, 2026.
- Week 1 contains 5 new coding IDs; Weeks 2–17 contain exactly 4 each.
- Interview readiness requires independent and cold re-attempts; first exposure alone is insufficient.
- The separate 2027 specialization coding set is authoritative for Search/IR + Recommendation/Ranking specialization work.