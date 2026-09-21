# Bank 02 — Core Machine Learning (FINAL)

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

### A1 — Learning Curves and Bias–Variance Diagnosis
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A1

**Q:** You train a gradient-boosted model and plot train and validation loss against the number of trees. Training loss falls steadily; validation loss falls, flattens, then slowly rises. A colleague says "it's overfitting, add regularization." Tell me what the curve is actually showing, what a *different* curve would have told you instead, and what each of the three obvious fixes — more data, fewer trees, stronger regularization — does to bias and to variance separately.

### A2 — L1, L2, and Elastic Net Regularization
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A2

**Q:** Explain why L1 regularization drives coefficients to exactly zero and L2 does not. Give both the geometric account and the optimization account. Then tell me what each does to the bias–variance tradeoff, what each does to the conditioning of the problem, and when elastic net is solving a problem that neither one alone solves.

### A3 — Cross-Validation Failure Modes
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A3

**Q:** Your 5-fold cross-validated AUC is 0.91. In production the model scores 0.72. Nothing about the code changed. Walk me through the ways cross-validation can produce a number that high and be wrong, in the order you would actually check them, and tell me what the correct validation scheme would have been in each case.

### A4 — High-Cardinality Categorical Encoding
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A4

**Q:** You have a categorical feature with 40,000 levels. One-hot encoding it blows up the feature space. A teammate proposes target encoding. Explain what target encoding does, exactly how it leaks, how the standard fixes work and what they cost, and what you would consider instead.

### A5 — Metrics for Severe Class Imbalance
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A5; absorbs A6, B27

**Q:** Your positive class is well under 1%. Explain why accuracy and ROC-AUC can look excellent while the model is unusable; connect base rates to precision, compare ROC-AUC with PR-AUC, and state what both curves hide about an operating threshold.

### A7 — Threshold Selection and Probability Calibration
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A7; absorbs A8

**Q:** Given asymmetric false-negative and false-positive costs plus a finite review capacity, show how you would choose an operating threshold. Then explain probability calibration, how to diagnose it, Platt versus isotonic calibration, and what class rebalancing does to calibrated probabilities.

### A9 — Offline-to-Online Metric Gaps
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A9

**Q:** Your IYML recommender showed a 5% apparel CTR gain offline, while sitewide CTR held neutral as a guardrail. An interviewer asks why an offline improvement so often fails to reproduce online. Give me the general mechanisms, then say which of them you can rule out for this specific result and which you cannot.

### A10 — Logistic Regression Fundamentals
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A10

**Q:** Walk me through logistic regression as if I had not seen it. What is it modeling, why is the output squashed by a sigmoid rather than clipped, why is squared error the wrong loss, and what exactly does a coefficient of 0.4 mean?

### A11 — MSE, MAE, and Huber Loss
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A11

**Q:** How do you choose a regression loss? Compare MSE, MAE, and Huber — not by their formulas but by what each one assumes about your errors and what each does when the assumption breaks. Then explain what a loss function has to do with a probability distribution at all.

### A12 — Bagging, Boosting, and Base Learners
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A12
**Prerequisites / cross-references:** B21/B22 foundations; decision-tree split mechanics are a required part of this conversation.  

**Q:** Explain bagging and boosting as answers to *different* problems. Use that framing to predict, without running anything, how each responds to a very deep base learner, to a noisy label, and to more estimators. Then tell me when you would pick a random forest over a gradient-boosted model in a real project.

**Follow-up tree:**
- Mechanically walk through one decision-tree split for classification and one for regression. State the split objective, what is greedy about the search, how leaf predictions are formed, and how depth/min-leaf constraints change bias and variance.

### A13 — Hyperparameter Search and Honest Evaluation
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A13

**Q:** You are tuning a gradient-boosted model with 8 hyperparameters. Describe how you would search, why random search usually beats grid search at equal budget, what Bayesian optimization buys you and when it does not, and how you would report a final performance number without lying to yourself.

