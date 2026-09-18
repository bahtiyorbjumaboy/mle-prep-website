# 2027 Search + Recommendation — Session Start Prompt Templates

**Status:** Operational convenience file  
**Authority:** This file does not override the 2027 master, roadmap, banks, or coding set.

---

# Website-compatible study artifact contract — MANDATORY

These templates create Markdown artifacts consumed by the curriculum website. Markdown remains the source of truth. Follow this contract exactly whenever a template writes study artifacts.

## 1. Canonical item keys

Use stable canonical keys in frontmatter and internal references.

- 2027 Search knowledge: `2027:S01`, `2027:S17`, etc.
- 2027 Recommendation knowledge: `2027:R01`, `2027:R08`, etc.
- 2027 coding: `2027:SRCH-01`, `2027:REC-05`, etc.

Do not reconstruct canonical IDs or question wording when the authoritative source can be retrieved.

## 2. Global Markdown/frontmatter rules

These rules apply to `interview-answer`, `lesson`, `coding-review`, and `session-note` artifacts.

1. **Frontmatter owns the page title.** Do not put an H1 (`# ...`) in the Markdown body. The body must begin at H2 (`## ...`) or lower.
2. **Quote every date value** so YAML parsers always receive strings, for example `created: "2026-09-17"`, `updated: "2026-09-17"`, and `date: "2026-09-17"`.
3. Preserve an existing `created` value when updating a durable artifact; change only `updated`.
4. Use canonical item keys as identity; never use question text or display titles as identity.
5. Do not create duplicate artifacts for the same canonical question/problem.
6. Do not invent canonical wording, IDs, mastery standards, prerequisites, follow-ups, or roadmap placement.
7. Tags are lowercase kebab-case when practical.
8. Reusable artifacts contain durable knowledge, **not live progress state**.

## 3. Single source of truth for mastery/progress

The website progress store (localStorage/exported progress JSON) is the source of truth for the learner's **current** completion/mastery state.

Therefore:

- `interview-answer`, `lesson`, and `coding-review` frontmatter MUST NOT contain `status`, `mastery`, `next_review`, `attempts`, sprint result/color, or similar live-progress fields.
- Their bodies MUST NOT contain a `Mastery Record`, attempt log, reconstruction evidence, dated repair history, or current review schedule.
- A `session-note` MAY record the mastery observed at the end of that historical session, the repairs made, and the review date planned in that session. Those values are historical evidence only and MUST NOT be treated as current progress by the website.

This separation keeps reusable Staff-depth material stable while mastery evolves.

## 4. Interview-answer artifact — exactly one knowledge item

For every knowledge question seriously covered, create or update exactly one question-scoped interview-answer Markdown file.

One interview-answer file maps to **exactly one** canonical knowledge item.

Preferred locations:

- Search: `curriculum/2027/interview-answers/search/<ID>.md`
- Recommendation: `curriculum/2027/interview-answers/recommendation/<ID>.md`

Required frontmatter:

```yaml
---
type: interview-answer
item: "2027:R08"
title: "<concise topic title>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - <tag>
---
```

Required body structure:

```markdown
## Canonical Staff-Depth Question

[Copy the exact canonical question from the authoritative bank.]

## Mastery Answer

## Learn the Concepts

## Material Follow-ups / Scenario Variants
```

Content contract:

- **`## Mastery Answer` is the interview answer.** Keep it polished, direct, mechanism-first, and at the bank's required depth. It should be strong enough to give aloud under interview time pressure, while still including the important assumptions, trade-offs, and failure modes needed by the canonical prompt.
- **`## Learn the Concepts` is mandatory for every interview-answer artifact, even when the learner answers the question perfectly cold.** It is not a remediation-only section. Make it a thorough self-study treatment of the concepts the question is testing so the learner does not need a second lesson file to learn this item.
- The `Learn the Concepts` section should include, when relevant: first-principles motivation; precise definitions; mechanism/derivation; worked or quantitative examples; assumptions; trade-offs; failure modes; metric/evaluation semantics; implementation or serving implications; debugging/diagnosis; changed-constraint reasoning; and connections needed to understand the canonical question deeply. Include only material that genuinely supports this item; do not expand into an unrelated textbook chapter.
- **`## Material Follow-ups / Scenario Variants` contains durable answers/explanations for canonical follow-ups and substantive interviewer probes or changed-constraint variants.** Do not merely list questions when the session established useful answer content.
- Do **not** add `Plain-English Model`, `Reasoning Chain`, `Staff Compression`, `Mastery Record`, reconstruction-log, repair-log, or review-plan sections.

