---
type: interview-answer
item: "2026:bank01:A8"
title: "Positive Definite and Positive Semi-Definite Matrices"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - positive-definite
  - positive-semidefinite
  - covariance
---

## Canonical Interview Question

What does it mean for a matrix to be positive definite versus positive semi-definite, and how would you actually check in practice? Give me three matrices that show up in ML that are guaranteed PSD and explain why. What does it mean if your empirical covariance matrix comes back with a slightly negative eigenvalue?

## Mastery Answer

For a real symmetric matrix $A$:

- $A$ is positive definite (PD) if

$$
z^TAz>0
$$

for every nonzero $z$.

- $A$ is positive semi-definite (PSD) if

$$
z^TAz\ge0
$$

for every $z$.

The exclusion of $z=0$ matters for PD because $0^TA0=0$ for every matrix.

For symmetric matrices, the equivalent eigenvalue test is:

- PD iff every eigenvalue is strictly positive;
- PSD iff every eigenvalue is nonnegative.

In practice, if I expect a symmetric matrix to be PD, I would usually try a Cholesky factorization

$$
A=LL^T.
$$

Standard unpivoted Cholesky succeeds for a symmetric/Hermitian PD matrix and is typically cheaper than computing a full eigendecomposition. If I specifically need to diagnose PSD or near-singularity, I would inspect the symmetric eigenspectrum or use a numerically appropriate symmetric factorization.

Three common PSD matrices in ML are all instances of the same squared-norm argument.

First, a Gram matrix $X^TX$ is PSD because

$$
z^TX^TXz
= (Xz)^T(Xz)
= \|Xz\|_2^2
\ge0.
$$

Second, a covariance matrix of centered data is

$$
C=\frac{1}{n-1}X^TX,
$$

so it is just a nonnegative scalar multiple of a Gram matrix and is therefore PSD.

Third, a kernel Gram matrix is PSD for any valid PSD kernel. If

$$
k(x_i,x_j)=\langle \phi(x_i),\phi(x_j)\rangle,
$$

then the kernel matrix is simply a Gram matrix in feature space.

These matrices are strictly PD only when there is no nonzero null direction. For example, $X^TX$ is PD iff $X$ has full column rank.

A true covariance matrix cannot have a negative eigenvalue mathematically. If an empirical covariance matrix has a very small negative eigenvalue, the usual explanation is floating-point error around a true zero or tiny positive eigenvalue, often in a nearly rank-deficient problem. I would judge the magnitude relative to matrix scale, dimension, conditioning, and solver tolerance. A materially negative eigenvalue is a reason to inspect symmetry, missing-value handling, weighting, preprocessing, or the covariance construction itself.

If a downstream method requires strict PD, adding a small diagonal jitter $\varepsilon I$ can lift the spectrum away from zero. If the goal is simply to restore PSD structure, one can also project onto the PSD cone by clipping small negative eigenvalues, while recognizing that this changes the matrix.

## Learn the Concepts

### 1. Quadratic forms are the central object

The quantity

$$
z^TAz
$$

is the quadratic form associated with $A$. For a symmetric matrix, it tells us whether the matrix assigns positive, zero, or negative curvature/energy to a direction $z$.

- PD means every nonzero direction has strictly positive quadratic form.
- PSD means no direction has negative quadratic form, but some directions may be flat.

Those flat directions are exactly what distinguish singular PSD matrices from PD matrices.

### 2. Why eigenvalues characterize PD and PSD

For a real symmetric matrix, the spectral theorem gives

$$
A=Q\Lambda Q^T.
$$

Let $c=Q^Tz$. Then

$$
z^TAz
= z^TQ\Lambda Q^Tz
= c^T\Lambda c
= \sum_i \lambda_i c_i^2.
$$

Because each $c_i^2\ge0$, the sign of the quadratic form is controlled entirely by the eigenvalues.

Therefore:

- all $\lambda_i>0$ implies PD;
- all $\lambda_i\ge0$ implies PSD;
- any $\lambda_i<0$ means the matrix is indefinite rather than PSD.

### 3. Cholesky as a practical PD check

For a symmetric PD matrix,

$$
A=LL^T
$$

with $L$ lower triangular and positive diagonal entries.

Cholesky is attractive when PD is expected because it is computationally efficient and directly gives a factor useful for solving linear systems and Gaussian likelihoods.

A singular PSD matrix may fail standard Cholesky because a zero pivot appears. That failure does not imply the matrix has a genuinely negative direction; it can simply be PSD rather than strictly PD.

### 4. Why Gram matrices are PSD

A Gram matrix stores pairwise inner products. For $G=X^TX$,

$$
z^TGz=\|Xz\|_2^2.
$$

Squared norms cannot be negative, so every Gram matrix is PSD.

It is strictly PD iff $Xz\ne0$ for every nonzero $z$, which is exactly the condition that $X$ has full column rank.

### 5. Covariance matrices are Gram matrices of centered data

If $X_c$ is centered data, then

$$
C=\frac{1}{n-1}X_c^TX_c.
$$

So covariance is automatically PSD.

If $d>n-1$, then the centered data can have rank at most $n-1$, so the covariance matrix must be singular. This is common in high-dimensional ML: zero eigenvalues can be structurally inevitable, not a bug.

### 6. Kernel matrices inherit PSD from feature-space inner products

A valid PSD kernel behaves like an inner product in some feature space:

$$
k(x,x')=\langle\phi(x),\phi(x')\rangle.
$$

For coefficients $c$,

$$
c^TKc
= \left\|\sum_i c_i\phi(x_i)\right\|_2^2
\ge0.
$$

This PSD property is what makes kernel methods mathematically well behaved.

### 7. Interpreting a slightly negative covariance eigenvalue

Exact covariance is PSD, but floating-point arithmetic is finite precision. Rounding error, imperfect symmetry, and ill-conditioning can perturb an eigenvalue that should be zero into a tiny negative number.

The correct diagnostic is relative, not purely absolute. Compare the negative eigenvalue with quantities such as:

- the largest eigenvalue;
- the matrix norm;
- the matrix dimension;
- expected floating-point tolerance;
- the condition number.

A value extremely close to zero can be numerical noise. A substantial negative value should trigger investigation of the pipeline rather than automatic clipping.

### 8. Jitter and ridge share the same eigenvalue-lifting operation

If

$$
A=Q\Lambda Q^T,
$$

then

$$
A+\varepsilon I
=Q(\Lambda+\varepsilon I)Q^T.
$$

Every eigenvalue increases by $\varepsilon$. Numerically, this can turn a nearly singular PSD matrix into a safely PD matrix. Algebraically this is the same spectrum-shifting operation that appears in ridge regression, although the modeling interpretation is different.

## Required / Important Follow-ups

### Does Cholesky test PSD as well as PD?

Not in the ordinary unpivoted form. Standard Cholesky is fundamentally a strict-PD factorization for symmetric/Hermitian matrices. A singular PSD matrix can fail because a pivot is zero.

### When is $X^TX$ strictly PD?

Exactly when $X$ has full column rank. If some nonzero $z$ satisfies $Xz=0$, then

$$
z^TX^TXz=0,
$$

so the matrix is PSD but not PD.

### What should I do with a small negative eigenvalue?

First determine whether it is plausibly numerical by comparing it with matrix scale and tolerance. If the matrix is supposed to be a covariance matrix and the value is only tiny relative to the spectrum, numerical error is likely. If it is materially negative, check how the matrix was constructed before repairing it. Jitter is appropriate when strict PD is required; eigenvalue clipping is a different repair that projects back toward PSD structure.
