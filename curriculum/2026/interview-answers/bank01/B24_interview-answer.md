---
type: interview-answer
item: "2026:bank01:B24"
title: "Eigenvalues, the Spectral Theorem, and PCA"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - eigenvalues
  - spectral-theorem
  - pca
---

## Canonical Interview Question

State the eigenvalue equation and what it means geometrically. What does the spectral theorem guarantee for symmetric matrices, and why does that guarantee matter so often in ML?

## Mastery Answer

An eigenpair satisfies
$$
Ax=\lambda x,
$$
with $x\neq 0$. Geometrically, $x$ is a direction that $A$ does not rotate away from its own line: $A$ only scales it. The magnitude $|\lambda|$ controls the scale change, while the sign controls direction reversal.

- $|\lambda|>1$: stretch.
- $0<|\lambda|<1$: shrink.
- $\lambda<0$: reverse direction in addition to scaling.
- $\lambda=0$: collapse that direction to zero.

For a real symmetric matrix, the spectral theorem guarantees real eigenvalues and an orthonormal eigenbasis. Equivalently,
$$
A=Q\Lambda Q^T
$$
with orthogonal $Q$ and diagonal real $\Lambda$.

This matters in ML because many important matrices are symmetric: covariance matrices, Gram matrices, Hessians, and many kernel matrices. Their geometry can be analyzed along orthogonal eigen-directions.

For PCA, if
$$
\Sigma=Q\Lambda Q^T
$$
and centered data are transformed to
$$
z=Q^Tx,
$$
then
$$
\operatorname{Cov}(z)
=
Q^T\Sigma Q
=
\Lambda.
$$
Because $\Lambda$ is diagonal, the principal-component coordinates are uncorrelated, and each eigenvalue is the variance along its corresponding principal component.

## Learn the Concepts

### Eigenvectors and eigenvalues

Most vectors change both direction and magnitude under a matrix transformation. An eigenvector is special:
$$
Ax=\lambda x.
$$

It stays on the same one-dimensional line.

The scale factor is governed by $|\lambda|$, not merely by whether $\lambda$ is numerically greater or less than $1$. For example, $\lambda=-3$ triples magnitude and reverses direction.

### Spectral theorem

For real symmetric $A$,
$$
A=A^T,
$$
the spectral theorem gives:

1. all eigenvalues are real;
2. eigenvectors can be chosen orthonormal;
3. $A$ can be orthogonally diagonalized:
$$
A=Q\Lambda Q^T.
$$

Because $Q$ is orthogonal,
$$
Q^{-1}=Q^T.
$$

The decomposition turns a complicated linear transformation into independent scalar actions along orthogonal coordinates.

### PCA

For centered data, PCA diagonalizes the covariance matrix.

If
$$
\Sigma=Q\Lambda Q^T,
$$
then PCA coordinates are
$$
z=Q^Tx.
$$

Their covariance is
$$
\operatorname{Cov}(z)
=
Q^T\Sigma Q
=
Q^TQ\Lambda Q^TQ
=
\Lambda.
$$

The off-diagonal entries vanish, so principal components are uncorrelated. The diagonal entries are their variances.

The uncorrelated result comes from **diagonalizing the covariance matrix**, not merely from the fact that the axes are orthogonal.

### Hessians

At a critical point, a symmetric Hessian has real eigenvalues.

- all eigenvalues strictly positive: strict local minimum;
- mixed signs: saddle;
- zero eigenvalues: the second-order test is inconclusive along flat directions.

## Required / Important Follow-ups

### Does a negative eigenvalue mean shrinkage?

Not necessarily. Magnitude and sign play different roles. $\lambda=-4$ stretches by a factor of four and reverses direction.

### Why is orthogonal diagonalization numerically convenient?

Orthogonal transformations preserve Euclidean norms and have inverse equal to transpose, which avoids introducing additional conditioning from the change of basis.

### Why do PCA eigenvalues represent variance?

Each diagonal entry of $\Lambda=Q^T\Sigma Q$ is the variance of the corresponding transformed principal-component coordinate.