Durable-update rule:

- The interview-answer file is the canonical study source for this knowledge item. It must become more complete as understanding improves.
- If a session teaches a substantive concept, asks the learner to reconstruct reasoning at greater depth than the file currently contains, resolves an important misconception, derives something useful, or answers a meaningful follow-up/variant, **update the existing interview-answer in the same session**. Do not leave that knowledge only in the chat or session note.
- Fold new durable content into the existing sections rather than creating a chronological or repair section: update `Mastery Answer` if the interview answer itself should improve; extend `Learn the Concepts` for deeper teaching/derivation/mechanism; extend `Material Follow-ups / Scenario Variants` for follow-up or changed-constraint knowledge.
- Reconstruction evidence itself (what the learner said, whether it was correct, attempts, mistakes, dates, mastery) belongs only in the session note. The **knowledge exposed by the reconstruction** belongs in the durable interview-answer.
- A separate lesson is **not** the default home for question-specific teaching. Do not create a lesson merely because the learner needed teaching or because `Learn the Concepts` is long. A lesson is justified only for genuinely reusable cross-item material that would otherwise be duplicated across multiple knowledge/coding artifacts. Even then, all material needed to understand and defend this canonical item must remain self-contained in its interview-answer.

Rules:

- Copy the exact canonical Staff-depth question from the authoritative bank; do not paraphrase it.
- Keep the artifact reusable, synthesized, and non-chronological.
- Preserve an existing `created` date; update `updated` whenever durable content changes.
- Do not append attempts, repair history, mastery state, review dates, sprint result, or reconstruction evidence here; those belong in the session note.

## 5. Lesson artifact — optional cross-item teaching only

A lesson is an optional reusable teaching unit for material that genuinely spans multiple canonical items. It is not the default teaching artifact for a knowledge question: the question's mandatory `Learn the Concepts` section owns all question-specific conceptual depth.

Create/update a lesson only when the material is meaningfully reusable across multiple Search/Recommendation knowledge/coding items and centralizing it prevents real duplication. A lesson may support one or many items, and an item may link to multiple lessons.

Preferred location:

`curriculum/2027/lessons/<stable-kebab-case-id>.md`

Required frontmatter:

```yaml
---
type: lesson
id: "<stable-kebab-case-id>"
title: "<lesson title>"
items:
  - "2027:R08"
  - "2027:S17"
  - "2027:REC-05"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - <tag>
---
```

Rules:

- `items` must be a non-empty YAML list of canonical keys.
- Do not force one lesson per curriculum item.
- Do not create a lesson merely because substantive teaching occurred; that teaching belongs in the interview-answer `Learn the Concepts` section first.
- Do not use a lesson to offload material required to understand or defend a canonical question. Interview answers must remain self-contained.
- Do not create trivial lesson stubs merely to satisfy the format.
- Do not duplicate interview answers verbatim. Teach only the genuinely cross-item reusable concept, including mechanisms, quantitative trade-offs, implementation/system connections, diagnosis, and changed-constraint transfer where relevant.
- The Markdown body must begin at H2; do not repeat `title` as an H1.
- No mastery/progress/attempt history belongs in a lesson.

## 6. Coding-review artifact — exactly one coding item

A coding review is the durable post-attempt explanation for one coding problem. It is separate from learner-owned implementation files and separate from the chronological session note.

Preferred locations:

