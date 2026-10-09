---
type: interview-answer
item: "2027:S17"
title: "Approximate Nearest Neighbor Index Design"
created: "2026-10-09"
updated: "2026-10-09"
tags:
  - approximate-nearest-neighbor
  - vector-search
  - hnsw
  - ivf
  - product-quantization
---

## Canonical Staff-Depth Question

Compare graph, inverted-file, quantized, and partitioned ANN families on recall, memory, build, update/delete, filtering, hardware, and latency.

## Mastery Answer

I would start by separating the ANN problem into three decisions: **how the search space is pruned, how vectors are stored, and how the system is operated**. There is no universally best ANN index. The right choice depends on corpus size, dimensionality, memory budget, query rate, update/delete rate, filter selectivity, hardware, and the recall-versus-tail-latency target.

**Graph ANN, especially HNSW**, builds a navigable proximity graph. At query time, search walks from coarse long-range links toward increasingly local neighbors. Its main strength is a strong recall/latency trade-off with relatively little tuning, especially for in-memory serving. The cost is memory: besides the vectors, the graph stores neighbor links and allocator/object overhead. Builds can be expensive, and deletes usually require tombstones or background rebuild/repair. Inserts are comparatively natural, but sustained churn can degrade graph quality. Filtering is awkward because graph connectivity was built without necessarily respecting the filter; naive post-filtering can destroy recall, while filter-aware traversal adds complexity.

**IVF-style indexes** first partition the vector space into coarse cells, usually by k-means centroids. A query probes only the closest `nprobe` cells rather than the whole corpus. This gives an explicit knob: more probed cells usually increase recall and latency together. IVF tends to be compact and hardware-friendly because work becomes large contiguous scans over selected posting lists. It is often attractive at very large scale or on accelerators. However, quality depends on the partition: skewed cells, boundary effects, and poor coarse quantization can hurt recall. Inserts are straightforward if the appropriate cell is known; deletes still need bookkeeping or compaction.

**PQ and OPQ are primarily compression mechanisms rather than independent candidate-partitioning strategies.** Product quantization splits a vector into subspaces and stores a small codeword index per subspace; approximate distances are computed from lookup tables. OPQ learns a rotation before PQ so the subspaces are easier to quantize. PQ dramatically reduces RAM and memory bandwidth, which can improve throughput, but introduces distance error and therefore recall loss. In practice it is often combined with IVF, as in IVF-PQ, or used as a compressed representation inside another retrieval design.

**Partitioned ANN** is the broader strategy of routing each query to only a subset of shards, clusters, leaves, or partitions, possibly with replication around boundaries. It can scale beyond one machine and reduce search work, but routing mistakes impose a hard recall ceiling: an excellent local search cannot recover a true neighbor placed in an unsearched partition. Partition balance, replication, and cross-partition merging therefore become first-class concerns.

I would choose by first defining the target—for example Recall@10 at p99 under a fixed RAM budget—then benchmark exact search as the gold standard. I would sweep HNSW parameters such as `efSearch`, IVF parameters such as `nlist` and `nprobe`, and compression level for PQ/OPQ. I would measure recall, p50/p95/p99 latency, QPS, index RAM, build time, insert/delete throughput, filtered-query behavior, and rebuild cost on realistic query and filter slices.

The decision is operational as much as algorithmic. If memory is ample and updates are moderate, HNSW is often a strong default. If the corpus is huge, hardware favors batched scans, or memory must be compressed, IVF or IVF-PQ becomes more attractive. If the corpus must be distributed, explicit partitioning may be necessary. The final answer should be the cheapest design that satisfies the required recall and tail-latency SLO with acceptable freshness and operational complexity.

## Learn the Concepts

### Foundation

The core problem is **nearest-neighbor search**. Suppose every document or item is represented by a vector such as

$$
x \in \mathbb{R}^d.
$$

Given a query vector $q$, exact nearest-neighbor search asks for the vectors with the smallest distance to $q$, or equivalently the largest similarity. Common choices are Euclidean distance, cosine similarity, or inner product.

If there are $N$ vectors, the simplest exact algorithm compares the query with all $N$ vectors. For dense $d$-dimensional vectors, this costs roughly $O(Nd)$ arithmetic per query. That can be perfectly acceptable for small corpora, but at tens or hundreds of millions of vectors it is often too expensive for a tight latency budget.

**Approximate nearest-neighbor (ANN) search** deliberately avoids examining the entire corpus. It accepts a controlled probability of missing some true nearest neighbors in exchange for lower latency, lower compute, or lower memory.

