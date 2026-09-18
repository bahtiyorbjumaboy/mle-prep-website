# 2026 Generalist MLE — Session Start Prompt Templates

**Status:** Operational convenience file  
**Authority:** Does not override the 2026 master, roadmap, banks, or coding set.

---

# Website-compatible study artifact contract — MANDATORY

These templates create Markdown artifacts consumed by the curriculum website. Markdown remains the source of truth. Follow this contract exactly whenever a template writes study artifacts.

## 1. Canonical item keys

Use stable canonical keys in frontmatter and internal references.

- 2026 knowledge: `2026:bank01:A3`, `2026:bank07:B24`, etc. The bank is mandatory because IDs such as `A1` repeat across banks.
- 2026 coding: `2026:DSA-01`, `2026:NP-02`, `2026:SQL-03`, etc.

Never infer a bank from a bare `A1`/`A2`-style ID when context is ambiguous. Resolve the exact authoritative source first.

## 2. Global Markdown/frontmatter rules

These rules apply to `interview-answer`, `lesson`, `coding-review`, and `session-note` artifacts.

1. **Frontmatter owns the page title.** Do not put an H1 (`# ...`) in the Markdown body. The body must begin at H2 (`## ...`) or lower.
2. **Quote every date value** so YAML parsers always receive strings, for example `created: "2026-09-17"`, `updated: "2026-09-17"`, and `date: "2026-09-17"`.
3. Preserve an existing `created` value when updating a durable artifact; change only `updated`.
4. Use canonical item keys in mappings; never use question text or display titles as identity.
5. Do not duplicate a canonical curriculum question/problem under a second identity.
6. Do not invent canonical wording, IDs, prerequisites, follow-ups, or roadmap placement.
7. Tags are lowercase kebab-case when practical.
8. Reusable artifacts contain durable knowledge, **not live progress state**.

## 3. Single source of truth for mastery/progress

The website progress store (localStorage/exported progress JSON) is the source of truth for the learner's **current** completion/mastery state.

Therefore:

- `interview-answer`, `lesson`, and `coding-review` frontmatter MUST NOT contain `status`, `mastery`, `next_review`, `attempts`, sprint color/result, or similar live-progress fields.
- Their bodies MUST NOT contain a `Mastery Record`, attempt log, reconstruction evidence, dated repair history, or current review schedule.
- A `session-note` MAY record the mastery observed at the end of that historical session, the repairs made, and the review date planned in that session. Those values are historical evidence only and MUST NOT be treated as current progress by the website.

This separation prevents reusable study content from becoming stale when mastery changes later.

## 4. Interview-answer artifact — exactly one knowledge item

For every knowledge question seriously covered, create or update exactly one question-scoped interview-answer Markdown file.

One interview-answer file maps to **exactly one** canonical knowledge item.

Preferred location:

`curriculum/2026/interview-answers/<bank>/<ID>.md`

Required frontmatter:

```yaml
---
type: interview-answer
item: "2026:bank01:A3"
title: "<concise topic title>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - <tag>
---
```

Required body structure:

```markdown
## Canonical Interview Question

[Copy the exact canonical question from the authoritative bank.]

## Mastery Answer

## Learn the Concepts

## Required / Important Follow-ups
```

Content contract:

- **`## Mastery Answer` is the interview answer.** Keep it polished, direct, technically rigorous, and at the bank's required depth. It should be suitable to give aloud while still covering the assumptions, derivation/trade-offs, failure modes, and evaluation points required by the canonical prompt.
- **`## Learn the Concepts` is mandatory for every interview-answer artifact, even when the learner answers the question perfectly cold.** It is not a remediation-only section. Make it a thorough self-study treatment of the concepts the question is testing so the learner does not need a second lesson file to learn this item.
- The `Learn the Concepts` section should include, when relevant: first-principles motivation; precise definitions; derivation/mechanism; worked or quantitative examples; assumptions; trade-offs; failure modes; evaluation semantics; implementation/system connections; debugging; and changed-constraint reasoning. Include only material that genuinely supports this item.
- **`## Required / Important Follow-ups` contains durable answers/explanations for canonical follow-ups and substantive interviewer probes.** Do not merely list questions when the session established useful answer content.
- Do **not** add `Plain-English Explanation`, `Reasoning Chain`, `Interview Compression`, `Mastery Record`, reconstruction-log, repair-log, or review-plan sections.