- Search: `curriculum/2027/coding-reviews/search/<ID>.md`
- Recommendation: `curriculum/2027/coding-reviews/recommendation/<ID>.md`

Required frontmatter:

```yaml
---
type: coding-review
item: "2027:REC-05"
title: "<canonical coding title>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - <tag>
---
```

Recommended body structure:

```markdown
## Canonical Problem

## Core Approach / Mechanism

## Correctness / Invariants

## Complexity / Resources

## Tests / Benchmark Contract

## Important Follow-ups

## Failure Modes / Debugging Notes
```

Rules:

- One coding-review file maps to exactly one canonical coding item.
- Preserve the exact canonical prompt/interface where included.
- Do not create/update a solution-revealing coding review while the learner is still in INTERVIEW or HINT mode.
- It may be created after the learner independently completes the problem or explicitly switches to REVIEW/SOLUTION mode.
- Keep live mastery state and chronological attempt history out of this file.

## 7. Session-note artifact — chronological evidence

Create one new session note per actual study session. A session note may reference multiple items.

Preferred location:

`curriculum/2027/notes/YYYY-MM-DD_<session-slug>.md`

Required frontmatter:

```yaml
---
type: session-note
title: "<concise session title>"
date: "YYYY-MM-DD"
curriculum: "2027"
session_type: "<theory | coding | review | oral-board | research | repair>"
items:
  - "<canonical-item-key>"
observed_mastery:
  "<canonical-item-key>": "<Unseen | Learned | Independent | Staff-depth mastered>"
next_review:
  "<canonical-item-key>": "YYYY-MM-DD"
---
```

`observed_mastery` and `next_review` may omit an item when no judgment/date was established. They are historical snapshots from this session, not live progress state.

Recommended body sections:

```markdown
## Items Covered

## Attempt / Reconstruction Evidence

## Repairs and Precision Corrections

## Material Follow-ups / Variants Completed

## Observed Mastery at Session End

## Review Plan
```

This is where attempts, reconstruction evidence, failures, repairs, observed mastery, and planned cold-review dates belong.

## 8. Math / LaTeX in Markdown

Preserve mathematical notation as real Markdown math source.

Inline:

```text
$p(y\mid x)$
```

Display:

```text
$$
\operatorname{NDCG}@k = \frac{\operatorname{DCG}@k}{\operatorname{IDCG}@k}
$$
```

Rules:

- Use `$...$` for inline math and `$$...$$` for display math.
- Do not put actual mathematical expressions in fenced code blocks merely because the chat UI may not render them. Code fences above are examples of syntax only.
- Do not replace LaTeX with Unicode approximations.
- Preserve backslashes and commands required by KaTeX/MathJax.
- The website is expected to render Markdown math with `remark-math` plus KaTeX/MathJax (or equivalent).

## 9. Artifact-write checklist

Before finishing any session that writes artifacts, verify:

- all canonical keys resolve;
- all date values are quoted strings;
- no artifact body contains an H1;
- each interview answer maps to exactly one knowledge item;
- every interview answer contains `Mastery Answer`, mandatory thorough `Learn the Concepts`, and the appropriate follow-up section;
- any substantive teaching/deeper reconstruction/follow-up knowledge discovered this session has been folded into the existing interview-answer sections;
- each coding review maps to exactly one coding item;
- lesson `items` is a non-empty canonical-key list;
- no durable artifact contains live mastery/progress fields;
- attempt/repair/review evidence lives in the session note;
- canonical wording was copied exactly where required;
- LaTeX delimiters/backslashes were preserved.
---
# Template A — Staff-Depth Theory Session

