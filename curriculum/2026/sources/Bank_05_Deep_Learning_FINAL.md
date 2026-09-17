# Bank 05 — Deep Learning & Optimization (FINAL)

**Status:** FINAL knowledge bank for the 25-week ML Interview Project.
**Final count:** 27 questions.

## Bank contract

- These are interview conversations, not flashcards.
- The main prompt is the scheduled unit; follow-ups do **not** count as separate roadmap questions.
- Coding owns implementation fluency; this bank owns explanation, derivation where appropriate, tradeoffs, failure analysis, and system connection.
- Preserve honest ownership: professional systems may be used only where supported by Project sources; independent portfolio implementations must be described as such.
- Canonical follow-ups listed in this bank are **question-specific**; generic boilerplate probes are not canonical requirements.
- Interviewers may still probe assumptions, failure modes, alternatives, or evaluation dynamically when the learner's answer exposes a meaningful gap.

## Final questions

### A1
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A1
**Prerequisites / cross-references:** B30/B31 before the full algorithmic account; Bank 01 A12 for matrix-shape derivation.  

**Q:** Explain backpropagation as an algorithm, not as a slogan. What is actually stored during the forward pass and why, what does the backward pass compute at each node, and why does training memory scale with batch size and depth in a way that inference memory does not?

### A2
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A2
**Prerequisites / cross-references:** A1/A3/A4 foundations.  

**Q:** Vanishing and exploding gradients — give the mechanism for each, then explain which of initialization, normalization, residual connections, gradient clipping, and activation choice addresses which problem. I want to know what each one does *not* fix.

### A3
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A3
**Prerequisites / cross-references:** B31 plus Bank 01 A17 for orthogonal initialization context.  

**Q:** Derive why initialization variance matters, and explain the difference between Xavier and He. Then tell me what happens with each of the two obvious wrong choices — all zeros, and standard normal with unit variance.

### A4
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A4

**Q:** Walk me through activation function choice. Why did ReLU displace sigmoid and tanh, what is the dead ReLU problem and how do the variants address it, and what does GELU do differently? Then say where sigmoid and tanh are still correct.

### A5
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A5; absorbs A6, B35
**Prerequisites / cross-references:** B31 and framework train/eval semantics; coding PT-02/PT-03 own implementation.  

**Q:** Compare BatchNorm, LayerNorm, and GroupNorm by the statistics they compute and their train/eval behavior. Then explain dropout, inference scaling, why dropout can interact poorly with BatchNorm, and the concrete bugs caused by incorrect train/eval state.

### A7
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A7

**Q:** How is regularizing a deep network different from regularizing a classical model? Cover the tools you actually reach for, and address the awkward fact that heavily over-parameterized networks generalize well despite fitting random labels.

### A8
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A8; absorbs A9
**Prerequisites / cross-references:** B30 and basic gradient-descent vocabulary.  

**Q:** Compare SGD, momentum, Adam, and AdamW. Explain Adam's moment estimates, when adaptivity helps or hurts, why L2 and weight decay diverge under Adam, and how decoupled weight decay changes the update.

### A10
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A10; absorbs B34
**Prerequisites / cross-references:** A8 and B30 before schedule/warmup trade-offs.  

**Q:** Why do transformers need learning-rate warmup? Explain the mechanism rather than citing the convention. Then cover schedule choice more generally, and tell me how the learning rate should change if you double the batch size.

### A11
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A11; absorbs A14

**Q:** Use Hessian eigenvalue signs to distinguish minima, maxima, and saddles; explain why saddles matter in high dimensions and discuss the sharp-versus-flat-minima/batch-size argument, including its limitations.

### A12
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A12

**Q:** I show you a training-loss curve. Walk me through what you would read off it in each of these cases: it plateaus immediately; it decreases then diverges to NaN; it oscillates without trending; it decreases smoothly while validation loss rises; it drops sharply at a fixed step. For each, what you conclude and what you check next.

### A13
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A13

**Q:** Why is cross-entropy computed from logits rather than from probabilities? Explain the log-sum-exp trick and what it prevents. Then tell me what else breaks numerically in mixed-precision training and how it is handled.

### A15
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A15

**Q:** Explain what a convolution layer actually computes and why it beats a fully-connected layer on images. Cover parameter counting, receptive field growth, and what stride and pooling each do. Then say what inductive bias you are buying and when it is wrong.

### A16
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A16

**Q:** Why do residual connections help? Give the gradient-flow argument precisely, then give the second argument about what the network is being asked to learn. Then explain why normalization placement relative to the residual branch matters.

### A17
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A17; absorbs A18
**Prerequisites / cross-references:** B33 plus A1; attention implementation is conceptual/derivational in the 2026 core and has no dedicated canonical coding ID.  

