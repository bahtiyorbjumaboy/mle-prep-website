# 2027 Search + Recommendation Specialization — Master Instructions

**Status:** ACTIVE 2027 SPECIALIZATION CONTROL FILE  
**Effective window:** Sunday, January 3, 2027 through Friday, December 31, 2027  
**Duration:** 52 weeks  
**Authoritative roadmap:** `03_2027_Search_Recs_STAFF_Roadmap_FINAL.md`

---

# 0. Instruction to every new 2027 specialization chat

Before substantive work:

1. Read this master file.
2. Read `03_2027_Search_Recs_STAFF_Roadmap_FINAL.md`.
3. Read the relevant 2027 specialization bank(s):
   - `Bank_2027_Search_IR_STAFF_SEARCH_RECS_ONLY.md`
   - `Bank_2027_Ranking_Recommendation_STAFF_SEARCH_RECS_ONLY.md`
4. For coding sessions, read `01_2027_Search_Recs_Coding_Set_STAFF.md`.
5. Preserve 2027 IDs, wording, counts, depth levels, scheduling, and ownership boundaries unless the user explicitly changes them.
6. Do not reconstruct canonical prompts from topic names when the source can be retrieved.
7. For theory sessions, create a new session-scoped Markdown study artifact.
8. For coding sessions, preserve learner code ownership: scaffold/tests are allowed, but do not prefill the target solution unless the learner explicitly switches to REVIEW/SOLUTION mode.
9. `04_2027_Search_Recs_Session_Start_Prompt_Templates.md` is operational only and cannot override the master, roadmap, banks, or coding set.
10. Maintain 2026 Generalist MLE skills through periodic cold review only.

## Explicit scope boundary

The 2027 specialization is **Search / Information Retrieval + Recommendation / Ranking only**.

Do **not** schedule or add a separate curriculum for:

- LLM architecture;
- language-model pretraining/post-training;
- RAG;
- agents/tools;
- LLM inference systems;
- prompt engineering;
- LLM evaluation.

If a Search/Recommendation topic uses text, image, audio, or video embeddings, treat it as retrieval/representation learning for Search/Recs rather than as LLM literacy.

## Responsibility rule

- **Master:** purpose, scope, source governance, mastery, workload, review, ownership boundaries, final acceptance.
- **Banks:** knowledge IDs, wording, depth, mastery standards.
- **Coding set:** coding IDs, prompts, formats, testing expectations, capstones.
- **Roadmap:** weekly sequencing, projects, transfer cases, research weeks, milestones, oral boards.
- **Templates:** convenience only.

---

# 1. 2027 source manifest

The intended 2027 source set contains exactly **6 Markdown files**:

| File | Status | Scope |
|---|---|---|
| `01_2027_Search_Recs_Coding_Set_STAFF.md` | AUTHORITATIVE | 48 coding IDs |
| `02_2027_Master_Instructions_SEARCH_RECS_STAFF.md` | AUTHORITATIVE | project-wide control |
| `03_2027_Search_Recs_STAFF_Roadmap_FINAL.md` | AUTHORITATIVE | 52-week sequencing |
| `04_2027_Search_Recs_Session_Start_Prompt_Templates.md` | OPERATIONAL | reusable session starters |
| `Bank_2027_Search_IR_STAFF_SEARCH_RECS_ONLY.md` | AUTHORITATIVE | 56 Search conversations |
| `Bank_2027_Ranking_Recommendation_STAFF_SEARCH_RECS_ONLY.md` | AUTHORITATIVE | 56 Recommendation conversations |

**2027 totals:** 112 knowledge conversations + 48 coding IDs + two production-shaped capstones + shared retrieval/ranking lab + three research reproductions + one original extension experiment.

Older three-track 2027 files containing an LLM specialization are superseded for this curriculum.

---

# 2. Purpose and target end-state

The 2026 curriculum establishes broad Generalist MLE interview readiness.

The 2027 curriculum develops deep specialization in:

> **Retrieval, Ranking, Search, Recommendation, and Personalization Systems**

By December 31, 2027, the learner should be able to:

- reason from first principles about retrieval and ranking mechanisms;
- design and evaluate lexical, sparse, dense, late-interaction, ANN, LTR, and industrial ranking systems;
- implement faithful reduced versions of important algorithms and system components;
- reason about logged-policy bias, counterfactual evaluation, online experiments, exploration, and long-horizon objectives;
- operate production-shaped index/retrieval/ranking systems with versioning, freshness, fallbacks, observability, and rollback;
- transfer the same technical substrate across very different product surfaces;
- reproduce and critique research results;
- teach and defend designs under adversarial Staff-level questioning;
- state remaining uncertainty precisely.

This curriculum targets **Staff-level technical knowledge and judgment**, not automatic Staff employment level. Professional leveling still requires real scope, ownership, impact, influence, and experience.

---

# 3. Specialization identity

The curriculum should build one coherent technical identity:

**Machine Learning Engineer specializing in Retrieval, Ranking, Search, and Recommendation Systems.**

Shared substrate:

`representation → candidate retrieval → ANN/indexing → feature/context hydration → learning-to-rank → reranking/constraints → evaluation → experimentation → serving/freshness → feedback loops`

The curriculum should repeatedly test which pieces transfer and which do not.

Search and Recommendation share algorithms but differ in:

- query/user/session semantics;
- label generation;
- exposure policy;
- candidate universe;
- relevance definition;
- latency/freshness needs;
- online feedback loops;
- marketplace/ecosystem effects.

Do not flatten these differences merely because both systems rank items.

---

# 4. Knowledge scope

## Search / IR — 56 conversations

Coverage includes:

- inverted indexes/postings/positions;
- BM25/BM25F and analyzers;
- query classes and routing;
- WAND/Block-Max WAND;
- segments/merges/deletes;
- distributed lexical search;
- facets/filters/canonicalization;
- dense retrieval;
- hard-negative mining;
- learned sparse retrieval;
- late interaction;
- cross-encoder reranking;
- distillation;
- HNSW/IVF/PQ/OPQ and filtered ANN;
- vector lifecycle/capacity;
- hybrid retrieval;
- spelling/rewrite/expansion/zero-result recovery;
- autocomplete;
- Search LTR/LambdaMART;
- feature systems;
- judgments/pooling;
- click models/counterfactual LTR;
- evaluation science;
- personalization/commercial relevance;
- multilingual/federated search;
- product/media/local/enterprise/marketplace/sponsored search;
- non-generative multimodal retrieval;
- latency/caching/freshness;
- observability/security/incidents;
- experiments/cost/capacity;
- Staff architecture cases.

## Recommendation / Ranking — 56 conversations

Coverage includes:

- exposure-conditioned feedback and point-in-time data;
- recommendation metrics;
- cold start;
- MF/co-visitation/content/graph retrieval;
- two-tower retrieval;
- negative sampling;
- ANN;
- large embedding systems;
- candidate blending;
- pointwise/pairwise/listwise LTR;
- LambdaMART/tree rankers;
- Wide&Deep/DeepFM/DLRM/DCN;
- multi-task ranking/MMoE/PLE-style systems;
- calibration and feature architecture;
- diversity/constraints/slate optimization;
- multi-objective/marketplace objectives;
- exposure and position bias;
- IPS/SNIPS/DR/counterfactual LTR;
- A/B/interleaving/switchbacks/interference;
- bandits/OPE;
- delayed/long-term objectives;
- session/SASRec/BERT4Rec/graph recommendation;
- feed/video, social/photo/content, commerce/items, ads, notifications, multi-surface recommendation;
- non-generative multimodal recommendation;
- serving/freshness/monitoring/capacity;
- privacy/safety/fairness/creator-seller health;
- causal/uplift thinking;
- distillation/compression;
- evaluation pathologies/incidents;
- Staff architecture cases.

---

# 5. Vertical-transfer requirement

The specialization is not complete if the learner only understands one generic recommender and one generic search engine.

Required Recommendation transfer surfaces:

- video/feed;
- social/photo/content;
- e-commerce/items;
- ads;
- marketplace;
- notifications/push;
- multi-module/homepage surfaces.

Required Search transfer surfaces:

- product/e-commerce;
- video/media/content;
- local/place;
- enterprise/document;
- marketplace;
- sponsored search;
- multimodal retrieval.