```text
We are continuing my 2027 Search + Recommendation specialization.

Before doing anything substantive, retrieve and follow:
1. `02_2027_Master_Instructions_SEARCH_RECS_STAFF.md`
2. `03_2027_Search_Recs_STAFF_Roadmap_FINAL.md`
3. the relevant bank:
   - `Bank_2027_Search_IR_STAFF_SEARCH_RECS_ONLY.md`
   - `Bank_2027_Ranking_Recommendation_STAFF_SEARCH_RECS_ONLY.md`

Today:
- Week/session: [WEEK]
- Knowledge IDs: [Sxx / Rxx OR "use today's roadmap items"]
- Session type: first exposure / review / cold re-test / oral-board repair
- Time available: [OPTIONAL]

Run the Staff-depth theory process:

1. Ask me the exact bank question cold.
2. Do not show the mastery answer before I make a serious attempt unless I explicitly switch to direct-study mode.
3. Probe mechanisms, assumptions, data-generating process, objective, architecture alternatives, quantitative trade-offs, failure modes, evaluation, and serving.
4. Distinguish substantive gaps from minor terminology/precision issues.
5. For a substantive gap:
   - teach the repair visibly;
   - update the session note;
   - make me reconstruct the repaired reasoning.
6. For a minor precision issue:
   - correct it briefly;
   - do not force repetition.
7. Change constraints when useful:
   - corpus/catalog size;
   - QPS;
   - p99 latency;
   - freshness;
   - memory;
   - candidate budget;
   - label sparsity;
   - exposure/position bias;
   - product objective;
   - vertical/task surface.
8. When relevant, force Search↔Recommendation transfer:
   - what stays the same?
   - what changes and why?
9. Rate:
   Unseen → Learned → Independent → Staff-depth mastered.
10. Schedule cold review.

Follow the website-compatible study artifact contract above.

- Create one NEW session-note file for this session; put attempts, reconstruction evidence, repairs, observed mastery, and next-review planning there.
- For every knowledge question seriously covered, create or update its one-item interview-answer with exactly these durable sections: `Canonical Staff-Depth Question`, `Mastery Answer`, mandatory thorough `Learn the Concepts`, and `Material Follow-ups / Scenario Variants`.
- `Learn the Concepts` is required even when my cold answer is already correct/complete. It must teach the underlying concepts thoroughly enough that this interview-answer is my self-contained study source for the item.
- Whenever teaching, a deeper reconstruction, a correction, or a substantive follow-up/variant produces durable knowledge not already present, immediately fold it into the appropriate existing interview-answer section in the same session. Do not create a reconstruction/repair section and do not leave the knowledge only in the session note.
- Create/update a lesson only for genuinely cross-item material that would otherwise be duplicated; never use a lesson as a substitute for the interview-answer's `Learn the Concepts` depth.
- Preserve LaTeX math source exactly using `$...$` / `$$...$$`.
- Keep the answer at the bank's required Staff depth and preserve canonical wording.

Start with the first scheduled question.
```

---

# Template B — Specialized Coding Session

```text
We are continuing my 2027 Search + Recommendation coding curriculum.

Before doing anything substantive, read:
1. `02_2027_Master_Instructions_SEARCH_RECS_STAFF.md`
2. `03_2027_Search_Recs_STAFF_Roadmap_FINAL.md`
3. `01_2027_Search_Recs_Coding_Set_STAFF.md`

Today:
- Week/session: [WEEK]
- Coding IDs: [REC-xx / SRCH-xx OR "use today's roadmap IDs"]
- Time available: [OPTIONAL]

Treat the coding set as authoritative.

Default to INTERVIEW mode:
- INTERVIEW = no solution disclosure.
- HINT = incremental hint ladder.
- REVIEW/SOLUTION = only after I explicitly switch modes.

For each coding ID:

1. Scaffold the minimum exercise workspace:
   README/problem statement
   solution/module
   tests
   notes
   benchmark/eval file if needed.

2. Do NOT implement the target solution.

3. Before coding, require:
   clarifications → assumptions → baseline → correctness → complexity/resources → improved mechanism/invariant.

4. Let me think aloud while coding.

5. Use deterministic tests and benchmark fixtures.
   When applicable include:
   - hand-computed fixture;
   - boundary case;
   - property/invariant;
   - adversarial bug case;
   - reproducibility check.

6. For retrieval/ranking tasks, require explicit:
   - corpus/catalog size;
   - candidate count;
   - metric contract;
   - latency/memory/build cost;
   - exact-vs-approximate baseline when relevant.

7. On failure:
   interpret → localize → hypothesize root cause → smallest fix → focused test → full suite.

8. After correctness:
   complexity/resource defense → benchmark interpretation → follow-ups → code review → mastery/re-test.

For CAPSTONE IDs, scaffold only the current milestone. Do not prebuild the entire system.

Artifact handling:
- Create one NEW session-note file for the coding session using the website-compatible contract; chronological attempts, bugs, repairs, observed mastery, and re-test dates belong there.
- After the learner independently completes the problem or explicitly enters REVIEW/SOLUTION mode, create/update the one-item `coding-review` when a durable review is useful.
- If substantive reusable conceptual teaching is produced, create/update a lesson and map it to the canonical coding ID.
- A lesson may also map to related Search/Recommendation knowledge IDs when that relationship is explicit.
- Do not create a lesson that reveals the target solution while still in INTERVIEW mode.
- Preserve LaTeX math source as `$...$` / `$$...$$`.

Start by retrieving the exact coding prompt.
```