**Q:** Explain self-attention mechanically—Q, K, V, scaling, masking, and multi-head attention—then explain why positional information is required and compare learned, sinusoidal, and relative/rotary-style position schemes, including extrapolation beyond training length.

**Follow-up tree:**
- Derive the sequence-length complexity of standard self-attention in time and memory. What changes with causal versus padding masks, and what kinds of approximations or kernels can reduce the practical bottleneck without changing the basic attention objective?
### A19
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A19
**Prerequisites / cross-references:** A17 and B33; this is the architecture/compute companion.  

**Q:** Draw me the anatomy of one transformer block and account for where its parameters live. Then tell me which part dominates the compute at short sequence lengths and which dominates at long ones.

**Follow-up tree:**
- At inference time, explain KV caching: what is cached per layer, why it changes decode complexity, and how cache memory scales with batch size, sequence length, layers, heads, and precision.

### A20
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A20

**Q:** How do embedding layers work and what is different about training them? Cover initialization, tying, dimension choice, and what goes wrong with rare tokens or rare items.

### A21
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A21; absorbs A22

**Q:** Explain contrastive representation learning and the mechanics of two-tower training: positive-pair construction, in-batch negatives, temperature, normalization, collapse/false negatives, training versus serving, and what tower separation buys and costs.

### A23
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A23

**Q:** Your fraud system uses ResNet152 as a feature extractor. Walk me through the decision space — frozen features, linear probe, partial fine-tuning, full fine-tuning — and what determines the right choice. Then tell me what would make you fine-tune, and what would go wrong if you did it carelessly.

### A25
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A25

**Q:** Explain quantization and distillation as two different ways to make a model cheaper. For quantization, cover what actually gets quantized and what breaks. For distillation, explain why a student trained on a teacher's outputs can beat the same student trained on the original labels.

### A26
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A26
**Prerequisites / cross-references:** A19 plus Bank 08 A7/A18 for serving/latency context.  

**Q:** You serve ResNet152 on Triton. Take me through the arithmetic you would do before deploying a model — parameters, activation memory, FLOPs per image — and explain what actually determines throughput on a GPU. Then say what you would change to serve twice the traffic on the same hardware.

**Follow-up tree:**
- Separate prefill from autoregressive decode, then explain dynamic/continuous batching and why sequence-length heterogeneity can hurt GPU utilization and tail latency.

### A27
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A27

**Q:** A network is not training — the loss is flat or nonsense. Give me your diagnostic sequence for a deep learning model specifically, in order, and say what each step rules out. Assume the data pipeline is someone else's code.

### A28
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A28

**Q:** Explain what an LSTM's gates do and what problem they were solving. Then give a fair account of why attention displaced recurrence — including anything RNNs are still better at.

### B30
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B30

**Q:** Define epoch, batch, iteration, and step. Say how many steps are in one epoch given a dataset size and a batch size, and what changes if you use gradient accumulation.

### B31
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B31

**Q:** What happens in a forward pass versus a backward pass, and what is retained between them? One line on why that retention drives training memory.

### B32
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B32

**Q:** Distinguish pretraining, fine-tuning, feature extraction, and a linear probe. One sentence each, and say which ones modify the backbone's weights.

### B33
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B33

**Q:** State what softmax does and what cross-entropy measures, and say in one sentence why they are almost always paired.

### B36
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B36

**Q:** What is the embedding dimension and what is the tradeoff in choosing it? One line on what happens if it is far too small.

---

## Old → final disposition

- **A6 → FOLD/MERGE into A5.** Coverage is preserved in the final prompt/follow-ups.
- **A9 → FOLD/MERGE into A8.** Coverage is preserved in the final prompt/follow-ups.
- **A14 → FOLD/MERGE into A11.** Coverage is preserved in the final prompt/follow-ups.
- **A18 → FOLD/MERGE into A17.** Coverage is preserved in the final prompt/follow-ups.
- **A22 → FOLD/MERGE into A21.** Coverage is preserved in the final prompt/follow-ups.
- **A24 → DEFER/FOLD.** Not a standalone final question; the concept is covered by another bank, coding track, recognition depth, or target-role overlay.
- **A29 → DEFER/FOLD.** Not a standalone final question; the concept is covered by another bank, coding track, recognition depth, or target-role overlay.
- **B34 → FOLD/MERGE into A10.** Coverage is preserved in the final prompt/follow-ups.
- **B35 → FOLD/MERGE into A5.** Coverage is preserved in the final prompt/follow-ups.

## Final coverage rule

Mastering this bank means being able to answer the main prompts cold, handle any listed question-specific follow-ups, respond to reasonable gap-driven interviewer probes, and connect the concept to the relevant coding/project/system-design work. Exact wording may change in interviews; conceptual ownership should transfer.
