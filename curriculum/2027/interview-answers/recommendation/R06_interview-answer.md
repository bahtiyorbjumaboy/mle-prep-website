---
type: interview-answer
item: "2027:R06"
title: "Multi-Channel Recommendation Retrieval"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - recommendation-systems
  - candidate-retrieval
  - collaborative-filtering
  - hybrid-retrieval
---

## Canonical Staff-Depth Question

Compare matrix factorization, item-item/co-visitation, content similarity, graph propagation, popularity/trending, and learned embeddings as candidate sources.

## Mastery Answer

I would treat these methods as complementary candidate generators rather than as mutually exclusive replacements. The retrieval stage is trying to produce a relatively small set with high recall for the downstream ranker under strict latency and cost constraints. Each source encodes a different inductive bias, so a strong production system usually fans out across several sources, deduplicates the union, preserves source attribution, and allocates budgets based on marginal recall rather than folklore.

**Matrix factorization** learns user and item vectors from the interaction matrix. It is strong when collaborative signal is dense enough and latent taste explains behavior, but it struggles with new users/items and can overrepresent historical exposure. It is cheap to serve if user and item factors are precomputed, and ANN can scale retrieval over large catalogs.

**Item-item or co-visitation retrieval** uses observed transitions or co-occurrence such as “users who viewed A also viewed B.” It is simple, interpretable, fresh, and often excellent for session intent, complements, and substitutes. Its weakness is that it can amplify popularity and exposure bias, and sparse items have weak neighborhoods.

**Content similarity** retrieves items using metadata, text, image, taxonomy, or other item features. It handles new-item cold start and can enforce semantic similarity, but it may produce narrow or redundant candidates and cannot discover collaborative taste that is absent from content features.

**Graph propagation** treats users, items, creators, categories, or other entities as nodes and interactions as edges. Multi-hop propagation can capture richer relationships than direct co-visitation, but the extra hops increase compute, staleness risk, and popularity leakage; unrestricted propagation can also wash out personalization.

**Popularity or trending** is the simplest source and is indispensable as a robust fallback, especially for new users and source failures. Global popularity is usually too blunt, so I prefer segmented and time-decayed variants. The danger is feedback-loop concentration if popularity becomes both the exposure mechanism and the training signal.

**Learned embeddings**, including two-tower retrieval, learn a representation specifically for the retrieval objective and can combine collaborative, content, and context features. They can generalize beyond exact co-occurrence, but their quality depends heavily on training data, negative sampling, freshness, and index/model version consistency. They also introduce ANN and embedding lifecycle complexity.

In production I would define candidate channels, per-channel budgets, and a deterministic fallback. Suppose the ranker consumes 1,000 unique candidates. I might initially request 400 from learned embeddings, 250 from co-visitation, 150 from MF, 100 from content, and 100 from trending, but the actual allocation should come from **marginal recall**: how many additional relevant items each source contributes after accounting for overlap and cost. I would log source membership for every candidate, deduplicate before expensive feature hydration/ranking, and distinguish source credit from final ranker credit because one item may arrive from several channels.

Evaluation should include per-source recall, union recall, overlap, unique contribution, recall by user/item coldness and session state, latency, failure rate, freshness, and downstream ranker outcomes. A source with high standalone recall can still have low marginal value if another source already retrieves the same items. Conversely, a smaller source may be worth preserving if it uniquely covers cold-start, tail, or intent-shift segments. The Staff-level decision is therefore not “which retrieval algorithm wins?” but “what portfolio of retrieval mechanisms gives the best quality, coverage, robustness, freshness, and cost under the downstream candidate budget?”

## Learn the Concepts

### Foundation

A recommender usually cannot score every item with its most expensive ranking model. If a catalog has millions of items, the system first performs **candidate retrieval**: quickly shrink the universe from millions of items to perhaps hundreds or thousands that have a plausible chance of being relevant. A slower ranker can then use richer features on that much smaller set.

The central mental model is:

**Different candidate sources are different ways of answering, “What small subset of the catalog is worth spending ranking compute on for this request?”**

They differ because they use different evidence.