Three beginner concepts matter immediately:

- **Recall@k:** among the true exact top-$k$ neighbors, what fraction did ANN return?
- **Candidate pruning:** what mechanism prevents the query from examining most vectors?
- **Distance approximation/compression:** are the distances computed against exact vectors or compressed approximations?

A crucial distinction is that these are different levers. HNSW is mainly a **search-space navigation** method. IVF is mainly a **coarse partition/pruning** method. PQ is mainly a **vector compression and approximate-distance** method. They can be combined.

A concrete example: suppose there are 100 million vectors, each with 768 float32 dimensions. Raw vector storage alone is

$$
100{,}000{,}000 \times 768 \times 4 \approx 307.2\text{ GB}.
$$

That excludes index metadata and replicas. Exact scanning of all 100 million vectors per query is not plausible for a low-latency online service. An ANN design must therefore reduce either the number of vectors visited, the bytes read per vector, or both.

For intuition, imagine a large city:

- **HNSW** builds a road network with expressways and local streets. Search navigates through the network toward the destination.
- **IVF** divides the city into neighborhoods. Search first chooses likely neighborhoods, then searches only inside them.
- **PQ** replaces full addresses with compact codes that are cheaper to store and compare.
- **Partitioned search** assigns regions to different machines or routing units and searches only selected partitions.

Important beginner distinctions:

1. **ANN recall is not model recall.** Here recall means agreement with exact nearest-neighbor results, not relevance-label recall.
2. **PQ is not the same thing as IVF.** IVF prunes candidate regions; PQ compresses vectors. IVF-PQ uses both.
3. **Fast average latency is not enough.** Production design normally cares about p95 or p99 because tail latency controls user-visible SLOs.
4. **A smaller index is not automatically faster.** Compression can reduce memory bandwidth but may add decoding/table-lookup work or hurt recall enough to require probing more candidates.
5. **Updates and deletes are part of the design.** A benchmark on a static snapshot is incomplete for a changing corpus.

### Core Interview Reasoning

A strong answer can be reconstructed with:

`workload → pruning mechanism → memory representation → operations → filtering → hardware → benchmark → decision`

**1. Define the workload.** Establish $N$, dimension $d$, metric, QPS, required Recall@$k$, p99 latency, memory budget, update/delete rate, filter selectivity, and whether the index must fit on one machine.

**2. Explain how each family avoids full search.**

- **HNSW:** graph traversal. Connectivity lets search move toward promising regions without scanning everything.
- **IVF:** coarse clustering. Search only selected posting lists.
- **PQ/OPQ:** compact codes and approximate distance. The main savings are RAM and memory bandwidth.
- **Partitioned search:** route the query to only part of the corpus, often across machines or partitions.

**3. Compare the operational trade-offs.**

HNSW typically offers excellent recall at low latency but uses substantial RAM and has nontrivial build/rebuild costs. IVF gives direct control over how much of the corpus is scanned and maps well to batched/vectorized hardware. PQ lowers storage and bandwidth at the cost of approximation error. Partitioning enables scale-out but creates routing, balance, replication, and global top-$k$ merge concerns.

**4. Treat filtering as a first-class requirement.**

A metadata filter such as `country=US AND category=shoes` can invalidate a benchmark that looked excellent without filters. With post-filtering, ANN may return many candidates that are later discarded. If the eligible set is small, recall can collapse. Alternatives include pre-partitioning, filter-aware indexes, bitmap-assisted search, graph-aware filtering, or falling back to another path for highly selective queries.

**5. Match the algorithm to hardware.**

Graph traversal is irregular and pointer-heavy, which often favors CPU memory-resident workloads. IVF and PQ can turn search into regular bulk scans and table lookups, which often vectorize and batch well and can map effectively to SIMD/GPU-style execution. The answer should not reduce this to “HNSW for CPU, IVF for GPU”; implementation, batch size, dimensionality, and memory hierarchy matter.

**6. Benchmark against exact top-$k$.**

Exact retrieval provides the correctness reference. For each ANN configuration, plot or tabulate:

- Recall@$k$ versus p95/p99 latency;
- QPS at the target recall;
- index bytes per vector / total RAM;
- build time;
- insert throughput;
- delete behavior and compaction/rebuild cost;
- filtered-query recall and latency by selectivity;
- performance under realistic concurrency and hardware.

The interview decision is not “which algorithm wins?” It is “which point on the measured quality-resource-operability frontier satisfies the product constraints?”

