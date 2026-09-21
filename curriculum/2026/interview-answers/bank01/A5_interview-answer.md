---
type: interview-answer
item: "2026:bank01:A5"
title: "Ridge Regression in SVD Coordinates"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - ridge-regression
  - svd
  - regularization
---

## Canonical Interview Question

Rewrite ridge regression in the SVD coordinates of X. What does λ do to each direction of the feature space, and why does that explain both the stabilization and the bias ridge introduces? Then state what the sum of those per-direction factors represents.

## Mastery Answer

Let

$$
X = U\Sigma V^T.
$$

Ridge regression solves

$$
\hat w_{\lambda}
= (X^TX+\lambda I)^{-1}X^Ty.
$$

Using the SVD,

$$
X^TX = V\Sigma^2V^T,
\qquad
X^Ty = V\Sigma U^Ty.
$$

Therefore

$$
\hat w_{\lambda}
= V(\Sigma^2+\lambda I)^{-1}\Sigma U^Ty
= V\,\operatorname{diag}\!\left(\frac{\sigma_i}{\sigma_i^2+\lambda}\right)U^Ty.
$$

So in singular direction $v_i$, the ridge coefficient is

$$
\frac{\sigma_i}{\sigma_i^2+\lambda}(u_i^Ty).
$$

OLS uses

$$
\frac{1}{\sigma_i}(u_i^Ty),
$$

so ridge multiplies the OLS coefficient in direction $i$ by

$$
\frac{\sigma_i^2}{\sigma_i^2+\lambda}.
$$

This is the direction-specific shrinkage factor.

If $\sigma_i^2 \gg \lambda$, the factor is near $1$, so a well-determined direction changes little. If $\sigma_i^2 \ll \lambda$, the factor is near $0$, so a weak or nearly collinear direction is strongly suppressed.

That explains stabilization. In OLS, noise in a small-singular-value direction is amplified by division by $\sigma_i$, and the coefficient variance scales like $1/\sigma_i^2$ up to the noise variance factor. Ridge removes that amplification by damping exactly those poorly determined directions.

The trade-off is bias. For every $\lambda>0$, each retained direction is shrunk relative to OLS, so the expected coefficient is pulled toward zero. Ridge deliberately accepts bias in exchange for a potentially much larger variance reduction.

The sum of the per-direction shrinkage factors is

$$
\operatorname{df}(\lambda)
= \sum_i \frac{\sigma_i^2}{\sigma_i^2+\lambda}.
$$

This equals the trace of the ridge hat matrix and is the effective degrees of freedom: the effective number of parameter directions the fitted model is using after shrinkage.

## Learn the Concepts

### 1. Why OLS becomes unstable in small-singular-value directions

For full-column-rank least squares,

$$
\hat w_{\text{OLS}}=(X^TX)^{-1}X^Ty.
$$

Substitute $X=U\Sigma V^T$:

$$
\hat w_{\text{OLS}}
= V\Sigma^{-1}U^Ty.
$$

The coefficient along singular vector $v_i$ is therefore

$$
\frac{u_i^Ty}{\sigma_i}.
$$

A small singular value means the design matrix barely varies in that feature-space direction. Dividing by a tiny number makes the fitted coefficient extremely sensitive to noise or small perturbations in $y$ and $X$.

This is the SVD view of multicollinearity and ill-conditioning.

### 2. Ridge modifies the denominator rather than simply clipping coefficients

Ridge minimizes

$$
\|y-Xw\|_2^2 + \lambda\|w\|_2^2.
$$

The normal equations become

$$
(X^TX+\lambda I)w=X^Ty.
$$

In the $V$ basis, $X^TX$ is diagonal with entries $\sigma_i^2$, so ridge acts independently along each singular direction:

$$
\text{ridge filter}_i
= \frac{\sigma_i}{\sigma_i^2+\lambda}.
$$

The key point is that ridge is not uniform shrinkage in the original coordinates. It is adaptive to how well each singular direction is supported by the data.

### 3. Relative shrinkage compared with OLS

