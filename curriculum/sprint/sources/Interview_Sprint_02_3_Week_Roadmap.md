# Search + Ranking + Recommendation Interview Sprint — Roadmap

**Default:** 3 weeks  
**Optional:** compress to 2 weeks or extend to 4 weeks  
**Purpose:** temporary overlay; not a replacement for 2026 or 2027.

## Scheduling rules

- **2 weeks:** merge Weeks 1–2; use final 2–3 days for Week 3 mocks.
- **3 weeks:** follow Weeks 1–3.
- **4 weeks:** Week 4 is cold mocks/repair only; no new syllabus.
- Borrowed 2027 IDs count as early first exposure when completed seriously.
- After interview day, resume 2026.

## Daily default

- 60–90 min knowledge/oral reasoning;
- 45–60 min ranking coding;
- 45–60 min system design or debugging;
- 20–30 min ownership-story defense/repair.

# Week 1 — Ranking fundamentals + coding

## Borrowed knowledge
- **R01 — Two-stage and multi-stage recommender architecture**
- **R02 — Explicit, implicit, and exposure-conditioned feedback**
- **R03 — Training-set construction and point-in-time correctness**
- **R04 — Recommendation metrics and metric contracts**
- **R06 — Collaborative, content, co-visitation, graph, and hybrid retrieval**
- **R08 — Two-tower retrieval**
- **R09 — Negative sampling and false negatives**
- **R13 — Pointwise, pairwise, and listwise learning to rank**
- **R14 — Gradient-boosted trees and LambdaMART for ranking**
- **S01 — End-to-end search architecture**
- **S03 — BM25, BM25F, exact match, phrase, and proximity**
- **S28 — Search learning-to-rank**

## Borrowed coding
- **REC-01 — Ranking Metrics Suite**
- **REC-02 — Point-in-Time Recommendation Dataset**
- **REC-05 — Two-Tower Retrieval**
- **REC-08 — Pointwise + Pairwise Ranker**
- **REC-09 — LambdaMART / Tree Ranker**
- **SRCH-01 — Inverted Index + BM25 + Positions**
- **SRCH-14 — Search LTR / LambdaMART**

## End-to-end ownership
- Prepare ownership story #1 using problem→data→model→evaluation→serving→monitoring.

## Model Design practice
- Choose candidate generation + ranker architecture for a 10M-item implicit-feedback recommender.
- Choose pointwise vs pairwise vs listwise/LambdaMART for three objectives.
- Choose lexical vs dense vs hybrid for exact-ID, head, and tail search queries.

## System Design practice
- Design a two-stage ranker under 120 ms p99. Allocate retrieval, feature hydration, ranker, rerank, and overhead budgets.

## Debugging / Incident practice
- Offline NDCG improves, candidate recall is unchanged, but online conversion drops. Diagnose objective mismatch, calibration, feature skew, and serving regressions.

## Gate
- Explain two-stage architecture, stage-specific metrics, LTR, two-tower, negatives, and ranking metrics cold.
- Complete at least 4 coding IDs independently.
- Complete one 60-minute system-design mock.

---

# Week 2 — System design + end-to-end ownership

## Borrowed knowledge
- **R18 — Calibration, uncertainty, and score semantics**
- **R19 — Feature architecture and leakage**
- **R25 — Exposure, position, and selection bias**
- **R26 — IPS, SNIPS, doubly robust estimation, and overlap**
- **R28 — A/B tests, interleaving, switchbacks, and interference**
- **R43 — Recommendation serving architecture**
- **R45 — Monitoring and failure diagnosis**
- **R46 — Capacity, cost, and scaling**
- **S05 — Query intent and query-class routing**
- **S11 — Dense bi-encoder retrieval**
- **S15 — Cross-encoder reranking**
- **S17 — ANN design: HNSW, IVF, PQ/OPQ, partitioned search**
- **S22 — Hybrid lexical+dense retrieval**
- **S29 — Search feature architecture**
- **S44 — Search latency engineering**
- **S50 — Capacity, cost, and scaling**

## Borrowed coding
- **REC-06 — ANN Candidate Benchmark**
- **REC-21 — Recommendation Evaluation + Slice Harness**
- **REC-22 — Recommendation Serving Simulator**
- **SRCH-08 — Dense Bi-Encoder Retrieval**
- **SRCH-11 — ANN Benchmark**
- **SRCH-13 — Cross-Encoder / Neural Reranker**
- **SRCH-22 — Search Serving + Cache Simulator**

