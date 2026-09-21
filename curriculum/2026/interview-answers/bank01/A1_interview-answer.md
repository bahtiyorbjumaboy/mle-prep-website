---
type: interview-answer
item: "2026:bank01:A1"
title: "Multicollinearity and Unstable Regression Coefficients"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-regression
  - multicollinearity
  - conditioning
  - ridge
---

## Canonical Interview Question

You fit a linear regression on a marketing dataset. The model's R² is fine, but when you refit on bootstrap resamples the coefficients swing wildly in magnitude and several flip sign. A colleague suggests standardizing the features. Walk me through what is actually happening, whether standardizing will fix it, and what you would do.

## Mastery Answer

The pattern suggests **multicollinearity**, more precisely near-linear dependence among columns of the design matrix $X$. In SVD terms, one or more singular values are small, so
$$
\kappa(X)=\frac{\sigma_{\max}(X)}{\sigma_{\min}(X)}
$$
is large.

For ordinary least squares, under the classical homoskedastic model,
$$
\operatorname{Var}(\hat\beta\mid X)=\sigma^2(X^TX)^{-1}.
$$
Near-null directions of $X$ correspond to tiny eigenvalues of $X^TX$, so the inverse strongly amplifies perturbations. Bootstrap resampling changes the sample slightly, and the fitted coefficient vector can move a lot along those weakly identified directions, including sign flips.

Standardization can help if bad conditioning is partly caused by very different feature scales, but it does **not** remove genuine near-linear dependence. It therefore does not solve multicollinearity by itself.

Coefficient instability can coexist with fairly stable predictions on the observed data manifold because different coefficient vectors can produce similar fitted values there. But prediction stability is not guaranteed, especially in weakly supported directions or under extrapolation, so it should be checked directly.

What I do depends on the goal. For prediction, I would evaluate holdout and bootstrap prediction stability and consider ridge or another regularized model. For interpretation, I would diagnose the dependence using singular values, condition diagnostics, VIF or auxiliary regressions, and domain knowledge, then remove, combine, or reparameterize redundant variables where scientifically defensible.

## Learn the Concepts

### Why coefficients become unstable

Least squares solves
$$
\hat\beta=(X^TX)^{-1}X^Ty
$$
when $X$ has full column rank.

Using the SVD
$$
X=U\Sigma V^T,
$$
the estimator contains factors proportional to
$$
\frac{1}{\sigma_i}.
$$

A small singular value means the data contain very little information along that parameter direction. Small changes in $X$ or $y$ can therefore require a large coefficient change.

### Why R² can still look fine

Multicollinearity is primarily an **identifiability and variance** problem, not necessarily an in-sample fit problem. Multiple coefficient vectors can induce nearly the same predictions on the observed feature manifold.

This is why attribution can be unstable while predictive metrics remain acceptable.

### Why standardization is not the cure

Suppose one feature ranges in millions and another in thousandths. Standardization can reduce scale-induced anisotropy.

But if
$$
x_3\approx 2x_1-x_2,
$$
rescaling the columns does not remove that near-dependence. The weak direction remains.

### VIF

Variance inflation factor for feature $j$ can be written
$$
\operatorname{VIF}_j=\frac{1}{1-R_j^2},
$$
where $R_j^2$ comes from regressing feature $j$ on the remaining predictors.

It measures how much the variance of $\hat\beta_j$ is inflated by linear dependence with the rest of the design. It is more general than a pairwise-correlation check.

### Ridge

Ridge solves
$$
\min_\beta \|y-X\beta\|^2+\lambda\|\beta\|^2.
$$

Its normal equations are
$$
(X^TX+\lambda I)\beta=X^Ty.
$$

The added $\lambda I$ lifts weak eigen-directions away from zero and reduces variance, at the cost of bias.

## Required / Important Follow-ups

### Do unstable coefficients imply stable predictions?

No. They **can** coexist with stable predictions on the observed data manifold, but prediction stability must be measured rather than assumed.

### When can prediction instability become serious?

When evaluating points that move strongly in weakly supported directions, under distribution shift, or during extrapolation beyond the correlated training manifold.

### Does ridge make coefficients trustworthy for interpretation?

Not automatically. Ridge stabilizes estimation and shrinks variance, but it introduces bias and does not turn observational coefficients into causal effects.

### If interpretation matters, what else can you do?

Use domain knowledge to remove redundant variables, combine them into meaningful composites, redesign measurements, or explicitly report uncertainty and dependence rather than over-interpreting individual coefficients.