Durable-update rule:

- The interview-answer file is the canonical study source for this knowledge item and must become more complete as understanding improves.
- If a session teaches a substantive concept, asks for a deeper reconstruction than the file currently contains, resolves an important misconception, derives something useful, or answers a meaningful follow-up, **update the existing interview-answer in the same session**. Do not leave that knowledge only in the chat or session note.
- Fold new durable content into the existing sections: update `Mastery Answer` when the interview answer itself should improve; extend `Learn the Concepts` for deeper teaching/derivation/mechanism; extend `Required / Important Follow-ups` for follow-up knowledge.
- Reconstruction evidence itself (attempts, mistakes, dates, mastery) belongs only in the session note. The **knowledge exposed by the reconstruction** belongs in the durable interview-answer.
- A separate lesson is **not** the default home for question-specific teaching. Do not create a lesson merely because the learner needed teaching or because `Learn the Concepts` is long. A lesson is justified only for genuinely reusable cross-item material that would otherwise be duplicated across multiple knowledge/coding artifacts. Even then, all material needed to understand and defend this canonical item must remain self-contained in its interview-answer.

Rules:

- Copy the exact canonical question from the authoritative bank; do not paraphrase it.
- Keep the artifact reusable, polished, and non-chronological.
- Preserve an existing `created` date; update `updated` whenever durable content changes.
- Do not append attempts, repair history, mastery state, review dates, or session evidence here; those belong in the session note.

## 5. Lesson artifact — optional cross-item teaching only

A lesson is an optional reusable teaching unit for material that genuinely spans multiple canonical items. It is not the default teaching artifact for a knowledge question: the question's mandatory `Learn the Concepts` section owns all question-specific conceptual depth.

Create/update a lesson only when the material is meaningfully reusable across multiple knowledge/coding items and centralizing it prevents real duplication. A lesson may support one or many items, and an item may link to multiple lessons.

Preferred location:

`curriculum/2026/lessons/<stable-kebab-case-id>.md`

Required frontmatter:

```yaml
---
type: lesson
id: "<stable-kebab-case-id>"
title: "<lesson title>"
items:
  - "2026:bank01:A3"
  - "2026:NP-02"
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
- Do not create trivial one-paragraph lesson stubs merely to satisfy the format.
- Do not duplicate canonical interview answers verbatim. Teach only the genuinely cross-item reusable concept.
- The Markdown body must begin at H2; do not repeat `title` as an H1.
- Useful sections may include mental model, derivation, worked example, failure modes, implementation notes, and interview connections.
- No mastery/progress/attempt history belongs in a lesson.

## 6. Coding-review artifact — exactly one coding item

A coding review is the durable post-attempt explanation for one coding problem. It is separate from learner-owned implementation files and separate from the chronological session note.

Preferred location:

`curriculum/2026/coding-reviews/<ID>.md`

Required frontmatter:

```yaml
---
type: coding-review
item: "2026:NP-02"
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

## Core Approach / Invariant

## Correctness Reasoning

## Complexity / Resources

## Tests and Edge Cases

## Important Follow-ups

## Common Failure Modes
```

Rules:

- One coding-review file maps to exactly one canonical coding item.
- Preserve the exact canonical prompt/interface where included.
- Do not create/update a solution-revealing coding review while the learner is still in INTERVIEW or HINT mode.
- It may be created after the learner independently completes the problem or explicitly switches to REVIEW/SOLUTION mode.
- Do not put live mastery state or attempt history in this file; record those in the session note/progress store.

## 7. Session-note artifact — chronological evidence

Create one new session note per actual study session. A session note may reference multiple items.

Preferred location:

`curriculum/2026/notes/YYYY-MM-DD_<session-slug>.md`

Required frontmatter:

```yaml
---
type: session-note
title: "<concise session title>"
date: "YYYY-MM-DD"
curriculum: "2026"
session_type: "<theory | coding | review | mock | repair>"
items:
  - "<canonical-item-key>"
observed_mastery:
  "<canonical-item-key>": "<Unseen | Learned | Interview-ready | Mastered>"
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

## Follow-ups Completed

