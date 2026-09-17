# Bank 01 — Linear Algebra for ML (FINAL)

**Status:** FINAL knowledge bank for the 25-week ML Interview Project.
**Final count:** 20 questions.

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

**Q:** You fit a linear regression on a marketing dataset. The model's R² is fine, but when you refit on bootstrap resamples the coefficients swing wildly in magnitude and several flip sign. A colleague suggests standardizing the features. Walk me through what is actually happening, whether standardizing will fix it, and what you would do.

### A2
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A2
**Prerequisites / cross-references:** B19, B20, B24; comfort with matrix-vector multiplication and singular/eigenvalue vocabulary.  

**Q:** Define the condition number of a matrix in terms of its singular values. Explain what it predicts about (a) how fast gradient descent converges on a least-squares objective and (b) how much numerical error you should expect when solving for the coefficients. Then explain why forming and inverting XᵀX is a worse idea than it looks.

### A3
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A3; absorbs B22
**Prerequisites / cross-references:** B19, B20, B23, B25; solve basic linear systems before the geometric derivation.  

**Q:** Explain least squares geometrically and algebraically: projection, normal equations, residual orthogonality, full-rank versus rank-deficient cases, no/one/many solutions of Ax=b, and what the pseudoinverse returns.

**Follow-up tree:**
- Compare the normal equations, QR factorization, and SVD as ways to solve least squares. Which would you choose for a well-conditioned full-rank matrix, an ill-conditioned matrix, and a rank-deficient matrix, and why?
### A5
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A5
**Prerequisites / cross-references:** A3 and A6; least-squares geometry plus SVD coordinates.  

**Q:** Rewrite ridge regression in the SVD coordinates of X. What does λ do to each direction of the feature space, and why does that explain both the stabilization and the bias ridge introduces? Then state what the sum of those per-direction factors represents.

### A6
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A6; absorbs A7
**Prerequisites / cross-references:** B24 and B19; eigenvalue/rank fundamentals before PCA/SVD derivations.  

**Q:** Compare eigendecomposition, SVD, and PCA as related spectral tools. State when each decomposition exists, the orthogonality guarantees, derive PCA from covariance and from the SVD of centered data, explain centering versus scaling, and identify a supervised-learning case where PCA can hurt.

### A8
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A8

**Q:** What does it mean for a matrix to be positive definite versus positive semi-definite, and how would you actually check in practice? Give me three matrices that show up in ML that are guaranteed PSD and explain why. What does it mean if your empirical covariance matrix comes back with a slightly negative eigenvalue?

### A9
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A9

**Q:** Compare the L1, L2, and L∞ unit balls geometrically, then explain why L1 regularization produces exactly zero coefficients while L2 does not. Give me the geometric argument first, then tell me what is happening to the penalty's derivative at zero that makes it possible.

### A11
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A11; absorbs A10, A18
**Prerequisites / cross-references:** A6; singular values and low-rank structure.  

**Q:** Explain truncated SVD and the Eckart–Young optimality result. Connect singular-spectrum shape to numerical rank, denoising, compression, latent-factor models, and embedding collapse; compare Frobenius, spectral, and nuclear norms and explain how you would choose a rank.

### A12
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A12
**Prerequisites / cross-references:** B20 and basic chain rule; Bank 05 A1 is the conceptual backprop companion.  

**Q:** Take a two-layer network: z₁ = W₁x + b₁, a₁ = φ(z₁), z₂ = W₂a₁ + b₂, scalar loss L. Derive the gradients with respect to W₁, W₂, b₁, and b₂. I care about the shapes and about *why* each transpose, each elementwise product, and each sum appears — not just the final expressions. Then tell me what happens to the weight gradient when you batch.

### A13
**Phase:** S1/G2  
**Depth:** D2  
**Source mapping:** A13

