---
type: interview-answer
item: "2026:bank01:A2"
title: "Conditioning, Gradient Descent, and Normal Equations"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - conditioning
  - least-squares
  - numerical-stability
---

## Canonical Interview Question

Define the condition number of a matrix in terms of its singular values. Explain what it predicts about (a) how fast gradient descent converges on a least-squares objective and (b) how much numerical error you should expect when solving for the coefficients. Then explain why forming and inverting XᵀX is a worse idea than it looks.

## Mastery Answer

For full-column-rank $X$, the 2-norm condition number is
$$
\kappa(X)=\frac{\sigma_{\max}(X)}{\sigma_{\min}(X)}.
$$
A large value means the transformation stretches some directions much more than others and that the inverse problem is sensitive to perturbations.

For least squares,
$$
f(\beta)=\frac12\|X\beta-y\|^2,
$$
the Hessian is
$$
H=X^TX.
$$
Its eigenvalues are $\sigma_i(X)^2$, so
$$
\kappa(H)=\kappa(X)^2.
$$
Therefore gradient-descent geometry is governed by the **squared** condition number of $X$. For a positive-definite quadratic with the optimal fixed step size, the contraction factor is
$$
\frac{\kappa(H)-1}{\kappa(H)+1}
=
\frac{\kappa(X)^2-1}{\kappa(X)^2+1}.
$$
As the condition number grows, the factor approaches one and convergence becomes slow.

Numerically, the condition number is a first-order sensitivity factor: relative perturbations can be amplified roughly in proportion to $\kappa$. A rule of thumb is that $\kappa\approx 10^p$ can cost about $p$ decimal digits in a worst-case relative-error sense.

Forming $X^TX$ is dangerous because
$$
\kappa(X^TX)=\kappa(X)^2.
$$
It squares the sensitivity before solving. Explicitly forming an inverse is also unnecessary and less stable than solving a system. QR is usually the stable default for full-rank least squares; SVD is preferred when conditioning is severe or rank deficiency matters.

## Learn the Concepts

### What condition number measures

For the 2-norm,
$$
\kappa(X)=\|X\|_2\|X^+\|_2.
$$

For full column rank this becomes the singular-value ratio. If $\sigma_{\min}$ is tiny, there is a direction that $X$ almost collapses. Recovering coefficients along that direction requires strong amplification.

### Least-squares geometry

The level sets of a quadratic objective are ellipsoids. The curvature in an eigen-direction of $H$ is the corresponding eigenvalue.

For least squares,
$$
H=X^TX=V\Sigma^2V^T.
$$

So curvature ratios are
$$
\frac{\sigma_{\max}^2}{\sigma_{\min}^2}
=
\kappa(X)^2.
$$

A highly elongated valley causes vanilla gradient descent to make progress at very different rates across directions, producing zig-zagging and slow contraction.

### Numerical sensitivity

Conditioning is a property of the mathematical problem; numerical stability is a property of the algorithm. A badly conditioned problem is intrinsically sensitive, while a poor algorithm can make matters even worse.

### Why normal equations square conditioning

The singular values of $X^TX$ are the squared singular values of $X$:
$$
\lambda_i(X^TX)=\sigma_i(X)^2.
$$

Therefore the ratio of largest to smallest becomes squared.

### Why avoid explicit inversion?

Even when the normal equations are used, one should solve
$$
(X^TX)\beta=X^Ty
$$
with a linear solver rather than compute
$$
(X^TX)^{-1}
$$
explicitly. Explicit inversion adds work and typically worsens numerical behavior.

## Required / Important Follow-ups

### Which condition number governs gradient descent?

The Hessian condition number:
$$
\kappa(H)=\kappa(X^TX)=\kappa(X)^2.
$$

### Is “lose $p$ digits when $\kappa=10^p$” exact?

No. It is a worst-case rule of thumb for relative sensitivity, not a guaranteed exact digit loss on every problem.

### What methods avoid forming $X^TX$?

QR solves least squares directly through an orthogonal-triangular factorization. SVD works through singular directions and is especially useful for ill-conditioning and rank deficiency.