- **Collaborative evidence:** what many users collectively interacted with.
- **Co-visitation evidence:** what tends to occur near the current item/session.
- **Content evidence:** what items are intrinsically similar in metadata or representation.
- **Graph evidence:** what is reachable through useful multi-hop relationships.
- **Popularity evidence:** what is broadly or recently popular.
- **Learned representation evidence:** what a trained model predicts to be close in a task-specific embedding space.

A candidate generator is not usually responsible for producing the final order. Its first responsibility is **recall under a budget**: avoid losing good items before the ranking stage can see them. This creates a critical retrieval ceiling. If the truly relevant item never enters the candidate set, no downstream ranker can recover it.

Suppose a catalog has 10 million products and the final ranker can score only 1,000 per request. Candidate retrieval must reduce 10,000,000 items to roughly 1,000 while retaining as many relevant items as possible. If the best item is absent from those 1,000, even a perfect ranker cannot put it first.

Several basic terms matter:

- **Candidate source/channel:** one retrieval mechanism producing candidate IDs and often a retrieval score.
- **Fan-out:** querying several candidate sources, often in parallel.
- **Quota/budget:** how many candidates a source may return.
- **Deduplication:** merging duplicate item IDs retrieved by multiple sources.
- **Source attribution:** recording which sources retrieved each item.
- **Union recall:** recall of the combined candidate set.
- **Marginal recall:** additional relevant items contributed by one source beyond what the other sources already retrieved.

A simple example makes this concrete. Imagine a user has just viewed hiking boots. Four sources return 5 candidates each:

- Co-visitation: hiking socks, waterproof spray, trail shoes, insoles, gaiters.
- Content similarity: other hiking boots, trail shoes, mountaineering boots, work boots, waterproof boots.
- Personalized MF: a backpack, trail shoes, trekking poles, wool socks, running shoes.
- Trending: popular sneakers, a jacket, a backpack, hiking socks, sandals.

The union has fewer than 20 unique items because some overlap. That overlap is useful evidence, but it also means a source's standalone recall can exaggerate its actual incremental value. If co-visitation and MF both retrieve trail shoes, the second source did not add a new candidate there. If the content source is the only one retrieving new waterproof boots, it may have high marginal value for new-item coverage even if its overall click rate is lower.

Important distinctions:

1. **Candidate quality is not final-ranking quality.** Retrieval favors recall under cost; ranking favors accurate ordering among retrieved items.
2. **Similarity is not always preference.** Two items can be semantically similar but not equally desirable to a user.
3. **Co-occurrence is not causality.** Items co-visited together may reflect exposure patterns, page layout, promotions, or popularity.
4. **Popularity is not personalization.** It is still valuable as a robust prior or fallback.
5. **Hybrid retrieval is not merely taking more candidates.** The goal is complementary coverage under a fixed candidate and latency budget.

### Core Interview Reasoning

A strong answer can be reconstructed with the sequence:

**source signal → inductive bias → strengths → blind spots → serving cost/freshness → portfolio role → marginal contribution**

For each retrieval family, first identify what signal it consumes and therefore what kinds of relevance it can discover. Then reason about when that signal is missing, biased, stale, or expensive. Finally decide what role the source should play in a multi-channel retrieval portfolio.

**Matrix factorization (MF).** Start with a user-item interaction matrix. MF approximates it using low-dimensional user and item factors, so a user score for item $i$ is often $u^\top v_i$. The learned geometry compresses collaborative patterns: users with similar interaction histories end up near similar items even without explicit item metadata. Strengths are cheap scoring after training, strong collaborative personalization, and a clean latent-factor baseline. Weaknesses are cold start, exposure bias, and limited ability to use rich request context unless extended. In retrieval, the item vectors can be indexed and the user vector used as the query.

**Item-item / co-visitation.** Count or weight pairs such as items viewed, clicked, watched, or purchased within a session/window. At serving time, current-session items seed a lookup into their neighbors. This is often extremely effective because it captures local intent directly and can refresh quickly. It is also easy to explain. But raw counts favor head items, sparse items have weak neighborhoods, and observed co-visitation reflects the current exposure policy. Normalization, time decay, event weighting, and directional transitions can improve it.