**Q:** Start from ‖u − v‖² = ‖u‖² + ‖v‖² − 2uᵀv. Use it to explain exactly when cosine similarity and Euclidean distance produce the same ranking, what goes wrong if you rank by raw inner product on unnormalized embeddings, and why approximate nearest-neighbor search still works in a space where distances are supposed to concentrate.

### A14
**Phase:** S1/G2  
**Depth:** D2  
**Source mapping:** A14; absorbs A26
**Prerequisites / cross-references:** A13; exact embedding geometry before ANN trade-offs.  

**Q:** In an embedding-retrieval system, reason through normalization, inner product versus L2, exact versus approximate search, IVF/HNSW/PQ-style tradeoffs, dimension reduction, reduced precision, and quantized codes. Explain what each choice does to memory, geometry, recall, latency, and rebuild needs.

### A15
**Phase:** S1/G2  
**Depth:** D2  
**Source mapping:** A15
**Prerequisites / cross-references:** A13 plus Bank 07 A21 for the probability view of banded LSH.  

**Q:** Your autocorrect pools candidates with Jaccard similarity over an LSH index. Explain what an LSH family preserves probabilistically and by what mechanism. Contrast MinHash for Jaccard with random-hyperplane/projection LSH for cosine. Then distinguish LSH collision guarantees from Johnson–Lindenstrauss random-projection guarantees rather than conflating them, and explain how MinHash band/row parameters convert a per-hash collision probability into the sharp threshold you actually want.

### A16
**Phase:** S1/G2  
**Depth:** D2  
**Source mapping:** A16
**Prerequisites / cross-references:** A6/A11 plus Bank 03 B23 for recommendation context.  

**Q:** Frame a user–item recommender as a low-rank factorization problem. What does the rank actually mean here, what does the span of the item factors tell you, and why does cold start appear as an identifiability/span problem in this factorization view rather than merely a shortage of global training data? Then say what breaks if you try to solve it with a literal SVD.

### A17
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A17
**Prerequisites / cross-references:** B23/B24 and Bank 05 A3 for initialization context.  

**Q:** What makes a matrix orthogonal, and what does an orthogonal transformation preserve? Use that to explain why orthogonal initialization helps deep networks, why L2 regularization is rotation-invariant while L1 is not, and what whitening does to the distances between your data points.

### B19
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B19

**Q:** Define span, linear independence, basis, and rank, and state how they relate. Why is row rank equal to column rank, and what is the rank of a product AB bounded by?

### B20
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B20

**Q:** Give me three different readings of the matrix product Ax, and explain the dummy-variable trap in terms of one of them.

### B21
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B21

**Q:** What do the trace and the determinant tell you about a matrix, and what does each fail to tell you? Where does log-determinant show up in ML?

### B23
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B23

**Q:** Define the dot product geometrically and algebraically. Derive the projection of one vector onto another, and state what a zero dot product does and does not imply.

### B24
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B24

**Q:** State the eigenvalue equation and what it means geometrically. What does the spectral theorem guarantee for symmetric matrices, and why does that guarantee matter so often in ML?

### B25
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B25

**Q:** Name the four fundamental subspaces of a matrix, state the rank-nullity theorem, and connect them to solving a linear system.

---

## Old → final disposition

- **A7 → FOLD/MERGE into A6.** Coverage is preserved in the final prompt/follow-ups.
- **A26 → FOLD/MERGE into A14.** Coverage is preserved in the final prompt/follow-ups.
- **A18 → FOLD/MERGE into A11.** Coverage is preserved in the final prompt/follow-ups.
- **B22 → FOLD/MERGE into A3.** Coverage is preserved in the final prompt/follow-ups.
- **A10 → FOLD/MERGE into A11.** Coverage is preserved in the final prompt/follow-ups.

## Final coverage rule

Mastering this bank means being able to answer the main prompts cold, handle any listed question-specific follow-ups, respond to reasonable gap-driven interviewer probes, and connect the concept to the relevant coding/project/system-design work. Exact wording may change in interviews; conceptual ownership should transfer.
