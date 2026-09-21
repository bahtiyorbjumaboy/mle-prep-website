---
type: interview-answer
item: "2026:bank01:B21"
title: "Trace, Determinant, and Log-Determinant"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - determinant
  - trace
  - gaussian-models
---

## Canonical Interview Question

What do the trace and the determinant tell you about a matrix, and what does each fail to tell you? Where does log-determinant show up in ML?

## Mastery Answer

For a square matrix $A$, the **trace**
$$
\operatorname{tr}(A)=\sum_i A_{ii}
$$
is also the sum of the eigenvalues, counting algebraic multiplicity.

The **determinant** is the signed volume-scaling factor of the linear transformation. Its magnitude $|\det(A)|$ tells how volumes scale, while its sign records orientation reversal. A zero determinant means the matrix is singular. The determinant is also the product of the eigenvalues.

Both are highly compressed scalar summaries. Trace does not reveal individual eigenvalues, eigenvectors, rank, or conditioning. A nonzero determinant proves full rank for a square matrix, but the determinant magnitude by itself is not a reliable conditioning diagnostic.

The **log-determinant** appears in multivariate Gaussian likelihoods and Gaussian-process objectives. For a covariance matrix $\Sigma$, $\log\det\Sigma$ measures covariance volume on a log scale and converts a product of eigenvalues into a sum:
$$
\log\det\Sigma=\sum_i\log\lambda_i.
$$

## Learn the Concepts

### Trace

The trace is
$$
\operatorname{tr}(A)=A_{11}+\cdots+A_{nn}.
$$

A fundamental identity is
$$
\operatorname{tr}(A)=\sum_i\lambda_i.
$$

Trace is invariant under a change of basis:
$$
\operatorname{tr}(Q^{-1}AQ)=\operatorname{tr}(A).
$$

This makes it a coordinate-independent scalar summary of a linear operator.

### Determinant

For a square matrix,
$$
\det(A)=\prod_i\lambda_i.
$$

Geometrically,
$$
|\det(A)|
$$
is the factor by which $A$ scales $n$-dimensional volume.

- $|\det(A)|>1$: volume expands.
- $0<|\det(A)|<1$: volume shrinks.
- $|\det(A)|=1$: volume magnitude is preserved.
- $\det(A)<0$: orientation is reversed.
- $\det(A)=0$: at least one dimension collapses, so $A$ is singular.

The magnitude, not the raw signed value, controls volume scaling.

### What these summaries miss

Two matrices can have the same trace and determinant but very different eigenvalue distributions, eigenvectors, geometry, and conditioning.

For example, determinant can be nonzero while the matrix is still badly conditioned: one singular value can be tiny while another is large enough to keep the product moderate.

### Why log-determinant?

For a positive-definite covariance matrix,
$$
\det(\Sigma)=\prod_i\lambda_i,
$$
so
$$
\log\det(\Sigma)=\sum_i\log\lambda_i.
$$

The logarithm turns a potentially huge or tiny product into a numerically and algebraically manageable sum.

In a multivariate Gaussian,
$$
-\log p(x)
$$
contains a quadratic Mahalanobis term and a normalization term involving
$$
\frac12\log\det\Sigma.
$$

The quadratic term penalizes distance relative to covariance geometry; the log-determinant term accounts for the volume occupied by the distribution.

## Required / Important Follow-ups

### Does $\det(A)>1$ always mean expansion?

No. Volume scaling depends on $|\det(A)|$. A determinant of $-3$ triples volume magnitude and reverses orientation.

### Can determinant diagnose conditioning?

Not reliably. Conditioning depends on the ratio of largest to smallest singular values, not their product.

### Why is log-determinant common for covariance matrices?

Covariance matrices are positive semidefinite, and positive-definite covariance matrices have positive eigenvalues. Log-determinant summarizes total variance-volume while being additive across eigen-directions.