**Content similarity.** Represent items using text, image, taxonomy, structured attributes, or hand-engineered features and retrieve nearby items. This directly addresses new-item cold start because a new item can be represented before it has interactions. Content retrieval is especially useful when semantics matter or collaborative data is sparse. Its main limitation is that “looks similar” is not the same as “this user will want it,” and overly literal content matching can reduce discovery and diversity.

**Graph propagation.** Construct a graph containing users/items or richer heterogeneous nodes. One-hop neighbors recover direct co-visitation; multi-hop propagation can uncover transitive structure and combine several relation types. Graph methods can capture richer collaborative structure but require careful control of degree bias, hop count, update cost, and leakage across time. More hops are not automatically better: they can move the signal away from current intent and toward globally popular regions.

**Popularity/trending.** Rank by global, segmented, contextual, or time-decayed interaction volume. It is cheap, robust, and has excellent availability, making it a default fallback and a useful source for anonymous/new users. The sophistication lies in the conditioning: trending-in-region-for-this-category-over-the-last-hour is very different from all-time global popularity. Its weakness is concentration and self-reinforcement because exposure creates interactions that create more exposure.

**Learned embeddings.** A model learns item and user/query representations so that positives are close and negatives are separated. Two-tower models are a canonical form: an item tower precomputes item embeddings; a user/query tower computes the request embedding online; ANN retrieves nearest items. This can integrate content, collaborative behavior, and context and can generalize beyond literal co-occurrence. It costs more operationally: embedding generation, ANN indexing, negative-sampling correctness, model/index versioning, and freshness all matter.

The multi-channel system should not choose one winner. It should answer:

1. Which segments or intent regimes does each source cover uniquely?
2. How much overlap exists?
3. What is each source's marginal relevant-item contribution per unit latency/memory/compute?
4. What happens when one source is empty, stale, or unavailable?
5. What candidate count should each source receive before union and deduplication?

A useful quantitative diagnostic for source $s$ is marginal recall:

$$
\Delta R_s = R(C_{\text{all}}) - R(C_{\text{all}\setminus s}),
$$

where $C_{\text{all}}$ is the union of all candidate sources. This measures how much recall is lost when source $s$ is removed from the portfolio. It is more useful than standalone recall when sources overlap heavily.

### Deeper Reasoning and Derivations

Candidate generation is an optimization problem under a constrained budget. Let source $s$ return $k_s$ candidates at cost $c_s(k_s)$. If the downstream system allows at most $K$ unique candidates and a latency/resource budget $B$, then conceptually we want to choose source budgets so that

$$
\left|\bigcup_s C_s(k_s)\right| \le K,
$$

while resource usage stays under $B$ and expected relevant-item coverage is maximized. Because sources overlap, the gain from increasing $k_s$ is not its raw source recall but its **marginal** contribution after accounting for the current union.

This yields a diminishing-returns view. The first 50 co-visitation candidates may add many relevant items; candidates 451–500 may mostly duplicate what the embedding source already found. A source budget should therefore be tuned from curves such as marginal Recall@K versus source count and latency, not set once and forgotten.

**MF geometry.** For a simple factor model,

$$
\hat r_{ui} = u_u^\top v_i.
$$

Retrieval becomes maximum inner-product search over item factors $v_i$. MF can discover relationships not encoded in item metadata because the vectors are fitted from interaction patterns. But a new item has no reliably learned $v_i$ unless side information or a mapping into the latent space is provided. That is why cold start is structural, not merely “less data overall.”

**Co-visitation weighting.** Raw pair count $n(i,j)$ is biased toward popular items. Common corrections include conditional probability-like scores, Jaccard/cosine normalization, pointwise mutual information variants, event-type weights, time decay, and directional windows. Each changes the meaning. For example,

$$
P(j\mid i) \approx \frac{n(i,j)}{n(i)}
$$

asks “given exposure/interaction with $i$, how often does $j$ follow?” whereas a symmetric cosine-normalized co-occurrence score reduces some popularity effect. Directional transitions can distinguish substitutes from next-step complements.

**Graph propagation.** If $A$ is a normalized adjacency-like operator and $x$ is a seed vector over current nodes, repeated propagation resembles