### Deeper Reasoning and Derivations

**Why exact search is expensive.** For $N$ vectors of dimension $d$, brute-force search is approximately $O(Nd)$. If vectors are float32, merely reading them costs roughly

$$
4Nd \text{ bytes/query}.
$$

For large $N$, memory bandwidth alone can dominate even when dot products are highly optimized.

**HNSW mechanism.** HNSW stores multiple graph layers. Upper layers contain fewer nodes and provide long-range navigation; the bottom layer is dense and local. Construction incrementally inserts nodes and chooses neighbors. Query search begins at a high layer, greedily improves the current location, then descends. At the bottom layer it maintains a candidate frontier rather than following a single greedy path.

Two important knobs are commonly discussed:

- `M`: approximate number of graph connections per node. Larger values increase memory/build cost and often improve navigability/recall.
- `efSearch`: size of the query-time exploration frontier. Larger values usually increase recall and latency.

The key causal chain is

`more graph connectivity or exploration → more candidate states visited → higher probability of reaching the true neighborhood → higher recall, but more memory/latency`.

HNSW does not have a clean worst-case sublinear guarantee in the way an interview whiteboard might tempt one to claim. Its strength is empirical navigability on many real embedding distributions.

**IVF mechanism.** Let coarse centroids be $c_1,\dots,c_K$. Each database vector is assigned to a coarse cell, often

$$
a(x)=\arg\min_j \|x-c_j\|^2.
$$

At query time, the system finds the closest `nprobe` centroids and searches only those posting lists. If `nprobe = K`, IVF degenerates toward exhaustive search over all cells. If `nprobe` is very small, latency is low but boundary neighbors may be missed.

A rough expected scan size under balanced cells is

$$
N_{\text{scan}} \approx N\frac{\text{nprobe}}{K}.
$$

Real cells are not perfectly balanced, so measured list-size distribution matters. Increasing `nlist` makes cells finer, but too many cells can increase routing/build overhead and leave sparse or skewed lists.

**PQ mechanism.** Suppose $d$ dimensions are split into $m$ sub-vectors. Each subspace has a codebook of $K_c$ centroids. A vector is represented by the index of one centroid per subspace. With 256 codewords per subspace, each sub-code fits in 8 bits, so a vector can be stored in roughly $m$ bytes rather than $4d$ bytes, excluding metadata.

For query $q=(q_1,\dots,q_m)$ and code $(i_1,\dots,i_m)$, approximate squared distance can be written as

$$
\hat d(q,x)
=
\sum_{j=1}^{m}
\|q_j-c_{j,i_j}\|^2.
$$

The query can precompute the table of distances from each $q_j$ to every centroid in subspace $j$, after which each candidate distance becomes a sum of table lookups. This is the idea behind asymmetric distance computation: the query remains uncompressed while database vectors are quantized.

The error arises because each original sub-vector $x_j$ is replaced by its centroid $c_{j,i_j}$. OPQ learns a rotation $R$ before applying PQ so that the subspaces are more quantization-friendly:

$$
x' = Rx.
$$

The goal is lower reconstruction/distance error for the same code budget.

**Why combinations matter.** IVF-PQ uses IVF to reduce how many vectors are considered and PQ to reduce bytes per considered vector. These attack different cost terms. A common pattern is coarse retrieval with compressed codes followed by exact or higher-precision reranking of a smaller candidate set.

**Partitioned search and the routing ceiling.** Suppose the true neighbor lives in partition $P^*$ but routing sends the query only to partitions $P_1,\dots,P_r$. If $P^*$ is excluded, no local ANN algorithm can recover that neighbor. Therefore total recall can be factored conceptually into

$$
P(\text{retrieve true neighbor})
\approx
P(\text{route to containing region})
\times
P(\text{local ANN finds it}\mid\text{correct region searched}).
$$

This is why partition recall must be measured separately from local-index recall.

**Deletes and churn.** In a static benchmark, index quality can look excellent. In production:

- HNSW may use tombstones or logical deletion; too many stale nodes waste memory/search work and can require rebuild.
- IVF can remove identifiers from posting lists, but fragmentation and compaction still matter.
- PQ-coded entries are easy to append or replace, but codebooks may become stale if the embedding distribution shifts.
- distributed partitioning must coordinate ownership and versions across shards.

So “supports insertion” is not the same as “supports high-churn production updates gracefully.”

### Advanced Staff-Depth Considerations