OLS has coefficient multiplier $1/\sigma_i$. Ridge has multiplier $\sigma_i/(\sigma_i^2+\lambda)$. Their ratio is

$$
\frac{\sigma_i/(\sigma_i^2+\lambda)}{1/\sigma_i}
= \frac{\sigma_i^2}{\sigma_i^2+\lambda}.
$$

This number lies in $(0,1)$ when $\lambda>0$ and $\sigma_i>0$.

- Large $\sigma_i$: almost no shrinkage.
- Small $\sigma_i$: aggressive shrinkage.
- Zero $\sigma_i$: the direction is unidentifiable from the data and ridge sets its fitted contribution to zero.

### 4. Why this reduces variance

Assume the standard linear model

$$
y=Xw^*+\varepsilon,
\qquad
\operatorname{Var}(\varepsilon)=\sigma_\varepsilon^2I.
$$

For OLS, the variance of the estimated coefficient in direction $v_i$ scales as

$$
\frac{\sigma_\varepsilon^2}{\sigma_i^2}.
$$

Thus directions with tiny $\sigma_i$ dominate estimator variance.

Ridge multiplies those directions by a factor close to zero, so it sharply reduces variance where the instability is worst. This is why ridge can make coefficient estimates much more stable under bootstrap resampling even though the training fit becomes slightly more biased.

### 5. Where the bias comes from

The same filter that suppresses noise also suppresses true signal. Relative to OLS, the expected coefficient in direction $v_i$ is multiplied by

$$
\frac{\sigma_i^2}{\sigma_i^2+\lambda}<1.
$$

So ridge intentionally underestimates coefficient magnitude. The statistical bet is that the reduction in variance is worth more than the added bias.

As $\lambda$ increases:

- variance decreases;
- bias increases;
- the fitted model becomes less flexible.

### 6. Effective degrees of freedom

The fitted values are

$$
\hat y = H_\lambda y,
$$

where

$$
H_\lambda
= X(X^TX+\lambda I)^{-1}X^T.
$$

Using the SVD,

$$
H_\lambda
= U\,\operatorname{diag}\!\left(\frac{\sigma_i^2}{\sigma_i^2+\lambda}\right)U^T.
$$

The eigenvalues of the smoother are therefore the same shrinkage factors. Its trace is

$$
\operatorname{tr}(H_\lambda)
= \sum_i \frac{\sigma_i^2}{\sigma_i^2+\lambda}.
$$

For OLS, each identifiable direction contributes approximately one full degree of freedom. Ridge lets each direction contribute a fractional amount between zero and one.

### 7. Limiting cases

If $\lambda\to0$, ridge approaches OLS on identifiable directions:

$$
\frac{\sigma_i^2}{\sigma_i^2+\lambda}\to1.
$$

If $\lambda\to\infty$,

$$
\frac{\sigma_i^2}{\sigma_i^2+\lambda}\to0,
$$

so the model collapses toward zero coefficients, assuming the intercept is handled separately and not penalized.

This gives a clean geometric interpretation of the regularization path: increasing $\lambda$ progressively removes effective model directions, beginning with the weakest singular directions.

## Required / Important Follow-ups

### Is ridge shrinkage uniform across directions?

No. Relative to OLS, singular direction $i$ is shrunk by

$$
\frac{\sigma_i^2}{\sigma_i^2+\lambda}.
$$

Small-singular-value directions are shrunk much more than large-singular-value directions.

### Why is the sum of shrinkage factors called effective degrees of freedom?

Because the ridge hat matrix has eigenvalues

$$
\frac{\sigma_i^2}{\sigma_i^2+\lambda},
$$

so

$$
\operatorname{df}(\lambda)
= \operatorname{tr}(H_\lambda)
= \sum_i\frac{\sigma_i^2}{\sigma_i^2+\lambda}.
$$

It measures how much total flexibility remains in the fitted linear smoother after regularization.

### What happens in a rank-deficient direction?

If $\sigma_i=0$, OLS cannot identify that coefficient direction from the data. Ridge makes the linear system invertible for $\lambda>0$ and assigns zero contribution to that unsupported singular direction in the fitted solution.