**Follow-up tree:**
- When do you need nested cross-validation, and how do repeated hyperparameter/model-selection trials make an ordinary validation score optimistically biased?
### A14 — Model Selection and Feature Importance
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A14; absorbs A15
**Prerequisites / cross-references:** A12 for tree-ensemble mechanics; Bank 01 A9 for norm/regularization geometry when comparing linear models.  

**Q:** Given a medium-sized tabular problem, compare linear models, tree ensembles, kernel SVMs, and kNN by inductive bias, scaling, feature preprocessing, dimensionality, latency, and interpretability. Then compare built-in importance, permutation importance, and SHAP and explain how correlated features can mislead each.

**Follow-up tree:**
- For tree-based models, explain why monotonic feature scaling usually does not change split decisions, and contrast that with distance- and gradient-based model families.

### A16 — Dataset Shift and Drift Detection
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A16

**Q:** Your fraud index runs over a rolling 2-year window and your autocorrect serves a catalog of 500K+ SKUs that turns over continuously. Distinguish covariate shift, label shift, and concept drift in these two systems with a concrete example of each. Then tell me how you would detect each one *without* waiting for labels, and what the correct response to each is.

### A17 — Debugging Models Below Baseline
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A17

**Q:** You have just trained a model and it performs worse than a trivial baseline. Give me your diagnostic sequence, in order, and say what each step rules in or out. Assume you cannot ask anyone else and have half a day.

### A18 — Missing-Data Mechanisms and Imputation
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A18

**Q:** A feature is missing for 30% of rows. Explain how the reason it is missing changes what you are allowed to do about it, what mean imputation quietly assumes and quietly destroys, and why "just let XGBoost handle it" is sometimes right and sometimes not.

### A19 — Clustering with k-Means and DBSCAN
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A19

**Q:** You are asked to segment customers with no labels. Explain what k-means assumes, how you would choose k without pretending there is a right answer, and what kind of structure it will fail on. Say briefly what DBSCAN does differently and what it costs.

### A20 — Accuracy–Latency Deployment Tradeoffs
**Phase:** G1  
**Depth:** D2  
**Source mapping:** A20

**Q:** Your autocorrect serves under 10ms across roughly 2M monthly search sessions. Suppose a heavier model would raise offline accuracy from about 90% to 94%. Walk me through how you would decide whether to ship it — and make the case that this is a modeling question rather than an engineering one.

### B21 — Supervised, Unsupervised, and Representation Learning
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B21

**Q:** Distinguish supervised, unsupervised, self-supervised, and semi-supervised learning, and say where each shows up in a production system you would actually build.

### B22 — Parameters, Hyperparameters, and Data Splits
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B22

**Q:** Parameter versus hyperparameter. Give the definition, one example of each from a model you know well, and say what the train/validation/test split is for — specifically, why three sets and not two.

### B23 — Generative and Discriminative Models
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B23

**Q:** Generative versus discriminative models. State what each one models, give an example of each, and say one situation where the generative framing wins.

### B24 — Precision, Recall, and F1
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B24

**Q:** Define precision, recall, and F1 from a confusion matrix. Then say in one sentence what F1 hides, and why it is the wrong summary when the two error types have different costs.

### B25 — Feature Scaling by Model Family
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B25

**Q:** Which model families require feature scaling and which do not, and why? Name the mechanism, not the list.

### B26 — Overfitting, Underfitting, and Regularization
**Phase:** G2  
**Depth:** D1  
**Source mapping:** B26

**Q:** Define overfitting and underfitting without using the word "generalization," then say in one sentence what regularization is.

---

## Old → final disposition

- **A6 → FOLD/MERGE into A5.** Coverage is preserved in the final prompt/follow-ups.
- **A8 → FOLD/MERGE into A7.** Coverage is preserved in the final prompt/follow-ups.
- **A15 → FOLD/MERGE into A14.** Coverage is preserved in the final prompt/follow-ups.
- **B27 → FOLD/MERGE into A5.** Coverage is preserved in the final prompt/follow-ups.

## Final coverage rule

Mastering this bank means being able to answer the main prompts cold, handle any listed question-specific follow-ups, respond to reasonable gap-driven interviewer probes, and connect the concept to the relevant coding/project/system-design work. Exact wording may change in interviews; conceptual ownership should transfer.