For each vertical, explicitly ask what changes in:

- labels;
- candidate sources;
- objectives;
- features;
- constraints;
- evaluation;
- experiment design;
- serving/freshness;
- ecosystem/business effects.

---

# 6. Preparation layers

## Layer A — Knowledge

The 112 conversations own:

- mechanisms and derivations;
- assumptions/data-generating process;
- architecture comparisons;
- quantitative trade-offs;
- failure modes;
- evaluation validity;
- serving/operations;
- changed-constraint scenario defense.

D3 is not a longer verbal answer. It must survive changed scale, objective, latency, freshness, bias, or product constraints.

## Layer B — Coding

The 48 coding IDs own:

- implementation;
- tests/invariants;
- benchmarking;
- debugging;
- evaluation harnesses;
- resource reasoning;
- transfer across domains;
- capstone integration.

Formats:

- **LIVE** — realistic interview-sized implementation.
- **EXTENDED_DRILL** — staged multi-part implementation.
- **CAPSTONE** — multi-session integration.

## Layer C — Systems / projects

Required:

- **P1+ Recommendation System**
- **P2+ Search Engine**
- **Shared Retrieval/Ranking Lab**

Projects must include reproducibility, measurement, versioning, failure injection, load/reliability work, documentation, and architecture defense.

## Layer D — Research / synthesis

Required:

- one Search reproduction;
- one Recommendation reproduction;
- one LTR/ranking reproduction;
- one original cross-domain experiment;
- oral boards and teaching.

---

# 7. Anti-duplication / transfer rule

Do not rebuild identical infrastructure merely because both domains use it.

Shared primitives include:

- exact top-k;
- cosine/dot-product retrieval;
- contrastive training;
- hard-negative mining;
- ANN;
- ranking metrics;
- LTR;
- calibration;
- replay/evaluation harnesses;
- versioning;
- latency/capacity arithmetic;
- experimentation.

A repeated implementation is justified only when the interface, data-generating process, objective, failure mode, or serving semantics materially differ.

Examples:

- Search ANN and recommendation ANN should share benchmark tooling but preserve different filter/freshness/candidate semantics.
- LambdaMART should be understood as a common ranking tool while query grouping and user/impression grouping remain domain-specific.
- Search clicks and recommendation engagement both contain policy bias, but their examination/exposure mechanisms differ.

---

# 8. Mastery contract

## Knowledge states

0. **Unseen**  
1. **Learned**  
2. **Independent**  
3. **Staff-depth mastered**

A Staff-depth mastered item must survive:

- cold spacing;
- changed constraints;
- cross-domain transfer;
- failure diagnosis;
- quantitative reasoning;
- architecture alternatives.

## Coding states

0. **Unseen**  
1. **Learned**  
2. **Independent**  
3. **Mastered**

Coding mastery requires:

- independent framing;
- correct implementation;
- tests;
- edge/adversarial cases;
- benchmark/validation;
- complexity/resources;
- later cold or transfer attempt.

Substantial hints or solution exposure require another independent attempt.

---

# 9. Theory session artifact contract

Each theory chat creates a **new session-scoped Markdown file**.

Suggested names:

- `2027_Search_W07_S13_S14.md`
- `2027_Rec_W21_R21_R22.md`
- `2027_LTR_Cold_Review.md`

Use:

**canonical question → cold attempt → dynamic probing → diagnosis → visible teaching for substantive gaps → notes repair → learner reconstruction only when needed → changed-constraint follow-up → mastery state → spaced review**

Each question entry should contain:

## Canonical Staff-Depth Question
## Mastery Answer
## Material Follow-ups / Scenario Variants
## Plain-English Model
## Reasoning Chain
## Staff Compression
## Mastery Record

Do not force reconstruction for terminology polish.

Do not prefill the mastery answer before a serious attempt unless the learner explicitly requests direct-study mode.

---

# 10. Coding / Codex contract

Default mode is **INTERVIEW**.

- INTERVIEW — no solution disclosure.
- HINT — incremental hint ladder.
- REVIEW/SOLUTION — only after explicit learner switch.

Recommended workspace:

```text
problems/
  <problem_id>/
    README.md
    solution.py
    test_solution.py
    notes.md
```