## Observed Mastery at Session End

## Review Plan
```

This is where attempts, reconstruction evidence, failures, repairs, observed mastery, and planned cold-review dates belong.

## 8. Math / LaTeX in Markdown

Preserve mathematical notation as real Markdown math source.

Inline:

```text
$x^T x$
```

Display:

```text
$$
A = U\Sigma V^T
$$
```

Rules:

- Use `$...$` for inline math and `$$...$$` for display math.
- Do not place actual math in fenced code blocks merely because the chat UI may not render it. Code fences above are examples of syntax only.
- Do not replace LaTeX with Unicode approximations.
- Preserve backslashes and commands needed by KaTeX/MathJax.
- The website is expected to render Markdown math with `remark-math` plus KaTeX/MathJax (or equivalent).

## 9. Artifact-write checklist

Before finishing any session that writes artifacts, verify:

- all canonical keys resolve;
- all date values are quoted strings;
- no artifact body contains an H1;
- each interview answer maps to exactly one knowledge item;
- every interview answer contains `Mastery Answer`, mandatory thorough `Learn the Concepts`, and `Required / Important Follow-ups`;
- any substantive teaching/deeper reconstruction/follow-up knowledge discovered this session has been folded into the existing interview-answer sections;
- each coding review maps to exactly one coding item;
- lesson `items` is a non-empty canonical-key list;
- no durable artifact contains live mastery/progress fields;
- attempt/repair/review evidence lives in the session note;
- canonical wording was copied exactly where required;
- LaTeX delimiters/backslashes were preserved.
---
# Template A — Theory Session

```text
We are continuing my 2026 Generalist MLE curriculum.

Before doing anything substantive, retrieve and follow:
1. `02_2026_Master_Instructions_GENERALIST_MLE.md`
2. `03_2026_Generalist_MLE_17_Week_Roadmap_FINAL.md`
3. the relevant core bank(s)

Today:
- Week/session: [WEEK]
- Knowledge IDs: [IDs OR "use today's roadmap items"]
- Session type: first exposure / review / cold re-test / mock repair
- Time available: [OPTIONAL]

For each question:

1. Ask the exact canonical question cold.
2. Do not show the answer before I make a serious attempt.
3. Probe only where my answer exposes a meaningful gap.
4. Diagnose correct points, missing points, incorrect reasoning, weak assumptions/derivation, and failure/evaluation gaps.
5. If the gap is substantive, teach it visibly, update the session notes, then make me reconstruct it.
6. If the issue is only wording/terminology/precision, correct it briefly and move on.
7. Run important question-specific follow-ups.
8. Rate:
   Unseen → Learned → Interview-ready → Mastered.
9. Schedule spaced review.

Follow the website-compatible study artifact contract above.

- Create one NEW session-note file for this session; put attempts, reconstruction evidence, repairs, observed mastery, and next-review planning there.
- For every knowledge question seriously covered, create or update its one-item interview-answer with exactly these durable sections: `Canonical Interview Question`, `Mastery Answer`, mandatory thorough `Learn the Concepts`, and `Required / Important Follow-ups`.
- `Learn the Concepts` is required even when my cold answer is already correct/complete. It must teach the underlying concepts thoroughly enough that this interview-answer is my self-contained study source for the item.
- Whenever teaching, a deeper reconstruction, a correction, or a substantive follow-up produces durable knowledge not already present, immediately fold it into the appropriate existing interview-answer section in the same session. Do not create a reconstruction/repair section and do not leave the knowledge only in the session note.
- Create/update a lesson only for genuinely cross-item material that would otherwise be duplicated; never use a lesson as a substitute for the interview-answer's `Learn the Concepts` depth.
- Preserve LaTeX math source exactly using `$...$` / `$$...$$`.
- Keep interview answers technically rigorous, self-contained for study, and faithful to the canonical bank wording.

Start with the first scheduled question.
```

---

# Template B — Coding Session in VS Code / Codex

```text
We are continuing my 2026 Generalist MLE coding curriculum.

Before doing anything substantive, read:
1. `02_2026_Master_Instructions_GENERALIST_MLE.md`
2. `03_2026_Generalist_MLE_17_Week_Roadmap_FINAL.md`
3. `01_2026_Generalist_MLE_Coding_Set_FINAL.md`