The universal Staff loop is:

`Baseline → Change → Mechanism → Measure → Act → Trade-off → Validate`

or, compressed:

`Assumption → Mechanism → Evidence → Decision → Trade-off → Validation`

For S17, the baseline is a corpus, vector distribution, index configuration, traffic profile, quality target, latency SLO, and memory budget. A changed constraint—more vectors, tighter RAM, selective filters, higher update rate, new hardware—affects a specific pruning or storage mechanism. The correct response is to localize which part of the ANN pipeline became limiting, measure the relevant quality/resource frontier, then change the index or its parameters and validate on realistic slices.

#### 1. Changed Constraints and Transfer Logic

ANN choices are conditional on the workload. The most important invariant is usually not the index family itself but the externally required contract: a target recall at an acceptable p99 latency, freshness, and cost.

A memory-rich, mostly static corpus may favor HNSW. If the corpus grows until graph-plus-vector RAM no longer fits economically, the constraint breaks the in-memory assumption. The redesign may introduce PQ, IVF-PQ, SSD/disk tiers, or explicit partitioning. If update rate becomes dominant, a design that was ideal for static recall may become operationally poor because rebuild and tombstone costs dominate.

- **Original assumption:** 50M vectors fit in RAM with HNSW plus replicas.
- **Changed constraint:** corpus grows to 300M vectors under a fixed RAM budget.
- **Invariant:** maintain the required Recall@10 and p99 search SLO.
- **Broken assumption:** full-precision vectors plus graph edges no longer fit economically.
- **Consequence:** memory pressure reduces replication headroom and may cause paging or force fewer replicas.
- **Design change:** benchmark IVF-PQ or partitioned HNSW/PQ tiers, potentially reranking a compressed candidate set with full-precision vectors.
- **Metric impact:** expect some ANN recall loss unless probe/search depth rises.
- **Trade-off:** lower RAM per vector versus extra approximation, tuning, and rebuild complexity.
- **Validation:** compare recall-latency-memory curves and failure behavior at production concurrency.

#### 2. Failure Modes and Diagnosis

ANN failures should be decomposed by stage:

`query embedding → routing/partition → ANN traversal/probing → candidate merge → filtering → rerank → response`

Common signatures differ. If exact top-$k$ using the same embeddings is also bad, the problem is likely representation/model-side, not ANN. If exact top-$k$ is stable but ANN recall drops, investigate index/version/configuration. If only filtered queries fail, inspect selectivity and filter execution. If recall is fine but p99 worsens, inspect visited-node counts, probed-list sizes, cache locality, shard skew, and concurrency.

- **Symptom:** production Recall@10 drops after an embedding-model rollout while exact top-$k$ remains healthy.
- **Stage decomposition:** embedding generation → index build/version → ANN search → merge.
- **Slices:** model version, index version, corpus shard, query cohort, vector norm.
- **Competing hypotheses:** mixed model/index versions; bad ANN parameters; corrupted or stale index; vector normalization mismatch.
- **Discriminating evidence:** exact-vs-ANN recall by version pair and replay against the prior index.
- **Offline/online comparison:** reproduce production queries against exact search and each candidate index.
- **Replay/isolation:** hold query vectors fixed and swap only index versions/configuration.
- **First divergence:** identify the first stage where candidate overlap with exact top-$k$ changes.
- **Immediate mitigation:** roll back to a compatible model/index pair.
- **Permanent prevention:** atomic version contracts plus pre-deploy exact-vs-ANN recall gates.

#### 3. Latency and Resource Trade-offs

ANN latency is dominated by work performed and bytes moved. HNSW spends work on irregular graph traversal and visited-set/frontier maintenance. IVF spends work selecting cells and scanning their contents. PQ reduces bytes but introduces approximate distance-table operations. Distributed partitioning adds routing, network, and merge costs.

Quality knobs usually have monotonic cost tendencies: higher `efSearch`, higher `nprobe`, more partitions, or more reranking candidates usually improve recall but increase latency or compute.

- **Budget:** p99 ANN retrieval below 25 ms.
- **Cost decomposition:** query preprocessing + routing + ANN search + cross-shard merge + filtering.
- **Dominant cost:** candidate exploration / memory access in the ANN stage.
- **Quality driver:** number and quality of explored graph nodes or probed cells.
- **Cost driver:** bytes touched and candidates evaluated.
- **Optimization knobs:** `efSearch`, `nprobe`, compression level, partition count, batch size, caching, candidate cap.
- **Fallback/degradation:** lower exploration budget or use a simpler cached/popular path under overload.
- **Trade-off curve:** Recall@k versus p99 latency and bytes/query.
- **Decision:** choose the lowest-cost configuration that clears the recall contract with headroom.