Adapt for ranking libraries, SQL/data work, simulators, services, or capstones.

Before implementation require:

**clarify → assumptions → baseline → correctness → complexity/resources → improved mechanism/invariant**

When tests fail:

**interpret → localize → hypothesize → smallest justified fix → focused test → full suite**

For benchmark/system work, require explicit:

- corpus/catalog size;
- candidate count;
- QPS;
- latency percentiles;
- memory;
- build/update cost;
- evaluation protocol.

For CAPSTONE work, scaffold only the current milestone.

---

# 11. Review queue

Every week prioritize:

1. failed/Red repair due;
2. first re-attempts due from prior 1–3 weeks;
3. oldest high-priority coding item not mastered;
4. oldest D3 knowledge item not mastered;
5. cross-domain Search↔Recommendation transfer;
6. one 2026 Generalist MLE maintenance item;
7. mixed oral-board/system-design item if capacity remains.

Do not delete due mastery work to preserve optional new reading.

---

# 12. Workload policy

The year deliberately finishes new syllabus exposure by Week 36.

This leaves Weeks 37–52 for:

- vertical transfer;
- capstone hardening;
- incidents;
- reliability;
- scale;
- research reproduction;
- teaching;
- oral boards;
- targeted repair.

Do not fill freed capacity with endless new questions.

When overloaded, reduce:

1. optional reading;
2. cosmetic artifact polish;
3. redundant implementation;
4. optional extensions.

Do not reduce due cold reviews, core project work, or milestone defenses without explicitly rescheduling them.

---

# 13. Generalist MLE maintenance

The 2026 Generalist MLE curriculum remains the source for:

- linear algebra;
- probability/statistics;
- Core ML;
- deep learning fundamentals;
- SQL;
- Python/NumPy/pandas;
- PyTorch;
- debugging/testing;
- ML engineering;
- general ML system design.

During 2027, perform one rotating cold maintenance block every 1–2 weeks.

The goal is maintenance, not replaying the entire 2026 curriculum.

---

# 14. Ownership and honesty

Always distinguish:

- professionally owned;
- professionally observed/adjacent;
- independently implemented/studied.

Do not represent portfolio/reproduction work as employer production ownership.

Never reproduce confidential employer code, data, schemas, metrics, architecture, or documents.

---

# 15. Research reproduction contract

Each reproduction must include:

- exact claim being tested;
- baseline;
- dataset/protocol;
- assumptions;
- implementation;
- reproducibility instructions;
- results;
- negative/failed findings;
- ablation/sensitivity;
- discrepancy analysis;
- deployment implication.

The original extension experiment must state a falsifiable hypothesis before execution and preserve negative results.

---

# 16. Staff oral-board standard

A Staff-depth board should mix:

- retrieval/ranking mechanism;
- data/labels;
- LTR/model choice;
- capacity arithmetic;
- relevance/evaluation validity;
- experiment design;
- serving/freshness;
- incident diagnosis;
- rollback/degradation;
- changed constraints.

The learner should state:

- what is known;
- what is assumed;
- what must be measured;
- what could fail;
- what would change the architecture decision.

---

# 17. Final acceptance

By December 31, 2027:

## Search / IR
Can design and defend lexical, sparse, dense, late-interaction, ANN, hybrid, LTR/reranking, query-understanding, relevance-science, distributed/index-lifecycle, latency, experiment, and incident systems across multiple verticals.

## Recommendation / Ranking
Can design and defend logged data, multi-channel retrieval, ANN, LTR/industrial ranking, multi-task/slate objectives, causal/off-policy evaluation, exploration, sequential/graph recommendation, serving, and ecosystem constraints across feed, commerce, ads, and social/content surfaces.

## Cross-domain
Can:

- transfer shared ranking/retrieval primitives without flattening domain differences;
- perform capacity/cost arithmetic;
- diagnose failures;
- reproduce research;
- teach advanced topics;
- survive adversarial Staff-level technical questioning.

The desired outcome is:

> **Comfortable performing Staff-depth Search/IR and Recommendation/Ranking technical work while holding a Senior-level role, assuming the real job provides appropriate production ownership and context.**

Completing the curriculum alone does not grant a Staff title.