---

# Template C — Weekly Start

```text
Read the 2027 master, roadmap, relevant bank(s), and coding set.

We are starting Week [XX].

Use the roadmap exactly.

Prioritize:
1. overdue Red repairs;
2. due cold re-tests;
3. scheduled knowledge;
4. scheduled coding;
5. P1+/P2+/shared-lab milestone;
6. one 2026 Generalist MLE maintenance block if due.

Do not add LLM/RAG/agent curriculum.

Then start the first actual task immediately.
```

---

# Template D — Search Staff Oral Board

```text
Read the 2027 master, Search bank, and roadmap.

Run a Staff-level Search/IR oral board.

Give me an ambiguous search system problem with:
- corpus/vertical;
- query mix;
- QPS;
- freshness requirement;
- p99 latency;
- relevance/business objectives;
- filters/constraints;
- update rate;
- reliability requirements.

Make me:
1. clarify requirements;
2. choose index/analyzers;
3. design lexical/neural/ANN retrieval;
4. choose LTR/reranking;
5. define labels/evaluation;
6. do rough capacity math;
7. define experiments;
8. define observability/versioning/rollback;
9. diagnose an incident you introduce;
10. adapt after you change one assumption.

Score only observed performance and create targeted repairs.
```

---

# Template E — Recommendation Staff Oral Board

```text
Read the 2027 master, Recommendation bank, and roadmap.

Run a Staff-level Recommendation/Ranking oral board.

Give me an ambiguous product surface:
[feed/video / social-photo / commerce-items / marketplace / ads / notifications / generic]

Specify:
- event/label environment;
- candidate universe;
- traffic/latency;
- objective(s);
- freshness;
- constraints;
- experimentation limitations.

Make me:
1. clarify data-generating process;
2. define labels/training data;
3. design candidate sources;
4. choose ANN/retrieval;
5. choose LTR/ranker architecture;
6. define multi-objective/constraint logic;
7. define offline/counterfactual/online evaluation;
8. do capacity math;
9. define serving/freshness/rollback;
10. diagnose a failure you introduce.

Change one assumption mid-board and make me redesign.

Score only observed performance and create targeted repairs.
```

---

# Template F — Learning-to-Rank Deep Dive

```text
Read both 2027 banks and the roadmap.

Run a cross-domain LTR session.

Cover:
- pointwise vs pairwise vs listwise;
- LambdaMART/tree ranking;
- neural ranking;
- feature interactions;
- calibration;
- multi-task ranking;
- debiasing/counterfactual LTR;
- reranking/slate constraints.

For each mechanism:
1. ask for objective and assumptions;
2. ask what metric it aligns with;
3. ask what labels/grouping it needs;
4. ask serving implications;
5. ask one Search case;
6. ask one Recommendation case;
7. ask what changes between the two.

Do not turn this into a memorized model catalog.
```