## End-to-end ownership
- Prepare ownership story #2 and run adversarial follow-ups on trade-offs, incidents, and what you personally changed.

## Model Design practice
- Choose ANN family and candidate count under memory/latency constraints.
- Choose pre-ranker vs one heavy ranker under fixed p99.
- Choose calibrated pointwise probability vs pure ordering score for downstream logic.

## System Design practice
- Design a 2–3 stage retrieval/ranking service under strict latency/QPS. Include ANN, feature serving, pre-rank, heavy rank, timeouts, fallback, versioning, rollback.

## Debugging / Incident practice
- p99 increases sharply after candidate count rises. Use per-stage latency, feature/cache telemetry, and ranker throughput to localize the bottleneck.

## Gate
- Complete one 75–90 minute Search/Recs system-design mock.
- Complete one model/system incident mock from telemetry.
- Defend two ownership stories under follow-up.

---

# Week 3 — Interview simulation + debugging + targeted repair

## Borrowed knowledge
- **S31 — Click models and behavior bias**
- **S33 — Search evaluation science**
- **S46 — Observability, replay, and relevance incidents**

## Borrowed coding
- **SRCH-17 — Search Evaluation + Replay Harness**

## End-to-end ownership
- Run two full ownership mocks. No notes. Repair only observed gaps.

## Model Design practice
- Run three ambiguous model-choice prompts without a target architecture.
- State what new data/metric would change each decision.

## System Design practice
- Run at least four timed designs: recommender, search, feed/ranking, and limited-latency two-stage model.

## Debugging / Incident practice
- Run at least six incidents: stale features, index/model skew, slice regression, cache collapse, objective mismatch, timeout fallback.

## Gate
- Pass two mixed loops: coding + system design + debugging + ownership.
- Remaining repair queue must be small and explicit.
- No broad rereading in final 48 hours.

---

# Week 4 — Optional fourth week — cold mocks only

## Borrowed knowledge
- No new borrowed knowledge. Cold review only.

## Borrowed coding
- No new coding ID. Timed reattempts/variants only.

## End-to-end ownership
- Repeat ownership stories with deeper pushback; improve precision, not length.

## Model Design practice
- Use model-choice variants only from observed weak areas.

## System Design practice
- Run full mixed mocks with changed constraints halfway through each design.

## Debugging / Incident practice
- Run incident boards from symptoms only; require prioritization, rollback, and prevention.

## Gate
- No new material; cold performance and repair only.
- Avoid fatigue once readiness stabilizes.

---

# High-priority system-design prompts

1. **Limited-latency two-stage recommender:** 100–120 ms total; retrieval + feature hydration + ranker exceed budget. Redesign.
2. **Search retrieval→reranking cascade:** head/torso/tail queries, lexical+dense retrieval, expensive reranker, strict p99.
3. **ANN service:** tens/hundreds of millions of embeddings, memory cap, continuous inserts/deletes, <50 ms retrieval.
4. **Feed/session ranking:** candidate generation, short-term intent, long-term state, creator constraints, exploration.
5. **Ad/ranking service:** hundreds of candidates, sub-30–50 ms scoring, calibration, feature freshness, fallback.

# High-priority debugging prompts

1. Offline NDCG +5%, online CTR −7%, Recall@1000 unchanged.
2. p99 +30 ms after candidates increase 200→1000.
3. Exact-ID search regresses after dense/hybrid rollout.
4. ANN recall collapses after model deploy but exact top-k is fine.
5. Ranker scores shift with no model change.
6. New-user segment regresses while aggregate metrics improve.
7. Cache hit rate drops after personalization launch.
8. Diversity improves but conversion/satisfaction falls.

# Final readiness

- [ ] Ranking metrics coded cold.
- [ ] Pointwise/pairwise or tree-LTR coding completed under time pressure.
- [ ] Two-stage architecture explained in <3 minutes and defended for 20+ minutes.
- [ ] One full latency-budget design completed with explicit numbers.
- [ ] Two end-to-end ownership stories are concise and technically deep.
- [ ] At least five debugging incidents solved without hints.
- [ ] Borrowed-ID ledger updated so 2027 does not repeat first exposure.