$$
x^{(t+1)} = A x^{(t)}.
$$

One step emphasizes direct neighbors; more steps mix information over increasingly distant neighborhoods. Degree normalization is critical because otherwise high-degree/popular nodes dominate. Excessive propagation causes oversmoothing or popularity collapse: local distinctions disappear as representations or scores become too similar.

**Popularity with decay.** Trending can be modeled as a decayed count,

$$
\text{trend}_i(t) = \sum_{e \in E_i} \exp(-\lambda (t-t_e)),
$$

so recent events matter more than old ones. Large $\lambda$ gives fast reaction but high variance; small $\lambda$ is stable but slow. Segmenting by locale, category, device, or surface often produces a better prior than one global list.

**Learned embedding objectives.** With a positive pair $(q,i^+)$ and negatives $i^-$, a contrastive softmax objective may use

$$
P(i^+\mid q)=\frac{\exp(s(q,i^+)/\tau)}{\sum_j \exp(s(q,i_j)/\tau)},
$$

where $s$ is typically dot product or cosine similarity and $\tau$ is temperature. The embedding source therefore inherits the biases of the positive/negative sampling process. If unexposed items are treated as negatives, the model can learn the logging policy rather than pure preference. If hard negatives contain false negatives, training can actively repel good items.

**Attribution after deduplication.** If item $i$ is retrieved by sources $A$, $B$, and $C$, retain the set $S_i=\{A,B,C\}$. Do not assign the item only to the first or highest-scoring source. This supports overlap analysis, marginal-value estimation, and debugging. The downstream ranker can optionally use source indicators as features, but that introduces feedback: the source itself may become a learned prior and should be evaluated carefully.

**Offline replay caveat.** Logged interactions expose only a biased subset of the catalog. Candidate recall computed only on historical positives can reward sources that reproduce the old policy. Strong evaluation therefore includes temporal replay, cold/tail slices, candidate-source ablations, and ultimately online experiments. If possible, randomized or exploratory traffic improves the ability to estimate value outside the old exposure policy.

### Advanced Staff-Depth Considerations

Staff-level reasoning for R06 follows:

**Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate**

or, compressed:

**Assumption → Mechanism → Evidence → Decision → Trade-off → Validation**

For this item, the baseline is a portfolio of candidate generators with known per-source budgets, latency, freshness, and segment coverage. The key mechanisms are how each source produces candidates, where its bias comes from, and how sources overlap. The critical observables are union/marginal recall, overlap, segment coverage, latency, freshness, failures, and downstream outcomes. Decisions change source algorithms or quotas; validation requires replay/ablation plus online testing where policy effects matter.

#### 1. Changed Constraints and Transfer Logic

The baseline portfolio assumes a certain catalog size, interaction density, freshness need, user-identification rate, and serving budget. Some invariants should remain: the ranker needs enough relevant candidates, candidate provenance must be preserved, and failures must degrade predictably. Fragile assumptions include dense collaborative history, slowly changing catalogs, and enough latency for several fan-out calls.

If anonymous traffic suddenly rises, user-factor or personalized embedding channels lose signal, but co-visitation from the active session, contextual popularity, and content channels remain usable. The redesign should move budget toward signals that exist at request time rather than simply returning fewer personalized candidates.

* Original assumption: Most requests have reliable user-history embeddings.
* Changed constraint: 60% of traffic becomes anonymous or identity is unavailable.
* Invariant: Preserve high candidate recall within the same total candidate/latency budget.
* Broken assumption: Long-term user history is available to MF/two-tower user representations.
* Consequence: Personalized channels become empty or generic, reducing useful recall.
* Design change: Reallocate quota toward session co-visitation, context-conditioned trending, and content/seed-item retrieval; keep a generic learned context tower if supported.
* Metric impact: Expect lower long-history personalization metrics but protect session-level Recall@K and conversion.
* Trade-off: Less individualized taste modeling in exchange for robust anonymous coverage.
* Validation: Compare anonymous/session slices, per-source marginal recall, and online outcomes before/after quota reallocation.

#### 2. Failure Modes and Diagnosis

