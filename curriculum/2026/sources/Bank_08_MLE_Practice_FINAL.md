# Bank 08 — ML Engineering Practice (FINAL)

**Status:** FINAL knowledge bank for the 25-week ML Interview Project.
**Final count:** 23 questions.

## Bank contract

- These are interview conversations, not flashcards.
- The main prompt is the scheduled unit; follow-ups do **not** count as separate roadmap questions.
- Coding owns implementation fluency; this bank owns explanation, derivation where appropriate, tradeoffs, failure analysis, and system connection.
- Preserve honest ownership: professional systems may be used only where supported by Project sources; independent portfolio implementations must be described as such.
- Canonical follow-ups listed in this bank are **question-specific**; generic boilerplate probes are not canonical requirements.
- Interviewers may still probe assumptions, failure modes, alternatives, or evaluation dynamically when the learner's answer exposes a meaningful gap.

## Final questions

### A1 — ML Testing and CI Strategy
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A1; absorbs A6
**Prerequisites / cross-references:** B23 before designing the full test pyramid.  

**Q:** Design the testing and CI strategy for an ML repository. Distinguish unit, data, integration, invariant/property, regression, and end-to-end tests; decide what runs per commit versus periodically; and explain how to handle slow, flaky, or stochastic tests without making CI meaningless.

### A2 — Training-Pipeline Data Validation
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A2

**Q:** How would you validate data entering a training pipeline? Say what you check, where the check lives, and what should happen on failure — and be specific about why "fail loudly" is not always the right answer.

### A3 — Reproducible and Auditable ML Experiments
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A3; absorbs A4, A19
**Prerequisites / cross-references:** B24 plus coding PT-07 for concrete state/checkpoint mechanics.  

**Q:** Make an ML experiment reproducible and auditable months later. Cover sources of nondeterminism, seeds/kernels/data order, environment and data versions, code/model/config lineage, prediction provenance, and what full determinism costs.

### A5 — Training and Serving Environments
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A5

**Q:** How do you manage dependencies and environments for training versus serving? Explain why they differ, what goes wrong when they drift apart, and what you would actually enforce.

### A7 — Profiling GPU ML Workloads
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A7; absorbs A8

**Q:** Profile a GPU-backed inference/training workload before optimizing it. Explain utilization versus throughput, CPU/input/transfer/kernel bottlenecks, batching, and when mixed precision is worth the operational complexity.

### A9 — Data and Model Parallelism
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A9

**Q:** Explain data parallelism and model parallelism, when each is forced on you, and what the communication cost looks like. Then say what you would try before reaching for distributed training at all.

### A10 — ML System Cost Modeling
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A10

**Q:** How would you reason about the cost of an ML system? Break it into its components, tell me which ones people underestimate, and explain the tradeoff against latency.

### A11 — Diagnosing Offline–Production Divergence
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A11; absorbs A12

**Q:** Same weights and code perform correctly offline but fail in production. Give an ordered diagnostic for data/feature skew, preprocessing, embedding/index versions, serialization, device/numerical differences, and observability needed to isolate the first divergence.

### A13 — Safe Deployment, Versioning, and Rollback
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A13; absorbs A17
**Prerequisites / cross-references:** B25 plus A11/A14 for version-coupling and skew context.  

**Q:** Design safe deployment and rollback for an ML model whose serving artifact may include an attached vector index or feature snapshot. Cover shadow/canary/blue-green, version coupling, atomic rollout, compatibility, index rebuild/versioning, and rollback semantics.

### A14 — Training–Serving Feature Consistency
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A14
**Prerequisites / cross-references:** B28 before the full feature-store trade-off.  

**Q:** How do you keep features consistent between a batch training pipeline and a real-time serving path? Explain what a feature store actually solves, and what it does not.

### A15 — ML Monitoring and Incident Response
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A15; absorbs A20

**Q:** Define production monitoring and incident response for an ML system. Separate service, data, model, segment, and business metrics; define paging versus non-page alerts; diagnose silent degradation; and explain how ML incidents differ from conventional service incidents.

