# Bank 07 — Probability & Inference (FINAL)

**Status:** FINAL knowledge bank for the 25-week ML Interview Project.
**Final count:** 24 questions.

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
**Prerequisites / cross-references:** B24-B28 for basic probability vocabulary and Bayes/base rates.  

**Q:** A test flags fraud with 95% sensitivity and 2% false-positive rate. Explain, using likelihood ratios rather than by recomputing a confusion matrix, why the same test is informative at one prevalence and nearly useless at another. Then tell me what would have to change to make a positive flag actionable at 0.5% prevalence.

### A2
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A2
**Prerequisites / cross-references:** B25/B26/B30 before dependence/conditioning subtleties.  

**Q:** Distinguish independence, uncorrelatedness, and conditional independence. Give an example of variables that are uncorrelated but dependent, and an example where conditioning creates dependence that was not there before. Then say why this matters for a model.

### A3
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A3; absorbs A4
**Prerequisites / cross-references:** B24-B28 plus Core ML A10/A11 for likelihood/loss context.  

**Q:** Connect likelihood, loss, MAP, and regularization. Derive squared error and cross-entropy from likelihood assumptions, show how common priors induce common penalties, explain what MAP omits relative to full Bayesian inference, and identify cases where the loss↔likelihood correspondence breaks.

### A5
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A5
**Prerequisites / cross-references:** B27/B28 before conjugacy; Bank 03 A12 is the product application.  

**Q:** Derive the Beta-Binomial conjugate update, then explain precisely why it makes Thompson sampling cheap. Say what the Beta's parameters mean, what happens as data accumulates, and what breaks if the reward is not Bernoulli.

### A6
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A6; absorbs A19
**Prerequisites / cross-references:** B25/B29/B30 before CLT/bootstrap/permutation distinctions.  

**Q:** State the CLT precisely and distinguish it from the law of large numbers. Explain the bootstrap and permutation test, why each works, where each fails, and when you would choose a parametric test, bootstrap, or randomization test.

**Follow-up tree:**
- Derive the one-sample and two-sample z/t test statistics at interview depth. When is a z-test justified, when do you use a t-test, what changes with paired versus independent samples, what determines the degrees of freedom, and how do the assumptions connect to the confidence interval?
### A7
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A7; absorbs A18, B31
**Prerequisites / cross-references:** B25/B29/B30 plus A17 for interval interpretation.  

**Q:** Design an experiment: sample size, power, duration, Type I/II errors, confidence intervals, and optional stopping. Then explain what changes when SUTVA fails because users/items/markets interfere, including cluster randomization and switchback designs.

**Follow-up tree:**
- What changes when you test many metrics, variants, or segments? Distinguish family-wise error rate from false discovery rate, and explain when you would use Bonferroni/Holm versus Benjamini-Hochberg rather than treating every p-value independently.
### A8
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A8

**Q:** Explain CUPED. What is it doing statistically, why does it not bias the estimate, and what determines how much it buys? Then name other variance-reduction techniques and say when each applies.

### A11
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A11
**Prerequisites / cross-references:** B25/B26 before the conditional-expectation proof.  

**Q:** Prove that the conditional expectation minimizes expected squared error. Then tell me what the analogous minimizer is for absolute error, and explain why this result is the foundation of regression.

### A12
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A12
**Prerequisites / cross-references:** B24-B26 plus Core ML/Deep Learning cross-entropy context.  

**Q:** Define entropy, cross-entropy, and KL divergence, and state exactly how they relate. Then explain how you would use KL or a related divergence to detect drift, and what its limitations are for that purpose.

### A13
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A13

**Q:** Explain Simpson's paradox with a concrete example, and say what is actually happening in causal terms. Then tell me how you would guard against it when reporting an experiment or a model comparison.

### A14
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A14

**Q:** You are streaming records of unknown total length and must keep a uniform random sample of k of them using O(k) memory. Give the algorithm and prove that every record ends up in the sample with equal probability.

### A15
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A15; absorbs A16

**Q:** Define estimator bias, variance, consistency, and efficiency, then compare MLE with method of moments. Give examples where a biased estimator is preferable and where MoM is attractive despite lower efficiency.

### A17
**Phase:** G1  
**Depth:** D3  
**Source mapping:** A17
**Prerequisites / cross-references:** B24-B30 basic inference vocabulary.  

**Q:** State what a 95% confidence interval means, precisely. Then tell me the three interpretations people commonly give that are wrong, and explain how a Bayesian credible interval differs.

### A20
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A20

**Q:** What is heteroscedasticity, how would you detect it, and what does it break? Be specific about what remains valid and what does not.

### A21
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A21

**Q:** Your autocorrect pools candidates with an LSH index over Jaccard similarity. Derive the collision probability for a banded LSH scheme and explain how the band and row parameters shape the S-curve. Then tell me how you would choose them for a sub-10ms latency budget.

### A22
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A22

**Q:** For a multivariate Gaussian, state what the conditional distribution of one block given another looks like, and explain why the result is remarkable. Then connect it to something you would actually build.

### A23
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A23

**Q:** *(Drill instruction: this question is not answered in depth. The task is to state, for each topic below, what it is in one sentence and where it would apply — then explicitly say that you have not prepared the derivation. Practicing that boundary aloud is the point.)* Give me a one-line account of each of the following and say where it would come up: instrumental variables; difference-in-differences; DAGs and d-separation; order statistics and the winner's curse; overdispersion and count models; memorylessness and hazard rates; Jensen's inequality; importance sampling; inverse transform sampling; and the measure-theoretic foundations of probability.

### B24
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B24

**Q:** Define a sample space and a random variable, then distinguish a PMF, a PDF, and a CDF. Say one thing a PDF is not.

### B25
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B25

**Q:** Define expectation and variance. State linearity of expectation, and say whether it requires independence.

### B26
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B26

**Q:** Distinguish joint, marginal, and conditional distributions, and state the chain rule. Then say which direction — forward or inverse — a probability question versus a statistics question is running.

### B27
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B27

**Q:** State Bayes' theorem and name each of the four terms. Then state it in odds form.

### B28
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B28

**Q:** Name the standard distributions — Bernoulli, binomial, Poisson, exponential, normal, uniform — with their means and variances, and say in one phrase what generative story each comes from.

### B29
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B29

**Q:** Distinguish the law of large numbers from the central limit theorem. Say what each one is about, and what CLT requires.

### B30
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B30

**Q:** Distinguish covariance from correlation, and standard error from standard deviation. For the second pair, say which one shrinks with sample size and why.

---

## Old → final disposition

- **A4 → FOLD/MERGE into A3.** Coverage is preserved in the final prompt/follow-ups.
- **A9 → DEFER/FOLD.** Not a standalone final question; the concept is covered by another bank, coding track, recognition depth, or target-role overlay.
- **A10 → DEFER/FOLD.** Not a standalone final question; the concept is covered by another bank, coding track, recognition depth, or target-role overlay.
- **A16 → FOLD/MERGE into A15.** Coverage is preserved in the final prompt/follow-ups.
- **A18 → FOLD/MERGE into A7.** Coverage is preserved in the final prompt/follow-ups.
- **A19 → FOLD/MERGE into A6.** Coverage is preserved in the final prompt/follow-ups.
- **B31 → FOLD/MERGE into A7.** Coverage is preserved in the final prompt/follow-ups.

## Final coverage rule

Mastering this bank means being able to answer the main prompts cold, handle any listed question-specific follow-ups, respond to reasonable gap-driven interviewer probes, and connect the concept to the relevant coding/project/system-design work. Exact wording may change in interviews; conceptual ownership should transfer.
