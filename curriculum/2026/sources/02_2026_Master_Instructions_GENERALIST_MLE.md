# 2026 Generalist MLE — Master Instructions

**Status:** ACTIVE 2026 GENERALIST PROJECT CONTROL FILE  
**Effective roadmap window:** Sunday, September 6, 2026 through Thursday, December 31, 2026  
**Duration:** 17 weeks  
**Authoritative roadmap:** `03_2026_Generalist_MLE_17_Week_Roadmap_FINAL.md`

---

# 0. Instruction to every new 2026 curriculum chat

Before substantive work:

1. Read this master file.
2. Read `03_2026_Generalist_MLE_17_Week_Roadmap_FINAL.md`.
3. Read the relevant core bank(s):
   - `Bank_01_Linear_Algebra_FINAL.md`
   - `Bank_02_Core_ML_FINAL.md`
   - `Bank_05_Deep_Learning_FINAL.md`
   - `Bank_07_Probability_Inference_FINAL.md`
   - `Bank_08_MLE_Practice_FINAL.md`
   - `Bank_09_System_Design_FINAL.md`
4. For coding, read `01_2026_Generalist_MLE_Coding_Set_FINAL.md`.
5. Preserve 2026 IDs, wording, counts, sequencing, mastery rules, and ownership boundaries unless the user explicitly changes them.
6. Do not use Banks 03, 04, or 06 for scheduled 2026 specialization work. Those topics are deferred to the separate 2027 Staff-depth specialization curriculum.
7. For theory sessions, create a new session-scoped Markdown notes artifact.
8. For coding sessions, scaffold/tests are allowed, but do not prefill the solution unless the learner explicitly switches to REVIEW/SOLUTION mode.
9. `04_2026_Session_Start_Prompt_Templates.md` is operational only and cannot override the master, roadmap, banks, or coding set.

## Responsibility rule

- **Master:** purpose, source governance, mastery, workload, ownership boundaries, final acceptance.
- **Core banks:** question IDs, wording, depth, prerequisites/cross-references, required follow-ups.
- **Coding set:** coding IDs, prompts, levels, formats, tests, follow-ups.
- **Roadmap:** weekly sequencing, P0 milestones, review cadence, and mock gates.
- **Session templates:** convenience only.

---

# 1. 2026 source manifest

The intended 2026 source set contains **10 Markdown files**:

| File | Scope |
|---|---|
| `01_2026_Generalist_MLE_Coding_Set_FINAL.md` | 69 core coding IDs |
| `02_2026_Master_Instructions_GENERALIST_MLE.md` | project control |
| `03_2026_Generalist_MLE_17_Week_Roadmap_FINAL.md` | 17-week sequencing |
| `04_2026_Session_Start_Prompt_Templates.md` | operational starters |
| `Bank_01_Linear_Algebra_FINAL.md` | 20 knowledge conversations |
| `Bank_02_Core_ML_FINAL.md` | 23 knowledge conversations |
| `Bank_05_Deep_Learning_FINAL.md` | 27 knowledge conversations |
| `Bank_07_Probability_Inference_FINAL.md` | 24 knowledge conversations |
| `Bank_08_MLE_Practice_FINAL.md` | 23 knowledge conversations |
| `Bank_09_System_Design_FINAL.md` | 13 knowledge conversations |

**2026 totals:** 130 core knowledge conversations + 69 core coding IDs + P0.

Banks 03/04/06 and all 2027 Staff-depth files are outside the scheduled 2026 curriculum.

---

# 2. Purpose

By December 31, 2026, the learner should be **interview-ready for Generalist Machine Learning Engineer roles**.

The learner should be able to:

- reason about linear algebra, probability/statistics, Core ML, and Deep Learning;
- implement common algorithms/ML components in Python/NumPy/PyTorch;
- write and reason about SQL/data transformations;
- debug ML/data/framework failures;
- reason about testing, reproducibility, serving, monitoring, latency, deployment, and retraining;
- design a general ML system end to end;
- defend a production-shaped ML project;
- communicate trade-offs clearly under interview time pressure.

The 2026 objective is **broad Generalist MLE readiness**, not Search/IR + Recommendation/Ranking specialization depth.

---

# 3. Fixed cadence

- Weeks 1–16: **8 new knowledge conversations/week**.
- Week 17: final **2** knowledge conversations + final validation.
- Week 1: **5** new coding IDs.
- Weeks 2–17: **4** new coding IDs/week.
- Total: **130 knowledge + 69 coding**.

The cadence is a first-exposure schedule. Mastery requires spaced re-attempts.

---

# 4. Knowledge scope

## Bank 01 — Linear Algebra
20 conversations.

## Bank 07 — Probability & Inference
24 conversations.

## Bank 02 — Core ML
23 conversations.

## Bank 05 — Deep Learning & Optimization
27 conversations.

## Bank 08 — ML Engineering Practice
23 conversations.

## Bank 09 — ML System Design
13 conversations.

Total: **130**.

Knowledge sessions own:
- explanation;
- derivation where relevant;
- assumptions;
- comparisons;
- failure modes;
- evaluation;
- production/system implications;
- follow-up defense.

---

# 5. Coding scope

The coding set contains:

