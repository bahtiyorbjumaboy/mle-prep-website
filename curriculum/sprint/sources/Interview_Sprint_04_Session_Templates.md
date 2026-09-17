# Search + Ranking + Recommendation Interview Sprint — Session Templates

# Website-compatible study artifact contract — MANDATORY

The sprint is an overlay, not a separate canonical curriculum. Borrowed 2027 knowledge/coding IDs retain their canonical 2027 identities. Reusable answers, coding reviews, and lessons MUST update the corresponding 2027 artifacts rather than create competing sprint-owned copies.

## 1. Canonical item keys

Use the original 2027 key for every borrowed item, for example:

- `2027:R08`
- `2027:S17`
- `2027:REC-05`
- `2027:SRCH-11`

Do not mint keys such as `sprint:R08` or duplicate canonical content under a sprint identity.

## 2. Global Markdown/frontmatter rules

1. Frontmatter owns the page title. Artifact bodies MUST NOT contain an H1 (`# ...`); start body sections at H2 (`## ...`) or lower.
2. Quote all date values as strings, e.g. `date: "2026-09-17"`, `created: "2026-09-17"`, `updated: "2026-09-17"`.
3. Preserve `created` when updating a durable artifact; update only `updated`.
4. Use canonical 2027 keys as identity.
5. Reusable artifacts contain durable knowledge, not live progress state.
6. Canonical wording comes from the 2027 bank/coding set and must not be silently rewritten.

## 3. Single source of truth for mastery/progress

The website progress store (localStorage/exported progress JSON) is the source of truth for **current** mastery/completion.

Therefore reusable `interview-answer`, `lesson`, and `coding-review` artifacts MUST NOT contain:

- `status` / current mastery;
- attempts count;
- next-review date;
- sprint Red/Yellow/Green result;
- reconstruction/attempt logs;
- dated repair history;
- a `Mastery Record` section.

Sprint session notes and the borrowed-ID ledger may record historical sprint evidence. That historical evidence is not the website's live progress state.

## 4. Borrowed theory item → canonical 2027 interview answer

When a borrowed theory item is seriously covered, create/update exactly one canonical 2027 interview-answer file.

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

Body must use the 2027 Staff-depth durable sections and begin at H2:

```markdown
## Canonical Staff-Depth Question

## Mastery Answer

## Material Follow-ups / Scenario Variants

## Plain-English Model

## Reasoning Chain

## Staff Compression
```

Do not include sprint result, mastery record, attempts, reconstruction evidence, repairs, or next-review scheduling in the interview-answer file.

## 5. Lesson artifact → canonical 2027 lesson

Create/update a lesson only for substantive reusable teaching.

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
  - "2027:REC-05"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - <tag>
---
```

A lesson is concept-scoped: it may map to multiple canonical 2027 items, and one item may have multiple lessons. `items` must be non-empty. Do not duplicate the interview answer verbatim. Do not put progress/attempt history in lessons. Body starts at H2, never H1.

## 6. Borrowed coding item → canonical 2027 coding review

After the learner independently completes the problem or explicitly switches to REVIEW/SOLUTION mode, a durable coding review may be created/updated.

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

Do not create/update a solution-revealing coding review while still in INTERVIEW or HINT mode. Keep attempt history and live mastery out of this durable file.

## 7. Sprint session notes — chronological evidence

Every substantive sprint session creates a sprint-owned session note:

`curriculum/sprint/notes/YYYY-MM-DD_<session-slug>.md`

Required frontmatter:

```yaml
---
type: session-note
title: "<concise sprint session title>"
date: "YYYY-MM-DD"
curriculum: "sprint"
session_type: "<theory | coding | system-design | debugging | ownership | mock>"
items:
  - "<canonical-2027-item-key>"
observed_mastery:
  "<canonical-2027-item-key>": "<Unseen | Learned | Independent | Mastered>"
sprint_result:
  "<canonical-2027-item-key>": "<Red | Yellow | Green>"
next_review:
  "<canonical-2027-item-key>": "YYYY-MM-DD"
---
```

Fields may omit an item when no judgment/date was established. These are historical sprint observations only.

Recommended body sections:

```markdown
## Items Covered

## Attempt / Reconstruction Evidence

## Repairs and Precision Corrections

## Follow-ups / Variants Completed

## Observed Sprint Result and Mastery