Today:
- Week/session: [WEEK]
- Coding IDs: [IDs OR "use today's roadmap IDs"]
- Time available: [OPTIONAL]

Treat the 2026 coding set as authoritative.

Default to INTERVIEW mode:
- INTERVIEW = no solution disclosure;
- HINT = incremental hint ladder;
- REVIEW/SOLUTION = only after I explicitly switch modes.

For each problem:

1. Scaffold a minimal workspace with README, solution file, tests, and notes.
2. Copy the exact prompt and required interface.
3. Do NOT implement or reveal the target solution.
4. Before coding, require:
   clarifications → assumptions → baseline → correctness → complexity → improved approach/invariant.
5. Let me think aloud while implementing.
6. Use deterministic tests; for ★ items include applicable boundary/property/adversarial/reproducibility tests.
7. On failure:
   interpret → localize → hypothesize root cause → smallest fix → focused test → full suite.
8. After correctness, require:
   complexity/resource defense → follow-ups → code review → mastery state → cold re-attempt target.

For SQL emphasize grain, joins, NULL semantics, ordering/ties.
For NumPy/pandas emphasize shapes, axes, vectorization, masking, memory.
For ML emphasize objective, assumptions, numerical stability, validation.
For PyTorch emphasize shapes, autograd, train/eval, state/device, masking, reproducibility.
For debugging use identify → explain → reproduce → fix → regression test.

Artifact handling:
- Create one NEW session-note file for the coding session using the website-compatible contract; chronological attempts, bugs, repairs, observed mastery, and re-test dates belong there.
- After the learner independently completes the problem or explicitly enters REVIEW/SOLUTION mode, create/update the one-item `coding-review` when a durable review is useful.
- If substantive reusable conceptual teaching is produced, create/update a lesson and map it to the canonical coding ID.
- A lesson may also map to related knowledge IDs when the connection is explicit and source-supported.
- Do not create a lesson that reveals the target solution while still in INTERVIEW mode.
- Preserve LaTeX math source as `$...$` / `$$...$$`.

Start by retrieving the exact problem and scaffolding it.
```

---

# Template C — Weekly Start

```text
Read the 2026 master, roadmap, and relevant banks/coding set.

We are starting Week [XX].

Use the roadmap exactly.

Prioritize:
1. overdue Red repairs;
2. due cold re-tests;
3. today's scheduled knowledge;
4. today's scheduled coding;
5. P0 milestone work.

Do not add specialization content.

Then start the first actual task immediately.
```

---

# Template D — Generalist Mock

```text
Read the 2026 master and roadmap.

Run a realistic Generalist MLE mock.

Mix:
- one coding problem;
- SQL/data or debugging;
- Core ML/statistics/deep learning;
- one ML-system-design scenario;
- P0/project defense when appropriate.

Score:
- framing;
- correctness;
- depth;
- implementation/testing;
- complexity/resources;
- ML judgment;
- system trade-offs;
- communication;
- ownership accuracy.

Create only targeted repair items from observed failures.
```

---

# Template E — Cold Review

```text
Read the 2026 master, roadmap, relevant banks, and coding set.

Run a cold mixed review without announcing the pattern/topic in advance.

Select from:
- failed/Red items due;
- first re-attempts due;
- oldest ★ coding item not mastered;
- oldest high-depth knowledge item not mastered;
- one random cross-domain core item.

Do not broad-reread strong material.
```

---

# Source-set note

The 2026 source set is:

1. `01_2026_Generalist_MLE_Coding_Set_FINAL.md`
2. `02_2026_Master_Instructions_GENERALIST_MLE.md`
3. `03_2026_Generalist_MLE_17_Week_Roadmap_FINAL.md`
4. `04_2026_Session_Start_Prompt_Templates.md`
5. `Bank_01_Linear_Algebra_FINAL.md`
6. `Bank_02_Core_ML_FINAL.md`
7. `Bank_05_Deep_Learning_FINAL.md`
8. `Bank_07_Probability_Inference_FINAL.md`
9. `Bank_08_MLE_Practice_FINAL.md`
10. `Bank_09_System_Design_FINAL.md`

Banks 03/04/06 and the 2027 Staff-depth files belong to the separate 2027 specialization curriculum.