The main failures are source outage, stale state, representation/index skew, candidate collapse, popularity domination, over-deduplication/underfill, malformed quotas, and silent loss of a segment-specific source. Diagnose by locating the first stage where the distribution differs from baseline.

The relevant chain is:

**request context → source calls → per-source candidates → union/dedup → feature hydration → ranker → exposure → outcome**

A useful signature is: if per-source candidate counts and union recall are stable but online outcomes fall, the problem is likely downstream. If one source's unique contribution disappears while its raw count stays constant, the source may have become redundant or stale.

* Symptom: Aggregate CTR drops and tail-item exposure collapses after a retrieval deployment.
* Stage decomposition: Request eligibility → each source output → overlap/dedup → final candidate set → ranker → exposure.
* Slices: Head/tail items, new items, new users, session depth, locale, device.
* Competing hypotheses: Embedding index skew; popularity quota increased; co-visitation table stale; dedup underfilled the set.
* Discriminating evidence: Version IDs, per-source unique counts, overlap matrix, tail Recall@K, candidate-set size after dedup.
* Offline/online comparison: Replay old and new retrieval stacks on identical requests; compare candidate diff before ranking.
* Replay/isolation: Disable one changed source at a time or replay with fixed downstream ranker.
* First divergence: Candidate union loses unique tail items before ranking.
* Immediate mitigation: Roll back source/config or raise fallback quota from a healthy channel.
* Permanent prevention: Version contracts, source-level SLOs, overlap/marginal-recall monitoring, and canary candidate-diff checks.

#### 3. Latency and Resource Trade-offs

Candidate retrieval spends quality budget to buy recall. The main costs are source fan-out latency, ANN probes, graph/co-visitation lookups, network calls, candidate transfer, deduplication, and downstream feature hydration proportional to unique candidate count. Parallelizing sources makes total retrieval latency closer to the slowest source than the sum, but tail latency and timeout probability become important.

A useful decomposition is

$$
L_{\text{total}} \approx \max_s L_s + L_{\text{merge/dedup}} + L_{\text{downstream}},
$$

when sources execute in parallel. Increasing a source's quota can also increase downstream ranking cost even if retrieval itself is cheap.

* Budget: 25 ms p99 for candidate generation, 1,000 unique candidates total.
* Cost decomposition: Parallel source calls + ANN/co-visitation lookup + merge/dedup + serialization.
* Dominant cost: Slow ANN/graph tail plus downstream cost from excess unique candidates.
* Quality driver: Union relevant-item recall and unique segment coverage.
* Cost driver: ANN probes, graph expansion, remote calls, and total unique candidates.
* Optimization knobs: Reduce low-marginal quotas, cache hot neighbors, precompute item neighbors, tune ANN search breadth, parallelize independent sources, early-stop after sufficient unique candidates.
* Fallback/degradation: Drop the slow optional source and replace with cached segmented popularity or co-visitation.
* Trade-off curve: Marginal Recall@K versus p99 latency and candidate count.
* Decision: Spend latency on sources with high unique contribution, not high redundant standalone recall.

#### 4. Scale and Capacity

As item count grows, exact vector search and large item-item tables stop fitting comfortably; as event volume grows, co-visitation updates and graph maintenance become expensive; as QPS grows, fan-out multiplies backend load. The first broken assumption depends on the source. MF/item embeddings mainly stress index memory and ANN throughput, while co-visitation stresses pair storage/update volume and graph propagation stresses neighborhood expansion.

Partitioning must preserve semantics. Sharding an ANN index by arbitrary item ID may require fan-out to every shard; semantic/category partitions can reduce fan-out but risk recall if routing is wrong. Co-visitation tables often need top-neighbor truncation rather than storing all pairs.

* Scaling dimension: Catalog grows from 1M to 100M items while QPS grows 20x.
* Baseline scale assumption: One in-memory ANN cluster and large hot co-visitation tables fit comfortably.
* First bottleneck: ANN memory/replication and fan-out throughput.
* Second-order effects: Rebuild duration, cache pressure, tail latency, index replication cost.
* Architectural response: Sharded/partitioned ANN, compressed vectors, tiered storage, top-N co-visitation truncation, query-aware routing.
* Partitioning/replication/caching/batching: Replicate hot partitions, cache head-item neighbors, batch ANN queries where possible.
* Consistency/freshness consequence: More shards and replicas increase mixed-version risk during updates.
* Operational failure mode: Partial shard outage silently reduces recall for certain item segments.
* Validation: Load test p99/QPS plus per-shard and per-segment recall under failure injection.