## Review Plan
```

This is the correct home for sprint result, mastery evidence, repairs, reconstruction evidence, and next-review planning.

## 8. Math / LaTeX in Markdown

Preserve actual mathematical source using `$...$` for inline math and `$$...$$` for display math. Do not replace LaTeX with Unicode approximations or put real math in code fences merely because the chat UI does not render it. Preserve backslashes/commands required by KaTeX/MathJax. The website is expected to render math through `remark-math` plus KaTeX/MathJax (or equivalent).

## 9. Artifact-write checklist

Before finishing any sprint session that writes artifacts, verify:

- borrowed items keep their canonical 2027 keys;
- all date values are quoted strings;
- no artifact body contains an H1;
- interview answers and coding reviews are one-item durable artifacts;
- lesson `items` is non-empty and canonical;
- no reusable artifact contains live progress or sprint-result fields;
- sprint evidence lives in the sprint session note / ledger;
- exact canonical wording is preserved;
- LaTeX delimiters/backslashes are preserved.
---
# Template A — Ranking Theory

```text
Read the sprint master, sprint roadmap, borrowed-ID ledger, and relevant 2027 bank.
Today: [IDs / week]

Run each item cold. Probe objective, labels/data-generating process, retrieval/ranking stage, metric, model choice, latency/resource constraints, failure modes, and online/offline mismatch.

Do not lecture first. End with mastery state and ledger update.

Follow the website-compatible artifact contract above exactly: create a sprint session note for attempt/repair/mastery/review evidence; create/update the canonical one-item 2027 interview-answer as durable content with no status or Mastery Record; create/update lessons only for substantive reusable teaching; quote all dates; use no H1 in artifact bodies; preserve LaTeX as `$...$` / `$$...$$`.
```

# Template B — Ranking Coding

```text
Read the sprint master, roadmap, ledger, and 2027 coding set.
Today: [coding IDs]

INTERVIEW mode.
Require: clarify → baseline → invariant/objective → implement → tests → complexity/resources → ranking/system follow-up.

After correctness ask: how does this scale, what changes online, what metric validates it, and what breaks under latency constraints?
Update the ledger.

Create a sprint coding session note for chronological evidence. After independent completion or explicit REVIEW/SOLUTION mode, create/update the canonical one-item 2027 coding-review when useful. Create/update a reusable 2027 lesson only for substantive conceptual teaching; never reveal the target solution through a lesson or coding-review while still in INTERVIEW/HINT mode. Quote all dates, use no H1 in artifact bodies, and preserve LaTeX as `$...$` / `$$...$$`.
```

# Template C — Limited-Latency System Design

```text
Follow the mandatory website-compatible artifact contract above. Create a sprint session note for this session; do not create an interview-answer unless a canonical knowledge item is actually studied/answered.

Run a Search/Recs system-design interview.
Give me use case, QPS, corpus/catalog size, total p99 latency, freshness, candidate count, current stage timings, and objective.

Do not reveal a target architecture.
Make me: clarify → decompose stages → allocate latency → choose retrieval → choose feature strategy → choose pre-rank/rank/rerank → choose candidate counts → define fallback/degradation → monitoring/versioning/rollback → quantify quality-vs-latency trade-offs.

Change one constraint midway.
Score requirements, ML judgment, systems judgment, quantitative reasoning, failure handling, communication.
```

# Template D — Model/System Debugging

```text
Follow the mandatory website-compatible artifact contract above. Create a sprint session note for this session; keep incident evidence and repairs in that note.

Run a ranking/search/recommendation debugging interview.
Give symptoms and limited telemetry: offline metrics, online metrics, candidate recall, score distributions, feature freshness, stage latency, cache/index/model versions, and segment metrics.

Do not reveal the root cause.
Require: triage → ranked hypotheses → discriminating checks → localization → mitigation/rollback → root cause → prevention/regression test.
```

# Template E — End-to-End Ownership

```text
Follow the mandatory website-compatible artifact contract above. Create a sprint session note for this session; do not convert personal-project discussion into a canonical interview-answer unless it is explicitly tied to a canonical curriculum item.

Run an end-to-end ML ownership interview.
Ask for one real project.
Probe: problem → data/logging → labels → leakage → baseline → model choice → offline eval → online experiment → serving → latency/resources → monitoring → incident → iteration.

Aggressively distinguish what I owned, what adjacent teams owned, and what I only observed.
Ask why this metric/model, what failed, what changed after launch, and what I would redesign now.
```

# Template F — Full Mock

```text
Follow the mandatory website-compatible artifact contract above. Create one sprint session note for the mock and keep observed gaps, repairs, mastery evidence, and review planning there.

Run a 90-minute Search + Ranking + Recommendation MLE mock:
1. 30 min ranking-oriented coding
2. 35 min system design with explicit latency budget
3. 15 min debugging incident
4. 10 min end-to-end ownership deep dive

Do not teach during the mock. Afterward provide only observed gaps and a repair queue.
```