---

# Template G — Vertical Transfer Session

```text
Read the 2027 master and relevant bank(s).

Today the vertical is:
[video/feed / social-photo/content / e-commerce/items / ads / marketplace / local search / enterprise search / media search]

Start from the generic Search or Recommendation stack and make me identify what changes in:
- labels;
- candidate sources;
- features;
- ranking objective;
- constraints;
- evaluation;
- experiments;
- freshness;
- serving;
- ecosystem/business effects.

Then introduce one failure/incident specific to that vertical.

End with a concise architecture-delta memo and mastery rating.
```

---

# Template H — Cold Mixed Review

```text
Read the 2027 master, roadmap, both banks, and coding set.

Run a cold mixed review without announcing the pattern.

Prioritize:
- failed/Red items due;
- D3 items due for recall;
- oldest unmastered coding item;
- Search↔Recommendation transfer;
- one 2026 Generalist MLE maintenance item if due.

Do not broad-review already strong material.
```

---

# Template I — Research Reproduction

```text
Read the 2027 master and roadmap research contract.

Today I am reproducing:
[PAPER / TECHNICAL RESULT]

Domain:
[Search / Recommendation / LTR]

Require:
- exact claim;
- baseline;
- dataset/protocol;
- assumptions;
- metric;
- success criterion;
- implementation plan;
- ablation/sensitivity plan;
- negative-result logging;
- reproducibility instructions.

When results arrive, make me explain:
- whether the claim reproduced;
- why/why not;
- discrepancies;
- evaluation weaknesses;
- system/deployment implications.

Do not let the session collapse into paper summarization.
```

---

# Template J — Short Theory Starter

```text
Read the 2027 Search+Recs master, roadmap, and relevant bank.

Run today's IDs cold:
attempt → probing → diagnose → visible repair for substantive gaps → reconstruction only if needed → changed-constraint/vertical transfer → mastery rating → cold re-test plan.

Follow the website-compatible artifact contract exactly: create a NEW concise session note for attempts/repairs/mastery/review evidence; create/update the one-item durable interview-answer for each seriously covered knowledge ID using exactly `Canonical Staff-Depth Question` → `Mastery Answer` → mandatory thorough `Learn the Concepts` → `Material Follow-ups / Scenario Variants`; require `Learn the Concepts` even after a perfect cold answer; fold every substantive teaching/deeper reconstruction/correction/follow-up into those existing sections in the same session; create a separate lesson only for genuinely cross-item reusable material; quote all dates; use no H1 in artifact bodies; preserve LaTeX as `$...$` / `$$...$$`.

Today: [WEEK / IDs]
```

---

# Template K — Short Coding Starter

```text
Read the 2027 Search+Recs master, roadmap, and coding set.

Run today's coding IDs in INTERVIEW mode.
Scaffold tests/files but do not reveal the solution.

Require:
clarify → baseline → invariant/mechanism → implement → test/benchmark/debug → resource defense → follow-up → review → mastery/re-test.

Follow the website-compatible artifact contract: create a NEW coding session note. In REVIEW/SOLUTION mode, create/update a reusable lesson only when substantive teaching is produced; never leak the target solution while still in INTERVIEW mode. Preserve LaTeX as `$...$` / `$$...$$`.

Today: [WEEK / IDs]
```

---

# Source-set note

The authoritative 2027 specialization source set is:

1. `01_2027_Search_Recs_Coding_Set_STAFF.md`
2. `02_2027_Master_Instructions_SEARCH_RECS_STAFF.md`
3. `03_2027_Search_Recs_STAFF_Roadmap_FINAL.md`
4. `04_2027_Search_Recs_Session_Start_Prompt_Templates.md`
5. `Bank_2027_Search_IR_STAFF_SEARCH_RECS_ONLY.md`
6. `Bank_2027_Ranking_Recommendation_STAFF_SEARCH_RECS_ONLY.md`

Older 2027 three-track files containing an LLM specialization are superseded.