- DSA / SWE Algorithms — 26
- SQL — 9
- Python / NumPy / pandas — 11
- General ML Implementation — 9
- PyTorch / Framework — 7
- Debugging / Testing / Existing Code — 7

Total: **69**.

Coding owns:
- problem framing;
- implementation;
- correctness;
- tests;
- debugging;
- complexity/resources;
- interview communication;
- cold re-attempts.

---

# 6. P0 — General MLE Pipeline

P0 is the only required 2026 portfolio project.

It should demonstrate:

- public/synthetic/self-generated data;
- clear ML problem/target;
- point-in-time-safe split and features;
- baseline model;
- stronger model or justified alternative;
- evaluation and calibration/thresholding where relevant;
- error/slice analysis;
- testing/data validation;
- reproducible environment/config;
- training loop/checkpointing where relevant;
- minimal batch-scoring or inference interface;
- monitoring/failure analysis;
- safe rollout/rollback reasoning;
- README/architecture diagram;
- limitations;
- interview defense.

Do not add P1/P2/P3 in 2026. Those belong to 2027.

---

# 7. Mastery contract

## Knowledge

0. Unseen  
1. Learned  
2. Interview-ready  
3. Mastered

**Interview-ready:** independent correct explanation with appropriate assumptions, derivation/trade-offs, and follow-ups.

**Mastered:** survives later cold mixed-context recall and connects to coding/project/system design.

## Coding

0. Unseen  
1. Learned  
2. Interview-ready  
3. Mastered

A coding problem is not Interview-ready merely because tests pass.

Interview-ready generally requires:
- correct clarification/assumptions;
- independent approach selection;
- implementation within appropriate time box;
- meaningful testing;
- complexity/resource reasoning;
- core follow-ups;
- coherent communication.

Mastered additionally requires a later cold attempt.

---

# 8. Review queue

Every week prioritize:

1. failed/Red repairs due;
2. first re-attempts due 1–3 weeks after learning;
3. oldest ★ coding item not mastered;
4. oldest high-depth knowledge item not mastered;
5. random cross-domain core item;
6. mixed mock item if capacity remains.

Do not delete due reviews merely to protect new-exposure counts.

---

# 9. Theory session contract

Every theory chat creates a **new session-scoped Markdown file**.

Use:

**canonical question → cold attempt → dynamic probing → diagnose → visible teaching for substantive gaps → update notes → learner reconstruction only when substantive → required follow-ups → mastery state → spaced re-test**

Do not prefill the final answer before a serious cold attempt unless the learner explicitly switches to direct-study mode.

Minor wording/terminology issues do not require reconstruction.

Suggested note sections:

## Canonical Interview Question
## Mastery Answer
## Required / Important Follow-ups
## Plain-English Explanation
## Reasoning Chain
## Interview Compression
## Mastery Record

Keep notes concise and technically rigorous.

---

# 10. Coding / Codex contract

Default mode: **INTERVIEW**.

- INTERVIEW — no solution disclosure.
- HINT — incremental hint ladder.
- REVIEW/SOLUTION — only after explicit learner switch.

Recommended workspace:

```text
problems/<problem_id>/
  README.md
  solution.py
  test_solution.py
  notes.md
```

Adapt for SQL/PyTorch/data/debugging tasks.

Scaffold:
- exact prompt;
- signatures/interfaces;
- deterministic fixtures/tests;
- TODOs;
- no solution;
- no giveaway pseudocode.

Before coding require:
clarify → assumptions → baseline → correctness → complexity → improved approach/invariant.

When tests fail:
interpret → localize → root-cause hypothesis → smallest fix → focused test → full suite.

For ★ problems include applicable:
- hand-computed fixture;
- boundary case;
- property/invariant;
- adversarial case;
- reproducibility check.

After correctness require:
- complexity/resource defense;
- follow-ups;
- code review;
- mastery state;
- cold re-attempt date.

---

# 11. Workload policy

The fixed first-exposure cadence is non-negotiable unless the user changes it:

- 8 knowledge/week Weeks 1–16;
- 2 knowledge in Week 17;
- 5 coding in Week 1;
- 4 coding/week Weeks 2–17.

If overloaded, reduce:
1. optional reading;
2. note polish;
3. optional follow-ups;
4. nonessential project polish.

Do not reduce:
- scheduled first exposure without explicitly rescheduling it;
- due Red repairs;
- essential cold re-tests;
- P0 acceptance work.

---

# 12. Ownership boundaries

Always distinguish:
- professionally owned;
- professionally observed/adjacent;
- independently implemented/studied.

Never reproduce confidential employer code, data, schemas, metrics, or architecture.

Portfolio/preparation work should use public/synthetic/self-generated material.

---

# 13. Final acceptance — December 31, 2026

Acceptance requires:

- all 130 core knowledge conversations exposed;
- all 69 core coding IDs exposed;
- high-priority knowledge/coding largely mastered;
- remaining later items at least interview-ready with re-tests queued;
- P0 complete and defensible;
- successful mixed generalist MLE mock without specialization support;
- ability to handle coding, SQL/data, ML/statistics/DL, debugging, MLE practice, and general ML system design in one interview loop.

The desired outcome is:

> **Interview-ready Generalist Machine Learning Engineer by end of 2026.**

After this gate, begin the separate 2027 Staff-depth Search/IR + Recommendation/Ranking specialization curriculum.
