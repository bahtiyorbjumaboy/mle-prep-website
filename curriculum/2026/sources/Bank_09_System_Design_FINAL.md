# Bank 09 — ML System Design (FINAL)

**Status:** FINAL knowledge bank for the 25-week ML Interview Project.
**Final count:** 13 questions.

## Bank contract

- These are interview conversations, not flashcards.
- The main prompt is the scheduled unit; follow-ups do **not** count as separate roadmap questions.
- Coding owns implementation fluency; this bank owns explanation, derivation where appropriate, tradeoffs, failure analysis, and system connection.
- Preserve honest ownership: professional systems may be used only where supported by Project sources; independent portfolio implementations must be described as such.
- Canonical follow-ups listed in this bank are **question-specific**; generic boilerplate probes are not canonical requirements.
- Interviewers may still probe assumptions, failure modes, alternatives, or evaluation dynamically when the learner's answer exposes a meaningful gap.

## Final questions

### A1 — ML System Design Interview Framework
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A1

**Q:** Before any specific scenario: what is your standard approach to an open-ended ML system design question? Walk me through your structure and tell me what you are trying to establish at each stage.

**Follow-up tree:**
- How would your structure change for an offline batch model, a retrieval/ranking system, and an LLM application?

### A2 — Retail Product Recommendations
**Phase:** G1/S1  
**Depth:** D2  
**Source mapping:** A2

**Q:** Design the recommendation module for a retail product page — "items you may like" — for a catalog of roughly 500K SKUs and a few million monthly sessions.

**Follow-up tree:**
- How do you prevent popularity/exposure feedback loops and support item/user cold start without breaking latency?

### A3 — Large-Catalog Site Search
**Phase:** G1/S1  
**Depth:** D2  
**Source mapping:** A3

**Q:** Design site search for a large retail catalog. Users type short, messy queries and expect the right product in the top few results.

**Follow-up tree:**
- How do you protect exact-match/SKU queries, handle zero-result queries, and decide where lexical versus dense retrieval belongs?

### A4 — Insurance-Claim Fraud Detection
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A4

**Q:** Design a system to detect fraudulent insurance claims using submitted photos, at hundreds of thousands of claims per year with fraud well under 1% of volume.

**Follow-up tree:**
- With fraud well under 1%, how do review capacity, calibration, thresholding, delayed labels, and human escalation change the design?

### A5 — Natural-Language Data-Warehouse Interface
**Phase:** G1/S1  
**Depth:** D2  
**Source mapping:** A5

**Q:** Design a natural-language interface that lets non-technical users query a company data warehouse.

**Follow-up tree:**
- How do schema linking, structured-output validation, least-privilege SQL execution, and prompt-injection defenses change the architecture?

### A6 — Feed Ranking and Session Personalization
**Phase:** G1/S1  
**Depth:** D2  
**Source mapping:** A6; absorbs A15

**Q:** Design a ranking/personalization system for a feed or session-aware surface. Cover objectives, candidate generation, ranking, short-term versus long-term state, exploration, creator/user guardrails, feedback loops, and how the architecture changes when intent shifts within a session.

**Follow-up tree:**
- How do you detect session-intent shifts, introduce exploration safely, and keep feedback loops from collapsing diversity?

### A7 — Low-Latency Ad CTR Prediction
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A7

**Q:** Design a click-through-rate prediction system for an ad auction with a sub-30ms budget for scoring hundreds of candidates.

**Follow-up tree:**
- How do calibration, auction feedback, feature freshness, and the sub-30ms budget constrain model choice and serving architecture?

### A8 — Shared Feature Platform
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A8

**Q:** Your organization has five teams building models, and each has reimplemented the same user features slightly differently. Design a system to fix that.

**Follow-up tree:**
- How do you guarantee point-in-time correctness, offline/online consistency, backfills, and feature-version compatibility?

### A9 — Large-Scale Vector Search
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A9

**Q:** Design a service that stores 100M+ embeddings and answers nearest-neighbour queries under 50ms, with continuous inserts and deletes.

**Follow-up tree:**
- What are the consistency semantics for inserts/deletes, index rebuilds, tombstones, and query-time versioning?

### A10 — A/B Testing Infrastructure
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A10

**Q:** Design the infrastructure your company would use to run hundreds of concurrent A/B tests.

**Follow-up tree:**
- How do interference, CUPED/variance reduction, metric governance, multiple testing, and experiment collisions affect the platform?
- How would the platform implement deterministic assignment and exposure logging, detect sample-ratio mismatch, enforce mutually exclusive experiments, and keep retries/cross-device identity from corrupting treatment assignment?
### A11 — Organization-Wide Model Monitoring and Safety
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A11; absorbs A14

**Q:** Design organization-wide model monitoring and safety operations across dozens of deployed models. Cover service/data/model/segment metrics, drift and fairness, alert ownership, incident triage, rollback/retraining hooks, and how high-risk moderation/safety models change the guardrails.

**Follow-up tree:**
- How do delayed labels, drift, segment harm/fairness, and alert fatigue change monitoring thresholds and incident ownership?

### A13 — Multi-Tenant Model-Serving Platform
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A13; absorbs A12

**Q:** Design a shared multi-tenant model-serving platform for many internal teams. Cover model packaging/registry, routing, autoscaling, batching, CPU/GPU placement, isolation, quotas, latency SLOs, observability, rollback, and how you would support both batch/notification-style jobs and online inference.

**Follow-up tree:**
- How do noisy-neighbor isolation, tenant quotas, model/index version coupling, and rollback work when one tenant causes a hotspot?

### A16 — Internal ML Training Platform
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A16

**Q:** Design an internal ML training platform used by many teams. Cover dataset/version lineage, feature access, reproducible environments, experiment tracking, distributed-job abstraction, checkpointing/retry, scheduling/quotas, artifact registry, evaluation gates, and the boundary between platform guarantees and model-owner responsibility.

**Follow-up tree:**
- How do preemption, checkpoint/retry semantics, data lineage, environment reproducibility, and quota fairness interact in the scheduler?

---

## Old → final disposition

- **A12 → FOLD/MERGE into A13.** Coverage is preserved in the final prompt/follow-ups.
- **A14 → FOLD/MERGE into A11.** Coverage is preserved in the final prompt/follow-ups.
- **A15 → FOLD/MERGE into A6.** Coverage is preserved in the final prompt/follow-ups.
- **A16 → ADD:** shared ML training-platform design scenario.

## Final coverage rule

Mastering this bank means being able to answer the main prompts cold, handle any listed question-specific follow-ups, respond to reasonable gap-driven interviewer probes, and connect the concept to the relevant coding/project/system-design work. Exact wording may change in interviews; conceptual ownership should transfer.