#### 5. Freshness, State, and Versioning

Different sources decay at different rates. Trending may need minute-scale freshness; session co-visitation may need near-real-time updates; MF factors may refresh daily; learned embeddings and ANN indexes may refresh on model or catalog cadence. New items require a path into content or learned indexes before enough collaborative history exists.

Version coupling matters most for learned retrieval: a query embedding from model version $v_2$ should not normally search an item index built with incompatible $v_1$ embeddings. Co-visitation tables also need event-window and schema versions so offline replay can reproduce what served.

* State that becomes stale: User/item embeddings, ANN index, co-visitation neighbors, trending counts, catalog availability.
* Why freshness matters: Stale candidates miss new inventory/intent and may surface unavailable items.
* Required freshness: Seconds/minutes for session/trending; hours/days for slower collaborative factors depending on product.
* Refresh cost: Event aggregation, embedding inference, index inserts/rebuilds, cache churn.
* Update architecture: Hybrid streaming for session/trending and incremental/batch refresh for embeddings/factors.
* Version consistency: Stamp model, embedding, index, neighbor-table, and catalog versions in serving/logs.
* Failure from version skew: Query vectors search an incompatible item space or stale neighbors point to invalid inventory.
* Fallback: Route to content/co-visitation/popularity sources with known-compatible state.
* Measurement: Candidate freshness age, stale-ID rate, source recall by item age, version-mismatch counters.
* Decision: Allocate freshness budget by how quickly each signal's value decays.

#### 6. Implementation, Serving, and Observability

A production hybrid retriever needs more than algorithms. Training jobs build factors/embeddings; streaming or batch aggregation builds co-visitation/trending state; content pipelines create searchable item representations; serving fans out to these stores/services, merges and deduplicates candidates, annotates provenance, and sends the final set downstream.

Each candidate should carry at least item ID, source membership, source-specific score(s), retrieval timestamp/version, and optional reason/context. The system should log both requested and returned counts because underfill is itself a failure. Replay requires reconstructing request context and source versions.

* Conceptual object: Multi-source candidate set with provenance.
* Training/data implementation: Interaction logs for MF/embeddings/co-visitation; item content pipeline; time-decayed aggregates.
* Stored artifact/state: Factor tables, vector indexes, neighbor lists, graph/index state, trending lists, catalog filters.
* Serving path: Parallel source fan-out → timeout handling → merge/dedup → quota/fill policy → downstream ranking.
* Component contract: Each source returns candidate IDs, scores, version, freshness metadata, and status within deadline.
* Logging: Per-source latency/count/status, candidate provenance, overlap, post-dedup count, request slice.
* Versioning: Model/index/table/config versions carried end-to-end.
* Failure mode: Source times out or returns stale/invalid candidates without obvious service failure.
* Observability: Source SLOs, marginal recall dashboards, underfill, overlap, stale-ID rates, segment coverage.
* Rollback: Versioned source/config deployment and deterministic fallback quotas.
* Testing/replay: Fixed-request candidate diffs, temporal replay, failure injection, dedup/quota invariants.

#### 7. Vertical Transfer

The invariant across verticals is the same: combine candidate mechanisms whose biases and coverage are complementary. What changes is the data-generating process, intent horizon, objective, and freshness requirement.

- **E-commerce/items:** Co-visitation captures complements/substitutes, content handles new SKUs, availability/inventory filters are hard constraints, and purchase conversion is delayed/sparse.
- **Video/feed:** Session intent changes rapidly, so recent-sequence/co-visitation and learned embeddings often need more budget; freshness and creator diversity matter more.
- **Ads:** Candidate eligibility, budget, pacing, and auction constraints dominate; a candidate source with good relevance but invalid campaign eligibility has zero practical value.
- **Marketplace:** Retrieval must consider both consumer relevance and provider/supply health; popularity-only channels can concentrate exposure dangerously.
- **Notifications:** Candidate volume is smaller and interruption cost is high, so precision and eligibility may dominate broad recall.