### A16 — Retraining Policies and Automation Risks
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A16

**Q:** How do you decide when to retrain? Compare scheduled retraining with triggered retraining, and tell me what could go wrong with an automated pipeline that retrains and deploys on its own.

### A18 — Tail-Latency Budgets
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A18
**Prerequisites / cross-references:** B26 before tail-latency diagnosis.  

**Q:** How do you set and hold a latency budget in production? Explain why p99 rather than the mean, what tail amplification is, and what you would actually do when the tail is out of budget but the median is fine.

### A21 — Batch and Online Inference
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A21
**Prerequisites / cross-references:** B27 before hybrid batch/online architecture.  

**Q:** Batch versus online inference — how do you choose, and what changes operationally between them? Cover the case where you need both.

### A22 — Scaling ML Serving Systems
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A22

**Q:** How would you scale and provision an ML serving system? Cover autoscaling, cold start, and GPU-specific problems, and say what makes ML services harder to scale than stateless web services.

### B23 — Unit, Integration, and Data Tests
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B23

**Q:** Distinguish a unit test, an integration test, and a data test in an ML context. Give one example of each, and say which one catches an upstream schema change.

### B24 — Model Registries and Artifact Lineage
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B24

**Q:** What is a model registry, and what does it give you that storing weights in object storage does not? Name two things a registered model version should point to.

### B25 — Shadow, Canary, and Blue-Green Deployments
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B25

**Q:** Distinguish shadow deployment, canary, and blue-green in one line each. Say which one tells you nothing about whether the new model is better, and why.

### B26 — Tail Latency and Fan-Out
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B26

**Q:** What do p50, p95, and p99 latency mean, and why do you set SLAs on the tail rather than the mean? One line on what fan-out does to a component's p99.

### B27 — Choosing Batch or Online Inference
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B27

**Q:** Batch versus online inference — one line each, one example each, and the single question you would ask to decide between them.

### B28 — Training–Serving Skew
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B28

**Q:** Define training/serving skew and name two concrete mechanisms that cause it. Say which mechanism a shared feature-definition/materialization path can eliminate or sharply reduce by construction, what assumptions that claim requires, and what forms of skew can still remain even when a feature store is present.

### A29 — Fairness and Segment-Harm Audits
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A29

**Q:** A model performs well overall but one customer, provider, or demographic segment experiences systematically worse outcomes. Design an operational fairness/segment-harm audit: how you would detect the disparity, localize it to data/model/threshold/exposure effects, decide whether to block rollout, and monitor it after deployment.

### A30 — Reliable Pipeline Retries and Backfills
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A30

**Q:** A scheduled ML pipeline partially fails and must be rerun after late-arriving data. Explain how you design retries, idempotency, partial-output handling, backfills, replay, watermark/time-boundary logic, lineage, and validation so rerunning the pipeline cannot silently duplicate or corrupt training/feature data.

---

## Old → final disposition

- **A4 → FOLD/MERGE into A3.** Coverage is preserved in the final prompt/follow-ups.
- **A6 → FOLD/MERGE into A1.** Coverage is preserved in the final prompt/follow-ups.
- **A8 → FOLD/MERGE into A7.** Coverage is preserved in the final prompt/follow-ups.
- **A12 → FOLD/MERGE into A11.** Coverage is preserved in the final prompt/follow-ups.
- **A17 → FOLD/MERGE into A13.** Coverage is preserved in the final prompt/follow-ups.
- **A19 → FOLD/MERGE into A3.** Coverage is preserved in the final prompt/follow-ups.
- **A20 → FOLD/MERGE into A15.** Coverage is preserved in the final prompt/follow-ups.
- **A29 → ADD:** operational fairness / segment harm.
- **A30 → ADD:** backfill, replay, idempotency, and late-data correctness.

## Final coverage rule

Mastering this bank means being able to answer the main prompts cold, handle any listed question-specific follow-ups, respond to reasonable gap-driven interviewer probes, and connect the concept to the relevant coding/project/system-design work. Exact wording may change in interviews; conceptual ownership should transfer.