#### 4. Scale and Capacity

As $N$ grows, raw vector memory, metadata, replicas, build duration, and recovery time all grow. The first bottleneck may be RAM rather than arithmetic. Later, index build time, shard fan-out, network merge cost, or recovery time can dominate.

Scale also changes the meaning of “simple.” A single HNSW index may be operationally easy at 10M vectors but difficult at 1B vectors because replication, rebuilds, and failure domains become large. Partitioning reduces local index size but introduces routing recall and cross-partition coordination.

- **Scaling dimension:** vector count from 20M to 500M.
- **Baseline scale assumption:** single-node or few-shard in-memory ANN.
- **First bottleneck:** index-plus-vector RAM and replica cost.
- **Second-order effects:** longer rebuilds, more shards, tail amplification, recovery time, cross-shard merge.
- **Architectural response:** shard/partition the corpus and introduce compression where justified.
- **Partitioning/replication/caching/batching:** route to a bounded set of partitions; replicate hot partitions; batch compatible queries.
- **Consistency/freshness consequence:** updates must reach the correct shard/index version.
- **Operational failure mode:** one stale or overloaded shard causes recall gaps or tail spikes.
- **Validation:** capacity/load tests with realistic shard skew and failure injection.

#### 5. Freshness, State, and Versioning

ANN indexes are stateful artifacts. The serving contract must identify which embedding model, preprocessing/normalization version, codebook or centroid version, and index snapshot belong together.

Freshness strategy depends on churn. Common patterns include a stable base index plus a small delta index, periodic compaction/rebuild, tombstones for deletes, and shadow-building a replacement index before atomic cutover. PQ/IVF centroids and codebooks can themselves become stale when the embedding distribution changes.

- **State:** embedding model version + transform/normalization + coarse centroids + PQ/OPQ codebooks + index snapshot.
- **Freshness target:** new/updated items searchable within a defined delay.
- **Update path:** incremental insert into a delta or mutable index.
- **Delete path:** tombstone immediately, compact/rebuild later.
- **Version invariant:** queries and database vectors must use compatible embedding/metric/index semantics.
- **Cutover:** validate a shadow index, then switch model/index pointers atomically.
- **Rollback:** retain the prior compatible index long enough to reverse safely.
- **Validation:** freshness lag, stale-item rate, exact-vs-ANN recall, and version-skew alarms.

#### 6. Implementation, Serving, and Observability

A production ANN service should expose enough telemetry to explain both quality and systems behavior. Useful metrics include p50/p95/p99 latency, QPS, timeout rate, candidates visited, HNSW hops/frontier work, IVF cells probed, posting-list sizes, filter selectivity, index RAM, cache hit rate, update lag, tombstone ratio, build duration, and index/model version.

Quality observability needs sampled exact-search comparison because service latency alone cannot detect silent ANN recall degradation.

- **Serving contract:** query vector + metric + filter + top-$k$ + compatible index version.
- **Quality telemetry:** sampled Recall@$k$ against exact or high-effort reference search.
- **System telemetry:** latency distributions, candidates examined, bytes/index memory, shard utilization.
- **Update telemetry:** ingestion lag, tombstones, failed inserts, rebuild progress.
- **Version telemetry:** model/index/codebook/centroid IDs on every request or trace.
- **Safety gate:** block deployment if exact-vs-ANN recall or critical filtered slices regress beyond threshold.
- **Debug primitive:** deterministic replay of captured query vectors against multiple index snapshots.

#### 7. Vertical Transfer

The ANN mechanics transfer across product search, media search, local search, enterprise search, and recommendation, but the constraints change.

E-commerce may need strict inventory/category filters and rapid catalog updates. Media search may prioritize freshness and multimodal embeddings. Local search combines ANN with geography and can have highly selective spatial filters. Enterprise search may require ACL filtering, where unauthorized candidates must never leak. Recommendation may update item embeddings frequently and care about personalized query vectors at high QPS.

- **Vertical:** enterprise document search.
- **Changed requirement:** every result must satisfy document ACLs.
- **ANN implication:** post-filtering can waste candidates and create recall collapse for users with narrow access.
- **Design response:** ACL-aware partitioning/bitmaps/filter-aware traversal or a fallback path for highly selective access sets.
- **Invariant:** security correctness is non-negotiable even if relevance falls.
- **Evaluation:** recall/latency by ACL selectivity plus explicit no-leak security tests.
- **Trade-off:** more index/filter complexity for guaranteed authorization semantics.