Representative transfer to video/feed:

* Invariant: Preserve complementary high-recall candidate coverage before ranking.
* Different data-generating process: Watch, skip, completion, and short-session sequence dominate over sparse purchases.
* Different objective: Immediate satisfaction plus longer-session/retention proxies.
* Different candidates/features: Fresh creators/content, sequence neighbors, embeddings, social graph.
* Different constraints: Freshness, diversity, creator caps, safety.
* Metric change: Watch/completion/session metrics plus candidate recall on fast-changing interests.
* Serving change: More real-time session-state retrieval and faster index refresh.
* Ecosystem effect: Over-concentration can suppress creator discovery and narrow content diversity.
* Validation: Session-intent slices, fresh-item coverage, creator distribution, online experiments.

#### 8. Objective and Metric Mismatch

Two failures must be separated. **Execution failure** means the retrieval portfolio did not correctly serve its intended candidates: stale index, wrong quota, timeout, version mismatch. **Objective mismatch** means it correctly optimized the chosen retrieval metric, but that metric did not represent product value.

For example, union Recall@1000 may improve by adding many popular items that are historically clicked, yet downstream conversion or satisfaction can fall because the new candidates crowd out fresh, diverse, high-value, or segment-specific items. High offline recall can also merely reproduce the historical exposure policy.

* Offline/model metric: Historical-positive Recall@1000 and per-source recall.
* Online/product outcome: Conversion, watch quality, satisfaction, retention, revenue, or other surface goal.
* Execution verification: Confirm source versions, quotas, candidate counts, latency, and exact candidate diffs.
* Metric semantics: Offline recall asks whether logged positives are present, not whether the new candidate mix improves decisions under a changed exposure policy.
* Blind spots: Exposure bias, diversity, novelty, value, delayed outcomes, cold/tail users/items.
* Missing product factor: Unique value of candidates to the downstream objective, not just historical positive recovery.
* Repair: Add slice metrics, marginal recall, downstream rerank replay, constraint/coverage metrics, and online experimentation.
* Trade-off: Broader or more diverse retrieval may slightly reduce historical-positive recall while improving true product outcomes.
* Online validation: A/B test portfolio/quota changes with source-level logging and guardrails.

## Material Follow-ups / Scenario Variants

### A source has the best standalone Recall@500. Should it get the largest quota?

Not necessarily. Standalone recall ignores overlap. If that source mostly retrieves items already found elsewhere, increasing its quota may add few unique relevant items while increasing latency and downstream ranking cost. Compare marginal recall curves as quota changes, segmented by user/item regime, and normalize by cost. Preserve sources that uniquely cover important slices even when their aggregate standalone recall is smaller.

### Collaborative sources collapse for new items. How should hybrid retrieval respond?

Route new items through content or metadata embeddings immediately, use segmented popularity/trending where appropriate, and reserve exploration capacity so the system can collect behavioral evidence. The downstream ranker should know item age/history sparsity so it does not systematically suppress these candidates. Evaluate new-item recall/exposure separately rather than letting head inventory dominate aggregate metrics.

### Why not train one learned embedding model and delete the hand-built channels?

A single learned model can simplify serving and may absorb several signals, but it creates correlated failure modes and may not match the strengths of specialized channels. Co-visitation can react faster to session intent, popularity is a robust fallback, content may cover brand-new items, and hand-built eligibility/graph relations can encode semantics the learned objective underweights. Remove a channel only after ablation shows low marginal value across important slices and after failure/freshness behavior is acceptable.

### Candidate count is fixed, but adding sources keeps underfilling after deduplication. What do you do?

Separate **requested count** from **unique post-dedup count**. Over-request from overlapping sources based on historical duplication rates, then run a fill policy from prioritized fallback channels until the unique target is reached or a deadline is hit. Monitor underfill by slice. Do not blindly increase all quotas because that can increase latency and preserve the same overlap pattern.