#### 8. Objective and Metric Mismatch

ANN optimization can fail when the metric being tuned does not match product needs. Maximizing aggregate Recall@100 may hide poor exact-ID queries, filtered cohorts, new documents, long-tail semantic queries, or p99 overload. Likewise, ANN recall against embedding-space exact neighbors says nothing by itself about human relevance if the embedding model is wrong.

The hierarchy is:

`representation quality → exact-neighbor quality → ANN fidelity to exact neighbors → downstream ranking/relevance → product outcome`

Each level needs its own metric.

- **Index objective:** reproduce exact top-$k$ neighbors cheaply.
- **Possible mismatch:** aggregate Recall@10 is high, but a selective-filter segment has very low usable-candidate recall.
- **Evidence:** exact-vs-ANN recall sliced by filter selectivity, query class, corpus shard, and freshness.
- **Decision:** tune or route the problematic slice separately rather than over-optimizing the aggregate.
- **Trade-off:** more routing/index complexity for robust slice behavior.
- **Validation:** maintain both ANN fidelity metrics and downstream relevance/product metrics.

## Material Follow-ups / Scenario Variants

### Choosing among families under a concrete workload

For a **moderate-to-large in-memory corpus with high recall requirements, low-to-moderate churn, and enough RAM**, HNSW is often the first benchmark because it commonly gives a strong recall/latency frontier and simple query-time tuning through exploration depth.

For a **very large corpus with strict memory pressure or hardware that benefits from regular batched scans**, benchmark IVF and IVF-PQ. Tune the coarse partition count and probe count, then choose whether compression is necessary. If compressed retrieval loses too much quality, rerank the top candidates with full-precision vectors.

For a **corpus too large for a single failure domain**, use explicit sharding or partitioning. Measure routing recall separately from local ANN recall, and replicate boundary or high-demand regions only when the gain justifies memory and update complexity.

### Filters become highly selective

When a filter leaves only a tiny eligible subset, post-filtering ANN candidates can fail badly because most retrieved neighbors are discarded. The response depends on the workload: prefilter into a smaller eligible candidate universe, maintain filter-aware partitions or bitmaps, use filter-aware graph traversal, or switch to an exact/alternate path when the eligible set is already small enough. The correct benchmark is recall and p99 latency *conditioned on filter selectivity*, not aggregate ANN recall.

### Update rate rises sharply

A design built for a mostly static corpus may become dominated by update cost. HNSW can absorb inserts but sustained churn, tombstones, and deletes can require rebuild/repair. IVF-style indexes can append to lists but need balancing and compaction. PQ/OPQ codebooks may become stale if the vector distribution shifts. A common production pattern is a stable base index plus a mutable delta index, queried in parallel, with periodic rebuild and atomic versioned cutover.

### Memory budget is cut in half

First quantify bytes per vector rather than immediately changing algorithms. If graph edges dominate, reduce graph degree or move toward IVF/partitioned retrieval. If full-precision vectors dominate, introduce scalar/int8 compression or PQ/OPQ and rerank a smaller candidate set at higher precision. Re-benchmark the complete frontier because compression may lower memory bandwidth enough to improve latency even while requiring more candidates to preserve recall.

### GPU becomes available

GPU availability does not automatically imply one ANN family. Regular, batched arithmetic and contiguous scans often benefit more than pointer-heavy graph walks. IVF/PQ-style search can map well to accelerator throughput, especially at high batch sizes. But for low batch, strict single-query latency, or moderate corpus size, CPU HNSW may still win operationally. Benchmark on the actual concurrency and batch regime.

### How to benchmark properly

1. Build a reproducible exact top-$k$ reference over a representative corpus/query set.
2. Hold embeddings, metric, preprocessing, and hardware constant while comparing index families.
3. Sweep each family's quality-cost knobs rather than comparing one arbitrary configuration.
4. Measure Recall@$k$, p50/p95/p99 latency, QPS, memory, build time, update/delete behavior, and filter slices.
5. Test realistic concurrency and warm/cold-cache conditions.
6. Include corpus skew, long-tail queries, selective filters, and recent items.
7. Repeat after incremental updates to detect degradation over time.
8. Select the configuration on the Pareto frontier that satisfies the production SLOs with operational headroom.
